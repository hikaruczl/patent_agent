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
        print("No patents found or an error occurred during search.") # This message could be more specific if core returns detailed errors
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
    print("Available commands: search <terms>, compare <id1> <id2>, compare_text <id> <text>, generate <section> about <topic>, summarize <id>, exit")

    while True:
        user_input = input("\nPatentAgent> ").strip()
        if not user_input: # Handle empty input line
            continue
        
        # CLI handles exit directly for immediate effect
        command_lower = user_input.split()[0].lower() if user_input.split() else "" # Get command for summary check
        
        if command_lower == 'exit': # Check command_lower for exit
            print("Exiting Patent Agent CLI. Goodbye!")
            break
        
        # print(f"Processing: '{user_input}'...") # Optional debug line
        try:
            result = process_command(user_input)

            if isinstance(result, list) and all(isinstance(item, PatentSearchResult) for item in result):
                display_search_results(result)
            elif isinstance(result, PatentComparisonResult):
                display_comparison_result(result)
            elif isinstance(result, PatentDraftSection):
                display_generated_section(result)
            elif isinstance(result, str): # Check if it's an error message or a valid string result (e.g. summary)
                if result.lower().startswith("error:"):
                    print(result) # Print error messages directly
                # Specific check for summarize command's valid string output
                elif command_lower == "summarize" and not result.startswith("Patent with ID") and not result.startswith("No abstract content") and not result.lower().startswith("error:"):
                    display_summary_result(result)
                elif result == "Exiting...": # If core handles exit command (it does now)
                    print("Exiting Patent Agent CLI. Goodbye!") # Should be caught by direct 'exit' check above ideally
                    break
                else: # Other string results that might not be errors but aren't summaries
                    print(result) 
            elif result is None: # Should ideally be an error string now from process_command
                 print("Error: Received no result or an unhandled error occurred in the agent core.")
            else:
                print(f"Error: Received an unexpected result type: {type(result)}")

        except Exception as e:
            print(f"A critical error occurred in CLI: {e}")
            # import traceback
            # traceback.print_exc() # Uncomment for debugging

if __name__ == '__main__':
    main()
