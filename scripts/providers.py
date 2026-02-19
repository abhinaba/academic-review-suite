#!/usr/bin/env python3
"""
Provider registry for academic-review-suite.
Defines all supported LLM providers with their base URLs and SDK types.
"""

PROVIDERS = {
    # Native APIs (provider-specific SDK)
    "anthropic": {
        "type": "anthropic",
        "base_url": None,
        "default_models": ["claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"],
        "display_name": "Anthropic (Claude)",
    },
    "openai": {
        "type": "openai",
        "base_url": None,
        "default_models": ["gpt-4o", "gpt-4o-mini"],
        "display_name": "OpenAI (GPT)",
    },
    "google": {
        "type": "google",
        "base_url": None,
        "default_models": ["gemini-2.0-flash", "gemini-2.0-pro"],
        "display_name": "Google (Gemini)",
    },
    # OpenAI-compatible providers
    "deepseek": {
        "type": "openai_compatible",
        "base_url": "https://api.deepseek.com/v1",
        "default_models": ["deepseek-chat", "deepseek-reasoner"],
        "display_name": "DeepSeek",
    },
    "openrouter": {
        "type": "openai_compatible",
        "base_url": "https://openrouter.ai/api/v1",
        "default_models": ["anthropic/claude-3.5-sonnet", "google/gemini-pro"],
        "display_name": "OpenRouter",
    },
    "fireworks": {
        "type": "openai_compatible",
        "base_url": "https://api.fireworks.ai/inference/v1",
        "default_models": ["accounts/fireworks/models/llama-v3p1-70b-instruct"],
        "display_name": "Fireworks AI",
    },
    "together": {
        "type": "openai_compatible",
        "base_url": "https://api.together.xyz/v1",
        "default_models": ["meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"],
        "display_name": "Together AI",
    },
    "nanogpt": {
        "type": "openai_compatible",
        "base_url": "https://api.nano-gpt.com/v1",
        "default_models": ["chatgpt-4o-latest"],
        "display_name": "NanoGPT",
    },
    "chutes": {
        "type": "openai_compatible",
        "base_url": "https://llm.chutes.ai/v1",
        "default_models": ["deepseek-ai/DeepSeek-R1"],
        "display_name": "Chutes AI",
    },
    "kimi": {
        "type": "openai_compatible",
        "base_url": "https://api.moonshot.cn/v1",
        "default_models": ["moonshot-v1-128k"],
        "display_name": "Kimi (Moonshot)",
    },
    "minimax": {
        "type": "openai_compatible",
        "base_url": "https://api.minimax.chat/v1",
        "default_models": ["abab6.5s-chat"],
        "display_name": "MiniMax",
    },
    "groq": {
        "type": "openai_compatible",
        "base_url": "https://api.groq.com/openai/v1",
        "default_models": ["llama-3.3-70b-versatile"],
        "display_name": "Groq",
    },
    "mistral": {
        "type": "openai_compatible",
        "base_url": "https://api.mistral.ai/v1",
        "default_models": ["mistral-large-latest"],
        "display_name": "Mistral AI",
    },
    "perplexity": {
        "type": "openai_compatible",
        "base_url": "https://api.perplexity.ai",
        "default_models": ["llama-3.1-sonar-large-128k-online"],
        "display_name": "Perplexity",
    },
    "sambanova": {
        "type": "openai_compatible",
        "base_url": "https://api.sambanova.ai/v1",
        "default_models": [],
        "display_name": "SambaNova",
    },
    "cerebras": {
        "type": "openai_compatible",
        "base_url": "https://api.cerebras.ai/v1",
        "default_models": [],
        "display_name": "Cerebras",
    },
    "novita": {
        "type": "openai_compatible",
        "base_url": "https://api.novita.ai/v3/openai",
        "default_models": [],
        "display_name": "Novita AI",
    },
}


def generate_default_settings_yaml():
    """Generate the default YAML settings template with all providers."""
    lines = ["---"]
    lines.append("providers:")
    for name, info in PROVIDERS.items():
        lines.append(f"  {name}:")
        if info["base_url"]:
            lines.append(f'    base_url: "{info["base_url"]}"')
        lines.append('    api_key: ""')
        models_str = ", ".join(f'"{m}"' for m in info["default_models"])
        lines.append(f"    models: [{models_str}]")
    lines.append("  custom:")
    lines.append('    base_url: ""')
    lines.append('    api_key: ""')
    lines.append("    models: []")
    lines.append("")
    lines.append("review:")
    lines.append("  max_concurrent_calls: 3")
    lines.append("  timeout_seconds: 120")
    lines.append("  cost_warning_threshold: 5.00")
    lines.append("")
    lines.append("pivot:")
    lines.append("  threshold_percent: 20")
    lines.append('  compare_against: "last_reviewed_version"')
    lines.append("---")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_default_settings_yaml())
