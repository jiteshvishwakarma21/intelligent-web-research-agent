
import re

from modules.search_engine import search_web
from modules.web_scraper import scrape_website
from modules.text_cleaner import clean_text
from modules.summarizer import summarize_text
from modules.evidence_verifier import verify_claim


MAX_CLAIMS_TO_VERIFY = 20


# ============================================================
# 1. REMOVE MODEL-GENERATED REFERENCES
# ============================================================

def remove_ai_references(report):
    """Remove model-generated bibliography sections."""

    if not report:
        return ""

    pattern = re.compile(
        r"(?im)^\s{0,3}#{0,3}\s*(references|bibliography)"
        r"\s*:?\s*$"
    )

    match = pattern.search(report)

    if match:
        report = report[:match.start()]

    return report.strip()


# ============================================================
# 2. VALIDATE AND NORMALIZE CITATIONS
# ============================================================

def validate_citations(report, valid_ids):
    """
    Validate source citations.

    Supported formats:
        [S1]
        [S1][S2]
        [S1-S3]
        [S1-3]
        (S1)

    Unknown source IDs are flagged.
    """

    unknown_ids = []

    valid_ids = {
        source_id.upper()
        for source_id in valid_ids
    }

    # Convert parenthetical citations into square brackets.
    report = re.sub(
        r"\((S\d+(?:\s*-\s*(?:S)?\d+)?)\)",
        r"[\1]",
        report,
        flags=re.IGNORECASE
    )

    citation_pattern = re.compile(
        r"\[(S\d+(?:\s*-\s*(?:S)?\d+)?)\]",
        re.IGNORECASE
    )

    def replace_citation(match):

        content = match.group(1).upper().strip()

        range_match = re.fullmatch(
            r"S(\d+)\s*-\s*(?:S)?(\d+)",
            content
        )

        if range_match:

            start = int(range_match.group(1))
            end = int(range_match.group(2))

            # Prevent malformed or excessively large ranges.
            if end < start or end - start > 20:

                unknown_ids.append(content)

                return "[UNVERIFIED CITATION]"

            source_ids = [
                f"S{number}"
                for number in range(start, end + 1)
            ]

        else:

            source_ids = [content]

        normalized = []

        for source_id in source_ids:

            if source_id in valid_ids:

                normalized.append(
                    f"[{source_id}]"
                )

            else:

                unknown_ids.append(source_id)

                normalized.append(
                    "[UNVERIFIED CITATION]"
                )

        return " ".join(normalized)

    report = citation_pattern.sub(
        replace_citation,
        report
    )

    return report, sorted(set(unknown_ids))


# ============================================================
# 3. CLEAN CITATION SPACING
# ============================================================

def clean_citation_spacing(report):
    """
    Correct citation placement and spacing.

    Example:
        diagnosis accuracy . [S1]

    Becomes:
        diagnosis accuracy [S1].
    """

    # Remove spaces before punctuation.
    report = re.sub(
        r"\s+([.,!?;:])",
        r"\1",
        report
    )

    # Move citations before sentence-ending punctuation.
    report = re.sub(
        r"\s+(\[(?:S\d+|UNVERIFIED CITATION)\])([.!?])",
        r" \1\2",
        report
    )

    # Normalize duplicate spaces.
    report = re.sub(
        r" {2,}",
        " ",
        report
    )

    return report.strip()


# ============================================================
# 4. EXTRACT INDIVIDUAL CLAIMS
# ============================================================

