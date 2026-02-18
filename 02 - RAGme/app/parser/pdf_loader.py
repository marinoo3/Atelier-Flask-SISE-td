from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


class PDFHandler:
    """A class to handle pdf files, including reading pdf from a file or from a bytes stream."""

    def read_pdf(self, file_path: Path) -> str:
        """Read pdf from a file

        Args:
            file_path (Path): The path of the file.

        Returns:
            str: The content of the pdf as a string.
        """
        with open(file_path, "rb") as f:
            pdf_stream = BytesIO(f.read())

        reader = PdfReader(pdf_stream)

        text = "\n".join(page.extract_text() for page in reader.pages)

        return text

    def read_pdf_from_bytes(self, pdf_bytes: bytes) -> str:
        """Read pdf from a bytes stream send by the UI.

        Args:
            pdf_bytes (bytes): the bytes stream.

        Returns:
            str: The content of the pdf as a string.
        """
        pdf_stream = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)

        text = "\n".join(page.extract_text() for page in reader.pages)

        return text
