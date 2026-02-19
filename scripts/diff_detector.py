#!/usr/bin/env python3
"""
Diff detector for academic-review-suite.
Measures percentage change between two versions of a paper.
Used for pivot detection (>20% triggers LLM re-review).
"""

import json
import sys
import argparse
import difflib


def compute_change_percentage(baseline_path, current_path):
    """Compute line-level change percentage between two text files."""
    with open(baseline_path) as f:
        baseline = f.readlines()
    with open(current_path) as f:
        current = f.readlines()

    matcher = difflib.SequenceMatcher(None, baseline, current)
    total_lines = max(len(baseline), len(current), 1)
    unchanged = sum(block.size for block in matcher.get_matching_blocks())
    changed = total_lines - unchanged
    percentage = (changed / total_lines) * 100

    # Get list of changed sections
    changed_sections = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            changed_sections.append({
                "type": tag,
                "baseline_lines": [i1 + 1, i2],
                "current_lines": [j1 + 1, j2],
                "preview": "".join(current[j1:min(j2, j1 + 3)]).strip()[:100],
            })

    return {
        "baseline_lines": len(baseline),
        "current_lines": len(current),
        "changed_lines": changed,
        "change_percentage": round(percentage, 1),
        "is_pivot": percentage > 20,
        "changed_sections": changed_sections[:20],  # Cap at 20 sections
    }


def main():
    parser = argparse.ArgumentParser(description="Paper diff detector")
    parser.add_argument("--baseline", required=True, help="Path to baseline version")
    parser.add_argument("--current", required=True, help="Path to current version")
    parser.add_argument("--threshold", type=float, default=20.0, help="Pivot threshold %%")
    args = parser.parse_args()

    result = compute_change_percentage(args.baseline, args.current)
    result["is_pivot"] = result["change_percentage"] > args.threshold
    result["threshold"] = args.threshold

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
