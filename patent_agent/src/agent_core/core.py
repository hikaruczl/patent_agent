from patent_agent.src.comparison_module import compare_patents, compare_patent_with_text, PatentComparisonResult
from patent_agent.src.writing_module import generate_patent_section, summarize_patent, PatentDraftSection
from patent_agent.src.search_module import search_patents, PatentSearchResult
from typing import Union, List, Dict, Any # Add Union

def process_command(full_command_str: str) -> Union[List[PatentSearchResult], PatentComparisonResult, PatentDraftSection, str, None]:
    parts = full_command_str.strip().split()
    if not parts:
        return "No command entered."

    command = parts[0].lower()
    args = parts[1:]

    print(f"Agent core processing command: '{command}' with args: {args}") # For debugging

    if command == "search":
        if not args:
            return "Search command requires query terms."
        query_terms = " ".join(args)
        # Basic filter handling (example, can be expanded)
        # search_filters_dict = {} # In a real scenario, parse filters from args too
        # For now, assuming filters might be part of the query_terms string or handled by search_patents if it evolves
        # Example: search apple assignee:"Apple Inc" date_from:"2022-01-01"
        # This would require more sophisticated parsing in search_patents or here.
        # Current search_patents expects a query string and an optional Dict for filters.
        # We'll just pass the query_terms for now.
        return search_patents(query=query_terms, filters=None) 

    elif command == "compare":
        if len(args) != 2:
            return "Compare command requires two patent IDs (e.g., compare ID1 ID2)."
        return compare_patents(patent_id_a=args[0], patent_id_b=args[1])

    elif command == "compare_text":
        if len(args) < 2: # Needs at least patent ID and one word of text
            return "Compare_text command requires a patent ID and text to compare (e.g., compare_text ID1 some text here)."
        patent_id = args[0]
        text_to_compare = " ".join(args[1:])
        return compare_patent_with_text(patent_id=patent_id, text_to_compare=text_to_compare)
        
    elif command == "generate":
        # Expecting: generate <section_type> about <topic_keywords>
        # e.g., "generate abstract about AI for drug discovery"
        # args[0] = section_type, args[1] = "about", args[2:] = topic_keywords
        if len(args) < 3 or args[1].lower() != "about":
            return "Generate command format: generate <section_type> about <topic_keywords> (e.g., generate abstract about AI)."
        section_type = args[0]
        topic_keywords = " ".join(args[2:])
        # Construct prompt for the module to understand the section and topic
        prompt = f"generate {section_type} about {topic_keywords}" 
        # existing_claims could be passed if there's a way to manage them in the agent_core state
        # For now, passing None as per the previous implementation of generate_patent_section
        return generate_patent_section(prompt=prompt, existing_claims=None)

    elif command == "summarize":
        if len(args) != 1:
            return "Summarize command requires one patent ID (e.g., summarize ID1)."
        return summarize_patent(patent_id=args[0])
        
    else:
        return f"Unknown command: '{command}'. Available commands: search, compare, compare_text, generate, summarize."

# Note: The example usage block `if __name__ == '__main__':` has been removed
# as it would need significant updates to test the new command structure.
# Testing should ideally be done via the CLI or dedicated unit/integration tests.
