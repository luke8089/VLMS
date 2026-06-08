"""
Google Gemini AI Service
Uses the Gemini REST API directly (no SDK — avoids pydantic/dependency conflicts).
Model: gemini-1.5-flash  (free tier: 15 RPM, 1M TPM, 1 500 RPD)

Configure via .env:
  GEMINI_API_KEY=<your key>
  GEMINI_MODEL=gemini-1.5-flash   (optional override)
"""

import json
import logging
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "60"))

_MAX_INPUT_CHARS = 150_000


def gemini_available() -> bool:
    """Return True if a Gemini API key is configured."""
    return bool(GEMINI_API_KEY)


def _generate(prompt: str) -> str:
    """Call the Gemini REST API and return the response text."""
    url = f"{GEMINI_BASE}/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4},
    }
    resp = requests.post(url, json=payload, timeout=GEMINI_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


# ───────────────────── public API ─────────────────────

def summarize_text(text: str, max_words: int = 400) -> str:
    """
    Summarise an academic document using Gemini 1.5 Flash.
    Sends the full document in one call (1M-token context window — no chunking needed).
    Falls back to TF-IDF extractive summarisation when Gemini is unavailable.
    """
    if not text or len(text.strip()) < 50:
        return text

    if not gemini_available():
        logger.warning("Gemini not configured — falling back to TF-IDF summariser")
        from ai_modules.learning_ai.summarizer import TextSummarizer
        return TextSummarizer().summarize(text, num_sentences=10)

    prompt = (
        f"You are an academic assistant. Carefully read the entire educational document "
        f"below and produce a comprehensive summary of at most {max_words} words. "
        f"Cover all major topics, key concepts, definitions, and important details. "
        f"Output ONLY the summary — no preamble, no headings.\n\n"
        f"--- DOCUMENT ---\n{text[:_MAX_INPUT_CHARS]}\n--- END ---"
    )

    try:
        return _generate(prompt)
    except Exception as e:
        logger.error("Gemini summarisation error: %s", e)
        from ai_modules.learning_ai.summarizer import TextSummarizer
        return TextSummarizer().summarize(text, num_sentences=10)


def generate_questions_llm(
    text: str,
    num_questions: int = 10,
    difficulty: str = "understand",
    question_types: list | None = None,
) -> list[dict]:
    """
    Generate exam questions from the full document text using Gemini 1.5 Flash.
    Sends the complete text in one call — no chunking, no truncation.
    Falls back to Ollama (then rule-based) if Gemini is unavailable.
    """
    if not text or len(text.strip()) < 50:
        return []

    if not gemini_available():
        logger.warning("Gemini not configured — falling back to Ollama")
        from ai_modules.ollama_service import generate_questions_llm as ollama_gen
        return ollama_gen(text, num_questions, difficulty, question_types)

    if question_types is None:
        question_types = ["mcq", "short_answer"]

    types_desc = ", ".join(question_types)

    prompt = f"""You are an expert academic exam creator. Read the entire educational document below and create exactly {num_questions} high-quality exam questions.

STRICT RULES:
- Every question MUST be directly answerable from the provided content — do NOT invent or assume facts
- Base every question and every answer option strictly on what is written in the material
- Difficulty level (Bloom's taxonomy): {difficulty}
- Question types: {types_desc}
- For MCQ: provide exactly 4 answer options; all must be plausible, only ONE is correct
- For short_answer: write a concise model answer using the document's own words
- For essay: list key points the answer should cover (all drawn from the material)

OUTPUT FORMAT — return ONLY a valid JSON array, nothing else (no markdown, no intro text):
[
  {{
    "question_text": "...",
    "question_type": "mcq" | "short_answer" | "essay",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "exact text of the correct option (mcq) or model answer (other types)",
    "marks": 2,
    "difficulty": "{difficulty}",
    "explanation": "one sentence noting where in the material this comes from"
  }}
]

--- COURSE MATERIAL ---
{text[:_MAX_INPUT_CHARS]}
--- END ---

JSON array:"""

    try:
        raw = _generate(prompt)
        return _parse_questions_json(raw, question_types, difficulty)
    except Exception as e:
        logger.error("Gemini question generation error: %s", e)
        return []


def _nlp_grade(question_type: str, student_answer: str, correct_answer: str, max_marks: float) -> tuple[float, str]:
    """NLP cosine-similarity fallback when Gemini is unavailable."""
    try:
        from ai_modules.assessment_ai.essay_grader import EssayGrader
        grader = EssayGrader()
        if question_type == "essay":
            score, feedback = grader.grade_essay(student_answer, correct_answer or "", max_marks)
            if isinstance(feedback, dict):
                feedback = " ".join(v.get("feedback", "") for v in feedback.values())
            return score, feedback
        return grader.grade_short_answer(student_answer, correct_answer or "", max_marks)
    except Exception as e:
        logger.error("NLP grader fallback error: %s", e)
        return 0.0, "Answer received. Awaiting manual review."


def grade_answer(
    question_text: str,
    question_type: str,
    student_answer: str,
    correct_answer: str,
    max_marks: float,
) -> tuple[float, str]:
    """
    Use Gemini to grade a student answer.
    Returns (score, feedback) — falls back to NLP grader if Gemini is unavailable.
    """
    if not gemini_available():
        return _nlp_grade(question_type, student_answer, correct_answer, max_marks)

    if not student_answer or not student_answer.strip():
        return 0.0, "No answer provided."

    prompt = f"""You are an expert academic examiner. Grade the following student answer fairly and accurately.

QUESTION ({question_type.replace('_', ' ')}):
{question_text}

CORRECT/MODEL ANSWER:
{correct_answer}

STUDENT ANSWER:
{student_answer}

MAX MARKS: {max_marks}

INSTRUCTIONS:
- Award a score between 0 and {max_marks} (decimals allowed, e.g. 1.5)
- For MCQ: award full marks if the student selected the correct option, 0 otherwise
- For short_answer: award marks proportional to correctness and completeness
- For essay: assess coverage of key points, depth of understanding, and accuracy
- Write 1-2 sentences of constructive feedback explaining the score
- Be strict but fair

RESPOND WITH EXACTLY THIS FORMAT (no other text):
SCORE: <number>
FEEDBACK: <your feedback>"""

    try:
        raw = _generate(prompt)
        score_match = re.search(r"SCORE:\s*([\d.]+)", raw)
        feedback_match = re.search(r"FEEDBACK:\s*(.+)", raw, re.DOTALL)
        if not score_match:
            raise ValueError("No score in Gemini response")
        score = min(float(score_match.group(1)), float(max_marks))
        score = max(0.0, score)
        feedback = feedback_match.group(1).strip() if feedback_match else "Graded by AI."
        return round(score, 2), feedback
    except Exception as e:
        logger.error("Gemini grading error: %s", e)
        return _nlp_grade(question_type, student_answer, correct_answer, max_marks)


def analyze_violations(
    violations: list[dict],
    student_name: str,
    exam_name: str,
    risk_score: int,
) -> str:
    """
    Use Gemini to produce a human-readable risk assessment from proctoring violations.
    Returns a narrative string; falls back to a formatted summary if Gemini is unavailable.
    """
    if not violations:
        return "No violations detected during this exam session."

    violation_lines = "\n".join(
        f"- {v.get('violation_type', 'unknown')} (severity +{v.get('severity', 0)})"
        + (f": {v.get('description', '')}" if v.get('description') else "")
        for v in violations
    )

    if not gemini_available():
        return (
            f"Proctoring Report for {student_name} — {exam_name}\n"
            f"Risk Score: {risk_score}/100\n\n"
            f"Violations detected:\n{violation_lines}\n\n"
            f"Manual review {'recommended' if risk_score >= 50 else 'not required at this time'}."
        )

    prompt = f"""You are an academic integrity officer reviewing an automated proctoring report.
Write a concise, professional risk assessment (3-5 sentences) for the following case.

STUDENT: {student_name}
EXAM: {exam_name}
CUMULATIVE RISK SCORE: {risk_score} / 100

VIOLATIONS DETECTED:
{violation_lines}

GUIDELINES:
- Risk score < 30: low concern, minor distractions
- Risk score 30-59: moderate concern, warrants review
- Risk score 60-79: high concern, likely irregularity
- Risk score ≥ 80: critical, strong evidence of malpractice

Write the assessment as plain prose — no bullet points, no headings, no markdown.
State the risk level, describe the pattern of behaviour suggested by the violations, and recommend a next action."""

    try:
        return _generate(prompt)
    except Exception as e:
        logger.error("Gemini violation analysis error: %s", e)
        return (
            f"Proctoring Report for {student_name} — {exam_name}\n"
            f"Risk Score: {risk_score}/100\n\n"
            f"Violations:\n{violation_lines}"
        )


def generate_recommendations(
    weak_areas: list[dict],
    study_pattern: dict,
    student_name: str,
    course_name: str,
) -> str:
    """
    Use Gemini to produce personalised learning recommendations.
    Returns a narrative string; falls back to generic rule-based text if unavailable.
    """
    if not gemini_available():
        recs = []
        for area in weak_areas:
            recs.append(
                f"Focus on {area.get('difficulty', 'core')} level topics — "
                f"current accuracy: {area.get('accuracy', 0):.0f}%"
            )
        return "\n".join(recs) if recs else "Keep up the good work and continue revising course materials."

    weak_lines = "\n".join(
        f"- Bloom's level: {a.get('difficulty', 'N/A')}, "
        f"accuracy: {a.get('accuracy', 0):.0f}%, "
        f"attempts: {a.get('attempts', 0)}"
        for a in weak_areas
    ) or "None identified"

    prompt = f"""You are a personalised learning coach. Write tailored, actionable study recommendations
for the following student based on their performance data.

STUDENT: {student_name}
COURSE: {course_name}

WEAK AREAS (topics where accuracy is below 70%):
{weak_lines}

STUDY PATTERN:
- Total study time: {study_pattern.get('total_time_hours', 0):.1f} hours
- Materials completed: {study_pattern.get('completed_materials', 0)} of {study_pattern.get('total_materials', 0)}
- Average exam score: {study_pattern.get('avg_score', 0):.1f}%

INSTRUCTIONS:
- Write 3-5 concrete, specific recommendations (numbered list)
- Reference the actual weak areas by their Bloom's level (e.g. "application-level questions")
- Suggest specific study strategies (e.g. practice problems, spaced repetition, concept mapping)
- Keep each recommendation to 1-2 sentences
- End with one encouraging sentence
- Use plain text only — no markdown headers or bold"""

    try:
        return _generate(prompt)
    except Exception as e:
        logger.error("Gemini recommendations error: %s", e)
        recs = [
            f"Focus on {a.get('difficulty', 'core')}-level topics (accuracy: {a.get('accuracy', 0):.0f}%)"
            for a in weak_areas
        ]
        return "\n".join(recs) if recs else "Continue reviewing all course materials regularly."


def _parse_questions_json(raw: str, question_types: list, difficulty: str) -> list[dict]:
    """
    Robust parser for LLM JSON question arrays.
    Handles single objects, markdown fences, truncated JSON, and variant field names.
    """
    if not raw:
        return []

    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()

    arr_start, arr_end = cleaned.find("["), cleaned.rfind("]")
    obj_start, obj_end = cleaned.find("{"), cleaned.rfind("}")

    if arr_start != -1 and arr_end > arr_start:
        segment = cleaned[arr_start: arr_end + 1]
    elif obj_start != -1 and obj_end > obj_start:
        segment = "[" + cleaned[obj_start: obj_end + 1] + "]"
    else:
        return []

    try:
        questions = json.loads(segment)
    except json.JSONDecodeError:
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

        qtext = (q.get("question_text") or q.get("question") or q.get("text") or "").strip()
        if not qtext:
            continue

        qtype = str(q.get("question_type") or q.get("type") or "short_answer").lower()
        if qtype not in ("mcq", "short_answer", "essay"):
            qtype = "short_answer"

        raw_opts = q.get("options") or q.get("choices")
        options = None
        if qtype == "mcq":
            if isinstance(raw_opts, list):
                options = [str(o) for o in raw_opts if o is not None and str(o).strip()]
            if not options or len(options) < 2:
                qtype = "short_answer"
                options = None

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
