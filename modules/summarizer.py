
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def generate_response(prompt, system_prompt=None):

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 2500
        }
    }

    if system_prompt:
        payload["system"] = system_prompt

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=240
        )

        response.raise_for_status()

        result = response.json().get("response", "").strip()

        if not result:
            raise RuntimeError("Ollama returned an empty response.")

        return result

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. Check whether Ollama is running."
        )

    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama request timed out.")

    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Ollama API error: {error}")


def get_source_ids(text):
    """Extract source IDs explicitly present in research material."""

    return sorted(set(
        re.findall(
            r"SOURCE ID:\s*\[(S\d+)\]",
            text
        )
    ))


def find_uncited_paragraphs(report):
    """Find factual paragraphs without valid inline citations."""

    uncited = []

    for paragraph in report.split("\n\n"):

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if paragraph.startswith("#"):
            continue

        if re.match(
            r"^(references|bibliography)\s*:?\s*$",
            paragraph,
            re.IGNORECASE
        ):
            break

        # Headings and empty paragraphs are ignored.
        if len(paragraph.split()) < 5:
            continue

        if not re.search(r"\[S\d+\]", paragraph):
            uncited.append(paragraph)

    return uncited


def summarize_text(text, topic):

    source_ids = get_source_ids(text)

    if not source_ids:
        raise ValueError(
            "No valid source IDs were found in research material."
        )

    allowed_ids = ", ".join(
        f"[{source_id}]" for source_id in source_ids
    )

    system_prompt = """
You are an academic research assistant.

STRICT RULES:

1. Use ONLY the supplied research material.
2. Do not use outside knowledge.
3. Every factual paragraph must contain an inline citation.
4. Use citations exactly in the format [S1], [S2], etc.
5. Only use source IDs explicitly supplied in the material.
6. Cite a source only when its content supports the statement.
7. Never invent studies, authors, statistics, dates or findings.
8. Do not use numeric citations.
9. Do not create a References or Bibliography section.
10. Do not repeat unsupported information.
11. If evidence is unavailable, explicitly state that.
12. Keep the report concise and academically structured.

A citation must appear at the end of the relevant factual sentence.
"""

    prompt = f"""
RESEARCH TOPIC:
{topic}

VALID SOURCE IDS:
{allowed_ids}

RESEARCH MATERIAL:
{text}

Write a research report with these sections:

1. Introduction
2. Main Findings
3. Important Insights
4. Benefits and Opportunities
5. Challenges and Limitations
6. Conclusion

CITATION REQUIREMENTS:

- Every factual paragraph must have at least one valid citation.
- Use only the source IDs listed above.
- Cite the source that actually supports each statement.
- Do not attach citations randomly.
- Do not invent information to fill gaps.
- Keep each paragraph focused on evidence from the sources.

Return only the report.
"""

    # STAGE 1: Generate the initial research report.
    report = generate_response(
        prompt,
        system_prompt
    )

    # Remove any model-generated reference section.
    report = re.sub(
        r"(?im)^\s{0,3}#{0,3}\s*(references|bibliography)"
        r"\s*:?\s*$[\s\S]*$",
        "",
        report
    ).strip()

    # STAGE 2: Check whether factual paragraphs have citations.
    uncited = find_uncited_paragraphs(report)

    if uncited:

        repair_prompt = f"""
RESEARCH TOPIC:
{topic}

VALID SOURCE IDS:
{allowed_ids}

ORIGINAL RESEARCH MATERIAL:
{text}

REPORT REQUIRING CITATION REPAIR:
{report}

TASK:

Rewrite the complete report.

Rules:

1. Every factual paragraph must contain a valid inline citation.
2. Use only these source IDs: {allowed_ids}.
3. Each citation must be supported by the corresponding source.
4. Do not invent or guess citations.
5. Remove claims that cannot be supported by the supplied sources.
6. Do not add outside information.
7. Preserve the original report structure.
8. Do not include a References section.

Return only the corrected report.
"""

        repair_system_prompt = """
You are an academic citation editor.

Your task is to correct missing or unsupported citations.
Never invent a source citation.
Use only evidence explicitly present in the supplied research material.
If a claim cannot be supported, remove it or state that evidence is
insufficient.
"""

        repaired_report = generate_response(
            repair_prompt,
            repair_system_prompt
        )

        if repaired_report:

            repaired_report = re.sub(
                r"(?im)^\s{0,3}#{0,3}\s*(references|bibliography)"
                r"\s*:?\s*$[\s\S]*$",
                "",
                repaired_report
            ).strip()

            report = repaired_report

    return report
