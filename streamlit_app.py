import streamlit as st
from health_assistant import health_assistant
from agents import Runner, Agent
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

def get_conversation_history_for_agent(messages: List[Dict]) -> List[Dict]:
    """
    Prepares a clean conversation history for LLM input by stripping out
    non-relevant metadata (like emojis).
    """
    return [
        {"role": msg.get("role", "user"), "content": msg.get("content", "")}
        for msg in messages
        if "content" in msg
    ]

async def generate_response_stream(agent: Agent, prompt: str) -> AsyncGenerator[Dict, None]:
    """Yields token deltas and agent handover updates."""
    result = Runner.run_streamed(agent, input=prompt)
    current_agent = agent.name

    async for event in result.stream_events():
        print(event)
        if event.type == "agent_updated_stream_event":
            new_agent = event.new_agent.name
            if new_agent != current_agent:
                print(f"[agent handover]: {current_agent} -> {new_agent}")
                yield {"step": f"🔄 Handover **{current_agent}** -> **{new_agent}**"}
                current_agent = new_agent
        elif event.type == "raw_response_event" and isinstance(event.data, ResponseOutputItemAddedEvent) and isinstance(event.data.item, ResponseFunctionToolCall):
            yield {"tool_call": f"🔄 Tool Call: {event.data.item.name}"}
        elif event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            yield {"delta": event.data.delta}

def render_streaming_response(generator) -> Dict:
    """Renders streaming content to Streamlit."""
    with st.chat_message("assistant"):
        steps_expander = st.expander("Steps")
        tool_call_expander = st.expander("Tool Calls")
        message_container = st.empty()

        full_response = ""
        steps = []
        tool_calls = ""
        
        async def stream_response():
            nonlocal full_response, steps, tool_calls
            async for chunk in generator:
                if "delta" in chunk:
                    full_response += chunk["delta"]
                    message_container.markdown(full_response)
                elif "step" in chunk:
                    steps.append(chunk["step"])
                    steps_expander.markdown("\n".join(steps))
                elif "tool_call" in chunk:
                    tool_calls += f"\n{chunk["tool_call"]}"
                    tool_call_expander.markdown(tool_calls)
            return {"response": full_response, "steps": steps, "tool_calls": tool_calls}
        
        # Streamlit requires running the async function in a thread
        final_result = asyncio.run(stream_response())
        return final_result

# Accept user input
if prompt := st.chat_input("Hello!  I'm your health assistant.  What's up?", key = "user_input"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # format chat history
    conversation_history = get_conversation_history_for_agent(st.session_state.messages)
        
    # stream response
    generator = generate_response_stream(health_assistant, conversation_history)
    response = render_streaming_response(generator)

    # save assistant response
    st.session_state["messages"].append({
        "role": "assistant",
        "content": response["response"],
        "steps": response["steps"],
        "tool_calls": response["tool_calls"],
    })


