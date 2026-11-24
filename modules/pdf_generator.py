
import os
import re
import html
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable
)


def generate_pdf(
    result,
    output_path="outputs/reports/research_report.pdf"
):
    """
    Generate a professionally formatted research report PDF.

    Parameters:
        result: Research result dictionary.
        output_path: Destination PDF path.

    Returns:
        Generated PDF file path.
    """

    # --------------------------------------------------
    # 1. CREATE OUTPUT DIRECTORY
    # --------------------------------------------------

    output_directory = os.path.dirname(output_path)

    if output_directory:
        os.makedirs(output_directory, exist_ok=True)

    # --------------------------------------------------
    # 2. DOCUMENT SETTINGS
    # --------------------------------------------------

    navy = colors.HexColor("#17365D")
    blue = colors.HexColor("#1F4E79")
    grey = colors.HexColor("#666666")
    dark = colors.HexColor("#222222")

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Intelligent Research Report",
        author="Intelligent Web Research and Summarization Agent"
    )

    styles = getSampleStyleSheet()

    # --------------------------------------------------
    # 3. PDF STYLES
    # --------------------------------------------------

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=27,
        alignment=TA_CENTER,
        textColor=navy,
        spaceAfter=16
    )

    topic_style = ParagraphStyle(
        "TopicStyle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=21,
        textColor=blue,
        spaceAfter=9
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=17,
        textColor=blue,
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=dark,
        spaceAfter=7,
        splitLongWords=1
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=body_style,
        leftIndent=16,
        firstLineIndent=-9,
        spaceAfter=5
    )

    metadata_style = ParagraphStyle(
        "Metadata",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=grey,
        spaceAfter=12
    )

    source_style = ParagraphStyle(
        "SourceStyle",
        parent=body_style,
        fontSize=8.5,
        leading=12,
        spaceAfter=8,
        wordWrap="CJK"
    )

    # --------------------------------------------------
    # 4. GET RESEARCH DATA
    # --------------------------------------------------

    topic = str(
        result.get("topic", "Research Report")
    )

    report = str(
        result.get("report", "")
    )

    sources = result.get("sources", [])

    story = []

    # --------------------------------------------------
    # 5. REPORT HEADER
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INTELLIGENT RESEARCH REPORT",
            title_style
        )
    )

    story.append(
        Paragraph(
            html.escape(topic),
            topic_style
        )
    )

    generated_date = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    story.append(
        Paragraph(
            f"Generated on: {generated_date}",
            metadata_style
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=blue,
            spaceBefore=4,
            spaceAfter=15
        )
    )

    # --------------------------------------------------
    # 6. REPORT CONTENT
    # --------------------------------------------------

    section_names = [
        "Introduction",
        "Main Findings",
        "Important Insights",
        "Benefits and Opportunities",
        "Challenges and Limitations",
        "Conclusion"
    ]

    section_pattern = "|".join(
        re.escape(name)
        for name in section_names
    )

    for original_line in report.splitlines():

        line = original_line.strip()

        if not line:
            continue

        # Stop if the AI generated its own references.
        if re.match(
            r"^(#{1,6}\s*)?(references|bibliography|research sources)\s*:?\s*$",
            line,
            re.IGNORECASE
        ):
            break

        # Remove Markdown heading markers.
        line = re.sub(
            r"^#{1,6}\s*",
            "",
            line
        )

        # Remove Markdown bold and italic markers.
        line = re.sub(
            r"\*\*(.*?)\*\*",
            r"\1",
            line
        )

        line = re.sub(
            r"(?<!\*)\*([^*]+)\*(?!\*)",
            r"\1",
            line
        )

        # Remove repetitive model-generated filler.
        line = re.sub(
            r"\s*However,\s*the report does not provide "
            r"further details on this finding\.?",
            "",
            line,
            flags=re.IGNORECASE
        ).strip()

        if not line:
            continue

        # Detect section headings, including headings
        # followed by text on the same line.
        heading_match = re.match(
            rf"^(?:\d+\.\s*)?({section_pattern})"
            rf"\s*:?\s*(.*)$",
            line,
            re.IGNORECASE
        )

        if heading_match:

            heading_text = heading_match.group(1).title()
            remaining_text = heading_match.group(2).strip()

            story.append(
                Paragraph(
                    html.escape(heading_text),
                    heading_style
                )
            )

            if not remaining_text:
                continue

            line = remaining_text

        # Identify bullet points.
        if line.startswith(("- ", "* ", "• ")):

            bullet_text = html.escape(
                line[2:].strip()
            )

            story.append(
                Paragraph(
                    f"&bull; {bullet_text}",
                    bullet_style
                )
            )

        else:

            paragraph = html.escape(line)

            story.append(
                Paragraph(
                    paragraph,
                    body_style
                )
            )

    # --------------------------------------------------
    # 7. RESEARCH SOURCES
    # --------------------------------------------------

    if sources:

        story.append(
            Spacer(1, 12)
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.7,
                color=colors.HexColor("#CCCCCC"),
                spaceBefore=4,
                spaceAfter=10
            )
        )

        story.append(
            Paragraph(
                "RESEARCH SOURCES",
                heading_style
            )
        )

        for index, source in enumerate(
            sources,
            start=1
        ):

            # Use the same source ID as the research report.
            source_id = str(
                source.get("id", f"S{index}")
            ).upper()

            source_title = html.escape(
                str(
                    source.get(
                        "title",
                        "Untitled Source"
                    )
                )
            )

            source_url = str(
                source.get("url", "")
            ).strip()

            source_content = (
                f"<b>[{html.escape(source_id)}] "
                f"{source_title}</b>"
            )

            if source_url.startswith(
                ("https://", "http://")
            ):

                safe_url = html.escape(
                    source_url,
                    quote=True
                )

                source_content += (
                    f'<br/><link href="{safe_url}" '
                    f'color="#1155CC">'
                    f'{html.escape(source_url)}'
                    f'</link>'
                )

            story.append(
                Paragraph(
                    source_content,
                    source_style
                )
            )

    else:

        story.append(
            Spacer(1, 10)
        )

        story.append(
            Paragraph(
                "No research sources were available.",
                body_style
            )
        )

    # --------------------------------------------------
    # 8. PAGE NUMBER FOOTER
    # --------------------------------------------------

    def add_page_number(canvas, doc):

        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.setFillColor(grey)

        canvas.drawCentredString(
            A4[0] / 2,
            0.35 * inch,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    # --------------------------------------------------
    # 9. BUILD PDF
    # --------------------------------------------------

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return output_path
