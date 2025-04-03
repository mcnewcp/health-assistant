import streamlit as st
from health_assistant import health_assistant
from agents import Runner

import nest_asyncio
nest_asyncio.apply()

st.title("Health Assistant `v0.01`")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Hello!  I'm your health assistant.  What's up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        result = Runner.run_sync(health_assistant, prompt)
        response = st.write(result.final_output)
    st.session_state.messages.append({"role": "assistant", "content": response})


