def build_ollama_tools(tool_registry: dict):
    ollama_format_tools = []
    
    for tool_name, tool_data in tool_registry.items():
        ollama_format_tools.append({
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_data["description"],
                "parameters": tool_data["input_schema"].model_json_schema()
            }
        })

    return ollama_format_tools


def build_openai_tools(tool_registry: dict):
    openai_format_tools = []

    for tool_name, tool_data in tool_registry.items():
        openai_format_tools.append({
            "type": "function",
            "name": tool_name,
            "description": tool_data["description"],
            "parameters": tool_data["input_schema"].model_json_schema()
        })

    return openai_format_tools