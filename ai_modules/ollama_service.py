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
import random
import re
import time
import requests

OLLAMA_BASE = "http://localhost:11434"
# llama3.2:1b is the default: fast enough on CPU (~3 tok/s) to complete within timeouts.
# For machines with a GPU or >8 GB RAM, set OLLAMA_MODEL=llama3.1:8b for much better quality.
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
REQUEST_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "15"))
SUMMARIZE_TIMEOUT = int(os.getenv("OLLAMA_SUMMARIZE_TIMEOUT", "180"))
_CHUNK_SIZE = 5000  # chars per chunk sent to Ollama

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
    """
    Return the best model for CPU-only inference.

    Preference order (fast, small models first for CPU):
      llama3.2 (1B) > gemma3 (1B) > llama3.1 / llama3 (8B, GPU recommended) > qwen (4B) > mistral

    On machines with a GPU, set OLLAMA_MODEL env var to a larger model.
    """
    if os.getenv("OLLAMA_MODEL"):
        return os.getenv("OLLAMA_MODEL")
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        if resp.status_code != 200:
            return DEFAULT_MODEL
        models = [m["name"] for m in resp.json().get("models", [])]
        for preferred in ("llama3.2", "gemma3", "llama3.1", "llama3", "qwen", "mistral"):
            for m in models:
                if preferred in m.lower():
                    return m
        return models[0] if models else DEFAULT_MODEL
    except Exception:
        return DEFAULT_MODEL


def _generate(prompt: str, model: str | None = None, temperature: float = 0.7, timeout: int | None = None) -> str:
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
        timeout=timeout or REQUEST_TIMEOUT,
    )
    elapsed = time.time() - t0
    _response_times.append(elapsed)
    if len(_response_times) > _MAX_SAMPLES:
        _response_times.pop(0)

    # If model requires more RAM than available, retry with the 1B fallback
    if resp.status_code != 200:
        err = resp.text or ''
        if 'more system memory' in err or 'out of memory' in err.lower():
            logger.warning("Model %s OOM — retrying with llama3.2:1b fallback", model)
            payload["model"] = "llama3.2:1b"
            resp = requests.post(
                f"{OLLAMA_BASE}/api/generate",
                json=payload,
                timeout=timeout or REQUEST_TIMEOUT,
            )

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

