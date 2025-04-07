import streamlit as st
from streamlit import session_state as ss
from health_assistant import health_assistant
from ui import stream_response, save_agent_response
import asyncio

st.title("Health Assistant `v0.01`")

# Initialize chat history
if "messages" not in ss:
    ss.messages = []

# Display chat messages from history on app rerun
for message in ss.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Hello!  I'm your health assistant.  What's up?", key = "user_input"):
    # Add user message to chat history
    ss.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = asyncio.run(stream_response(health_assistant, prompt))
    
    # save response to session state messages
    save_agent_response(response)

    # temp write session state messages
    st.write(ss.messages)
