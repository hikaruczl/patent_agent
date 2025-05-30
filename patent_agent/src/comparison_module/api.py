from dataclasses import dataclass, field
from typing import List, Dict, Set, Any # Ensure Any is imported

@dataclass
class PatentComparisonResult:
    patent_a_id: str
    patent_b_id: str
    similarities: List[str] = field(default_factory=list)
    differences: List[str] = field(default_factory=list)
    overall_similarity_score: float = 0.0
    # New fields for more detailed comparison
    claim_comparison: Dict[str, Any] = field(default_factory=dict) 
    ipc_comparison: Dict[str, Any] = field(default_factory=dict)

MOCK_PATENT_DATABASE: Dict[str, Dict] = {
    "US20230000001A1": {
        "patent_id": "US20230000001A1", 
        "title": "Novel Quantum Computing Method", 
        "abstract": "A method for improving qubit stability in quantum computers. This method involves advanced cooling.", 
        "publication_date": "2023-01-01", 
        "assignee": "Tech Innovations Inc.", 
        "claims": [
            "1. A method for quantum computation, comprising the steps of: (a) providing a qubit; (b) applying an advanced cooling cycle.",
            "2. The method of claim 1, wherein the advanced cooling cycle includes phase change materials."
        ],
        "ipc_classifications": ["G06N 10/00", "H01L 39/00"]
    },
    "US20230000002A1": {
        "patent_id": "US20230000002A1", 
        "title": "AI-Powered Drug Discovery Platform", 
        "abstract": "Utilizing machine learning to accelerate the identification of potential drug candidates. This platform uses AI.", 
        "publication_date": "2023-01-15", 
        "assignee": "Pharma Solutions LLC", 
        "claims": [
            "1. A platform for drug discovery, the platform comprising a processor configured to execute instructions to: (a) receive biological data; (b) apply a machine learning model to the biological data to identify drug candidates.",
            "2. The platform of claim 1, wherein the machine learning model is a neural network."
        ],
        "ipc_classifications": ["G16H 50/20", "G06N 3/08"]
    },
    "CN100000000A": {
        "patent_id": "CN100000000A", 
        "title": "Method for preparing a therapeutic composition", 
        "abstract": "The invention discloses a method for preparing a therapeutic composition, which comprises advanced mixing steps.", 
        "publication_date": "2022-05-10", 
        "assignee": "BioFuture Ltd.", 
        "claims": [
            "1. A method for preparing a therapeutic composition, comprising: (a) mixing ingredient A with ingredient B; (b) heating the mixture."
        ],
        "ipc_classifications": ["A61K 9/00", "A61K 47/02"]
    },
    "US20220000001A1": {
        "patent_id": "US20220000001A1", 
        "title": "Advanced Cooling System for Processors", 
        "abstract": "An advanced cooling mechanism for high-performance computer processors. This method is novel.", 
        "publication_date": "2022-03-12", 
        "assignee": "Tech Innovations Inc.",
        "claims": [
            "1. A cooling system for a processor, comprising: (a) a heat sink; (b) a fan coupled to the heat sink.",
            "2. The system of claim 1, further comprising a thermoelectric cooler.",
            "3. The system of claim 2, wherein the thermoelectric cooler uses phase change materials."
        ],
        "ipc_classifications": ["H01L 23/367", "G06F 1/20"]
    }
}

