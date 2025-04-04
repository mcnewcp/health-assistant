import streamlit as st
from health_assistant import health_assistant
from agents import Runner, Agent, ItemHelpers
from openai.types.responses import ResponseTextDeltaEvent, ResponseOutputItemAddedEvent, ResponseFunctionToolCall
from typing import Dict, List, AsyncGenerator
import asyncio

st.title("Health Assistant `v0.01`")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

async def stream_response(agent:Agent, prompt:str):
    result = Runner.run_streamed(
        agent,
        input=prompt,
    )
    st.markdown("=== Run starting ===")

    current_event_type = ""
    async for event in result.stream_events():
        # if the event type changes, clear the container
        if event.type != current_event_type:
            if event.type == "raw_response_event":
                container = st.empty()
            else:
                container = st.expander(f"{event.type}")
            content = ""
            current_event_type = event.type

        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            content += event.data.delta
            container.markdown(content)
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            content += f"Agent updated: {event.new_agent.name}"
            container.markdown(content)
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                content += "-- Tool was called"
                container.markdown(content)
            elif event.item.type == "tool_call_output_item":
                content += f"-- Tool output: {event.item.output}"
                container.markdown(content)
            elif event.item.type == "message_output_item":
                content += "-- Message output item"
                container.markdown(content)
                # st.markdown(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
            else:
                pass  # Ignore other event types

    st.markdown("=== Run complete ===")

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



