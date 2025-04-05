import streamlit as st
from health_assistant import health_assistant
from ui import stream_response
from agents import Runner, Agent, ItemHelpers
from openai.types.responses import ResponseTextDeltaEvent
import asyncio

st.title("Health Assistant `v0.01`")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Hello!  I'm your health assistant.  What's up?", key = "user_input"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = asyncio.run(stream_response(health_assistant, prompt))
    # st.session_state.messages.append({"role": "assistant", "content": response})



