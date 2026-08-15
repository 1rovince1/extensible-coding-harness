import streamlit as st
import requests
import httpx
import uuid
import json

SERVER_URL = "http://localhost:8008"

st.title("ex-codhar")

# 1. Fetch active sessions with error handling
try:
    response = requests.get(f"{SERVER_URL}/all_active_sessions", timeout=5)
    active_sessions = response.json().get("active_sessions", [])
except Exception as e:
    st.sidebar.error(f"Failed to fetch sessions from server: {e}")
    active_sessions = []

NEW_SESSION = "NEW_SESSION"
sessions = [NEW_SESSION] + active_sessions

# 2. Callback function to handle session selection changes ONLY when user changes selectbox
def on_session_change():
    selected = st.session_state.selected_session_option
    if selected == NEW_SESSION:
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
    else:
        st.session_state.session_id = str(selected[0])
        st.session_state.messages = list(selected[1].get("session_messages", []))

# 3. Initialize state on initial app load
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []

def stream_sse_response(payload):
    api_url = f"{SERVER_URL}/request_agent/stream"
    with httpx.Client() as client:
        with client.stream("POST", api_url, json=payload, timeout=60.0) as response:
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data"):
                    data_content = line[5:].strip()
                    # if data_content == "[DONE]":
                    #     break
                    try:
                        chunk_json = json.loads(data_content)
                        # print(chunk_json)
                        yield(chunk_json)
                        # token = chunk_json.get("thinking_chunk", "") or chunk_json.get("response_chunk", "")
                        # if token:
                        #     yield token
                    except Exception as e:
                        # st.error(e)
                        yield data_content

# 4. Sidebar selection with on_change callback
with st.sidebar:
    st.selectbox(
        label="Sessions",
        options=sessions,
        key="selected_session_option",
        format_func=lambda x: "New Session" if x == NEW_SESSION else str(x[0]),
        on_change=on_session_change
    )
    streaming = st.checkbox(
        label="Streaming",
        value=True
    )


def create_stream_ui(stream_name: str):
    if stream_name == "main_agent_reasoning":
        with st.chat_message("assistant"):
            expander = st.expander("Thoughts", expanded=True)
            with expander:
                placeholder = st.empty()
        return placeholder
    elif stream_name == "main_agent_response":
        with st.chat_message("assistant"):
            return st.empty()
    elif stream_name == "context_compression_reasoning":
        with st.chat_message("assistant"):
            expander = st.expander("Context compression thoughts", expanded=False)
            with expander:
                placeholder = st.empty()
        return placeholder
    elif stream_name == "context_compression_response":
        with st.chat_message("assistant"):
            expander = st.expander("Context compression response", expanded=False)
            with expander:
                placeholder = st.empty()
        return placeholder

def finalize_stream(stream_name: str, content: str):
    if stream_name == "main_agent_reasoning":
        st.session_state.messages.append({
            "type": "reasoning",
            "summary": [{
                "type": "summary_text",
                "text": content
            }]
        })
    elif stream_name == "main_agent_response":
        st.session_state.messages.append({
            "role": "assistant",
            "content": content
        })
    elif stream_name == "context_compression_response":
        st.session_state.messages.append({
            "role": "user",
            "content": content
        })


def render_session_messages(messages: list):
    for message in messages:
        if message.get("type") == "reasoning" or message.get("role") == "assistant":
            with st.chat_message("assistant"):
                if message.get("type") == "reasoning":
                    thoughts = "\n\n".join(summary["text"] for summary in message.get("summary", []))
                    if thoughts:
                        with st.expander("Thoughts", expanded=False):
                            st.markdown(thoughts)

                elif message.get("role") == "assistant":
                    st.markdown(message["content"])

        elif message.get("role") == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])


# 5. Render chat history from st.session_state
render_session_messages(st.session_state.messages)

# 6. Chat Input Logic
if prompt := st.chat_input():
    # Render and store user prompt
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call backend agent
    with st.spinner("Working..."):
        try:
            json_payload={
                "session_id": st.session_state.session_id,
                "user_query": prompt
            }

            if not streaming:
                res = requests.post(
                    url=f"{SERVER_URL}/request_agent",
                    json=json_payload
                    # timeout=30
                )
                res.raise_for_status()
                parsed_response = res.json()
                # ai_reply = parsed_response.get("ai_response", "")
                
                # # Render and store assistant response
                # with st.chat_message("assistant"):
                #     st.markdown(ai_reply)
                # st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                new_messages = parsed_response.get("new_messages", [])
                render_session_messages(new_messages)
                st.session_state.messages.extend(new_messages)

            else:
                # with st.chat_message("assistant"):
                #     # ai_response = st.write_stream(stream_sse_response(json_payload))
                #     raw_token_stream = stream_sse_response(json_payload)

                #     def thinking_generator():
                #         for token in raw_token_stream:
                #             if token.get("thinking_chunk"):
                #                 yield token.get("thinking_chunk", "")
                #             else:
                #                 break

                #     def response_generator():
                #         for token in raw_token_stream:
                #             if token.get("response_chunk"):
                #                 yield token.get("response_chunk", "")
                #             else:
                #                 break

                #     with st.expander("Thinking...") as thinking_box:
                #         thinking_response = st.write_stream(thinking_generator)
                #     ai_response = st.write_stream(response_generator)
                # st.session_state.messages.append({"role": "assistant", "content": ai_response})

                # with st.chat_message("assistant"):
                current_stream = None
                current_text = ""
                current_placeholder = None

                for event in stream_sse_response(json_payload):
                    if event["type"] == "chunk":
                        stream = event["stream"]
                        if current_stream != stream:
                            current_stream = stream
                            current_text = ""
                            current_placeholder = create_stream_ui(stream) 

                        current_text += event["content"]
                        current_placeholder.markdown(current_text)

                    elif event["type"] == "stream_break":
                        finalize_stream(
                            event["stream"],
                            current_text
                        )
                        current_stream = None
                        current_text = ""
                        current_placeholder = None

        except Exception as e:
            st.error(f"Error communicating with agent: {e}")