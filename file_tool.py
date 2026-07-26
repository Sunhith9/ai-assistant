"""
file_tool.py
File-reading agent - reads PDFs, Excel/CSV files, and plain text files
from your computer. Fully free, fully local, no API needed.
"""

import os


# ---------- PDF READER AGENT ----------
def read_pdf(file_path: str, max_chars: int = 3000) -> str:
    """Extract text from a PDF file given its full path."""
    try:
        from pypdf import PdfReader

        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            if len(text) >= max_chars:
                break

        if not text.strip():
            return "Could not extract any text (file may be scanned/image-based)."

        return text[:max_chars]
    except Exception as e:
        return f"PDF reader agent error: {e}"


# ---------- EXCEL / CSV READER AGENT ----------
def read_spreadsheet(file_path: str, max_rows: int = 20) -> str:
    """Read an Excel (.xlsx) or CSV file and return a preview of its contents."""
    try:
        import pandas as pd

        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        preview = df.head(max_rows).to_string(index=False)
        return f"Columns: {list(df.columns)}\nTotal rows: {len(df)}\n\nPreview:\n{preview}"
    except Exception as e:
        return f"Spreadsheet reader agent error: {e}"


# ---------- TEXT FILE READER AGENT ----------
def read_text_file(file_path: str, max_chars: int = 3000) -> str:
    """Read a plain text file (.txt, .md, .json, .log, etc)."""
    try:
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)

        return content if content.strip() else "File is empty."
    except Exception as e:
        return f"Text file reader agent error: {e}"


# ---------- WRITE TO SPREADSHEET AGENT (for data entry tasks) ----------
def append_to_spreadsheet(file_path: str, row_data: list) -> str:
    """Append a row of data to an existing Excel file, or create it if it doesn't exist.
    row_data is a list of values, e.g. ['John', 'john@email.com', '2026-06-20']
    """
    try:
        import pandas as pd

        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            new_row = pd.DataFrame([row_data], columns=df.columns[:len(row_data)])
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = pd.DataFrame([row_data])

        df.to_excel(file_path, index=False)
        return f"Row added to {file_path}: {row_data}"
    except Exception as e:
        return f"Spreadsheet writer agent error: {e}"