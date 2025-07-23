from dotenv import load_dotenv
from toolregistry import TOOL_REGISTRY

load_dotenv()

def dispatch_tool(tool_name, input_data):
    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        return f"Tool '{tool_name}' not found. Consider implementing it."

    try:
        return tool["function"](**input_data)  # 🔧 unpack the dict as kwargs
    except Exception as e:
        return f"Error running tool '{tool_name}': {str(e)}"



def build_tool_schema():
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        k: {"type": "string", "description": v}
                        for k, v in tool.get("parameters", {}).items()
                    },
                    "required": list(tool.get("parameters", {}).keys())
                }
            }
        }
        for name, tool in TOOL_REGISTRY.items()
    ]