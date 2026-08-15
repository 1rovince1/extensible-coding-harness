def create_stream_event(
        type: str,
        stream: str,
        content: str | None = None
):
    # stream_event = {
    #     type: {
    #         "stream": stream
    #     }
    # }
    # if content:
    #     stream_event[type]["content"] = content

    # return stream_event
    stream_event = {
        "type": type,
        "stream": stream
    }
    if content:
        stream_event["content"] = content

    return stream_event