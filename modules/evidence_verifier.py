
import re

from modules.summarizer import generate_response


ALLOWED_STATUSES = {
    "SUPPORTED",
    "NOT SUPPORTED",
    "INSUFFICIENT EVIDENCE"
}


def verify_claim(claim, source_text):

    if not claim.strip() or not source_text.strip():
        return {
            "status": "INSUFFICIENT EVIDENCE",
            "explanation": "Claim or source material is empty."
        }

    system_prompt = """
You are a strict academic evidence verification assistant.

Your task is to determine whether the supplied source
actually provides evidence for the supplied claim.

STRICT RULES:

1. Use ONLY the supplied source material.
2. Do not use outside knowledge.
3. SUPPORTED:
   The source explicitly provides evidence for the claim.
4. NOT SUPPORTED:
   The source explicitly contradicts the claim.
5. INSUFFICIENT EVIDENCE:
   The source does not provide enough information.
6. Similar wording alone does not prove a claim.
7. Do not assume facts that the source does not state.
8. Never invent quotations or evidence.
9. If uncertain, choose INSUFFICIENT EVIDENCE.

Return exactly this format:

STATUS: SUPPORTED

EXPLANATION: Explain the evidence in the source.

Allowed statuses:
SUPPORTED
NOT SUPPORTED
INSUFFICIENT EVIDENCE
"""

    prompt = f"""
CLAIM TO VERIFY:
{claim}

SOURCE MATERIAL:
{source_text[:12000]}

Determine whether this exact source supports the claim.
"""

    response = generate_response(prompt, system_prompt)

    status_match = re.search(
        r"STATUS\s*:\s*(SUPPORTED|NOT SUPPORTED|INSUFFICIENT EVIDENCE)",
        response,
        re.IGNORECASE
    )

    explanation_match = re.search(
        r"EXPLANATION\s*:\s*(.*)",
        response,
        re.IGNORECASE | re.DOTALL
    )

    status = (
        status_match.group(1).upper()
        if status_match
        else "INSUFFICIENT EVIDENCE"
    )

    if status not in ALLOWED_STATUSES:
        status = "INSUFFICIENT EVIDENCE"

    explanation = (
        explanation_match.group(1).strip()
        if explanation_match
        else "The AI could not provide a valid verification explanation."
    )

    return {
        "status": status,
        "explanation": explanation
    }
