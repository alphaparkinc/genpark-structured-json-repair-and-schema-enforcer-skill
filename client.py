"""Structured JSON Repair and Schema Enforcer.
100% Python Standard Library.
"""

from typing import Dict, Any, Tuple, Optional
import re
import json


class StructuredJSONRepair:
    """Detects and automatically fixes common LLM JSON syntax deviations,
    strips markdown code blocks, balances brackets, and validates against schemas."""

    @classmethod
    def clean_markdown_fences(cls, raw_text: str) -> str:
        """Strips leading/trailing markdown code block indicators."""
        text = raw_text.strip()
        # Remove ```json ... ``` or ``` ... ```
        pattern = r"^```(?:json|JSON)?\s*\n?(.*?)\n?```$"
        m = re.match(pattern, text, re.DOTALL)
        if m:
            return m.group(1).strip()
        return text

    @classmethod
    def repair_syntax(cls, raw_text: str) -> str:
        """Applies heuristic regex repairs for common JSON syntax errors."""
        text = cls.clean_markdown_fences(raw_text)

        # 1. Remove trailing commas before closing braces/brackets
        text = re.sub(r",\s*([\]}])", r"\1", text)

        # 2. Convert unquoted keys: {key: "val"} -> {"key": "val"}
        text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_-]*)\s*:', r'\1"\2":', text)

        # 3. Replace single-quoted strings with double quotes when not escaping double quotes
        # Simple heuristic: replace single quotes around words
        text = re.sub(r":\s*'([^']*)'", r': "\1"', text)

        # 4. Auto-balance trailing brackets if cutoff
        open_braces = text.count("{") - text.count("}")
        open_brackets = text.count("[") - text.count("]")

        if open_brackets > 0:
            text += "]" * open_brackets
        if open_braces > 0:
            text += "}" * open_braces

        return text

    @classmethod
    def parse_and_repair(cls, raw_text: str) -> Dict[str, Any]:
        """Attempts direct JSON parse first; falls back to repair pipeline if invalid."""
        clean = cls.clean_markdown_fences(raw_text)
        try:
            parsed = json.loads(clean)
            return {
                "success": True,
                "repaired": False,
                "data": parsed,
                "error": None,
            }
        except json.JSONDecodeError as initial_err:
            repaired_text = cls.repair_syntax(raw_text)
            try:
                parsed = json.loads(repaired_text)
                return {
                    "success": True,
                    "repaired": True,
                    "repaired_text": repaired_text,
                    "data": parsed,
                    "error": None,
                }
            except json.JSONDecodeError as final_err:
                return {
                    "success": False,
                    "repaired": False,
                    "repaired_text": repaired_text,
                    "data": None,
                    "error": f"Failed after repair: {str(final_err)} (Original: {str(initial_err)})",
                }

    @classmethod
    def enforce_schema_types(
        cls, data: Dict[str, Any], schema_types: Dict[str, str]
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Casts mismatched types (e.g., "123" -> 123) according to target schema specification."""
        enforced = dict(data)
        errors = {}

        for key, expected_type in schema_types.items():
            if key not in enforced:
                continue
            val = enforced[key]
            expected = expected_type.lower()
            try:
                if expected == "int" or expected == "integer":
                    enforced[key] = int(val)
                elif expected == "float" or expected == "number":
                    enforced[key] = float(val)
                elif expected == "bool" or expected == "boolean":
                    if isinstance(val, str):
                        enforced[key] = val.lower() in ("true", "1", "yes")
                    else:
                        enforced[key] = bool(val)
                elif expected == "str" or expected == "string":
                    enforced[key] = str(val)
                elif expected == "list" or expected == "array":
                    if not isinstance(val, list):
                        enforced[key] = [val]
            except (ValueError, TypeError) as exc:
                errors[key] = f"Could not cast {val} ({type(val).__name__}) to {expected_type}: {exc}"

        return enforced, errors
