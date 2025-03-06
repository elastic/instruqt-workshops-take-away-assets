from pydantic import BaseModel


class SearchQuery(BaseModel):
    query: str
    context_type: str  # This matches the payload from the frontend correctly now
