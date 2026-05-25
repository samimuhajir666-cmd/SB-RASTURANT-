import streamlit as st 
import os
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage

# --- 1. Global Setup ---
# --- 1. Global Setup ---
GROQ_API_KEY = "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"
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
# --- 2. Premium UI Styles ---
def apply_premium_styles_from_url():
    bg_style = "linear-gradient(135deg, #14141f 0%, #0b0b10 100%)"    
    st.markdown(
        f"""
        <style>
        .stApp {{ background: {bg_style}; background-size: cover; background-attachment: fixed; }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
        .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label {{ color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }}
        .glass-card {{ background: rgba(22, 22, 30, 0.85) !important; backdrop-filter: blur(12px); border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.08); padding: 22px !important; margin-top: 15px; margin-bottom: 15px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5); }}
        .stTextInput input {{ color: #000000 !important; background-color: #ffffff !important; border-radius: 8px !important; font-weight: 500; }}
        </style>
        """,
        unsafe_allow_html=True
    )

def get_full_menu_for_ai():
    file_path = "data/menu.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file: return file.read()
    return "Menu options available."

# --- 3. LangGraph Framework ---
class AgentState(TypedDict):
    messages: list[AnyMessage]
    menu_data: str
    api_key: str

def manager_node(state: AgentState):
    user_key = state.get("api_key", "")
    if not user_key:
        return {"messages": [AIMessage(content="⚠️ Please enter your Groq API Key in the sidebar to start.")]}
        
    # Using Llama 3 8b via Groq (Super Fast & Free)
    llm = ChatGroq(model="llama3-8b-8192", groq_api_key=user_key, temperature=0.6)
    
    system_prompt = f"""
    You are the polite AI Sales Representative of 'Siddique Brothers Restaurant' located in Karachi.
    Guide customers beautifully through the menu. Keep answers slightly short and premium.
    OFFICIAL RESTAURANT MENU:\n{state['menu_data']}
    """
    padded_messages = [SystemMessage(content=system_prompt)] + state["messages"]
    try:
        bot_output = llm.invoke(padded_messages)
        return {"messages": [AIMessage(content=bot_output.content)]}
    except Exception as e:
        return {"messages": [AIMessage(content=f"⚠️ Connection Error: Please check your Key.")]}

workflow = StateGraph(AgentState)
workflow.add_node("manager", manager_node)
workflow.add_edge(START, "manager")
workflow.add_edge("manager", END)
memory = MemorySaver()
restaurant_app = workflow.compile(checkpointer=memory)

# --- 4. Streamlit Interface ---
st.set_page_config(page_title="SB-RESTAURANT AI", page_icon="🍔", layout="wide")
apply_premium_styles_from_url()

st.sidebar.markdown("### 🛠️ Developer Control")
input_api_key = st.sidebar.text_input("Enter Groq API Key:", type="password", help="Paste your gsk_ key here.")

st.markdown("<h1 style='text-align: center; font-weight: 700;'>🍔 Siddique Brothers AI Sales Counter</h1>", unsafe_allow_html=True)
st.write("---")

if "chat_history" not in st.session_state: st.session_state.chat_history = []

with st.form(key="chat_form", clear_on_submit=True):
    text_query = st.text_input("Type your message here:")
    if st.form_submit_button("Send Message") and text_query:
        if not input_api_key:
            st.warning("👈 Please paste your Groq API Key in the left sidebar first!")
        else:
            st.session_state.chat_history.append(HumanMessage(content=text_query))
            initial_state = {
                "messages": st.session_state.chat_history, 
                "menu_data": get_full_menu_for_ai(),
                "api_key": input_api_key
            }
            final_output = restaurant_app.invoke(initial_state, {"configurable": {"thread_id": "sami_groq"}})
            st.session_state.chat_history.append(final_output["messages"][-1])

if st.session_state.chat_history:
    for msg in reversed(st.session_state.chat_history):
        if isinstance(msg, AIMessage): st.markdown(f'<div class="glass-card"><b>🤖 Agent:</b><br>{msg.content}</div>', unsafe_allow_html=True)
        elif isinstance(msg, HumanMessage): st.markdown(f'<div style="margin: 5px 0; color: white;"><b>👤 You:</b> {msg.content}</div>', unsafe_allow_html=True)
