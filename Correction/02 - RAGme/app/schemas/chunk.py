from typing import Optional

from pydantic import BaseModel, ConfigDict, field_serializer


class Chunk(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    chroma_id: str
    content: str

    distance: Optional[float] = None
    score: Optional[float] = None

    metadata: Optional[dict] = None

    @field_serializer("distance")
    def serialize_distance(self, d: float, _info):
        # Round distance to 3 digits for json export
        return round(d, 3)

    @field_serializer("score")
    def serialize_score(self, s: float, _info):
        # Round distance to 2 digits for json export
        return round(s, 2)
