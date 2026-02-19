from io import BytesIO
from typing import Optional

from pydantic import BaseModel, computed_field


class DocumentSchema(BaseModel):
    # TODO: Configurer le model_config pour la génération via SQLAlchemy

    # TODO: Créer les champs correspondants au modèle de données Document

    # -------------------------------------------- Computed fields for ChromaDB integration --------------------------------------------
    @computed_field
    @property
    def chroma_metadata(self) -> dict:
        """Generate ChromaDB metadata from the Document instance."""
        metadata = {
            "document_id": self.id,
            "title": self.title,
            "category": self.category,
            "url": self.url,
        }
        return {k: v for k, v in metadata.items() if v is not None}

    @computed_field
    @property
    def chroma_id(self) -> str:
        """Generate a unique ChromaDB ID for the document."""
        return f"document_{self.id}"

    def convert_blob(self) -> BytesIO:
        """Convert binary data to a blob"""
        return BytesIO(self.binary)
