# Academic Review Suite

A Claude Code plugin for comprehensive pre-submission academic paper review. Three-stage pipeline: multi-LLM consensus, reference verification, and human-perception stress testing.

## Why

Papers often pass methodology checks but fail human reviewers due to presentation issues ("Soundness 4, Overall 2" gap). Conversely, well-written papers may have methodological blind spots a single reviewer misses. This plugin addresses both by combining external LLM reviews with systematic human-perception testing.

## Install

```bash
claude plugin install abhinaba/academic-review-suite
```

## Usage

```bash
/review-paper path/to/paper.tex
/review-paper path/to/paper.pdf --venue ACL
/review-paper --resume  # Continue interrupted review
```

On first run, the plugin prompts for LLM provider API keys.

## Pipeline

The `/review-paper` command runs a 6-step pipeline:

| Step | What | External APIs? |
|------|------|----------------|
| 1. Setup | Load settings, extract paper text, create baseline | No |
| 2. LLM Review | Dispatch paper to multiple LLMs, synthesize reviews | Yes |
| 3. Fix Loop | Fix writing issues, detect pivots (>20% change triggers re-review) | No |
| 4. Reference Check | Verify references against OpenAlex, Semantic Scholar, CrossRef | Yes (free) |
| 5. Human Perception | Three-stage C/B/A stress test funnel | No |
| 6. Final Gate | Green/Yellow/Red readiness assessment | No |

## Components

### Agents

| Agent | Purpose |
|-------|---------|
| `llm-reviewer` | Coordinates multi-LLM reviews with health checks, cost estimation, and consensus synthesis |
| `reference-checker` | Extracts and verifies all references against 3 academic APIs |
| `human-perception` | Runs the C/B/A three-stage human-perception stress test |

### Scripts

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `providers.py` | Registry of 17+ LLM providers with settings template | stdlib only |
| `call_llm.py` | Universal LLM caller routing to Anthropic/OpenAI/Google SDKs | `anthropic`, `openai`, `google-generativeai` |
| `check_references.py` | Reference verification against CrossRef, OpenAlex, Semantic Scholar | stdlib only |
| `diff_detector.py` | Line-level diff for pivot detection (20% threshold) | stdlib only |

### Human Perception Review (C/B/A Funnel)

**Stage C** (runs once): Broad sweep
- C1: Presentation quality (red thread, worked examples, figure self-containment)
- C2: Logical consistency (number matching, cross-references, overclaiming)
- C3: Adversarial stress test (weakest claim, missing comparisons, counterarguments)

**Stage B** (runs after C, then after each A): Role-based stress test
- B1: The Skimmer (title/abstract/figures only, 2-minute read)
- B2: The Confused Reader (flags every point of confusion)
- B3: The Hostile Reviewer (5 specific objections with damage ratings)
- B4: The Copy Editor (grammar, formatting, consistency)

**Stage A** (fine-grained): Reader journey
- A1: First impression (30-second skim)
- A2: Narrative thread (red thread construction, argument breaks, sag point)
- A3: Concrete grounding (examples for every key claim, math islands)
- A4: Internal consistency audit (numbers, cross-references, claims vs evidence)
- A5: Reviewer pushback simulation (mock Overall:2 and Overall:4 reviews)

**Loop**: A -> fix -> B -> pass? If no, back to A. Max 3 iterations.

### Readiness Assessment

| Level | Criteria | Recommendation |
|-------|----------|----------------|
| Green | 0 Critical, <=2 Important, B1 interest >= 4 | Submit with confidence |
| Yellow | 0 Critical, <=5 Important, B1 interest >= 3 | Submit with known risks |
| Red | Any Critical OR >5 Important OR B1 interest < 3 | Revise before submitting |

## Supported LLM Providers

**Native APIs**: Anthropic (Claude), OpenAI (GPT), Google (Gemini)

**OpenAI-compatible**: DeepSeek, OpenRouter, Fireworks, Together, NanoGPT, Chutes, Kimi, MiniMax, Groq, Mistral, Perplexity, SambaNova, Cerebras, Novita, plus any custom endpoint.

## Configuration

Settings are stored in `.claude/academic-review-suite.local.md` (per-project, gitignored). The file uses YAML frontmatter:

```yaml
---
providers:
  anthropic:
    api_key: "sk-..."
    models: ["claude-sonnet-4-20250514"]
  openai:
    api_key: "sk-..."
    models: ["gpt-4o"]

review:
  max_concurrent_calls: 3
  timeout_seconds: 120
  cost_warning_threshold: 5.00

pivot:
  threshold_percent: 20
---
```

Generate a default template:

```bash
python3 ~/.claude/plugins/academic-review-suite/scripts/providers.py
```

## Requirements

- Claude Code
- Python 3.10+
- For LLM review: `pip install anthropic openai google-generativeai` (only the SDKs for your configured providers)
- For reference checking and diff detection: no extra packages (stdlib only)

## License

MIT
