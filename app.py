import streamlit as st 
import os
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from gtts import gTTS
import base64

# --- 1. Global API Key & Environment Setup ---
OPENAI_API_KEY = "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"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# --- 2. Ultra-Clean UI Custom Styles ---
def apply_premium_styles_from_url():
    bg_style = "linear-gradient(135deg, #14141f 0%, #0b0b10 100%)"    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {bg_style};
            background-size: cover;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
        
        .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label {{
            color: #ffffff !important;
            font-family: 'Segoe UI', sans-serif;
        }}
        
        .glass-card {{
            background: rgba(22, 22, 30, 0.85) !important; 
            backdrop-filter: blur(12px);
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 22px !important;
            margin-top: 15px;
            margin-bottom: 15px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        }}
        
        .stTextInput input {{
            color: #000000 !important;
            background-color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 500;
        }}
        
        /* Custom Premium Mic Button Pulsing Effect */
        .mic-btn {{
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(255, 75, 75, 0.4);
            transition: all 0.3s ease;
        }}
        .mic-btn:hover {{
            background-color: #e03e3e;
            transform: scale(1.02);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Voice Sunane K Liye (Text-To-Speech Autoplay Setup) ---
def play_voice_output(text_to_speak):
    try:
        clean_text = text_to_speak.replace("**", "").replace("*", "").replace("`", "")
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save("response.mp3")
        
        with open("response.mp3", "rb") as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay="true" />'
        st.markdown(audio_html, unsafe_allow_html=True)
        
        if os.path.exists("response.mp3"):
            os.remove("response.mp3")
    except Exception as e:
        pass

# --- 3. Menu Data File Parsers ---
def get_category_menu(category_name):
    file_path = "data/menu.txt"
    if not os.path.exists(file_path):
        return "📋 Menu details will appear here once data/menu.txt is loaded."
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    sections = content.split("---")
    for i in range(len(sections)):
        clean_section = sections[i].strip().upper()
        if category_name.upper() in clean_section:
            if i + 1 < len(sections):
                return sections[i+1].strip()
    return "Items coming soon!"

def get_full_menu_for_ai():
    file_path = "data/menu.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return "Menu: Fast Food, Pizza, Biryani, Karahi, Nihari, Drinks, Ice Cream available."

# --- 4. LangGraph Core State Framework & Padding System ---
class AgentState(TypedDict):
    messages: list[AnyMessage]
    menu_data: str

def manager_node(state: AgentState):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6)
    
    system_prompt = f"""
    You are the polite, energetic, and highly professional AI Sales Representative of 'Siddique Brothers Restaurant'.
    Your objective is to guide customers flawlessly through our premium menu choices, answer prices, and craft brilliant deals.
    
    CRITICAL INSTRUCTIONS:
    1. Respond in clear, natural English with a welcoming and premium tone.
    2. Format items elegantly using bold text and clean bullet points for easy reading.
    3. Keep your answers slightly concise so that it sounds good when spoken out loud.
    4. Do not hallucinate items outside the menu.
    
    OFFICIAL RESTAURANT MENU:
    {state['menu_data']}
    """
    
    padded_messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    try:
        bot_output = llm.invoke(padded_messages)
        return {"messages": [AIMessage(content=bot_output.content)]}
    except Exception as e:
        return {"messages": [AIMessage(content=f"⚠️ Connection Setup Note: {str(e)}")]}

workflow = StateGraph(AgentState)
workflow.add_node("manager", manager_node)
workflow.add_edge(START, "manager")
workflow.add_edge("manager", END)

memory = MemorySaver()
restaurant_app = workflow.compile(checkpointer=memory)

# --- 5. Streamlit Main Interface Render ---
st.set_page_config(page_title="SB-RESTAURANT AI", page_icon="🍔", layout="wide")
apply_premium_styles_from_url()

st.markdown("<h1 style='text-align: center; font-weight: 700; margin-bottom: 5px;'>🍔 Siddique Brothers AI Sales Counter</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #b0b0b5 !important; font-size: 16px;'>Experience the future of premium dining with Full-Voice Automation</p>", unsafe_allow_html=True)
st.write("---")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

col1, col2 = st.columns([1.1, 1], gap="large")

# --- LEFT COLUMN: DIGITAL PORTAL MENU ---
with col1:
    st.markdown("<h2 style='margin-top: 0;'>📋 Interactive Digital Menu</h2>", unsafe_allow_html=True)  
    with st.expander("📖 CLICK TO EXPAND LIVE RESTAURANT MENU", expanded=True):
        st.markdown("<h3 style='color:#ff4b4b !important; text-align:center; font-size: 18px;'>🍽️ EXPLORE OUR CUISINES</h3>", unsafe_allow_html=True)
        
        category_choice = st.selectbox(
            "Select Category:", 
            ["Click to expand...", "🍔 FAST FOOD & BURGERS", "🍕 PIZZA CORNER", "🍛 BIRYANI & TRADITIONAL RICE", "🍲 KARAHI & TRADITIONAL HANDI", "🍖 NIHARI", "🥤 REFRESHMENTS & DRINKS", "🍦 ICE CREAM PARLOR"],
            label_visibility="collapsed",
            key="category_select"
        )
        st.write("---")
        
        if category_choice != "Click to expand...":
            target = "FAST FOOD & BURGERS"
            if "FAST FOOD" in category_choice: target = "FAST FOOD & BURGERS"
            elif "PIZZA" in category_choice: target = "PIZZA CORNER"
            elif "BIRYANI" in category_choice: target = "BIRYANI & TRADITIONAL RICE"
            elif "KARAHI" in category_choice: target = "KARAHI & TRADITIONAL HANDI"
            elif "NIHARI" in category_choice: target = "RAWAL / NIHARI"
            elif "REFRESHMENTS" in category_choice: target = "REFRESHMENTS & DRINKS"
            elif "ICE CREAM" in category_choice: target = "ICE CREAM PARLOR"
                
            st.markdown(f"<h4 style='color:#ff4b4b; margin-bottom: 10px;'>{category_choice}:</h4>", unsafe_allow_html=True)
            st.code(get_category_menu(target), language="text")

# --- RIGHT COLUMN: AI CHATBOT SALES COUNTER (Real-Time Mic Pipeline) ---
with col2:
    st.markdown("<h2 style='margin-top: 0;'>💬 Smart Voice Desk</h2>", unsafe_allow_html=True)
    
    processed_query = ""
    latest_ai_response = ""
    
    # 🎤 NATIVE BROWSER HTML5 RECORDER (Bypasses local Streamlit mic issues)
    st.markdown("<span style='font-size: 14px; font-weight: 500; color: #ff4b4b !important;'>🎙️ Tap Mic to Speak Directly:</span>", unsafe_allow_html=True)
    
    import streamlit.components.v1 as components
    
    # Custom high-speed native JavaScript voice recorder component
    custom_mic_html = """
    <div style="text-align: center; padding: 10px;">
        <button id="recordBtn" class="mic-btn" style="background-color: #ff4b4b; color: white; border: none; padding: 12px 24px; border-radius: 50px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 12px rgba(255,75,75,0.3);">🎙️ CLICK TO TALK</button>
        <p id="status" style="color: #b0b0b5; font-family: sans-serif; font-size: 13px; margin-top: 8px;">Ready to record</p>
    </div>
    
    <script>
        let mediaRecorder;
        let audioChunks = [];
        const recordBtn = document.getElementById('recordBtn');
        const status = document.getElementById('status');
        let isRecording = false;

        recordBtn.onclick = async () => {
            if (!isRecording) {
                audioChunks = [];
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = e => {
                    audioChunks.push(e.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        // Send the audio back to Streamlit window seamlessly
                        window.parent.postMessage({type: 'streamlit:setComponentValue', value: base64Audio}, '*');
                    };
                    status.innerText = "Processing Voice...";
                    recordBtn.style.backgroundColor = "#ff4b4b";
                    recordBtn.innerText = "🎙️ CLICK TO ASK";
                };

                mediaRecorder.start();
                isRecording = true;
                status.innerText = "🔴 Listening... Speak now!";
                recordBtn.style.backgroundColor = "#d32f2f";
                recordBtn.innerText = "⏹️ STOP RECORDING";
            } else {
                mediaRecorder.stop();
                isRecording = false;
            }
        };
    </script>
    """
    
    # Render the custom component cleanly
    voice_data = components.html(custom_mic_html, height=100)
    
    # Catch the incoming JS background signal
    if voice_data:
        with st.spinner("Converting voice to text..."):
            try:
                # Convert the base64 browser data straight back into binary bytes
                raw_voice_bytes = base64.b64decode(voice_data)
                audio_file_payload = ("live_audio.wav", raw_voice_bytes, "audio/wav")
                
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
                
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file_payload
                )
                
                if transcription.text:
                    processed_query = transcription.text
                    st.info(f"🗣️ You Said: \"{processed_query}\"")
            except Exception as e:
                pass

    st.write("---")
    
    # ⌨️ TEXT INPUT OPTION
    with st.form(key="chat_form", clear_on_submit=True):
        text_query = st.text_input("Or type your message here instead:")
        submit_button = st.form_submit_button(label="Send Message")
        
    if submit_button and text_query:
        processed_query = text_query
    
    # --- Execute LangGraph State Graph Processing ---
    if processed_query:
        st.session_state.chat_history.append(HumanMessage(content=processed_query))
        with st.spinner("Siddique Brothers Agent responding..."):
            initial_state = {
                "messages": st.session_state.chat_history,
                "menu_data": get_full_menu_for_ai()
            }
            config = {"configurable": {"thread_id": "sami_restaurant_session"}}
            final_output = restaurant_app.invoke(initial_state, config=config)
            
            ai_msg = final_output["messages"][-1]
            st.session_state.chat_history.append(ai_msg)
            latest_ai_response = ai_msg.content

    # 🔊 VOICE SUNAYE (Automatic Background Voice Trigger)
    if latest_ai_response:
        play_voice_output(latest_ai_response)

    # Rendering the History Panel Look
    if st.session_state.chat_history:
        st.markdown("<h3 style='margin-top: 20px; font-size: 16px; color: #ff4b4b !important;'>Live Counter Chat History</h3>", unsafe_allow_html=True)
        for msg in reversed(st.session_state.chat_history):
            if isinstance(msg, AIMessage):
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <h4 style='margin-top:0; color:#ff4b4b !important; font-size:15px; margin-bottom: 8px;'>🤖 Siddique Brothers Agent (Speaking):</h4>
                        <p style='font-size:15px; line-height: 1.6; margin: 0; white-space: pre-line;'>{msg.content}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif isinstance(msg, HumanMessage):
                st.markdown(
                    f"""
                    <div style="padding: 10px 12px; background: rgba(255,255,255,0.04); border-radius: 8px; margin-bottom: 5px; margin-top: 5px;">
                        <span style="color: #ff4b4b !important; font-weight: bold;">👤 You:</span> <span style="font-size: 15px;">{msg.content}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
