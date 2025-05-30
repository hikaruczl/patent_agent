from typing import List, Optional 
import re 
from dataclasses import dataclass, field
from patent_agent.config import get_api_key

# Attempt to import InferenceClient and specific exceptions
try:
    from huggingface_hub import InferenceClient
    # Attempt to import specific exceptions. If they are not found, define them as None
    # so the except blocks don't cause NameErrors if huggingface_hub is older or changes structure.
    try:
        from huggingface_hub.utils import HfHubHTTPError, GatedRepoError, ModelNotFoundError
    except ImportError:
        print("WARNING: Specific Hugging Face Hub exceptions (HfHubHTTPError, GatedRepoError, ModelNotFoundError) not found. Will rely on generic error handling for LLM calls.")
        HfHubHTTPError = None 
        GatedRepoError = None
        ModelNotFoundError = None
except ImportError:
    InferenceClient = None
    HfHubHTTPError = None 
    GatedRepoError = None
    ModelNotFoundError = None
    print("WARNING: huggingface_hub.InferenceClient could not be imported. LLM generation will be disabled.")

LLM_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

@dataclass
class PatentDraftSection:
    section_title: str
    content: str
    confidence_score: float = 0.0

MOCK_PATENT_DATABASE = { # Remains unchanged
    "US20230000001A1": {"patent_id": "US20230000001A1", "title": "Novel Quantum Computing Method", "abstract": "A method for improving qubit stability in quantum computers. This method involves advanced cooling techniques and materials.", "publication_date": "2023-01-01", "assignee": "Tech Innovations Inc.", "claims": ["A method of cooling qubits.", "A system for quantum computation."]},
    "US20230000002A1": {"patent_id": "US20230000002A1", "title": "AI-Powered Drug Discovery Platform", "abstract": "Utilizing machine learning to accelerate the identification of potential drug candidates. This platform uses AI for analyzing biological data.", "publication_date": "2023-01-15", "assignee": "Pharma Solutions LLC", "claims": ["A platform for drug discovery.", "A method using AI for identification."]},
    "CN100000000A": {"patent_id": "CN100000000A", "title": "Method for preparing a therapeutic composition", "abstract": "The invention discloses a method for preparing a therapeutic composition, which comprises advanced mixing steps and purification processes.", "publication_date": "2022-05-10", "assignee": "BioFuture Ltd.", "claims": ["A method of preparing compositions.", "A therapeutic composition."]},
    "US20220000001A1": {"patent_id": "US20220000001A1", "title": "Advanced Cooling System for Processors", "abstract": "An advanced cooling mechanism for high-performance computer processors. This method is novel and improves efficiency.", "publication_date": "2022-03-12", "assignee": "Tech Innovations Inc.", "claims": ["A cooling system.", "A method for reducing processor temperature."]}
}

def _extract_keywords(prompt: str) -> str: # Remains unchanged
    prompt_lower = prompt.lower()
    keywords = []
    match_prep = re.search(r"(?:about|for|related to|regarding|concerning)\s+([\w\s,]+)", prompt_lower)
    if match_prep:
        extracted_phrase = match_prep.group(1).replace(',', '') 
        potential_keywords = [word for word in extracted_phrase.split() if len(word) > 2]
        keywords.extend(potential_keywords[:3]) 
    if not keywords:
        excluded_words = {"generate", "draft", "write", "section", "patent", "invention", "describe", "develop", "what", "how", "the", "and", "for", "with", "system", "method"}
        parts = [word for word in re.split(r'\s|[,.]', prompt_lower) if len(word) > 3 and word not in excluded_words]
        keywords = parts[:3] 
    return " ".join(list(set(keywords))) if keywords else "the disclosed technology"

