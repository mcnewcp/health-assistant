import streamlit as st
from streamlit import session_state as ss
from agents import Runner, Agent
from agents.result import RunResultStreaming
from openai.types.responses import (
    ResponseTextDeltaEvent,
    ResponseFunctionToolCall,
    ResponseWebSearchCallCompletedEvent,
    ResponseFunctionWebSearch
)

async def stream_response(agent: Agent, prompt: str):
    """
    Stream an AI agent's response to the Streamlit UI, handling various response events.

    This function processes different types of events from the agent's response stream and
    displays them appropriately in the Streamlit interface. It handles:
    - Text streaming from the agent
    - Web search notifications
    - Agent handoffs between different AI agents
    - Tool calls and their outputs

    Args:
        agent (Agent): The AI agent instance that will process the prompt
        prompt (str): The user's input text to be processed by the agent

    Returns:
        The result object from the agent's run
    """
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

def save_agent_response(response):
    """
    Processes and saves agent responses to the session state messages.
    This function handles different types of response items and formats them appropriately
    for storage in the session state. It processes:
    - Agent handoffs
    - Web search calls
    - Messages
    - Tool calls and their outputs
    Args:
        response: A response object containing new_items to be processed.
                 Expected to have a 'new_items' attribute with items having 'type'
                 and 'raw_item' attributes.
    The function appends formatted dictionaries to ss.messages with the following structure:
        "type": <message_type>,
        "content": <formatted_content>,
        "name": <tool_name> (only for tool calls)
    Note:
        - Uses global session state (ss) to store messages
        - Tracks tool calls to properly pair inputs with outputs
        - Ignores unrecognized item types
    """
    
    # keep track if the previous item was a tool call
    # this allows us to add the tool call outputs to the corresponding inputs
    after_tool_call = False
    
    for item in response.new_items:
        # agent handoffs
        if item.type == "handoff_output_item":
            ss.messages.append(
                {
                    "role": "assistant",
                    "type": "handoff",
                    "content": f"🧠 Agent handoff: `{item.source_agent.name}` → `{item.target_agent.name}`"
                }
            )
            after_tool_call = False
        
        # web search calls
        elif item.type == "tool_call_item" and isinstance(item.raw_item, ResponseFunctionWebSearch):
            ss.messages.append(
                {
                    "role": "assistant",
                    "type": "web_search",
                    "content": "🔍 Searched the web"
                }
            )
            after_tool_call = False

        # messages
        elif item.type == "message_output_item":
            for m in item.raw_item.content:
                try:
                    ss.messages.append(
                        {
                            "role": "assistant",
                            "type": "message",
                            "content": m.text
                        }
                    )
                except Exception:
                    pass
            after_tool_call = False
            
        # tool calls
        elif item.type == "tool_call_item" and isinstance(item.raw_item, ResponseFunctionToolCall):
            last_tool_call_name = item.raw_item.name
            ss.messages.append(
                {
                    "role": "assistant",
                    "type": "tool_call",
                    "name": item.raw_item.name,
                    "content": f'**Inputs**: \n`{item.raw_item.arguments}`'
                }
            )
            after_tool_call = True
        elif item.type == "tool_call_output_item" and after_tool_call:
            ss.messages[-1]["content"] += f'\n**Outputs**: \n`{item.output}`'
            after_tool_call = False
        
        # ignore all other item types
        else:
            pass

def display_messages():
    for m in ss.messages:
        # user messages
        if m["role"] == "user":
            with st.chat_message("user"):
                st.markdown(m["content"])
        # assistant
        if m["role"] == "assistant":
            # messages
            if m["type"] == "message":
                with st.chat_message("assistant"):
                    st.markdown(m["content"])
            # agent handoff
            elif m["type"] == "handoff":
                st.info(m["content"], icon="🧠")
            # web search
            elif m["type"] == "web_search":
                st.success(m["content"], icon="🔍")
            # tool calls
            elif m["type"] == "tool_call":
                with st.status(f"🛠️ Called Tool: {m["name"]}"):
                    st.markdown(m["content"])
        