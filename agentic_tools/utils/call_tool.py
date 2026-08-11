import logging

logger = logging.getLogger(__name__)


async def call_function(tool_registry: dict, fn_name: str, fn_args: dict):
    logger.debug(f"Calling function {fn_name} with args: {fn_args}")

    if fn_name not in tool_registry:
        return "Tool not found in registry"
    
    callable_fn = tool_registry[fn_name]["callable_fn"]
    tool_result = await callable_fn(**fn_args)

    return tool_result