def _generate_content_with_llm(section_type: str, topic_keywords: str, existing_claims: Optional[List[str]] = None) -> Optional[str]:
    if InferenceClient is None:
        # Already printed a warning at import time.
        return None

    api_key = get_api_key("HUGGINGFACE_API_KEY")
    if not api_key:
        print("INFO: LLM generation skipped: HUGGINGFACE_API_KEY not found in settings.ini or is empty.")
        return None

    # Construct a more detailed prompt for better LLM guidance
    if section_type.lower() == "claims" and existing_claims: # Ensure lowercase comparison for section_type
        claims_str = "\n".join(existing_claims)
        llm_prompt_text = (
            f"You are a patent drafting assistant. The patent is about '{topic_keywords}'.\n"
            f"Existing claims are:\n{claims_str}\n\n"
            f"Generate a new dependent claim that logically follows and builds upon the existing claims, "
            f"or if more appropriate, a new independent claim if it covers a distinct inventive aspect related to the topic. "
            f"Ensure the new claim is concise and clear. For example, if adding a dependent claim, start with 'The method/system of claim X, further comprising...'."
        )
    elif section_type.lower() == "claims": # Ensure lowercase comparison
        llm_prompt_text = (
            f"You are a patent drafting assistant. Generate a set of 1-3 initial patent claims for an invention related to '{topic_keywords}'. "
            f"Start with a broad independent claim, followed by a dependent claim if appropriate. For example: '1. A system for {topic_keywords}, comprising: (a) a first component; (b) a second component.'"
        )
    else:
        llm_prompt_text = (
            f"You are a patent drafting assistant. Generate a patent '{section_type}' section for an invention titled '{topic_keywords}'. "
            f"The section should be detailed, technically sound, and appropriate for a formal patent document. "
            f"For an abstract, provide a concise summary. For background, discuss prior art and problems. For summary, briefly explain the invention's advantages."
        )
    
    # print(f"DEBUG: LLM Prompt: {llm_prompt_text}") # Uncomment for debugging

    try:
        client = InferenceClient(token=api_key)
        print(f"INFO: Calling LLM for section: {section_type}, topic: {topic_keywords}") # Moved print before API call
        completion = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": llm_prompt_text}],
            max_tokens=350, 
            temperature=0.7,
        )
        generated_text = completion.choices[0].message.content.strip()
        
        if len(generated_text) < 20: # Check for very short content
            print(f"WARN: LLM generated unusually short content for {section_type} on '{topic_keywords}'. Length: {len(generated_text)}. Content: '{generated_text}'")
            # Consider this a failure to force fallback to template
            return None 
        return generated_text

    # Specific Hugging Face client errors, if they were successfully imported
    except (ModelNotFoundError if ModelNotFoundError else Exception) as e: # type: ignore
        if ModelNotFoundError and isinstance(e, ModelNotFoundError):
             print(f"ERROR: LLM model '{LLM_MODEL_NAME}' not found. Please check the model name. Details: {e}")
        # This block will only be specifically effective if ModelNotFoundError is a distinct, imported exception
        # Otherwise, it falls into the generic Exception.
        # To make it truly conditional on ModelNotFoundError being non-None and e being an instance of it:
        # if ModelNotFoundError is not None and isinstance(e, ModelNotFoundError):
        #    print(f"ERROR: LLM model '{LLM_MODEL_NAME}' not found. Details: {e}")
        #    return None
        # elif GatedRepoError is not None and isinstance(e, GatedRepoError):
        #    print(f"ERROR: Access to LLM model '{LLM_MODEL_NAME}' is gated. Details: {e}")
        #    return None
        # elif HfHubHTTPError is not None and isinstance(e, HfHubHTTPError):
        #    print(f"ERROR: LLM API request failed with HTTP error. Status: {e.response.status_code if hasattr(e, 'response') and e.response else 'N/A'}. Details: {e}")
        #    if hasattr(e, 'response') and e.response and e.response.status_code == 401:
        #        print("INFO: This might be due to an invalid or unauthorized HUGGINGFACE_API_KEY.")
        #    return None
        # else: # Generic catch-all for other errors or if specific exceptions are None
            error_name = type(e).__name__
            print(f"ERROR: An error occurred during LLM content generation: {error_name} - {e}")
            if "401" in str(e).lower() or "unauthorized" in str(e).lower():
                print("INFO: This could be due to an invalid or unauthorized HUGGINGFACE_API_KEY.")
            elif "modelnotfound" in str(e).lower().replace(" ", "") or "404" in str(e).lower() : # More robust check for model not found
                print(f"INFO: The model '{LLM_MODEL_NAME}' might be incorrect or unavailable.")
            elif "rate limit" in str(e).lower():
                print("INFO: LLM API rate limit possibly exceeded.")
            # Dynamic check for HfHubHTTPError if it was not imported at top level or was None
            try:
                from huggingface_hub.utils import HfHubHTTPError as DynHfHubHTTPError
                if isinstance(e, DynHfHubHTTPError):
                     print(f"DEBUG: HfHubHTTPError details: Response code {e.response.status_code if hasattr(e, 'response') and e.response else 'N/A'}")
            except ImportError:
                pass # huggingface_hub not available or HfHubHTTPError not found
        return None
    except Exception as e: # Fallback for any other unexpected exception
        error_name = type(e).__name__
        print(f"ERROR: A critical unexpected error occurred during LLM content generation: {error_name} - {e}")
        return None


