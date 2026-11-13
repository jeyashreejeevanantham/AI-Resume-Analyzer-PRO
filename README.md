# AI Resume Analyzer PRO

An AI-powered Resume Analyzer built using Python and Streamlit. The application allows users to upload PDF resumes and analyze their content using Natural Language Processing and semantic similarity techniques.

## Features

- **PDF Resume Upload:** Upload resumes in PDF format.
- **Resume Text Extraction:** Extract text from uploaded PDF documents.
- **AI-Powered Analysis:** Use Sentence Transformers for semantic text analysis.
- **Interactive Interface:** Simple and user-friendly Streamlit interface.
- **Python-Based Processing:** Resume processing and analysis using Python.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming |
| Streamlit | Web application interface |
| Sentence Transformers | Semantic text analysis |
| PyTorch | Deep learning framework |
| PyPDF2 | PDF text extraction |
| Pandas | Data processing |
| Matplotlib | Data visualization |

## Project Structure

```text
Resume_Analyzer_PRO/
│
├── app.py
├── resume_utils.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/jeyashreejeevanantham/AI-Resume-Analyzer-PRO.git
```

### 2. Navigate to the project folder

```bash
cd AI-Resume-Analyzer-PRO
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser at:

`http://localhost:8501`

## Requirements

- Python 3.9 or compatible version
- pip package manager
- Internet connection for downloading dependencies and AI models

## Developer

**Jeyashree J**

GitHub: [jeyashreejeevanantham](https://github.com/jeyashreejeevanantham)

## License

This project is available for educational and portfolio purposes.