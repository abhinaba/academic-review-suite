#!/usr/bin/env python3
"""
Universal LLM caller for academic-review-suite.
Routes to the correct SDK based on provider type.
Handles: anthropic, openai, google, and openai-compatible providers.
"""

import json
import sys
import time
import argparse


def call_anthropic(api_key, model, prompt, timeout=120):
    """Call Anthropic Claude API."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    start = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
        timeout=timeout,
    )
    elapsed = time.time() - start
    text = response.content[0].text
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return {"text": text, "usage": usage, "latency": elapsed, "model": model}


def call_openai(api_key, model, prompt, base_url=None, timeout=120):
    """Call OpenAI or OpenAI-compatible API."""
    import openai
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = openai.OpenAI(**kwargs)
    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        timeout=timeout,
    )
    elapsed = time.time() - start
    text = response.choices[0].message.content
    usage = {
        "input_tokens": response.usage.prompt_tokens if response.usage else 0,
        "output_tokens": response.usage.completion_tokens if response.usage else 0,
    }
    return {"text": text, "usage": usage, "latency": elapsed, "model": model}


def call_google(api_key, model, prompt, timeout=120):
    """Call Google Gemini API."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gen_model = genai.GenerativeModel(model)
    start = time.time()
    response = gen_model.generate_content(
        prompt,
        request_options={"timeout": timeout},
    )
    elapsed = time.time() - start
    text = response.text
    usage = {
        "input_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
        "output_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
    }
    return {"text": text, "usage": usage, "latency": elapsed, "model": model}


def health_check(provider_type, api_key, model, base_url=None, timeout=10):
    """Quick health check: send 'Respond with OK' and verify response."""
    prompt = "Respond with exactly: OK"
    try:
        if provider_type == "anthropic":
            result = call_anthropic(api_key, model, prompt, timeout=timeout)
        elif provider_type == "google":
            result = call_google(api_key, model, prompt, timeout=timeout)
        else:
            result = call_openai(api_key, model, prompt, base_url=base_url, timeout=timeout)
        return {"healthy": True, "latency": result["latency"], "model": model}
    except Exception as e:
        return {"healthy": False, "error": str(e), "model": model}


def call_llm(provider_type, api_key, model, prompt, base_url=None, timeout=120):
    """Route to the correct SDK based on provider type."""
    if provider_type == "anthropic":
        return call_anthropic(api_key, model, prompt, timeout=timeout)
    elif provider_type == "google":
        return call_google(api_key, model, prompt, timeout=timeout)
    else:
        return call_openai(api_key, model, prompt, base_url=base_url, timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description="Universal LLM caller")
    parser.add_argument("--provider-type", required=True, choices=["anthropic", "openai", "google", "openai_compatible"])
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--health-check", action="store_true")
    args = parser.parse_args()

    ptype = args.provider_type if args.provider_type != "openai_compatible" else "openai_compatible"

    if args.health_check:
        result = health_check(ptype, args.api_key, args.model, args.base_url, timeout=min(args.timeout, 15))
    else:
        result = call_llm(ptype, args.api_key, args.model, args.prompt, args.base_url, args.timeout)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
