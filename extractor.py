import csv
from pathlib import Path

import pandas as pd
import pdfplumber
from docx import Document


MAX_TEXT_LENGTH = 15000


class TextExtractor:

    def extract(self, file_path: str) -> str:

        path = Path(file_path)

        extension = path.suffix.lower()

        try:

            if extension == ".txt":
                text = self._extract_txt(path)

            elif extension == ".pdf":
                text = self._extract_pdf(path)

            elif extension == ".docx":
                text = self._extract_docx(path)

            elif extension == ".xlsx":
                text = self._extract_xlsx(path)

            elif extension == ".csv":
                text = self._extract_csv(path)

            else:
                text = ""

            return self._normalize(text)

        except Exception as e:

            print(f"[ERROR] Extraction failed: {path}")
            print(e)

            return ""

    def _extract_txt(self, path: Path) -> str:

        encodings = [
            "utf-8",
            "cp1251",
            "latin-1"
        ]

        for encoding in encodings:

            try:
                with open(path, "r", encoding=encoding) as f:
                    return f.read()

            except Exception:
                pass

        return ""

    def _extract_pdf(self, path: Path) -> str:

        text = []

        with pdfplumber.open(path) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text.append(page_text)

        return "\n".join(text)

    def _extract_docx(self, path: Path) -> str:

        document = Document(path)

        paragraphs = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():
                paragraphs.append(paragraph.text)

        return "\n".join(paragraphs)

    def _extract_xlsx(self, path: Path) -> str:

        result = []

        excel_file = pd.ExcelFile(path)

        for sheet_name in excel_file.sheet_names:

            df = pd.read_excel(
                path,
                sheet_name=sheet_name,
                dtype=str
            )

            result.append(f"=== SHEET: {sheet_name} ===")

            result.append(
                df.fillna("").to_string(index=False)
            )

        return "\n".join(result)

    def _extract_csv(self, path: Path) -> str:

        rows = []

        encodings = [
            "utf-8",
            "cp1251",
            "latin-1"
        ]

        for encoding in encodings:

            try:

                with open(
                    path,
                    "r",
                    encoding=encoding,
                    newline=""
                ) as file:

                    reader = csv.reader(file)

                    for row in reader:
                        rows.append(" | ".join(row))

                return "\n".join(rows)

            except Exception:
                pass

        return ""

    def _normalize(self, text: str) -> str:

        text = text.replace("\x00", "")

        text = " ".join(text.split())

        return text[:MAX_TEXT_LENGTH]


if __name__ == "__main__":

    extractor = TextExtractor()

    sample_file = "uploads/test.docx"

    text = extractor.extract(sample_file)

    print("=" * 80)
    print(text[:3000])
    print("=" * 80)