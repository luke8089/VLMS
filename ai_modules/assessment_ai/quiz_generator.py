"""
Quiz Generator Module
Automatically generates quiz questions from text content.
Supports MCQ, short answer, and essay questions across Bloom's taxonomy levels.
"""
import re
import random
from collections import Counter


class QuizGenerator:
    """Generate quiz questions from text content."""

    # Bloom's taxonomy question stems
    BLOOM_STEMS = {
        'remember': [
            'What is {}?',
            'Define {}.',
            'List the {}.',
            'Name the {} mentioned.',
        ],
        'understand': [
            'Explain {} in your own words.',
            'What is the significance of {}?',
            'Describe {}.',
            'Summarize the concept of {}.',
        ],
        'apply': [
            'How would you apply {}?',
            'Give an example of {}.',
            'Demonstrate how {} works.',
            'How is {} used in practice?',
        ],
        'analyze': [
            'Compare and contrast {}.',
            'What are the key components of {}?',
            'Analyze the relationship between {}.',
            'What factors contribute to {}?',
        ],
        'evaluate': [
            'Evaluate the effectiveness of {}.',
            'What is your assessment of {}?',
            'Justify the importance of {}.',
            'Critique {}.',
        ],
        'create': [
            'Design a solution using {}.',
            'Propose an alternative approach to {}.',
            'How would you improve {}?',
            'Develop a plan for {}.',
        ],
    }

    def generate_from_text(self, text, num_questions=10, difficulty='understand',
                           question_types=None):
        """
        Generate questions from text content.
        Returns list of question dicts ready for database insertion.
        """
        if not text or len(text.strip()) < 50:
            return []

        if question_types is None:
            question_types = ['mcq', 'short_answer', 'essay']

        key_terms = self._extract_key_terms(text)
        sentences = self._split_sentences(text)

        questions = []

        # Generate MCQs
        if 'mcq' in question_types:
            mcqs = self._generate_mcq(sentences, key_terms, difficulty)
            questions.extend(mcqs)

        # Generate short answer questions
        if 'short_answer' in question_types:
            short_answers = self._generate_short_answer(sentences, key_terms, difficulty)
            questions.extend(short_answers)

        # Generate essay questions
        if 'essay' in question_types:
            essays = self._generate_essay(key_terms, difficulty)
            questions.extend(essays)

        random.shuffle(questions)
        return questions[:num_questions]

    def generate_from_material(self, material_id, num_questions=10, difficulty='understand'):
        """Generate questions from a stored material."""
        from database.models import Material
        material = Material.query.get(material_id)
        if not material:
            return [], 'Material not found'

        # For text-based materials, extract content
        # In production, parse PDFs with PyPDF2, slides with python-pptx, etc.
        text = material.ai_summary or ''
        if not text:
            return [], 'No text content available for this material'

        questions = self.generate_from_text(text, num_questions, difficulty)
        return questions, None

    def _extract_key_terms(self, text):
        """Extract important terms from text."""
        words = re.findall(r'\b[A-Za-z]{4,}\b', text)
        stopwords = {
            'that', 'this', 'with', 'from', 'have', 'been', 'were', 'they',
            'their', 'which', 'would', 'there', 'these', 'other', 'about',
            'when', 'what', 'some', 'them', 'than', 'each', 'make', 'like',
            'also', 'many', 'into', 'over', 'such', 'after', 'most', 'only',
            'could', 'very', 'more',
        }
        filtered = [w for w in words if w.lower() not in stopwords]
        counter = Counter(filtered)
        return [term for term, count in counter.most_common(20)]

    def _split_sentences(self, text):
        """Split text into meaningful sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if len(s.split()) > 5]

    # Question stems for MCQ by difficulty
    MCQ_STEMS = {
        'remember': 'According to the material, which of the following correctly describes {}?',
        'understand': 'Which statement best explains {}?',
        'apply': 'Which of the following demonstrates how {} is applied?',
        'analyze': 'Which option best analyzes the role of {}?',
        'evaluate': 'Which statement best evaluates the importance of {}?',
        'create': 'Which approach best describes how to work with {}?',
    }

    def _generate_mcq(self, sentences, key_terms, difficulty):
        """Generate multiple choice questions using sentences as answer options."""
        questions = []
        stem = self.MCQ_STEMS.get(difficulty, self.MCQ_STEMS['understand'])

        # Keep only sentences long enough to serve as answer options
        usable = [s.strip() for s in sentences if len(s.split()) >= 6]

        for i, sentence in enumerate(usable[:10]):
            target_word = None
            for term in key_terms:
                if term.lower() in sentence.lower():
                    target_word = term
                    break
            if not target_word:
                continue

            question_text = stem.format(target_word)
            correct_answer = sentence

            # Use other sentences as distractors so options are topical
            distractors = [s for s in usable if s != sentence][:3]
            while len(distractors) < 3:
                distractors.append(f"None of the above statements about {target_word} are correct.")

            options = distractors[:3] + [correct_answer]
            random.shuffle(options)
            correct_index = options.index(correct_answer)

            questions.append({
                'question_text': question_text,
                'question_type': 'mcq',
                'options': options,
                'correct_answer': str(correct_index),
                'marks': 2,
                'difficulty': difficulty,
                'explanation': f'From document: {correct_answer}',
            })

        return questions

    def _generate_short_answer(self, sentences, key_terms, difficulty):
        """Generate short answer questions anchored to document sentences."""
        questions = []
        stems = self.BLOOM_STEMS.get(difficulty, self.BLOOM_STEMS['understand'])

        for term in key_terms[:5]:
            # Find the richest sentence (most words) that mentions this term
            matching = [s for s in sentences if term.lower() in s.lower()]
            if not matching:
                continue
            best_sentence = max(matching, key=lambda s: len(s.split()))

            stem = random.choice(stems)
            question_text = stem.format(term)

            questions.append({
                'question_text': question_text,
                'question_type': 'short_answer',
                'options': None,
                'correct_answer': best_sentence,
                'marks': 5,
                'difficulty': difficulty,
                'explanation': f'Reference: {best_sentence}',
            })

        return questions

    def _generate_essay(self, key_terms, difficulty):
        """Generate essay questions."""
        questions = []
        stems = self.BLOOM_STEMS.get(difficulty, self.BLOOM_STEMS['evaluate'])

        # Combine terms for essay topics
        if len(key_terms) >= 2:
            topic = f"{key_terms[0]} and {key_terms[1]}"
        elif key_terms:
            topic = key_terms[0]
        else:
            return []

        stem = random.choice(stems)
        questions.append({
            'question_text': stem.format(topic),
            'question_type': 'essay',
            'options': None,
            'correct_answer': None,
            'marks': 20,
            'difficulty': difficulty,
            'explanation': 'Evaluate based on depth, clarity, and evidence.',
        })

        return questions
