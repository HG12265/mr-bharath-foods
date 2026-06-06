from pydantic import BaseModel


class AutocompleteResponse(BaseModel):
    suggestions: list[str]

class TrendingSearch(BaseModel):
    query: str
    count: int

class TrendingResponse(BaseModel):
    trending: list[TrendingSearch]
