# import streamlit as st
# import requests
# import uuid

# st.title("ex-codhar")
# SERVER_URL = "http://localhost:8008"

# with st.sidebar:
#     response = requests.get(
#         url=SERVER_URL + "/all_active_sessions"
#     )
#     active_sessions = response.json()["active_sessions"]
#     NEW_SESSION = "NEW_SESSION"

#     sessions = [NEW_SESSION] + active_sessions

#     selected_session = st.selectbox(
#         label="sessions",
#         options=sessions,
#         format_func=lambda x:(
#             "new_session" if x == NEW_SESSION 
#             else str(x[0])
#         )
#     )

# if selected_session == NEW_SESSION:
#     st.session_state.session_id = uuid.uuid4()
#     st.session_state.messages = []
# else:
#     st.session_state.session_id = selected_session[0]
#     st.session_state.messages = selected_session[1]["session_messages"]


# # if "messages" not in st.session_state:
# #     st.session_state.messages = selected_session["session_messages"]
# # if "session_id" not in st.session_state:
# #     st.session_state.session_id = uuid.uuid4()

# # st.session_state.messages = selected_session[1]["session_messages"]
# # st.session_state.session_id = selected_session[0]

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input():
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     st.session_state.messages.append({
#         "role": "user",
#         "content": prompt
#     })

#     with st.spinner("Working..."):
#         try:
#             response = requests.post(
#                 url=SERVER_URL + "/request_agent",
#                 json={
#                     "session_id": str(st.session_state.session_id),
#                     "user_query": prompt
#                 }
#             )
#             parsed_response = response.json()

#             with st.chat_message("assistant"):
#                 st.markdown(parsed_response["ai_response"])
#             st.session_state.messages.append({
#                 "role": "assistant",
#                 "content": parsed_response["ai_response"]
#             })
#         except Exception as e:
#             st.error(str(e))







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
                    data_content = line[6:]
                    if data_content == "[DONE]":
                        break
                    try:
                        chunk_json = json.loads(data_content)
                        print(chunk_json)
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

# 5. Render chat history from st.session_state
for message in st.session_state.messages:
    # if (message["role"] == "user" or message["role"] == "assistant") and message.get("content", None):
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])

    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            thoughts = message.get("thoughts", "")
            if thoughts:
                with st.expander("Thoughts", expanded=False):
                    st.markdown(thoughts)
            st.markdown(message["content"])
        else:
            st.markdown(message["content"])

# 6. Chat Input Logic
if prompt := st.chat_input():
    # Render and store user prompt
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call backend agent
    with st.spinner("Working..."):
        try:
            # res = requests.post(
            #     url=f"{SERVER_URL}/request_agent",
            #     json={
            #         "session_id": st.session_state.session_id,
            #         "user_query": prompt
            #     },
            #     # timeout=30
            # )
            # res.raise_for_status()
            # parsed_response = res.json()
            # ai_reply = parsed_response.get("ai_response", "")
            
            # Render and store assistant response
            # with st.chat_message("assistant"):
            #     st.markdown(ai_reply)
            # st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            json_payload={
                "session_id": st.session_state.session_id,
                "user_query": prompt
            }
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
            with st.chat_message("assistant"):
                with st.expander("Thinking...", expanded=True):
                    thinking_placeholder = st.empty()
                response_placeholder = st.empty()

                thinking_text = ""
                response_text = ""

                for token in stream_sse_response(json_payload):

                    if chunk := token.get("thinking_chunk"):
                        thinking_text += chunk
                        thinking_placeholder.markdown(thinking_text)
                    if chunk := token.get("response_chunk"):
                        response_text += chunk
                        response_placeholder.markdown(response_text)

                st.session_state.messages.append({
                    "role": "assistant",
                    "thoughts": thinking_text,
                    "content": response_text 
                })



        except Exception as e:
            st.error(f"Error communicating with agent: {e}")