def summarize_text(text: str, max_words: int = 200) -> str:
    """
    Summarise an academic document.

    Splits long documents into chunks, summarises each chunk via Ollama,
    then consolidates into a final summary.  Falls back to TF-IDF extractive
    summarisation when Ollama is unavailable.
    """
    if not text or len(text.strip()) < 50:
        return text

    if not _ollama_available():
        from ai_modules.learning_ai.summarizer import TextSummarizer
        return TextSummarizer().summarize(text, num_sentences=12)

    chunks = _chunk_text(text, _CHUNK_SIZE)

    if len(chunks) == 1:
        return _summarize_chunk(chunks[0], max_words)

    # Summarise each chunk independently then consolidate
    per_chunk_words = max(80, max_words // len(chunks) + 20)
    chunk_summaries = [s for s in (_summarize_chunk(c, per_chunk_words) for c in chunks) if s]

    if not chunk_summaries:
        return ''

    combined = '\n\n'.join(chunk_summaries)
    if len(combined.split()) <= max_words:
        return combined

    # Final consolidation pass over the chunk summaries
    return _summarize_chunk(combined, max_words, final_pass=True)


def _chunk_text(text: str, chunk_size: int) -> list[str]:
    """Split text into chunks at paragraph boundaries to avoid mid-sentence cuts."""
    paragraphs = text.split('\n\n')
    chunks, current, current_len = [], [], 0
    for para in paragraphs:
        if current_len + len(para) > chunk_size and current:
            chunks.append('\n\n'.join(current))
            current, current_len = [para], len(para)
        else:
            current.append(para)
            current_len += len(para)
    if current:
        chunks.append('\n\n'.join(current))
    return chunks or [text[:chunk_size]]


def _summarize_chunk(text: str, max_words: int, final_pass: bool = False) -> str:
    """Send one chunk to Ollama and return the summary text."""
    if final_pass:
        prompt = (
            "You are an academic assistant. The following are partial summaries of sections of "
            "an educational document. Consolidate them into a single coherent summary of at most "
            f"{max_words} words. Keep all key concepts, definitions, and important details. "
            "Output ONLY the final summary.\n\n"
            f"--- PARTIAL SUMMARIES ---\n{text}\n--- END ---"
        )
    else:
        prompt = (
            "You are an academic assistant. Summarise the following section of educational "
            f"material in at most {max_words} words. Keep key concepts, definitions, and "
            "important details. Output ONLY the summary, no preamble.\n\n"
            f"--- MATERIAL ---\n{text}\n--- END ---"
        )
    try:
        return _generate(prompt, temperature=0.3, timeout=SUMMARIZE_TIMEOUT)
    except Exception:
        return ''


def generate_questions_llm(
    text: str,
    num_questions: int = 10,
    difficulty: str = "understand",
    question_types: list[str] | None = None,
) -> list[dict]:
    """
    Use Ollama to generate exam questions from the full document text.

    For long documents the text is split into chunks; questions are generated
    per chunk and combined.  Returns dicts ready for DB insertion.
    """
    if not text or len(text.strip()) < 50:
        return []

    if not _ollama_available():
        return []

    if question_types is None:
        question_types = ["mcq", "short_answer"]

    chunks = _chunk_text(text, 6000)

    if len(chunks) == 1:
        return _gen_questions_from_chunk(text, num_questions, difficulty, question_types)

    # Distribute questions proportionally across chunks
    per_chunk = max(3, (num_questions + len(chunks) - 1) // len(chunks))
    all_questions: list[dict] = []
    for chunk in chunks:
        qs = _gen_questions_from_chunk(chunk, per_chunk, difficulty, question_types)
        all_questions.extend(qs)

    random.shuffle(all_questions)
    return all_questions[:num_questions]


def _gen_questions_from_chunk(
    text: str,
    num_questions: int,
    difficulty: str,
    question_types: list[str],
) -> list[dict]:
    """Send one chunk to Ollama and return parsed question dicts."""
    types_desc = ", ".join(question_types)
    prompt = f"""You are an expert academic exam creator. Read the educational content below carefully and create exactly {num_questions} high-quality exam questions.

CRITICAL RULES:
- Every question MUST be directly answerable from the provided content — do NOT invent facts
- Base every question and answer strictly on what is written in the material
- Difficulty level (Bloom's taxonomy): {difficulty}
- Question types to include: {types_desc}
- For MCQ: provide exactly 4 options; all options must be plausible but only one correct
- For short_answer: provide a concise model answer drawn from the material
- For essay: list the key points the answer should cover (from the material)

OUTPUT FORMAT — return ONLY a valid JSON array (no markdown, no extra text). Each element:
  "question_text": string,
  "question_type": one of "mcq", "short_answer", "essay",
  "options": array of 4 strings (mcq only, else null),
  "correct_answer": string,
  "marks": integer (mcq=2, short_answer=5, essay=10),
  "difficulty": "{difficulty}",
  "explanation": one sentence citing the source in the material

--- COURSE MATERIAL ---
{text}
--- END ---

JSON array:"""

    raw = _generate(prompt, temperature=0.4, timeout=SUMMARIZE_TIMEOUT)
    return _parse_questions_json(raw, question_types, difficulty)


def _parse_questions_json(
    raw: str, question_types: list[str], difficulty: str
) -> list[dict]:
    """
    Best-effort extraction of question dicts from LLM output.
    Handles: JSON arrays, single objects, markdown fences, truncated JSON,
    null/missing options, and variant field names from smaller models.
    """
    if not raw:
        return []

    # Strip markdown fences and leading/trailing whitespace
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()

    # Prefer a [ ... ] array; fall back to wrapping a lone { ... } object
    arr_start = cleaned.find("[")
    arr_end = cleaned.rfind("]")
    obj_start = cleaned.find("{")
    obj_end = cleaned.rfind("}")

    if arr_start != -1 and arr_end > arr_start:
        segment = cleaned[arr_start: arr_end + 1]
    elif obj_start != -1 and obj_end > obj_start:
        segment = "[" + cleaned[obj_start: obj_end + 1] + "]"
    else:
        return []

    # Attempt parse; if it fails try to recover truncated JSON
    try:
        questions = json.loads(segment)
    except json.JSONDecodeError:
        # Try trimming trailing incomplete object
        last_close = segment.rfind("}")
        if last_close != -1:
            try:
                questions = json.loads(segment[: last_close + 1] + "]")
            except json.JSONDecodeError:
                return []
        else:
            return []

    if isinstance(questions, dict):
        questions = [questions]
    if not isinstance(questions, list):
        return []

    marks_default = {"mcq": 2, "short_answer": 5, "essay": 10}

    valid = []
    for q in questions:
        if not isinstance(q, dict):
            continue

        # Accept variant field names small models produce
        qtext = (q.get("question_text") or q.get("question") or q.get("text") or "").strip()
        if not qtext:
            continue

        qtype = str(q.get("question_type") or q.get("type") or "short_answer").lower()
        if qtype not in ("mcq", "short_answer", "essay"):
            qtype = "short_answer"

        # Options: filter out null entries; downgrade to short_answer if < 2 real options
        raw_options = q.get("options") or q.get("choices")
        options = None
        if qtype == "mcq":
            if isinstance(raw_options, list):
                options = [str(o) for o in raw_options if o is not None and str(o).strip()]
            if not options or len(options) < 2:
                qtype = "short_answer"
                options = None

        # correct_answer: accept index (int/str) or literal text
        correct_answer = str(
            q.get("correct_answer") or q.get("answer") or q.get("correct") or ""
        ).strip()

        explanation = str(
            q.get("explanation") or q.get("explaining_text") or q.get("rationale") or ""
        ).strip()

        try:
            marks = int(q.get("marks") or marks_default.get(qtype, 2))
        except (TypeError, ValueError):
            marks = marks_default.get(qtype, 2)

        valid.append({
            "question_text": qtext,
            "question_type": qtype,
            "options": options,
            "correct_answer": correct_answer,
            "marks": marks,
            "difficulty": str(q.get("difficulty") or difficulty),
            "explanation": explanation,
        })

    return valid
