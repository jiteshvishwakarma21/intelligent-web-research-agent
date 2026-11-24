from modules.research_analyzer import conduct_research
from modules.pdf_generator import generate_pdf


topic = "Impact of Artificial Intelligence on Healthcare"

try:

    print("\nStarting research for PDF generation...")

    result = conduct_research(topic, max_results=3)

    print("\nGenerating PDF report...")

    pdf_path = generate_pdf(
        result,
        "outputs/reports/AI_Healthcare_Research_Report.pdf"
    )

    print("\nPDF GENERATED SUCCESSFULLY!")
    print("File location:", pdf_path)

except Exception as error:

    print("\nERROR:", error)