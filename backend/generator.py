import logging
from openai import OpenAI
from .config import cfg

logger = logging.getLogger(__name__)

_PROMPT = """\
You are a precise assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say: "I couldn't find that in the provided documents."
Be concise (3-5 sentences). Do not speculate.

Context:
{context}

Question: {question}

Answer:"""


class Generator:
    def __init__(self):
        self._client = OpenAI(
            api_key=cfg.OPENROUTER_API_KEY,
            base_url=cfg.OPENROUTER_BASE_URL,
        )

    def generate(self, question: str, docs: list) -> str:
        if not docs:
            context = "No relevant documents found."
        else:
            context = "\n\n---\n\n".join(
                f"[Source: {d.metadata.get('source', 'unknown')}]\n{d.page_content}"
                for d in docs
            )

        prompt = _PROMPT.format(context=context, question=question)

        try:
            resp = self._client.chat.completions.create(
                model=cfg.OPENROUTER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=cfg.LLM_TEMPERATURE,
                max_tokens=cfg.LLM_MAX_TOKENS,
                extra_body={"reasoning": {"enabled": True}},
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            raise RuntimeError(f"LLM error: {e}") from e
