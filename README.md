# AI Finance Buddy 💰

A modern Streamlit web app for financial data analysis with AI-powered insights.

## Features

- **Multi-format Data Input**: Upload Excel/CSV files, PDF documents, or paste plain text
- **Smart Data Parsing**: Automatically extracts financial data using regex and pdfplumber
- **Interactive Dashboard**: Pie charts, bar charts, and transaction tables using Plotly
- **AI Insights**: LLaMA-3 powered financial analysis via Groq API
- **Data Export**: Download normalized data as Excel or CSV
- **Premium UI**: Modern gradient design with responsive layout

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add your Groq API key to `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your-actual-groq-api-key"
```

3. Run the app:
```bash
streamlit run app.py
```

## Usage

1. **Upload Data**: Use the sidebar to upload files or paste text in format:
   ```
   Groceries 2000
   Rent 8000
   Transport 1500
   ```

2. **View Dashboard**: Analyze spending with interactive charts and metrics

3. **Get AI Insights**: Click "Get AI Analysis" for personalized financial recommendations

4. **Export Data**: Download your normalized data in Excel or CSV format

## Deployment

The app is ready for Streamlit Cloud deployment. Just push to GitHub and connect your repository.

## Data Format

All inputs are normalized to:
```json
[
  {"category": "Food", "amount": 2000, "date": "2025-01-15"},
  {"category": "Rent", "amount": 8000, "date": "2025-01-01"}
]
```