STOP_WORDS: Set[str] = {"a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "should", "can", "could", "may", "might", "must", "in", "on", "at", "by", "for", "with", "about", "to", "from", "of", "and", "or", "but", "this", "that", "it", "which", "method", "system", "invention", "discloses", "comprises", "platform", "uses", "for", "in", "to", "of", "claim", "claims", "herein", "said", "wherein", "means", "apparatus", "step", "steps", "process", "device", "first", "second", "third", "a", "b", "c"}

def _get_words_from_text(text: str) -> Set[str]:
    words = set(text.lower().replace(",", "").replace(".", "").replace(";", "").replace(":", "").replace("(", "").replace(")", "").split())
    return words - STOP_WORDS

def compare_patents(patent_id_a: str, patent_id_b: str) -> PatentComparisonResult:
    patent_a_data = MOCK_PATENT_DATABASE.get(patent_id_a)
    patent_b_data = MOCK_PATENT_DATABASE.get(patent_id_b)

    comparison_result = PatentComparisonResult(
        patent_a_id=patent_id_a,
        patent_b_id=patent_id_b,
    )

    if not patent_a_data or not patent_b_data:
        if not patent_a_data:
            comparison_result.similarities.append(f"Patent ID {patent_id_a} not found.")
        if not patent_b_data:
            comparison_result.similarities.append(f"Patent ID {patent_id_b} not found.")
        comparison_result.differences.append("Data unavailable for full comparison.")
        comparison_result.overall_similarity_score = 0.0
        return comparison_result

    # Abstract comparison
    words_a_abstract = _get_words_from_text(patent_a_data.get("abstract", ""))
    words_b_abstract = _get_words_from_text(patent_b_data.get("abstract", ""))
    common_abstract_keywords = list(words_a_abstract.intersection(words_b_abstract))
    if common_abstract_keywords:
        comparison_result.similarities.append(f"Common abstract keywords: {', '.join(sorted(common_abstract_keywords))}")
    else:
        comparison_result.differences.append("No significant common keywords found in abstracts.")
    
    unique_to_a_abstract = sorted(list(words_a_abstract - words_b_abstract))
    unique_to_b_abstract = sorted(list(words_b_abstract - words_a_abstract))
    if unique_to_a_abstract:
        comparison_result.differences.append(f"Abstract keywords unique to A (up to 5): {', '.join(unique_to_a_abstract[:5])}{'...' if len(unique_to_a_abstract) > 5 else ''}")
    if unique_to_b_abstract:
        comparison_result.differences.append(f"Abstract keywords unique to B (up to 5): {', '.join(unique_to_b_abstract[:5])}{'...' if len(unique_to_b_abstract) > 5 else ''}")


    # Assignee comparison
    assignee_a = patent_a_data.get("assignee")
    assignee_b = patent_b_data.get("assignee")
    assignee_bonus = 0.0
    if assignee_a and assignee_b and assignee_a == assignee_b:
        comparison_result.similarities.append(f"Same assignee: {assignee_a}")
        assignee_bonus = 0.2
    else:
        comparison_result.differences.append(f"Different assignees: A='{assignee_a}', B='{assignee_b}'")

    # Jaccard for abstract
    union_abstract_words = words_a_abstract.union(words_b_abstract)
    jaccard_abstract_score = 0.0
    if union_abstract_words:
        jaccard_abstract_score = len(common_abstract_keywords) / len(union_abstract_words)
    
    current_score = min(1.0, (jaccard_abstract_score * 0.8) + assignee_bonus)
    comparison_result.overall_similarity_score = round(current_score, 2)

    # Claim Comparison
    claims_a = patent_a_data.get("claims", [])
    claims_b = patent_b_data.get("claims", [])
    comparison_result.claim_comparison["patent_a_num_claims"] = len(claims_a)
    comparison_result.claim_comparison["patent_b_num_claims"] = len(claims_b)

    if len(claims_a) == len(claims_b) and len(claims_a) > 0:
        comparison_result.similarities.append(f"Same number of claims: {len(claims_a)}")
    else:
        comparison_result.differences.append(f"Different number of claims (A: {len(claims_a)}, B: {len(claims_b)})")

    all_claims_text_a = " ".join(claims_a)
    all_claims_text_b = " ".join(claims_b)
    words_a_claims = _get_words_from_text(all_claims_text_a)
    words_b_claims = _get_words_from_text(all_claims_text_b)
    common_claim_keywords = sorted(list(words_a_claims.intersection(words_b_claims)))
    if common_claim_keywords:
        comparison_result.claim_comparison["common_claim_keywords"] = common_claim_keywords
        comparison_result.similarities.append(f"Common claim keywords: {', '.join(common_claim_keywords[:5])}{'...' if len(common_claim_keywords) > 5 else ''}")
    else:
        comparison_result.claim_comparison["common_claim_keywords"] = []
        comparison_result.differences.append("No significant common keywords found in claims.")

    # IPC Classification Comparison
    ipc_a = patent_a_data.get("ipc_classifications", [])
    ipc_b = patent_b_data.get("ipc_classifications", [])
    comparison_result.ipc_comparison["patent_a_ipc"] = ipc_a
    comparison_result.ipc_comparison["patent_b_ipc"] = ipc_b
    
    common_ipc = sorted(list(set(ipc_a).intersection(set(ipc_b))))
    if common_ipc:
        comparison_result.ipc_comparison["common_ipc_codes"] = common_ipc
        comparison_result.similarities.append(f"Common IPC codes: {', '.join(common_ipc)}")
    else:
        comparison_result.ipc_comparison["common_ipc_codes"] = []
        comparison_result.differences.append("No common IPC codes found.")
        
    main_ipc_groups_a = sorted(list(set([ipc[:4] for ipc in ipc_a if len(ipc) >= 4])))
    main_ipc_groups_b = sorted(list(set([ipc[:4] for ipc in ipc_b if len(ipc) >= 4])))
    common_main_ipc_groups = sorted(list(set(main_ipc_groups_a).intersection(set(main_ipc_groups_b))))
    if common_main_ipc_groups:
        comparison_result.ipc_comparison["common_main_ipc_groups"] = common_main_ipc_groups
        comparison_result.similarities.append(f"Common main IPC groups: {', '.join(common_main_ipc_groups)}")
        # Add small bonus for common main IPC groups
        current_score = min(1.0, current_score + 0.05 * len(common_main_ipc_groups)) # Reduced bonus slightly from example
    else:
        comparison_result.ipc_comparison["common_main_ipc_groups"] = []
        comparison_result.differences.append("No common main IPC groups.")
    
    comparison_result.overall_similarity_score = round(current_score, 2)

    return comparison_result

def compare_patent_with_text(patent_id: str, text_to_compare: str) -> PatentComparisonResult:
    # This function's PatentComparisonResult will not have claim_comparison or ipc_comparison populated
    # as it compares a patent only with raw text.
    # The result dataclass will have these as empty dicts by default.
    patent_a_data = MOCK_PATENT_DATABASE.get(patent_id)

    comparison_result = PatentComparisonResult(
        patent_a_id=patent_id,
        patent_b_id="CustomText",
    )

    if not patent_a_data:
         comparison_result.similarities.append(f"Patent ID {patent_id} not found in mock database.")
         comparison_result.differences.append("Data unavailable for comparison due to missing patent.")
         comparison_result.overall_similarity_score = 0.0
         return comparison_result

    words_a = _get_words_from_text(patent_a_data.get("abstract", ""))
    words_text = _get_words_from_text(text_to_compare)
    
    common_words = sorted(list(words_a.intersection(words_text)))
    if common_words:
        comparison_result.similarities.append(f"Common keywords with text: {', '.join(common_words)}")
    else:
        comparison_result.similarities.append("No significant common keywords found between patent abstract and text.")
    
    union_words = words_a.union(words_text)
    jaccard_score = 0.0
    if union_words:
        jaccard_score = len(common_words) / len(union_words)
    comparison_result.overall_similarity_score = round(jaccard_score, 2)

    unique_to_patent = sorted(list(words_a - words_text))
    unique_to_text = sorted(list(words_text - words_a))
    if unique_to_patent:
        comparison_result.differences.append(f"Keywords in patent abstract not in text (up to 5): {', '.join(unique_to_patent[:5])}{'...' if len(unique_to_patent) > 5 else ''}")
    if unique_to_text:
        comparison_result.differences.append(f"Keywords in text not in patent abstract (up to 5): {', '.join(unique_to_text[:5])}{'...' if len(unique_to_text) > 5 else ''}")
    
    if not unique_to_patent and not unique_to_text and common_words:
        comparison_result.differences.append("Patent abstract and text are very similar based on filtered keywords.")
    elif not unique_to_patent and not unique_to_text and not common_words:
         comparison_result.differences.append("Both patent abstract and text yield no keywords after filtering, or are empty.")


    return comparison_result
