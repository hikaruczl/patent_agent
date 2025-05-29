from dataclasses import dataclass, field # Ensure dataclass is imported
from typing import List, Dict, Set # Ensure List, Dict, Set are imported

@dataclass
class PatentComparisonResult:
    patent_a_id: str
    patent_b_id: str
    similarities: List[str] = field(default_factory=list)
    differences: List[str] = field(default_factory=list)
    overall_similarity_score: float = 0.0

MOCK_PATENT_DATABASE: Dict[str, Dict] = {
    "US20230000001A1": {"patent_id": "US20230000001A1", "title": "Novel Quantum Computing Method", "abstract": "A method for improving qubit stability in quantum computers. This method involves advanced cooling.", "publication_date": "2023-01-01", "assignee": "Tech Innovations Inc.", "claims": ["A method of cooling qubits.", "A system for quantum computation."]},
    "US20230000002A1": {"patent_id": "US20230000002A1", "title": "AI-Powered Drug Discovery Platform", "abstract": "Utilizing machine learning to accelerate the identification of potential drug candidates. This platform uses AI.", "publication_date": "2023-01-15", "assignee": "Pharma Solutions LLC", "claims": ["A platform for drug discovery.", "A method using AI for identification."]},
    "CN100000000A": {"patent_id": "CN100000000A", "title": "Method for preparing a therapeutic composition", "abstract": "The invention discloses a method for preparing a therapeutic composition, which comprises advanced mixing steps.", "publication_date": "2022-05-10", "assignee": "BioFuture Ltd.", "claims": ["A method of preparing compositions.", "A therapeutic composition."]},
    "US20220000001A1": {"patent_id": "US20220000001A1", "title": "Advanced Cooling System for Processors", "abstract": "An advanced cooling mechanism for high-performance computer processors. This method is novel.", "publication_date": "2022-03-12", "assignee": "Tech Innovations Inc.", "claims": ["A cooling system.", "A method for reducing processor temperature."]}
}

