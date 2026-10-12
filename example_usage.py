"""Example usage for Structured JSON Repair and Schema Enforcer."""
from client import StructuredJSONRepair

if __name__ == "__main__":
    # Test malformed LLM output with markdown wrapper, trailing comma, and unquoted keys
    dirty_llm_output = """```json
    {
        name: "GenPark Assistant",
        version: "1.0",
        active: "true",
        retries: "5",
    }
    ```"""

    repair_res = StructuredJSONRepair.parse_and_repair(dirty_llm_output)
    print("Repaired Successfully:", repair_res["success"])
    print("Repaired Data:", repair_res["data"])

    # Enforce strict types
    schema = {
        "version": "str",
        "active": "bool",
        "retries": "int"
    }
    enforced, errors = StructuredJSONRepair.enforce_schema_types(repair_res["data"], schema)
    print("\nEnforced Data:", enforced)
    print("Casting Errors:", errors)
