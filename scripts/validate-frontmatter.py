#!/usr/bin/env python3
"""Validate YAML frontmatter in Hugo content files."""

import os
import re
import sys
from datetime import date, datetime

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)

CONTENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content")

REQUIRED_FIELDS = ["title", "date", "type", "summary", "tags"]

FISHING_REQUIRED = {
    "location": ["body_of_water"],
    "conditions": ["weather"],
    "results": ["total_kept", "total_released"],
}

RECIPE_REQUIRED = {
    "recipe": ["cuisine", "prep_minutes", "cook_minutes"],
}

NUMERIC_FIELDS = [
    "air_temp_f",
    "water_temp_f",
    "pressure_inhg",
    "prep_minutes",
    "cook_minutes",
    "servings",
    "best_weight_lb",
    "count",
    "depth_ft",
]


def parse_frontmatter(filepath):
    """Extract YAML frontmatter from a markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    return yaml.safe_load(match.group(1))


def validate_date(value, field_name, filepath):
    """Validate that a value is a valid date."""
    errors = []
    if isinstance(value, (date, datetime)):
        return errors
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
        except ValueError:
            errors.append(f"  {filepath}: '{field_name}' is not a valid ISO date: {value}")
    else:
        errors.append(f"  {filepath}: '{field_name}' should be a date, got {type(value).__name__}")
    return errors


def validate_numeric(data, filepath):
    """Recursively check that numeric fields contain numbers."""
    errors = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key in NUMERIC_FIELDS:
                if value is not None and not isinstance(value, (int, float)):
                    errors.append(f"  {filepath}: '{key}' should be numeric, got {type(value).__name__}: {value}")
            else:
                errors.extend(validate_numeric(value, filepath))
    elif isinstance(data, list):
        for item in data:
            errors.extend(validate_numeric(item, filepath))
    return errors


def validate_file(filepath):
    """Validate a single content file."""
    errors = []
    rel_path = os.path.relpath(filepath, CONTENT_DIR)

    fm = parse_frontmatter(filepath)
    if fm is None:
        errors.append(f"  {rel_path}: No YAML frontmatter found")
        return errors

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in fm or fm[field] is None:
            errors.append(f"  {rel_path}: Missing required field '{field}'")

    # Validate date
    if "date" in fm:
        errors.extend(validate_date(fm["date"], "date", rel_path))

    # Validate tags is a list
    if "tags" in fm and not isinstance(fm.get("tags"), list):
        errors.append(f"  {rel_path}: 'tags' should be a list")

    # Type-specific validation
    content_type = fm.get("type", "")

    if content_type == "fishing":
        for block, sub_fields in FISHING_REQUIRED.items():
            if block not in fm or fm[block] is None:
                errors.append(f"  {rel_path}: Fishing post missing '{block}' block")
            else:
                for sf in sub_fields:
                    if sf not in fm[block] or fm[block][sf] is None:
                        errors.append(f"  {rel_path}: '{block}' missing required field '{sf}'")

    elif content_type == "recipes":
        for block, sub_fields in RECIPE_REQUIRED.items():
            if block not in fm or fm[block] is None:
                errors.append(f"  {rel_path}: Recipe post missing '{block}' block")
            else:
                for sf in sub_fields:
                    if sf not in fm[block] or fm[block][sf] is None:
                        errors.append(f"  {rel_path}: '{block}' missing required field '{sf}'")
        # Validate ingredients
        if "ingredients" in fm:
            if not isinstance(fm["ingredients"], list):
                errors.append(f"  {rel_path}: 'ingredients' should be a list")
            else:
                for i, ing in enumerate(fm["ingredients"]):
                    if not isinstance(ing, dict):
                        errors.append(f"  {rel_path}: ingredient #{i+1} should be an object")
                    elif "name" not in ing or "amount" not in ing:
                        errors.append(f"  {rel_path}: ingredient #{i+1} missing 'name' or 'amount'")

    elif content_type == "investing":
        if "position" in fm and fm["position"] is not None:
            pos = fm["position"]
            if "status" not in pos:
                errors.append(f"  {rel_path}: 'position' missing 'status'")

    # Validate numeric fields recursively
    errors.extend(validate_numeric(fm, rel_path))

    return errors


def main():
    all_errors = []
    file_count = 0

    for root, _dirs, files in os.walk(CONTENT_DIR):
        for filename in files:
            if not filename.endswith(".md"):
                continue
            if filename == "_index.md":
                continue

            filepath = os.path.join(root, filename)
            file_count += 1
            errors = validate_file(filepath)
            all_errors.extend(errors)

    print(f"Validated {file_count} content files.")

    if all_errors:
        print(f"\nFound {len(all_errors)} error(s):\n")
        for err in all_errors:
            print(err)
        sys.exit(1)
    else:
        print("All files passed validation.")
        sys.exit(0)


if __name__ == "__main__":
    main()