STOP_WORDS: Set[str] = {"a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "should", "can", "could", "may", "might", "must", "in", "on", "at", "by", "for", "with", "about", "to", "from", "of", "and", "or", "but", "this", "that", "it", "which", "method", "system", "invention", "discloses", "comprises", "platform", "uses", "for", "in", "to", "of"} # Added more common words

def _get_words_from_text(text: str) -> Set[str]:
    # Simple tokenizer: lowercase, split by space, remove punctuation
    words = set(text.lower().replace(",", "").replace(".", "").replace(";", "").replace(":", "").split())
    return words - STOP_WORDS

def compare_patents(patent_id_a: str, patent_id_b: str) -> PatentComparisonResult:
    patent_a_data = MOCK_PATENT_DATABASE.get(patent_id_a)
    patent_b_data = MOCK_PATENT_DATABASE.get(patent_id_b)

    similarities: List[str] = []
    differences: List[str] = []
    overall_similarity_score: float = 0.0

    if not patent_a_data:
        similarities.append(f"Patent ID {patent_id_a} not found in mock database.")
    if not patent_b_data:
        similarities.append(f"Patent ID {patent_id_b} not found in mock database.")
    
    if not patent_a_data or not patent_b_data:
        return PatentComparisonResult(
            patent_a_id=patent_id_a,
            patent_b_id=patent_id_b,
            similarities=similarities,
            differences=["Data unavailable for full comparison due to missing patent(s)."],
            overall_similarity_score=0.0
        )

    words_a = _get_words_from_text(patent_a_data["abstract"])
    words_b = _get_words_from_text(patent_b_data["abstract"])

    common_words = list(words_a.intersection(words_b))
    
    if common_words:
        similarities.append(f"Common abstract keywords: {', '.join(sorted(list(common_words)))}") # sorted for consistency
    else:
        similarities.append("No significant common keywords found in abstracts.")

    # Compare assignees
    assignee_bonus = 0.0
    if patent_a_data["assignee"] == patent_b_data["assignee"]:
        similarities.append(f"Same assignee: {patent_a_data['assignee']}")
        assignee_bonus = 0.2 # Assignee match bonus
    else:
        differences.append(f"Different assignees: Patent A - '{patent_a_data['assignee']}', Patent B - '{patent_b_data['assignee']}'")
        
    # Jaccard index for abstracts
    union_words = words_a.union(words_b)
    if not union_words: 
        jaccard_score = 0.0
    else:
        # len(common_words) is len(words_a.intersection(words_b))
        jaccard_score = len(words_a.intersection(words_b)) / len(union_words) 
    
    # Combine scores (heuristic)
    # Jaccard score (0-1) contributes up to 0.8 to the final score. Assignee bonus (0 or 0.2) adds to this.
    overall_similarity_score = min(1.0, (jaccard_score * 0.8) + assignee_bonus)

    # Simple difference reporting based on unique words
    unique_to_a = sorted(list(words_a - words_b)) # sorted for consistency
    unique_to_b = sorted(list(words_b - words_a)) # sorted for consistency

    if unique_to_a:
        differences.append(f"Keywords unique to Patent A's abstract (up to 5): {', '.join(unique_to_a[:5])}{'...' if len(unique_to_a) > 5 else ''}")
    if unique_to_b:
        differences.append(f"Keywords unique to Patent B's abstract (up to 5): {', '.join(unique_to_b[:5])}{'...' if len(unique_to_b) > 5 else ''}")
    
    if not unique_to_a and not unique_to_b and common_words: # Abstracts are identical based on keywords
        differences.append("Abstracts are very similar or identical based on filtered keywords.")
    elif not differences: # If no specific differences were noted yet
        differences.append("Differences noted in abstract content beyond simple keywords or assignees.")


    return PatentComparisonResult(
        patent_a_id=patent_id_a,
        patent_b_id=patent_id_b,
        similarities=similarities,
        differences=differences,
        overall_similarity_score=round(overall_similarity_score, 2) # Round to 2 decimal places
    )

def compare_patent_with_text(patent_id: str, text_to_compare: str) -> PatentComparisonResult:
    patent_a_data = MOCK_PATENT_DATABASE.get(patent_id)

    if not patent_a_data:
         return PatentComparisonResult(
            patent_a_id=patent_id,
            patent_b_id="CustomText", # Special identifier for the text being compared
            similarities=[f"Patent ID {patent_id} not found in mock database."],
            differences=["Data unavailable for comparison due to missing patent."],
            overall_similarity_score=0.0
        )

    words_a = _get_words_from_text(patent_a_data["abstract"])
    words_text = _get_words_from_text(text_to_compare)
    
    common_words = list(words_a.intersection(words_text))
    similarities = []
    if common_words:
        similarities.append(f"Common keywords with text: {', '.join(sorted(list(common_words)))}") # sorted
    else:
        similarities.append("No significant common keywords found between patent abstract and text.")
    
    union_words = words_a.union(words_text)
    if not union_words:
        jaccard_score = 0.0
    else:
        jaccard_score = len(words_a.intersection(words_text)) / len(union_words)

    # Simple difference reporting
    differences = []
    unique_to_patent = sorted(list(words_a - words_text))
    unique_to_text = sorted(list(words_text - words_a))

    if unique_to_patent:
        differences.append(f"Keywords in patent abstract not in text (up to 5): {', '.join(unique_to_patent[:5])}{'...' if len(unique_to_patent) > 5 else ''}")
    if unique_to_text:
        differences.append(f"Keywords in text not in patent abstract (up to 5): {', '.join(unique_to_text[:5])}{'...' if len(unique_to_text) > 5 else ''}")
    
    if not differences and common_words:
        differences.append("Patent abstract and text are very similar based on filtered keywords.")
    elif not differences:
        differences.append("Comparison with raw text is basic. Only abstract keyword overlap considered.")


    return PatentComparisonResult(
        patent_a_id=patent_id,
        patent_b_id="CustomText", 
        similarities=similarities,
        differences=differences,
        overall_similarity_score=round(jaccard_score, 2) # Score based purely on Jaccard for text comparison
    )
