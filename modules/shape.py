from datetime import date
from dataclasses import dataclass, field
from typing import List

@dataclass
class Date:
    """
    Custom Date wrapper for handling archived newspaper dates.
    
    Provides utility methods for sorting and conversion to native 
    Python datetime objects.
    """
    day: int
    month: int
    year: int

    def __str__(self):
        return f"{self.year}/{self.month:02d}/{self.day:02d}"

    def __lt__(self, other):
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)

    def to_python_datetime(self) -> date:
        return date(self.year, self.month, self.day)

@dataclass
class Source:
    """
    Represents the metadata and content of a single archived document.
    """
    summary: str
    extract: str
    filename: str
    keywords: List[str]
    image_path: str
    topics: List[str]
    publication: str
    publication_date: Date
    page: int
    tags: List[str]
    # populated later via llm call during enrichment.
    # TODO (ogieva): extend search to return relevant extract
    relevant_extract: str = ""

    def __str__(self):
        return f"Source({self.filename}): {self.summary[:100]}..."

@dataclass
class Entry:
    """
    A wrapper for a Source that includes search metadata 
    like database IDs and semantic relevance scores.
    """
    id: str
    source: Source
    semantic_relevance: float

    def __str__(self):
        return f"Entry(id={self.id}, relevance={self.semantic_relevance:.4f})"
    
    def to_dict(self) -> dict:
        """Serialize to the API output contract."""
        return {
            "id":                 self.id,
            "semantic_relevance": round(self.semantic_relevance, 4),
            "publication":        self.source.publication,
            "publication_date":   str(self.source.publication_date),
            "page":               self.source.page,
            "summary":            self.source.summary,
            "filename":           self.source.filename,
            "image_path":         self.source.image_path,
        }

@dataclass
class EnrichedCluster:
    """
    The final output structure. A group of Entries synthesized into 
    a single narrative theme.
    """
    index: int
    label: str           # The date-range label (e.g., "1990 to 1991")
    title: str
    summary: str       
    entries: List[Entry] # The list of original sources in this cluster
    start_date: Date
    end_date: Date
    cover_story: Entry   # The entry with the best relationship to the generated cluster description.

    def to_dict(self) -> dict:
        """Serialize to the cluster_enriched SSE event payload."""
        return {
            "index":       self.index,
            "label":       self.label,
            "title":       self.title,
            "summary":     self.summary,
            "entry_count": len(self.entries),
            "entries":     [e.to_dict() for e in self.entries],
            "cover_story": self.cover_story.to_dict()
        }