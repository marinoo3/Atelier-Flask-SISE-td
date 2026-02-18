"""
PDF Loader script. Run this script to load all the pdf files from the folder data/pdf into the database.
Run using: 'python -m scripts.pdf_loader' from the root of the project.
"""

from pathlib import Path

from app.database import db
from app.services.document_services import DocumentService

pdf_folder = Path(__file__).parent.parent / "data" / "pdf"

service = DocumentService()

# initialize db if not existing
db.init_db()

# load all the pdf files from the folder data/pdf into the database
service.create_from_pdf_folder(pdf_folder)
