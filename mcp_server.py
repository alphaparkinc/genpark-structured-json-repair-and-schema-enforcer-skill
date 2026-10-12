"""MCP server for Structured JSON Repair and Schema Enforcer."""
import sys
import json
from client import StructuredJSONRepair


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "repair_and_parse_json",
                    "description": "Repairs and parses malformed JSON text containing markdown code fences, unquoted keys, trailing commas, or unclosed brackets",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "raw_text": {"type": "string", "description": "Raw string containing JSON payload"}
                        },
                        "required": ["raw_text"],
                    },
                },
                {
                    "name": "enforce_schema_types",
                    "description": "Enforces target primitive types (int, float, bool, str) on parsed dictionary keys with automatic type casting",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "object", "description": "Parsed dictionary object"},
                            "schema_types": {
                                "type": "object",
                                "description": "Mapping of field names to target types (e.g. {'age': 'int'})",
                            },
                        },
                        "required": ["data", "schema_types"],
                    },
                },
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "repair_and_parse_json":
            res = StructuredJSONRepair.parse_and_repair(args.get("raw_text", ""))
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "enforce_schema_types":
            data = args.get("data", {})
            schema_types = args.get("schema_types", {})
            enforced, errs = StructuredJSONRepair.enforce_schema_types(data, schema_types)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"enforced_data": enforced, "errors": errs}, indent=2),
                    }
                ]
            }
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()
