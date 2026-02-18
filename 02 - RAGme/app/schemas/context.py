from pydantic import BaseModel, computed_field

from app.schemas import Chunk


class Context(BaseModel):
    query: str
    chunks: list[Chunk]

    @computed_field
    @property
    def context(self) -> str:
        ctx = []
        for chunk in self.chunks:
            if chunk.metadata is not None:
                ctx.append(
                    f"> {chunk.metadata.get('title', 'Unknown')} ({chunk.metadata.get('category', 'Unknown')})"
                    f"\n...{chunk.content}..."
                )

        return "\n\n".join(ctx)
