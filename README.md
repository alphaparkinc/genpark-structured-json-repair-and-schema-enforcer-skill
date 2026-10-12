# genpark-structured-json-repair-and-schema-enforcer-skill

Repairs common LLM JSON generation errors including markdown code blocks, unquoted keys, trailing commas, and enforces target schema types.

100% Python Standard Library implementation with zero external dependencies.

## Key Capabilities
- **Markdown Enclosure Stripping**: Cleanly removes triple backtick wrappers (````json ... ````) produced by conversational LLMs.
- **Syntax Anomaly Normalization**: Removes trailing commas before closing braces/brackets, wraps unquoted object keys, and auto-balances unclosed brackets.
- **Type Casting & Schema Enforcement**: Converts string-represented primitives (`"10" -> 10`, `"true" -> True`) according to target schema definitions.
- **Zero Overhead**: Pure standard library implementation with microsecond parsing performance.

## Architecture

```
[Raw/Malformed LLM Output]
           │
           ▼
┌──────────────────────────────────────────────┐
│  StructuredJSONRepair                        │
│  ├─ Markdown Fence Stripper                  │
│  ├─ Trailing Comma & Key Quote Repair        │
│  ├─ Bracket Balance Synthesizer              │
│  └─ Primitive Type Enforcer (int/bool/str)   │
└──────────────────────────────────────────────┘
           │
           ▼
[Validated Python Dictionary & Tool Payload]
```

## MCP Server Integration

Run standard MCP stdio server:
```bash
python mcp_server.py
```

Exposed Tools:
- `repair_and_parse_json`: Repairs and parses malformed JSON text containing markdown fences, trailing commas, or unquoted keys.
- `enforce_schema_types`: Casts dictionary values to specified primitive types (int, float, bool, str).

## Quickstart

```python
from client import StructuredJSONRepair

raw = '```json\n{ name: "Agent Alpha", count: "42", }\n```'
res = StructuredJSONRepair.parse_and_repair(raw)
print(res["data"])  # {'name': 'Agent Alpha', 'count': '42'}

enforced, _ = StructuredJSONRepair.enforce_schema_types(res["data"], {"count": "int"})
print(enforced["count"])  # 42 (integer)
```

---

## GenPark Ecosystem

- **Official Website**: [https://www.genpark.ai](https://www.genpark.ai)
- **LinkedIn Page**: [https://www.linkedin.com/company/92955550](https://www.linkedin.com/company/92955550)
