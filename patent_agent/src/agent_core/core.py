from patent_agent.src.comparison_module import compare_patents, compare_patent_with_text, PatentComparisonResult
from patent_agent.src.writing_module import generate_patent_section, summarize_patent, PatentDraftSection
from patent_agent.src.search_module import search_patents, PatentSearchResult
from typing import Union, List, Dict, Any # Add Union

def process_command(full_command_str: str) -> Union[List[PatentSearchResult], PatentComparisonResult, PatentDraftSection, str, None]:
    parts = full_command_str.strip().split()
    if not parts:
        return "Error: No command entered. Available commands: search, compare, compare_text, generate, summarize, exit."

    command = parts[0].lower()
    args = parts[1:]

    # print(f"Agent core processing command: '{command}' with args: {args}") # For debugging

    if command == "search":
        if not args:
            return "Error: Search command requires query terms. Usage: search <query_terms>"
        query_terms = " ".join(args).strip()
        if not query_terms:
            return "Error: Search query terms cannot be empty."
        # ... rest of search logic
        return search_patents(query=query_terms, filters=None)

    elif command == "compare":
        if len(args) != 2:
            return "Error: Compare command requires exactly two patent IDs. Usage: compare <patent_id_1> <patent_id_2>"
        # Further ID validation could go here
        return compare_patents(patent_id_a=args[0], patent_id_b=args[1])

    elif command == "compare_text":
        if len(args) < 2:
            return "Error: Compare_text command requires a patent ID and text. Usage: compare_text <patent_id> <text_to_compare>"
        patent_id = args[0]
        text_to_compare = " ".join(args[1:]).strip()
        if not text_to_compare:
            return "Error: Text for comparison cannot be empty."
        return compare_patent_with_text(patent_id=patent_id, text_to_compare=text_to_compare)
        
    elif command == "generate":
        if len(args) < 3 or args[1].lower() != "about":
            return "Error: Generate command format is 'generate <section_type> about <topic_keywords>'. Example: generate abstract about AI."
        
        section_type = args[0].lower()
        supported_sections = ["abstract", "background", "summary", "claims"]
        if section_type not in supported_sections:
            return f"Error: Unsupported section type '{args[0]}'. Supported types are: {', '.join(supported_sections)}."
            
        topic_keywords = " ".join(args[2:]).strip()
        if not topic_keywords:
            return "Error: Topic keywords for generation cannot be empty."
            
        prompt = f"generate {section_type} about {topic_keywords}"
        return generate_patent_section(prompt=prompt, existing_claims=None)

    elif command == "summarize":
        if len(args) != 1:
            return "Error: Summarize command requires exactly one patent ID. Usage: summarize <patent_id>"
        return summarize_patent(patent_id=args[0])
        
    elif command == "exit": # Explicitly handle exit if it reaches here, though CLI might catch it first
        return "Exiting..." # Or None, depending on how CLI handles it.
        
    else:
        return f"Error: Unknown command '{command}'. Available commands: search, compare, compare_text, generate, summarize, exit."

# Note: The example usage block `if __name__ == '__main__':` has been removed
# as it would need significant updates to test the new command structure.
# Testing should ideally be done via the CLI or dedicated unit/integration tests.
