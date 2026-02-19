#!/usr/bin/env python3
"""
Reference checker for academic-review-suite.
Verifies references against OpenAlex, Semantic Scholar, and CrossRef.
No API keys required for any of these services.
"""

import json
import sys
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error


USER_AGENT = "AcademicReviewSuite/0.1 (https://github.com/academic-review-suite)"


def _get_json(url, headers=None):
    """Simple GET request returning parsed JSON."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        return {"error": str(e)}


def check_crossref(title=None, doi=None):
    """Check CrossRef for a reference by DOI or title."""
    if doi:
        url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
        data = _get_json(url)
        if "message" in data:
            msg = data["message"]
            return {
                "found": True,
                "source": "crossref",
                "title": msg.get("title", [""])[0],
                "doi": msg.get("DOI", ""),
                "year": msg.get("published", {}).get("date-parts", [[None]])[0][0],
                "authors": [a.get("family", "") for a in msg.get("author", [])],
                "type": msg.get("type", ""),
            }
    if title:
        encoded = urllib.parse.quote(title)
        url = f"https://api.crossref.org/works?query.title={encoded}&rows=1"
        data = _get_json(url)
        if "message" in data and data["message"].get("items"):
            item = data["message"]["items"][0]
            return {
                "found": True,
                "source": "crossref",
                "title": item.get("title", [""])[0],
                "doi": item.get("DOI", ""),
                "year": item.get("published", {}).get("date-parts", [[None]])[0][0],
                "authors": [a.get("family", "") for a in item.get("author", [])],
                "score": item.get("score", 0),
            }
    return {"found": False, "source": "crossref"}


def check_openalex(title=None, doi=None):
    """Check OpenAlex for a reference."""
    if doi:
        url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
    elif title:
        encoded = urllib.parse.quote(title)
        url = f"https://api.openalex.org/works?filter=title.search:{encoded}&per_page=1"
    else:
        return {"found": False, "source": "openalex"}

    data = _get_json(url)

    if doi and "id" in data:
        return {
            "found": True,
            "source": "openalex",
            "title": data.get("title", ""),
            "doi": data.get("doi", ""),
            "year": data.get("publication_year"),
            "cited_by_count": data.get("cited_by_count", 0),
            "open_access": data.get("open_access", {}).get("is_oa", False),
        }
    elif not doi and "results" in data and data["results"]:
        item = data["results"][0]
        return {
            "found": True,
            "source": "openalex",
            "title": item.get("title", ""),
            "doi": item.get("doi", ""),
            "year": item.get("publication_year"),
            "cited_by_count": item.get("cited_by_count", 0),
            "open_access": item.get("open_access", {}).get("is_oa", False),
        }
    return {"found": False, "source": "openalex"}


def check_semantic_scholar(title=None, doi=None):
    """Check Semantic Scholar for a reference."""
    if doi:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi)}?fields=title,year,authors,venue,citationCount"
    elif title:
        encoded = urllib.parse.quote(title)
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded}&limit=1&fields=title,year,authors,venue,citationCount"
    else:
        return {"found": False, "source": "semantic_scholar"}

    data = _get_json(url)

    if doi and "paperId" in data:
        return {
            "found": True,
            "source": "semantic_scholar",
            "title": data.get("title", ""),
            "year": data.get("year"),
            "venue": data.get("venue", ""),
            "citation_count": data.get("citationCount", 0),
            "authors": [a.get("name", "") for a in data.get("authors", [])],
        }
    elif not doi and "data" in data and data["data"]:
        item = data["data"][0]
        return {
            "found": True,
            "source": "semantic_scholar",
            "title": item.get("title", ""),
            "year": item.get("year"),
            "venue": item.get("venue", ""),
            "citation_count": item.get("citationCount", 0),
            "authors": [a.get("name", "") for a in item.get("authors", [])],
        }
    return {"found": False, "source": "semantic_scholar"}


def check_reference(title=None, doi=None, expected_year=None, expected_authors=None):
    """Check a single reference against all 3 APIs and classify it."""
    results = []
    for checker in [check_crossref, check_openalex, check_semantic_scholar]:
        result = checker(title=title, doi=doi)
        results.append(result)
        time.sleep(0.2)  # Rate limiting

    found_count = sum(1 for r in results if r.get("found"))

    if found_count >= 2:
        classification = "verified"
    elif found_count == 1:
        classification = "partial"
    else:
        classification = "not_found"

    # Check for metadata mismatches
    if found_count > 0 and expected_year:
        years = [r.get("year") for r in results if r.get("found") and r.get("year")]
        if years and all(abs(y - expected_year) > 1 for y in years):
            classification = "mismatch"

    return {
        "title": title,
        "doi": doi,
        "classification": classification,
        "apis": results,
        "found_in": found_count,
    }


def main():
    parser = argparse.ArgumentParser(description="Reference checker")
    parser.add_argument("--references-json", required=True, help="Path to JSON file with references list")
    parser.add_argument("--output", default=None, help="Output path for results")
    args = parser.parse_args()

    with open(args.references_json) as f:
        references = json.load(f)

    results = []
    for i, ref in enumerate(references):
        print(f"Checking reference {i+1}/{len(references)}: {ref.get('title', 'unknown')[:60]}...", file=sys.stderr)
        result = check_reference(
            title=ref.get("title"),
            doi=ref.get("doi"),
            expected_year=ref.get("year"),
            expected_authors=ref.get("authors"),
        )
        results.append(result)

    output = {
        "total": len(results),
        "verified": sum(1 for r in results if r["classification"] == "verified"),
        "partial": sum(1 for r in results if r["classification"] == "partial"),
        "not_found": sum(1 for r in results if r["classification"] == "not_found"),
        "mismatch": sum(1 for r in results if r["classification"] == "mismatch"),
        "references": results,
    }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Results saved to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