def extract_claims(report):
    """
    Extract individual sentences while preserving paragraph
    citations.
    """

    claims = []
    seen = set()

    for line in report.splitlines():

        line = line.strip()

        if not line:
            continue

        # Ignore headings.
        if line.startswith("#"):
            continue

        # Ignore bibliography.
        if re.match(
            r"^(references|bibliography)\s*:?\s*$",
            line,
            re.IGNORECASE
        ):
            break

        # Ignore markdown table rows.
        if line.startswith("|"):
            continue

        # Remove bullet formatting.
        line = re.sub(
            r"^[-*•]\s*",
            "",
            line
        )

        citations = re.findall(
            r"\[(S\d+)\]",
            line
        )

        # Remove citations before sentence splitting.
        clean_line = re.sub(
            r"\[(?:S\d+|UNVERIFIED CITATION|\d+)\]",
            "",
            line
        ).strip()

        sentences = re.split(
            r'(?<=[.!?])\s+(?=[A-Z0-9“"])',
            clean_line
        )

        for sentence in sentences:

            sentence = sentence.strip()

            if len(sentence.split()) < 5:
                continue

            if not re.search(r"[.!?]$", sentence):
                continue

            # Restore original paragraph citations.
            if citations:

                sentence += " " + " ".join(
                    f"[{source_id}]"
                    for source_id in sorted(set(citations))
                )

            if sentence not in seen:

                claims.append(sentence)
                seen.add(sentence)

    return claims


# ============================================================
# 5. NORMALIZE SENTENCES FOR MATCHING
# ============================================================

def normalize_sentence(sentence):
    """Normalize sentences for reliable citation matching."""

    sentence = re.sub(
        r"\[(?:S\d+|UNVERIFIED CITATION|\d+)\]",
        "",
        sentence
    )

    sentence = re.sub(
        r"\s+",
        " ",
        sentence
    )

    return sentence.strip().casefold()


# ============================================================
# 6. VERIFY CLAIMS AGAINST SOURCES
# ============================================================

def verify_against_sources(claim, source_ids, source_texts):
    """
    Verify one claim against multiple retrieved sources.

    SUPPORTED:
        At least one source supports the claim.

    NOT SUPPORTED:
        All checked sources contradict the claim.

    INSUFFICIENT EVIDENCE:
        Evidence is inconclusive or unavailable.
    """

    results = []
    explanations = []

    for source_id in source_ids:

        source_text = source_texts.get(
            source_id,
            ""
        )

        if not source_text:
            continue

        try:

            result = verify_claim(
                claim,
                source_text
            )

            status = result.get(
                "status",
                "INSUFFICIENT EVIDENCE"
            ).upper().strip()

            explanation = result.get(
                "explanation",
                "No explanation provided."
            )

            allowed_statuses = {
                "SUPPORTED",
                "NOT SUPPORTED",
                "INSUFFICIENT EVIDENCE"
            }

            if status not in allowed_statuses:

                status = "INSUFFICIENT EVIDENCE"

            results.append({

                "source_id": source_id,

                "status": status,

                "explanation": explanation

            })

            explanations.append(
                f"{source_id}: {status} - {explanation}"
            )

        except Exception as error:

            results.append({

                "source_id": source_id,

                "status": "INSUFFICIENT EVIDENCE",

                "explanation": str(error)

            })

    statuses = [
        result["status"]
        for result in results
    ]

    if not statuses:

        final_status = "INSUFFICIENT EVIDENCE"

    elif "SUPPORTED" in statuses:

        final_status = "SUPPORTED"

    elif all(
        status == "NOT SUPPORTED"
        for status in statuses
    ):

        final_status = "NOT SUPPORTED"

    else:

        final_status = "INSUFFICIENT EVIDENCE"

    return {

        "status": final_status,

        "explanation": " ".join(explanations),

        "source_results": results

    }


# ============================================================
# 7. AUTOMATIC VERIFIED CITATION ATTRIBUTION
# ============================================================

