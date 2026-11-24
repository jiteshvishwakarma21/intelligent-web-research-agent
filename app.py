
import os
from pathlib import Path

import streamlit as st

from modules.research_analyzer import conduct_research
from modules.pdf_generator import generate_pdf


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Intelligent Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# 2. APPLICATION SETTINGS
# ==========================================

OUTPUT_DIR = Path("outputs/reports")
PDF_PATH = OUTPUT_DIR / "research_report.pdf"

st.session_state.setdefault("research_result", None)
st.session_state.setdefault("pdf_path", None)


# ==========================================
# 3. CUSTOM CSS
# ==========================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 36px;
        font-weight: 700;
        color: #17365D;
        text-align: center;
    }

    .subtitle {
        font-size: 16px;
        color: #666666;
        text-align: center;
        margin-bottom: 30px;
    }

    .section-title {
        color: #1F4E79;
        font-weight: 600;
    }

    .stButton > button {
        background-color: #1F4E79;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #17365D;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# 4. APPLICATION HEADER
# ==========================================

st.markdown(
    '<div class="main-title">'
    '🔍 Intelligent Research Agent'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered web research and automated report generation'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# 5. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("About the Project")

    st.write(
        """
        This application automatically researches
        a topic using web search, extracts information
        from websites, cleans the content, generates
        an AI-powered research report and evaluates
        cited claims against the extracted sources.
        """
    )

    st.subheader("Technology Stack")

    st.markdown(
        """
        - Python
        - Streamlit
        - Ollama
        - Llama 3.2
        - BeautifulSoup
        - DuckDuckGo Search
        - ReportLab
        """
    )

    st.divider()

    st.subheader("How It Works")

    st.markdown(
        """
        1. Enter a research topic.
        2. Search relevant websites.
        3. Extract webpage content.
        4. Clean the extracted text.
        5. Generate an AI research report.
        6. Validate source citations.
        7. Evaluate cited claims.
        8. Download the PDF report.
        """
    )

    st.divider()

    st.caption(
        "Intelligent Web Research and Summarization Agent"
    )


# ==========================================
# 6. RESEARCH INPUT
# ==========================================

st.subheader("Start Your Research")

st.write(
    "Enter a topic below to search the web "
    "and generate an AI-powered research report."
)

with st.form("research_form"):

    topic = st.text_input(
        "Research Topic",
        placeholder=(
            "Example: Impact of Artificial Intelligence on Healthcare"
        )
    )

    max_results = st.slider(
        "Number of Web Sources",
        min_value=1,
        max_value=5,
        value=3
    )

    start_research = st.form_submit_button(
        "🚀 Start Research",
        use_container_width=True
    )


# ==========================================
# 7. START RESEARCH
# ==========================================

if start_research:

    if not topic.strip():

        st.warning("Please enter a research topic.")

    else:

        st.session_state["research_result"] = None
        st.session_state["pdf_path"] = None

        progress = st.empty()

        try:

            with st.spinner(
                "Searching, analyzing and verifying research..."
            ):

                progress.info(
                    "Step 1: Searching websites and extracting content..."
                )

                result = conduct_research(
                    topic.strip(),
                    max_results=max_results
                )

                progress.info(
                    "Step 2: Generating the PDF report..."
                )

                OUTPUT_DIR.mkdir(
                    parents=True,
                    exist_ok=True
                )

                pdf_path = generate_pdf(
                    result,
                    str(PDF_PATH)
                )

                if not pdf_path or not Path(pdf_path).is_file():
                    raise RuntimeError(
                        "PDF generation failed. Check pdf_generator.py."
                    )

                st.session_state["research_result"] = result
                st.session_state["pdf_path"] = str(pdf_path)

            progress.empty()

            st.success(
                "Research report generated successfully!"
            )

        except Exception as error:

            progress.empty()

            st.error(f"An error occurred: {error}")
            st.exception(error)


# ==========================================
# 8. DISPLAY RESEARCH RESULTS
# ==========================================

result = st.session_state.get("research_result")

if result:

    st.divider()

    # ======================================
    # 9. RESEARCH REPORT
    # ======================================

    st.markdown(
        '<h2 class="section-title">📄 Research Report</h2>',
        unsafe_allow_html=True
    )

    st.subheader(
        result.get("topic", "Research Report")
    )

    st.markdown(
        result.get("report", "No report was generated.")
    )

    # ======================================
    # 10. RESEARCH STATISTICS
    # ======================================

    st.divider()

    st.markdown(
        '<h2 class="section-title">📊 Research Statistics</h2>',
        unsafe_allow_html=True
    )

    statistics = result.get("statistics", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Sources Searched",
            statistics.get("total_searched", 0)
        )

    with col2:
        st.metric(
            "Successfully Processed",
            statistics.get("total_processed", 0)
        )

    with col3:
        st.metric(
            "Failed Sources",
            statistics.get("total_failed", 0)
        )

    # ======================================
    # 11. EVIDENCE VERIFICATION STATISTICS
    # ======================================

    st.divider()

    st.markdown(
        '<h2 class="section-title">🛡️ Evidence Verification</h2>',
        unsafe_allow_html=True
    )

    verification_col1, verification_col2, verification_col3 = (
        st.columns(3)
    )

    with verification_col1:
        st.metric(
            "Claims Checked",
            statistics.get("claims_checked", 0)
        )

    with verification_col2:
        st.metric(
            "Supported Claims",
            statistics.get("claims_supported", 0)
        )

    with verification_col3:
        st.metric(
            "Not Supported",
            statistics.get("claims_not_supported", 0)
        )

    st.metric(
        "Insufficient Evidence",
        statistics.get("claims_insufficient", 0)
    )

    st.caption(
        "Evidence results are AI-assisted assessments, "
        "not independent proof of factual accuracy."
    )

    # ======================================
    # 12. DETAILED VERIFICATION RESULTS
    # ======================================

    verification_results = result.get(
        "verification_results", []
    )

    with st.expander("🔍 View Detailed Evidence Verification"):

        if verification_results:

            for index, item in enumerate(
                verification_results,
                start=1
            ):

                st.markdown(
                    f"**Claim {index}:** {item.get('claim', '')}"
                )

                st.caption(
                    f"Source ID: {item.get('source_id', 'Unknown')}"
                )

                status = item.get("status", "")

                if status == "SUPPORTED":

                    st.success("SUPPORTED")

                elif status == "NOT SUPPORTED":

                    st.error("NOT SUPPORTED")

                else:

                    st.warning("INSUFFICIENT EVIDENCE")

                st.write(
                    item.get("explanation", "")
                )

                st.divider()

        else:

            st.info(
                "No cited claims were available for verification."
            )

    # ======================================
    # 13. INDIVIDUAL SOURCE STATUS
    # ======================================

    with st.expander("🔎 View Individual Source Status"):

        source_details = result.get("source_details", [])

        if source_details:

            for index, source in enumerate(
                source_details,
                start=1
            ):

                st.markdown(
                    f"**{index}. {source.get('title', 'Untitled Source')}**"
                )

                source_url = source.get("url", "")

                if source_url:
                    st.markdown(
                        f"[Open Source]({source_url})"
                    )

                if source.get("status") == "Successfully processed":

                    st.success("Successfully processed")

                else:

                    st.error(
                        "Failed: "
                        + source.get("reason", "Unknown error")
                    )

                st.divider()

        else:

            st.info(
                "Source status information is unavailable."
            )

    # ======================================
    # 14. RESEARCH SOURCES
    # ======================================

    st.divider()

    st.markdown(
        '<h2 class="section-title">🌐 Research Sources</h2>',
        unsafe_allow_html=True
    )

    sources = result.get("sources", [])

    if sources:

        for source in sources:

            source_id = source.get("id", "")
            title = source.get("title", "Untitled Source")
            url = source.get("url", "")

            st.markdown(
                f"**[{source_id}] {title}**"
            )

            if url:
                st.markdown(
                    f"[Visit Website]({url})"
                )

    else:

        st.info("No research sources were found.")

    # ======================================
    # 15. PDF DOWNLOAD
    # ======================================

    st.divider()

    st.markdown(
        '<h2 class="section-title">📥 Download Report</h2>',
        unsafe_allow_html=True
    )

    pdf_path = st.session_state.get("pdf_path")

    if pdf_path and os.path.isfile(pdf_path):

        with open(pdf_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()

        st.download_button(
            label="📄 Download Research Report (PDF)",
            data=pdf_data,
            file_name="Research_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.success("Your PDF report is ready.")

    else:

        st.warning("PDF report is not available.")


# ==========================================
# 16. FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#888888; font-size:13px;">
        Intelligent Web Research and Summarization Agent
        <br>
        Powered by Python, Streamlit and Ollama
    </div>
    """,
    unsafe_allow_html=True
)