def generate_patent_section(prompt: str, existing_claims: Optional[List[str]] = None) -> PatentDraftSection:
    prompt_lower = prompt.lower()
    cleaned_prompt_for_keywords = prompt_lower.replace("generate", "").replace("draft", "").replace("write", "").replace("section", "").replace("claims about", "").replace("abstract for", "").replace("background on", "").replace("summary of", "").strip()
    topic_keywords_extracted = _extract_keywords(cleaned_prompt_for_keywords)

    section_title_to_generate = "General Section" 
    if "abstract" in prompt_lower: section_title_to_generate = "Abstract"
    elif "background" in prompt_lower: section_title_to_generate = "Background of the Invention"
    elif "summary" in prompt_lower or "brief summary" in prompt_lower: section_title_to_generate = "Summary of the Invention"
    elif "claim" in prompt_lower: section_title_to_generate = "Claims"
    
    llm_generated_content = _generate_content_with_llm(section_title_to_generate, topic_keywords_extracted, existing_claims)

    if llm_generated_content: # Check if content is not None (already checked for min length in helper)
        return PatentDraftSection(
            section_title=section_title_to_generate, 
            content=llm_generated_content, 
            confidence_score=0.75 
        )
    # Fallback to existing template-based generation logic
    print(f"INFO: Falling back to template generation for section: {section_title_to_generate}, topic: {topic_keywords_extracted}")
    section_title = section_title_to_generate 
    content = f"Please specify a standard patent section like 'Abstract', 'Background', 'Summary', or 'Claims' for {topic_keywords_extracted}."
    confidence = 0.1

    if section_title == "Abstract": 
        content = f"The present invention relates to {topic_keywords_extracted}. It provides a method and system for achieving enhanced results in this field, offering significant advantages over prior art such as improved efficiency and novel functionalities."
        confidence = 0.35
    elif section_title == "Background of the Invention":
        content = f"The technical field of this invention is {topic_keywords_extracted}. Existing approaches in this area often suffer from limitations such as high cost, low efficiency, or excessive complexity. Therefore, there is a recognized need for an improved solution that addresses these shortcomings and advances the state of the art."
        confidence = 0.3
    elif section_title == "Summary of the Invention":
        content = f"The present invention provides a solution to the aforementioned problems by disclosing a novel system and method for {topic_keywords_extracted}. The invention achieves superior performance and greater utility compared to existing technologies by incorporating innovative features and optimized processes."
        confidence = 0.32
    elif section_title == "Claims":
        is_system_claim = "system" in topic_keywords_extracted.lower() or "apparatus" in topic_keywords_extracted.lower() or "device" in topic_keywords_extracted.lower()
        is_method_claim = "method" in topic_keywords_extracted.lower() or "process" in topic_keywords_extracted.lower() or "technique" in topic_keywords_extracted.lower()
        claim_type_text = "system" if is_system_claim and not is_method_claim else "method"
        base_claim_text = f"A {claim_type_text} for {topic_keywords_extracted}, comprising:" if claim_type_text == "system" else f"A {claim_type_text} for {topic_keywords_extracted}, comprising the steps of:"
        if existing_claims:
            num_existing = len(existing_claims)
            if existing_claims[0].lower().startswith("a system") or existing_claims[0].lower().startswith("an apparatus"): claim_type_text = "system"
            elif existing_claims[0].lower().startswith("a method") or existing_claims[0].lower().startswith("a process"): claim_type_text = "method"
            additional_feature_prompt = prompt_lower.replace("generate dependent claim", "").replace("draft dependent claim", "").replace("write dependent claim","").strip()
            additional_feature = _extract_keywords(additional_feature_prompt) if "further comprising" in prompt_lower else "an additional innovative feature"
            content = f"{num_existing + 1}. The {claim_type_text} of claim {num_existing}, further comprising {additional_feature}."
        else:
            content = f"1. {base_claim_text}\n   (a) a first {'component' if claim_type_text == 'system' else 'step'}; and\n   (b) a second {'component' if claim_type_text == 'system' else 'step'} operatively associated with the first {'component' if claim_type_text == 'system' else 'step'}."
        confidence = 0.25
    
    return PatentDraftSection(section_title=section_title, content=content, confidence_score=confidence)

def summarize_patent(patent_id: str, target_length: int = 200) -> str: # Remains unchanged
    patent_data = MOCK_PATENT_DATABASE.get(patent_id)
    if not patent_data:
        return f"Patent with ID '{patent_id}' not found in the mock database."
    abstract = patent_data.get("abstract", "").strip()
    if not abstract: 
        return "No abstract content available to summarize for this patent."
    if len(abstract) <= target_length:
        return abstract
    else:
        cut_point = abstract.rfind(' ', 0, target_length)
        if cut_point == -1 or cut_point < target_length / 2: 
             summary_text = abstract[:target_length].strip()
        else:
             summary_text = abstract[:cut_point].strip()
        return summary_text + "..."