def attach_verified_citations(report, verification_results):
    """
    Remove model-generated citations and attach citations
    only from sources marked SUPPORTED by the verifier.
    """

    verified_map = {}

    for item in verification_results:

        claim_key = normalize_sentence(
            item["claim"]
        )

        supported_ids = [

            result["source_id"]

            for result in item.get(
                "source_results",
                []
            )

            if result.get("status") == "SUPPORTED"

        ]

        if supported_ids:

            verified_map[claim_key] = sorted(
                set(supported_ids)
            )

    updated_lines = []

    for line in report.splitlines():

        stripped = line.strip()

        if not stripped:

            updated_lines.append(line)
            continue

        # Preserve headings.
        if stripped.startswith("#"):

            updated_lines.append(line)
            continue

        # Preserve table rows without inventing citations.
        if stripped.startswith("|"):

            updated_lines.append(line)
            continue

        # Remove model-generated citations.
        clean_line = re.sub(
            r"\[(?:S\d+|UNVERIFIED CITATION|\d+)\]",
            "",
            stripped
        ).strip()

        # Preserve bullet formatting.
        bullet_match = re.match(
            r"^([-*•]\s*)",
            clean_line
        )

        bullet = (
            bullet_match.group(1)
            if bullet_match
            else ""
        )

        if bullet:

            clean_line = clean_line[
                len(bullet):
            ].strip()

        sentences = re.split(
            r'(?<=[.!?])\s+(?=[A-Z0-9“"])',
            clean_line
        )

        updated_sentences = []

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            source_ids = verified_map.get(
                normalize_sentence(sentence),
                []
            )

            if source_ids:

                citations = " ".join(
                    f"[{source_id}]"
                    for source_id in source_ids
                )

                sentence = (
                    f"{sentence} {citations}"
                )

            updated_sentences.append(sentence)

        if updated_sentences:

            updated_lines.append(
                bullet + " ".join(updated_sentences)
            )

    return "\n".join(updated_lines)


# ============================================================
# 8. MAIN RESEARCH FUNCTION
# ============================================================

