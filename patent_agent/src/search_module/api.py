from dataclasses import dataclass
from typing import Optional, List, Dict # Added Dict

@dataclass
class PatentSearchResult:
    patent_id: str
    title: str
    abstract: str
    publication_date: str  # Consider using datetime.date
    assignee: str
    relevance_score: float

def search_patents(query: str, filters: Optional[Dict] = None) -> List[PatentSearchResult]: # Changed Optional[dict] to Optional[Dict] for consistency with prompt
    """
    Searches for patents based on a query and optional filters.

    Args:
        query: The search query string.
        filters: Optional dictionary of filters (e.g., date range, assignee).

    Returns:
        A list of PatentSearchResult objects.
    """
    print(f"Searching for patents with query: '{query}' and filters: {filters}") # For debugging
    # Mock data
    mock_results = [
        PatentSearchResult(
            patent_id="US20230000001A1",
            title="Novel Quantum Computing Method",
            abstract="A method for improving qubit stability in quantum computers.",
            publication_date="2023-01-01",
            assignee="Tech Innovations Inc.",
            relevance_score=0.95
        ),
        PatentSearchResult(
            patent_id="US20230000002A1",
            title="AI-Powered Drug Discovery Platform",
            abstract="Utilizing machine learning to accelerate the identification of potential drug candidates.",
            publication_date="2023-01-15",
            assignee="Pharma Solutions LLC",
            relevance_score=0.92
        ),
        PatentSearchResult(
            patent_id="CN100000000A",
            title="Method for preparing a therapeutic composition",
            abstract="The invention discloses a method for preparing a therapeutic composition, which comprises the following steps...",
            publication_date="2022-05-10",
            assignee="BioFuture Ltd.",
            relevance_score=0.88
        )
    ]
    # Simulate filtering if a query is present
    if query:
        # Simple keyword search in title or abstract
        query_lower = query.lower()
        filtered_results = [
            result for result in mock_results
            if query_lower in result.title.lower() or query_lower in result.abstract.lower()
        ]
        return filtered_results
    return mock_results
