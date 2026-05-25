import streamlit as st 
import os
import base64
import streamlit.components.v1 as components
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from openai import OpenAI

# --- 1. Global Setup (Groq Key for AI, OpenAI Key for Whisper Voice) ---
GROQ_API_KEY = "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"
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Voice Processing (Whisper) ke liye aapki fresh OpenAI key yahan use hogi
OPENAI_API_KEY = "YOUR_NEW_OPENAI_API_KEY_HERE" 

# --- 2. Premium UI Custom Styles ---
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
        </style>
        """,
        unsafe_allow_html=True
    )

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

# --- 4. LangGraph Core Framework ---
class AgentState(TypedDict):
    messages: list[AnyMessage]
    menu_data: str

def manager_node(state: AgentState):
    # Upgraded stable model
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY, temperature=0.5)
    
    system_prompt = f"""You are the polite, energetic, and highly professional AI Sales Representative of 'Siddique Brothers Restaurant' located in Karachi.
    if any person say assalamualaikum ans them w salam !.
    if any one say hi say it assalamualaikum .
    you are ai agent not a human attitude it like a robot not a human .
    not saying it wsalam in every message.
    if someone ask except about rasturant do say sorry dear i just create for rasturant menu and order comfirmation and like that .
Your objective is to guide customers flawlessly through our premium menu choices, answer prices, and craft brilliant deals.
never say assalamualaikum in every message just say 1 time when the talking start 
you can send every emojis no problem buddy 
CRITICAL INSTRUCTIONS:
1. Respond in clear, natural English with a welcoming tone.
2. Format items elegantly using bold text and clean bullet points.
3. Keep your answers slightly concise and to the point.
4. just reply about rasturant things and advice whitch thing is good or avarag.

OFFICIAL RESTAURANT MENU:
{state['menu_data']}"""

    formatted_messages = [SystemMessage(content=system_prompt)]
    
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            formatted_messages.append(HumanMessage(content=msg.content))
        elif isinstance(msg, AIMessage):
            formatted_messages.append(AIMessage(content=msg.content))
            
    try:
        bot_output = llm.invoke(formatted_messages)
        return {"messages": [AIMessage(content=bot_output.content)]}
    except Exception as e:
        return {"messages": [AIMessage(content=f"⚠️ Counter Engine Sync Notice: {str(e)}")]}

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
st.markdown("<p style='text-align: center; color: #b0b0b5 !important; font-size: 16px;'>Experience the future of premium dining</p>", unsafe_allow_html=True)
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

# --- RIGHT COLUMN: AI CHATBOT SALES COUNTER (WITH PREMIUM MIC) ---
with col2:
    st.markdown("<h2 style='margin-top: 0;'>💬SB-COUNTER-AGENT</h2>", unsafe_allow_html=True)
    
    processed_query = ""
    
    # 🎙️ LIVE VOICE RECORDER CONTROLLER
  # ⌨️ TEXT FORM INPUT
    with st.form(key="chat_form", clear_on_submit=True):
        text_query = st.text_input("Or type your message here instead:")
        submit_button = st.form_submit_button(label="Send Message")
        
    if submit_button and text_query:
        processed_query = text_query
    
    # --- Execute LangGraph Processing ---
    if processed_query:
        st.session_state.chat_history.append(HumanMessage(content=processed_query))
        
        initial_state = {
            "messages": st.session_state.chat_history,
            "menu_data": get_full_menu_for_ai()
        }
        config = {"configurable": {"thread_id": "sami_restaurant_session"}}
        final_output = restaurant_app.invoke(initial_state, config=config)
        
        ai_msg = final_output["messages"][-1]
        st.session_state.chat_history.append(ai_msg)

    # Chat History Render Panel
    if st.session_state.chat_history:
        st.markdown("<h3 style='margin-top: 20px; font-size: 16px; color: #ff4b4b !important;'>Live Counter Chat History</h3>", unsafe_allow_html=True)
        for msg in reversed(st.session_state.chat_history):
            if isinstance(msg, AIMessage):
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <h4 style='margin-top:0; color:#ff4b4b !important; font-size:15px; margin-bottom: 8px;'>🤖 Siddique Brothers Agent:</h4>
                        <p style='font-size:15px; line-height: 1.6; margin: 0; white-space: pre-line;'>{msg.content}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif isinstance(msg, HumanMessage):
                st.markdown(
                    f"""
                    <div style="padding: 10px 12px; background: rgba(255,255,255,0.04); border-radius: 8px; margin-bottom: 5px; margin-top: 5px;">
                        <span style="color: #ff4b4b !important; font-weight: bold;">👤 You:</span> <span style="font-size: 15px; color: white !important;">{msg.content}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
