import sys
import os

# Adjust path to import from the project's src directory.
# This assumes that the script might be run from the root of the project,
# or that 'src' is in PYTHONPATH.
# A common way is to add the project root to sys.path if running the script directly for development.

# Attempting a relative import structure if possible, or relying on PYTHONPATH
try:
    from patent_agent.src.agent_core import process_command # Updated import
    from patent_agent.src.search_module import PatentSearchResult
    from patent_agent.src.comparison_module import PatentComparisonResult
    from patent_agent.src.writing_module import PatentDraftSection
    from typing import Union, List, Any # For type hints
except ImportError:
    # Fallback for when running the script directly from ui directory for example
    # This adds the directory containing 'patent_agent' to sys.path
    # Get the absolute path to the directory containing 'patent_agent'
    # current_script_path = .../patent_agent/src/ui/cli.py
    # ui_dir = .../patent_agent/src/ui
    # src_dir = .../patent_agent/src
    # patent_agent_package_dir = .../patent_agent
    # repo_root_dir = .../ (directory containing patent_agent)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    patent_agent_package_dir = os.path.dirname(src_dir)
    repo_root_dir = os.path.dirname(patent_agent_package_dir)

    if repo_root_dir not in sys.path:
        sys.path.insert(0, repo_root_dir) # Add repo root to sys.path
    
    from patent_agent.src.agent_core import process_command
    from patent_agent.src.search_module import PatentSearchResult
    from patent_agent.src.comparison_module import PatentComparisonResult
    from patent_agent.src.writing_module import PatentDraftSection
    from typing import Union, List, Any


def display_search_results(results: List[PatentSearchResult]):
    if not results:
        print("No patents found or an error occurred during search.")
        return
    print("\n--- Search Results ---")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Patent ID: {result.patent_id}")
        print(f"  Title: {result.title}")
        if result.abstract:
             print(f"  Abstract: {result.abstract[:200]}{'...' if len(result.abstract) > 200 else ''}")
        else:
            print("  Abstract: Not available")
        print(f"  Publication Date: {result.publication_date or 'N/A'}")
        print(f"  Assignee: {result.assignee or 'N/A'}")
        print(f"  Relevance Score: {result.relevance_score:.2f}")
        if result.patent_url:
            print(f"  URL: {result.patent_url}")
    print("\n--------------------")

def display_comparison_result(result: PatentComparisonResult):
    print("\n--- Comparison Result ---")
    print(f"Comparison between: {result.patent_a_id} and {result.patent_b_id}")
    print(f"Overall Similarity Score: {result.overall_similarity_score:.2f}")
    print("\nSimilarities:")
    if result.similarities:
        for sim in result.similarities:
            print(f"- {sim}")
    else:
        print("- None found.")
    print("\nDifferences:")
    if result.differences:
        for diff in result.differences:
            print(f"- {diff}")
    else:
        print("- None found or not applicable.")
    print("\n-----------------------")

def display_generated_section(result: PatentDraftSection):
    print("\n--- Generated Patent Section ---")
    print(f"Section Title: {result.section_title}")
    print(f"Confidence: {result.confidence_score:.2f}")
    print("\nContent:")
    print(result.content)
    print("\n----------------------------")

def display_summary_result(result_text: str):
    print("\n--- Patent Summary ---")
    print(result_text)
    print("\n--------------------")

def main():
    print("Welcome to the Patent Agent CLI!")
    print("Commands: search <terms>, compare <id1> <id2>, compare_text <id> <text>, generate <section> about <topic>, summarize <id>, exit")

    while True:
        user_input = input("\nPatentAgent> ").strip()
        if not user_input:
            continue
        if user_input.lower() == 'exit':
            print("Exiting Patent Agent CLI. Goodbye!")
            break
        
        print(f"Processing: '{user_input}'...")
        try:
            # Pass the whole string to the agent core
            result: Union[List[PatentSearchResult], PatentComparisonResult, PatentDraftSection, str, None] = process_command(user_input)

            if isinstance(result, list) and all(isinstance(item, PatentSearchResult) for item in result):
                display_search_results(result)
            elif isinstance(result, PatentComparisonResult):
                display_comparison_result(result)
            elif isinstance(result, PatentDraftSection):
                display_generated_section(result)
            elif isinstance(result, str) and ("Unknown command" in result or "requires" in result or "No command" in result or "not found" in result or "error occurred" in result or "Search query or filters must be provided." in result or "No valid query conditions constructed." in result): # Error message string
                print(f"Info: {result}") # Changed "Error:" to "Info:" for user feedback that isn't necessarily a critical error
            elif isinstance(result, str): # Assume it's a summary if it's a string not matching error patterns
                display_summary_result(result)
            elif result is None: # Should ideally not happen if process_command returns error strings
                 print("No result or an unhandled error occurred.")
            else:
                print(f"Received an unexpected result type: {type(result)}")

        except Exception as e:
            print(f"A critical error occurred in CLI: {e}")
            # import traceback
            # traceback.print_exc()

if __name__ == '__main__':
    main()
