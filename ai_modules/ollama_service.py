"""
Ollama Integration Service
Connects to a locally-running Ollama instance for LLM-powered features:
  - Document summarization
  - Quiz / exam question generation
  - Content analysis

Requires: Ollama running at http://localhost:11434
Install: https://ollama.com   then `ollama pull llama3` or `ollama pull mistral`
"""

import json
import os
import re
import time
import requests

OLLAMA_BASE = "http://localhost:11434"
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
REQUEST_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "15"))

_response_times: list[float] = []  # rolling window of last 20 generate() durations (seconds)
_MAX_SAMPLES = 20


# ───────────────────── helpers ─────────────────────

def _ollama_available() -> bool:
    """Check whether the Ollama daemon is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


def _pick_model() -> str:
    """Return the first available model, preferring llama3.2 > llama3 > mistral > anything."""
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        if resp.status_code != 200:
            return DEFAULT_MODEL
        models = [m["name"] for m in resp.json().get("models", [])]
        for preferred in ("llama3.2", "llama3", "mistral", "gemma"):
            for m in models:
                if preferred in m.lower():
                    return m
        return models[0] if models else DEFAULT_MODEL
    except Exception:
        return DEFAULT_MODEL


def _generate(prompt: str, model: str | None = None, temperature: float = 0.7) -> str:
    """Send a prompt to Ollama and return the generated text."""
    model = model or _pick_model()
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    t0 = time.time()
    resp = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    elapsed = time.time() - t0
    _response_times.append(elapsed)
    if len(_response_times) > _MAX_SAMPLES:
        _response_times.pop(0)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def get_avg_response_time() -> str | None:
    """Return the average AI response time as a formatted string.

    Falls back to timing an Ollama /api/tags ping if no generate calls have
    been recorded yet.  Returns None only if Ollama is unreachable.
    """
    if _response_times:
        avg_s = sum(_response_times) / len(_response_times)
    else:
        # No generate calls yet — use a lightweight ping as a proxy
        try:
            t0 = time.time()
            resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
            if resp.status_code != 200:
                return None
            avg_s = time.time() - t0
        except Exception:
            return None

    if avg_s >= 1:
        return f"{avg_s:.1f}s"
    return f"{int(avg_s * 1000)}ms"


# ───────────────────── public API ─────────────────────

def summarize_text(text: str, max_words: int = 300) -> str:
    """
    Use Ollama to produce a concise summary of *text*.

    Falls back to returning the original text (truncated) if Ollama is
    unavailable.
    """
    if not text or len(text.strip()) < 50:
        return text

    if not _ollama_available():
        # Fallback: return first ~max_words words
        words = text.split()
        return " ".join(words[:max_words])

    prompt = (
        "You are an academic assistant. Summarise the following educational "
        f"material in at most {max_words} words. Keep key concepts, definitions, "
        "and important details. Output ONLY the summary, no preamble.\n\n"
        f"--- MATERIAL ---\n{text[:8000]}\n--- END ---"
    )
    return _generate(prompt, temperature=0.3)


def generate_questions_llm(
    text: str,
    num_questions: int = 10,
    difficulty: str = "understand",
    question_types: list[str] | None = None,
) -> list[dict]:
    """
    Use Ollama to generate exam questions from *text*.

    Returns a list of dicts ready for DB insertion:
      {question_text, question_type, options, correct_answer, marks, difficulty, explanation}
    """
    if not text or len(text.strip()) < 50:
        return []

    if not _ollama_available():
        return []  # caller should fall back to rule-based generator

    if question_types is None:
        question_types = ["mcq", "short_answer"]

    types_desc = ", ".join(question_types)

    prompt = f"""You are an expert academic exam creator. From the educational content below, create exactly {num_questions} high-quality exam questions.

REQUIREMENTS:
- Difficulty level (Bloom's taxonomy): {difficulty}
- Question types to include: {types_desc}
- For MCQ: provide exactly 4 options and indicate the correct one
- For short_answer: provide a concise model answer
- For essay: provide key points the answer should cover

OUTPUT FORMAT — return ONLY a valid JSON array (no markdown fences, no extra text). Each element must be an object with these exact keys:
  "question_text": string,
  "question_type": one of "mcq", "short_answer", "essay",
  "options": array of 4 strings (for mcq) or null,
  "correct_answer": string,
  "marks": integer (mcq=2, short_answer=5, essay=10),
  "difficulty": "{difficulty}",
  "explanation": brief explanation string

--- COURSE MATERIAL ---
{text[:6000]}
--- END ---

JSON array:"""

    raw = _generate(prompt, temperature=0.5)

    # Parse the JSON from the response
    return _parse_questions_json(raw, question_types, difficulty)


def _parse_questions_json(
    raw: str, question_types: list[str], difficulty: str
) -> list[dict]:
    """Best-effort extraction of a JSON array of question dicts from LLM output."""
    # Try to find JSON array in the response
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    cleaned = cleaned.strip("`").strip()

    # Try to locate [ ... ] bracket pair
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    try:
        questions = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    if not isinstance(questions, list):
        return []

    valid = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        if "question_text" not in q:
            continue

        qtype = q.get("question_type", "short_answer")
        if qtype not in ("mcq", "short_answer", "essay"):
            qtype = "short_answer"

        options = q.get("options")
        if qtype == "mcq":
            if not isinstance(options, list) or len(options) < 2:
                options = None
                qtype = "short_answer"

        marks_default = {"mcq": 2, "short_answer": 5, "essay": 10}

        valid.append({
            "question_text": str(q["question_text"]),
            "question_type": qtype,
            "options": options if qtype == "mcq" else None,
            "correct_answer": str(q.get("correct_answer", "")),
            "marks": int(q.get("marks", marks_default.get(qtype, 2))),
            "difficulty": q.get("difficulty", difficulty),
            "explanation": str(q.get("explanation", "")),
        })

    return valid
