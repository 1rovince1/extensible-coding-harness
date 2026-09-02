from typing import Type, Dict, Any

from pydantic import BaseModel


# Schema Inliner (Removes $defs, inlines $ref, strips unwanted metadata)
def inline_pydantic_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Generates a clean JSON schema completely safe for Ollama, OpenAI,
    and local LLMs without $defs, $ref, or redundant title fields.
    """
    schema = model.model_json_schema()
    defs = schema.pop("$defs", {})

    def _resolve(node: Any) -> Any:
        if isinstance(node, dict):
            if "$ref" in node:
                ref_key = node["$ref"].split("/")[-1]
                return _resolve(defs.get(ref_key, {}))
            return {k: _resolve(v) for k, v in node.items() if k != "title"}
        elif isinstance(node, list):
            return [_resolve(item) for item in node]
        return node

    clean_schema = _resolve(schema)
    return {
        "type": "object",
        "properties": clean_schema.get("properties", {}),
        "required": clean_schema.get("required", [])
    }