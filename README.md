
# Intelligent Web Research and Summarization Agent

An AI-powered research application that searches the web, extracts webpage content, summarizes information, checks claims against sources, and generates PDF research reports.

## Features
- Web search using DuckDuckGo
- Webpage scraping and text cleaning
- AI summarization using Ollama
- Research analysis and evidence checking
- Source references and citations
- PDF report generation
- Streamlit user interface

## Technology Stack
- Python
- Streamlit
- Ollama (llama3.2:3b)
- BeautifulSoup
- DuckDuckGo Search
- ReportLab

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Download the Ollama model:

```bash
ollama pull llama3.2:3b
```

## Run the Application

```bash
streamlit run app.py
```

## Run Tests

```bash
python -m unittest discover
```

## Limitations
- Some websites may block automated access.
- Evidence verification is AI-assisted, not definitive proof.
- AI-generated summaries may contain errors.

## Disclaimer
This application is intended for educational and research assistance. Always verify important information using original sources.
