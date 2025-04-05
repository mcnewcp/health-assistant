import streamlit as st
from health_assistant import health_assistant
from agents import Runner, Agent
from openai.types.responses import (
    ResponseTextDeltaEvent,
    ResponseFunctionToolCall,
    ResponseWebSearchCallCompletedEvent
)

async def stream_response(agent: Agent, prompt: str):
    result = Runner.run_streamed(agent, input=prompt)

    current_agent = agent.name
    content = ""
    message_container = None
    streaming_text_active = False

    last_tool_call_name = None
    tool_status_container = None

    print("=== Run starting ===")
    async for event in result.stream_events():
        # Text streaming
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            if not streaming_text_active:
                # New message starting → create new container
                message_container = st.empty()
                content = ""
                streaming_text_active = True

            content += event.data.delta
            message_container.markdown(content)

        # Web search
        elif event.type == "raw_response_event" and isinstance(event.data, ResponseWebSearchCallCompletedEvent):
            notification_container = st.empty()
            notification_container.markdown("🔍 Searched the web")
            streaming_text_active = False  # End of text stream

        # Agent handoff
        elif event.type == "agent_updated_stream_event":
            if event.new_agent.name != current_agent:
                notification_container = st.empty()
                notification_container.markdown(f"🧠 Agent handoff: `{current_agent}` → `{event.new_agent.name}`")
                current_agent = event.new_agent.name
            streaming_text_active = False

        # Tool calls
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item" and isinstance(event.item.raw_item, ResponseFunctionToolCall):
                last_tool_call_name = event.item.raw_item.name
                tool_status_container = st.status(last_tool_call_name)
                with tool_status_container:
                    st.write(f"**Inputs**: {event.item.raw_item.arguments}")
                streaming_text_active = False

            elif event.item.type == "tool_call_output_item" and event.name == "tool_output":
                if tool_status_container:
                    with tool_status_container:
                        st.write(f"**Output**: {event.item.output}")
                streaming_text_active = False
            else:
                streaming_text_active = False
        else:
            streaming_text_active = False

    print("=== Run complete ===")
    return result