def conduct_research(topic, max_results=3):

    print("\nStarting research...")
    print("Topic:", topic)

    if not topic or not topic.strip():

        raise ValueError(
            "Research topic cannot be empty."
        )

    research_material = []
    sources = []
    source_details = []
    source_texts = {}

    verification_results = []
    unverified_claims = []

    # --------------------------------------------------------
    # STEP 1: WEB SEARCH
    # --------------------------------------------------------

    try:

        results = search_web(
            topic,
            max_results
        )

    except Exception as error:

        raise RuntimeError(
            f"Web search unavailable: {error}"
        )

    if not results:

        raise RuntimeError(
            "Web search returned no results."
        )

    total_searched = len(results)

    # --------------------------------------------------------
    # STEP 2: SCRAPE AND CLEAN SOURCES
    # --------------------------------------------------------

    for index, result in enumerate(
        results,
        start=1
    ):

        title = result.get(
            "title",
            "Untitled source"
        )

        url = result.get(
            "url",
            ""
        )

        print(
            f"\n[{index}/{total_searched}] Scraping: {title}"
        )

        source_info = {

            "title": title,

            "url": url,

            "status": "Failed",

            "reason": ""

        }

        try:

            if not url:

                raise ValueError(
                    "Missing source URL."
                )

            content = scrape_website(url)

            if not content:

                raise ValueError(
                    "Unable to extract webpage content."
                )

            cleaned_content = clean_text(content)

            if not cleaned_content:

                raise ValueError(
                    "No usable text after cleaning."
                )

            # Assign source IDs only after successful scraping.
            source_id = f"S{len(sources) + 1}"

            sources.append({

                "id": source_id,

                "title": title,

                "url": url

            })

            source_texts[source_id] = cleaned_content

            research_material.append(
                f"""
SOURCE ID: [{source_id}]
SOURCE TITLE: {title}
SOURCE URL: {url}

SOURCE CONTENT:
{cleaned_content}
"""
            )

            source_info["status"] = (
                "Successfully processed"
            )

            print(
                f"Source [{source_id}] processed successfully."
            )

        except Exception as error:

            source_info["reason"] = str(error)

            print(
                "Source processing failed:",
                error
            )

        source_details.append(source_info)

    total_processed = len(sources)

    total_failed = (
        total_searched - total_processed
    )

    if not research_material:

        raise RuntimeError(
            "No research content could be extracted."
        )

    # --------------------------------------------------------
    # STEP 3: GENERATE AI RESEARCH REPORT
    # --------------------------------------------------------

    combined_text = "\n\n".join(
        research_material
    )

    print("\nGenerating AI research report...")

    report = summarize_text(
        combined_text,
        topic
    )

    if not report or not report.strip():

        raise RuntimeError(
            "AI report generation returned an empty response."
        )

    report = remove_ai_references(report)

    # --------------------------------------------------------
    # STEP 4: VALIDATE GENERATED CITATIONS
    # --------------------------------------------------------

    valid_ids = {
        source["id"]
        for source in sources
    }

    report, unknown_ids = validate_citations(
        report,
        valid_ids
    )

    # --------------------------------------------------------
    # STEP 5: EXTRACT CLAIMS
    # --------------------------------------------------------

    print("\nExtracting individual claims...")

    claims = extract_claims(report)

    claims_checked = 0
    claims_supported = 0
    claims_not_supported = 0
    claims_insufficient = 0
    claims_uncited = 0

    claims_skipped = max(
        0,
        len(claims) - MAX_CLAIMS_TO_VERIFY
    )

    # --------------------------------------------------------
    # STEP 6: VERIFY CLAIMS
    # --------------------------------------------------------

    print("\nStarting evidence verification...")

    for claim in claims[:MAX_CLAIMS_TO_VERIFY]:

        cited_ids = sorted(
            set(
                re.findall(
                    r"\[(S\d+)\]",
                    claim
                )
            )
        )

        if not cited_ids:

            claims_uncited += 1

        # Check all retrieved sources so the system can
        # discover the sources that actually support a claim.
        target_sources = list(
            source_texts.keys()
        )

        clean_claim = re.sub(
            r"\[(?:S\d+|UNVERIFIED CITATION|\d+)\]",
            "",
            claim
        ).strip()

        verification = verify_against_sources(
            clean_claim,
            target_sources,
            source_texts
        )

        status = verification["status"]

        verification_results.append({

            "claim": claim,

            "source_id": ", ".join(target_sources),

            "status": status,

            "explanation": verification["explanation"],

            "cited": bool(cited_ids),

            "source_results": verification["source_results"]

        })

        claims_checked += 1

        if status == "SUPPORTED":

            claims_supported += 1

        elif status == "NOT SUPPORTED":

            claims_not_supported += 1
            unverified_claims.append(claim)

        else:

            claims_insufficient += 1
            unverified_claims.append(claim)

        print(
            f"Claim {claims_checked}: {status}"
        )

    # --------------------------------------------------------
    # STEP 7: ATTACH VERIFIED CITATIONS
    # --------------------------------------------------------

    print("\nAttaching verified citations...")

    report = attach_verified_citations(
        report,
        verification_results
    )

    # --------------------------------------------------------
    # STEP 8: FINAL FORMATTING
    # --------------------------------------------------------

    report = clean_citation_spacing(report)

    # --------------------------------------------------------
    # STEP 9: GENERATE STATISTICS
    # --------------------------------------------------------

    statistics = {

        "total_searched": total_searched,

        "total_processed": total_processed,

        "total_failed": total_failed,

        "claims_checked": claims_checked,

        "claims_supported": claims_supported,

        "claims_not_supported": claims_not_supported,

        "claims_insufficient": claims_insufficient,

        "claims_uncited": claims_uncited,

        "claims_skipped": claims_skipped,

        "unknown_citations": len(unknown_ids)

    }

    # --------------------------------------------------------
    # STEP 10: RETURN FINAL RESULTS
    # --------------------------------------------------------

    print("\nResearch completed successfully.")

    print("\nResearch Statistics:")

    for key, value in statistics.items():

        print(f"{key}: {value}")

    return {

        "topic": topic,

        "report": report,

        "sources": sources,

        "source_details": source_details,

        "statistics": statistics,

        "verification_results": verification_results,

        "unknown_citations": unknown_ids,

        "unverified_claims": unverified_claims

    }
