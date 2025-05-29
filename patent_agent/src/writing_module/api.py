from typing import List, Optional # Ensure List, Optional are imported
import re # For simple keyword extraction

# Data class (should already exist)
# Ensure this matches the definition from the earlier step (e.g., using dataclasses)
from dataclasses import dataclass, field

@dataclass
class PatentDraftSection:
    section_title: str
    content: str
    confidence_score: float = 0.0

MOCK_PATENT_DATABASE = {
    "US20230000001A1": {"patent_id": "US20230000001A1", "title": "Novel Quantum Computing Method", "abstract": "A method for improving qubit stability in quantum computers. This method involves advanced cooling techniques and materials.", "publication_date": "2023-01-01", "assignee": "Tech Innovations Inc.", "claims": ["A method of cooling qubits.", "A system for quantum computation."]},
    "US20230000002A1": {"patent_id": "US20230000002A1", "title": "AI-Powered Drug Discovery Platform", "abstract": "Utilizing machine learning to accelerate the identification of potential drug candidates. This platform uses AI for analyzing biological data.", "publication_date": "2023-01-15", "assignee": "Pharma Solutions LLC", "claims": ["A platform for drug discovery.", "A method using AI for identification."]},
    "CN100000000A": {"patent_id": "CN100000000A", "title": "Method for preparing a therapeutic composition", "abstract": "The invention discloses a method for preparing a therapeutic composition, which comprises advanced mixing steps and purification processes.", "publication_date": "2022-05-10", "assignee": "BioFuture Ltd.", "claims": ["A method of preparing compositions.", "A therapeutic composition."]},
    "US20220000001A1": {"patent_id": "US20220000001A1", "title": "Advanced Cooling System for Processors", "abstract": "An advanced cooling mechanism for high-performance computer processors. This method is novel and improves efficiency.", "publication_date": "2022-03-12", "assignee": "Tech Innovations Inc.", "claims": ["A cooling system.", "A method for reducing processor temperature."]}
}

def _extract_keywords(prompt: str) -> str:
    prompt_lower = prompt.lower()
    keywords = []
    # Attempt to find phrases after prepositions like "about", "for", etc.
    match_prep = re.search(r"(?:about|for|related to|regarding|concerning)\s+([\w\s,]+)", prompt_lower)
    if match_prep:
        extracted_phrase = match_prep.group(1).replace(',', '') # Remove commas
        # Take up to 3 words from this phrase, avoiding very short words if possible
        potential_keywords = [word for word in extracted_phrase.split() if len(word) > 2]
        keywords.extend(potential_keywords[:3]) 
    
    # If no keywords from prepositional phrase, try to get some from the general prompt
    if not keywords:
        # Exclude common instruction words and very short words
        excluded_words = {"generate", "draft", "write", "section", "patent", "invention", "describe", "develop", "what", "how", "the", "and", "for", "with", "system", "method"}
        parts = [word for word in re.split(r'\s|[,.]', prompt_lower) if len(word) > 3 and word not in excluded_words]
        keywords = parts[:3] # take first 3 significant words found this way

    return " ".join(list(set(keywords))) if keywords else "the disclosed technology" # Use set to avoid duplicate keywords if logic allows


def generate_patent_section(prompt: str, existing_claims: Optional[List[str]] = None) -> PatentDraftSection:
    prompt_lower = prompt.lower()
    # Clean up prompt for keyword extraction by removing common instruction verbs
    cleaned_prompt_for_keywords = prompt_lower.replace("generate", "").replace("draft", "").replace("write", "").replace("section", "").replace("claims about", "").replace("abstract for", "").replace("background on", "").replace("summary of", "").strip()
    topic_keywords = _extract_keywords(cleaned_prompt_for_keywords)

    section_title = "General Section"
    content = f"Please specify a standard patent section like 'Abstract', 'Background', 'Summary', or 'Claims' for {topic_keywords}."
    confidence = 0.1

    if "abstract" in prompt_lower:
        section_title = "Abstract"
        content = f"The present invention relates to {topic_keywords}. It provides a method and system for achieving enhanced results in this field, offering significant advantages over prior art such as improved efficiency and novel functionalities."
        confidence = 0.35
    elif "background" in prompt_lower:
        section_title = "Background of the Invention"
        content = f"The technical field of this invention is {topic_keywords}. Existing approaches in this area often suffer from limitations such as high cost, low efficiency, or excessive complexity. Therefore, there is a recognized need for an improved solution that addresses these shortcomings and advances the state of the art."
        confidence = 0.3
    elif "summary" in prompt_lower or "brief summary" in prompt_lower:
        section_title = "Summary of the Invention"
        content = f"The present invention provides a solution to the aforementioned problems by disclosing a novel system and method for {topic_keywords}. The invention achieves superior performance and greater utility compared to existing technologies by incorporating innovative features and optimized processes."
        confidence = 0.32
    elif "claim" in prompt_lower: 
        section_title = "Claims"
        # Try to infer system or method from keywords or prompt
        is_system_claim = "system" in topic_keywords.lower() or "apparatus" in topic_keywords.lower() or "device" in topic_keywords.lower()
        is_method_claim = "method" in topic_keywords.lower() or "process" in topic_keywords.lower() or "technique" in topic_keywords.lower()

        claim_type_text = "system" if is_system_claim and not is_method_claim else "method" # Default to method if unclear or both
        
        base_claim_text = f"A {claim_type_text} for {topic_keywords}, comprising:" if claim_type_text == "system" else f"A {claim_type_text} for {topic_keywords}, comprising the steps of:"
        
        if existing_claims:
            num_existing = len(existing_claims)
            # Try to infer type from existing claims if possible
            if existing_claims[0].lower().startswith("a system") or existing_claims[0].lower().startswith("an apparatus"):
                claim_type_text = "system"
            elif existing_claims[0].lower().startswith("a method") or existing_claims[0].lower().startswith("a process"):
                claim_type_text = "method"
            
            additional_feature_prompt = prompt_lower.replace("generate dependent claim", "").replace("draft dependent claim", "").replace("write dependent claim","").strip()
            additional_feature = _extract_keywords(additional_feature_prompt) if "further comprising" in prompt_lower else "an additional innovative feature"


            content = f"{num_existing + 1}. The {claim_type_text} of claim {num_existing}, further comprising {additional_feature}."
        else:
            content = f"1. {base_claim_text}\n   (a) a first {'component' if claim_type_text == 'system' else 'step'}; and\n   (b) a second {'component' if claim_type_text == 'system' else 'step'} operatively associated with the first {'component' if claim_type_text == 'system' else 'step'}."
        confidence = 0.25

    return PatentDraftSection(section_title=section_title, content=content, confidence_score=confidence)

def summarize_patent(patent_id: str, target_length: int = 200) -> str:
    patent_data = MOCK_PATENT_DATABASE.get(patent_id)
    if not patent_data:
        return f"Patent with ID '{patent_id}' not found in the mock database."
    
    abstract = patent_data.get("abstract", "").strip() # Ensure strip here
    
    if not abstract: # Handle empty or whitespace-only abstracts after stripping
        return "No abstract content available to summarize for this patent."

    if len(abstract) <= target_length:
        return abstract
    else:
        # Try to cut at the last space within target_length
        cut_point = abstract.rfind(' ', 0, target_length)
        # If no space is found, or if the space is too early (less than half the target length),
        # just cut at target_length. This avoids very short summaries if a space is found very early.
        if cut_point == -1 or cut_point < target_length / 2: 
             summary_text = abstract[:target_length].strip()
        else:
             summary_text = abstract[:cut_point].strip()
        return summary_text + "..."
