"""Modal app: hosts an open-source instruction-tuned LLM and exposes a single
web endpoint used by the backend for two jobs:

  - task="score_relevance": confirm FMCG-deal relevance + extract structured
    deal fields (companies, deal type, amount, one-line summary) for a batch
    of prefiltered articles in one call.
  - task="draft_newsletter": turn a batch of relevant, credibility-tagged
    articles into a structured newsletter (markdown + JSON sections).

Model choice is left to whoever deploys this (swap MODEL_NAME below). Any
vLLM-servable instruct model with decent JSON-following works; a 7-8B model
is plenty for this task and keeps cold starts/cost low.

Run locally with:  modal serve modal_app/llm_service.py
Deploy with:        modal deploy modal_app/llm_service.py
"""
from __future__ import annotations

import json

import modal

MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"  # swap for whichever OSS model you host

app = modal.App("fmcg-intel-llm")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("vllm==0.6.3", "fastapi[standard]", "huggingface_hub")
)

RELEVANCE_SYSTEM_PROMPT = """You are an analyst screening news articles for an FMCG \
(fast-moving consumer goods) M&A and investment newsletter. For each article, decide \
whether it describes an actual FMCG-sector deal (acquisition, merger, investment, \
funding round, stake purchase, divestment, IPO, or joint venture). Respond with STRICT \
JSON only, matching this shape:
{"results": [{"index": 0, "is_relevant": true, "relevance_score": 0.9, \
"deal_type": "acquisition", "companies": ["Acquirer", "Target"], \
"deal_amount": "$120M", "one_line_summary": "..."}]}
If an article is not a real FMCG deal, set is_relevant to false and leave the deal \
fields null. deal_amount should be null if not stated in the text -- do not guess."""

NEWSLETTER_SYSTEM_PROMPT = """You are drafting a concise FMCG M&A/investment newsletter \
for a business audience who skims it in under two minutes. Group the given deals into \
sensible sections (e.g. "Top Deals", "Funding Rounds", "Other Activity") ordered by \
significance. Respond with STRICT JSON only, matching this shape:
{"markdown": "# FMCG Deal Intelligence\\n\\n## Top Deals\\n...", \
"sections": [{"title": "Top Deals", "deals": [{"headline": "...", \
"companies": ["..."], "deal_type": "acquisition", "deal_amount": "$120M", \
"summary": "one or two sentences", "sources": ["reuters.com"], \
"credibility_tier": "A"}]}]}
Keep each deal summary to 1-2 sentences. Do not invent facts not present in the input."""


@app.cls(gpu="A10G", image=image, scaledown_window=300)
class LLMService:
    @modal.enter()
    def load(self):
        from vllm import LLM, SamplingParams

        self.llm = LLM(model=MODEL_NAME, max_model_len=8192)
        self.sampling_params = SamplingParams(temperature=0.1, max_tokens=2048)

    def _generate_json(self, system_prompt: str, user_content: str) -> dict:
        prompt = (
            f"<|start_header_id|>system<|end_header_id|>\n{system_prompt}"
            f"<|eot_id|><|start_header_id|>user<|end_header_id|>\n{user_content}"
            f"<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
        )
        output = self.llm.generate([prompt], self.sampling_params)[0]
        text = output.outputs[0].text.strip()
        # models occasionally wrap JSON in markdown fences -- strip if present
        if text.startswith("```"):
            text = text.strip("`")
            text = text.split("\n", 1)[1] if "\n" in text else text
        return json.loads(text)

    @modal.method()
    def score_relevance(self, articles: list[dict]) -> dict:
        return self._generate_json(RELEVANCE_SYSTEM_PROMPT, json.dumps({"articles": articles}))

    @modal.method()
    def draft_newsletter(self, articles: list[dict]) -> dict:
        return self._generate_json(NEWSLETTER_SYSTEM_PROMPT, json.dumps({"articles": articles}))


@app.function(image=image)
@modal.fastapi_endpoint(method="POST")
def infer(body: dict):
    """Single HTTP entrypoint the backend calls: {"task": ..., "payload": {...}}."""
    task = body.get("task")
    payload = body.get("payload", {})
    service = LLMService()

    if task == "score_relevance":
        return service.score_relevance.remote(payload.get("articles", []))
    if task == "draft_newsletter":
        return service.draft_newsletter.remote(payload.get("articles", []))
    return {"error": f"unknown task: {task}"}
