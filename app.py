import streamlit as st 
import os
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from gtts import gTTS
import base64
import re
from dotenv import load_dotenv

# --- 1. Global API Key & Environment Setup (FIXED & SECURE) ---
# Pehle .env file load karein taake agar local ho to os.environ me key aa jaye
load_dotenv()

# Streamlit Secrets ya .env se key uthane ka saba se behtareen tareeqa
if "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
else:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    if OPENAI_API_KEY:
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

# --- 4. LangGraph Core State Framework & Padding System ---
class AgentState(TypedDict):
    messages: list[AnyMessage]
    menu_data: str

def manager_node(state: AgentState):
    # FIXED: Explicitly passing api_key to avoid connection drops
    if not OPENAI_API_KEY:
        return {"messages": [AIMessage(content="⚠️ API Key missing. Please check your .env file or Streamlit Secrets.")]}
        
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.6, openai_api_key=OPENAI_API_KEY)
    
    system_prompt = f"""
    You are the polite, energetic, and highly professional AI Sales Representative of 'Siddique Brothers Restaurant' located in Karachi.
    Your objective is to guide customers flawlessly through our premium menu choices, answer prices, and craft brilliant deals.
    
    CRITICAL INSTRUCTIONS:
    1. Respond in clear, natural English with a welcoming and premium tone.
    2. Format items elegantly using bold text and clean bullet points for easy reading.
    3. Keep your answers slightly concise so that it looks good when spoken out loud.
    4. Do not hallucinate items outside the menu.
    
    OFFICIAL RESTAURANT MENU:
    {state['menu_data']}
    """
    
    padded_messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    try:
        bot_output = llm.invoke(padded_messages)
        return {"messages": [AIMessage(content=bot_output.content)]}
    except Exception as e:
        return {"messages": [AIMessage(content=f"⚠️ Connection Notice: {str(e)}")]}

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

# --- RIGHT COLUMN: AI CHATBOT SALES COUNTER ---
with col2:
    st.markdown("<h2 style='margin-top: 0;'>💬 Smart Voice Desk</h2>", unsafe_allow_html=True)
    
    # Text input fallback for quick testing and seamless chats
    user_text = st.text_input("Type your order/question here:", key="user_message_input")
    
    if st.button("Send Message") and user_text:
        # Run AI processing logic
        menu_content = get_full_menu_for_ai()
        
        # Append User Message to history format
        st.session_state.chat_history.append(HumanMessage(content=user_text))
        
        # Invoke LangGraph
        config = {"configurable": {"thread_id": "restaurant_live_session"}}
        response = restaurant_app.invoke(
            {"messages": st.session_state.chat_history, "menu_data": menu_content}, 
            config
        )

        
        # Update chat history with AI Response
        st.session_state.chat_history = response["messages"]
    
    # Display Elegant Chat History Inside Glass Card UI
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if isinstance(msg, HumanMessage):
            st.markdown(f"**👤 You:** {msg.content}")
        elif isinstance(msg, AIMessage):
            st.markdown(f"**🤖 Agent:** {msg.content}")
            st.write("---")
    st.markdown("</div>", unsafe_allow_html=True)
