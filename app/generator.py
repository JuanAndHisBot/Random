import json
from anthropic import Anthropic
from config import Config


client = Anthropic()


def generate_daily_module(topic):
    """
    Generate a daily learning module using Claude API.
    Returns a dict with topic, theory_overview, code_examples, and socratic_questions.
    """
    prompt = f"""Generate a high-level, educational learning module about: {topic}

Create the output in JSON format with the following structure:
{{
    "topic": "{topic}",
    "theory_overview": "2-3 paragraph overview introducing key concepts",
    "code_examples": [
        {{
            "title": "Example Title",
            "language": "python/javascript/go/etc",
            "code": "code snippet here"
        }}
    ],
    "socratic_questions": [
        {{
            "question_number": 1,
            "question_text": "Opening question that probes understanding",
            "model_answer": "Concise answer",
            "explanation": "Why this answer matters and connects to theory",
            "code_context": {{"referenced_example": 0}} or {{}}
        }},
        ... (7 questions total, progressively building)
    ]
}}

Guidelines for Socratic questions:
- Q1: Introductory, probes prior knowledge
- Q2-Q5: Progressive questions building on answers, revealing deeper concepts
- Q6-Q7: Synthesis questions connecting concepts and encouraging practical thinking
- Keep model_answer concise (2-3 sentences)
- Explanation should clarify WHY the answer matters and how it connects to the theory
- code_context can reference code_examples by index or be empty
- All answers should encourage deeper thinking, not just memorization

Ensure the output is valid JSON that can be parsed."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    try:
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            module_data = json.loads(json_str)
        else:
            raise ValueError("Could not find JSON in response")
    except json.JSONDecodeError as e:
        print(f"Error parsing Claude response: {e}")
        print(f"Response: {response_text}")
        raise

    return module_data
