import streamlit as st
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

st.set_page_config(page_title="Percy Jackson", page_icon="🌊", layout="wide")

# Knowledge Base
@st.cache_resource
def load_knowledge():
    docs = [
        "Percy Jackson is the son of Poseidon and Sally Jackson.",
        "His sword Riptide (Anaklusmos) looks like a ballpoint pen.",
        "Percy is sarcastic, witty, brave, loyal, and has ADHD. He loves the ocean and blue food.",
        "He calls Annabeth Chase 'Seaweed Brain'. Grover Underwood is his satyr best friend.",
        "Camp Half-Blood is the safe haven for Greek demigods on Long Island.",
        "Percy has water powers - he can control water, create waves, and heal in water.",
    ]
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 5})

retriever = load_knowledge()

# Strong Percy Personality
SYSTEM_PROMPT = """You are Percy Jackson from Rick Riordan's books. 
Speak exactly like Percy: sarcastic, funny, casual teen language with words like "dude", "man", "oh gods", "seriously?", "Seaweed Brain".
Be loyal and brave but complain about quests. Stay 100% in character at all times.
Only use real information from the Percy Jackson series. If you're not sure, say so in character."""

# Session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("🌊 Percy Jackson")
    st.caption("Son of Poseidon")
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    if st.button("🗡️ New Quest"):
        st.session_state.messages = []
        st.rerun()

# Main Chat
st.title("🌊 Talk to Percy Jackson")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="🌊").write(msg["content"])

# User Input
if prompt := st.chat_input("Hey Percy, what's up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant", avatar="🌊"):
        # Get relevant lore
        retrieved = retriever.invoke(prompt)
        context = "\n".join([doc.page_content for doc in retrieved])

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nRelevant Lore:\n{context}\n\nUser asked: {prompt}"
        
        response = llm.invoke(full_prompt).content
        
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})