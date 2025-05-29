import sys
# Adjust the path to import from the project's src directory.
# This assumes that the script might be run from the root of the project,
# or that 'src' is in PYTHONPATH.
# A common way is to add the project root to sys.path if running the script directly for development.
project_root = '.' # This might need adjustment depending on where you run it from.
# If patent_agent is the root, and this script is in patent_agent/src/ui/cli.py
# then to access patent_agent.src.agent_core, the PYTHONPATH should include the 'patent_agent' directory.
# For simplicity in a direct script run, let's assume we might need to adjust sys.path:
import os
# Assuming the script is in patent_agent/src/ui/
# and the modules are in patent_agent/src/
# We want to add 'patent_agent' directory to sys.path so that 'from patent_agent.src...' works
current_dir = os.path.dirname(os.path.abspath(__file__))
# patent_agent/src/ui -> patent_agent/src -> patent_agent
project_root_dir = os.path.dirname(os.path.dirname(current_dir)) 
# Now project_root_dir should be 'patent_agent'
# If 'patent_agent' itself is inside another root for the repo, adjust accordingly.
# For now, let's assume 'patent_agent' is the top-level package directory.
# To make `from patent_agent.src...` work, the directory *containing* `patent_agent` must be in sys.path.
# Or, if `patent_agent` is the root, then `from src...`
# This path adjustment is tricky. For now, let's assume direct execution from project root or PYTHONPATH is set.

# Attempting a relative import structure if possible, or relying on PYTHONPATH
try:
    from patent_agent.src.agent_core import handle_query
    from patent_agent.src.search_module import PatentSearchResult # For type annotation and accessing fields
except ImportError:
    # Fallback for when running the script directly from ui directory for example
    # This adds patent_agent/src to sys.path, then patent_agent to sys.path
    # sys.path.insert(0, os.path.join(project_root_dir, 'src')) # to find agent_core, search_module
    sys.path.insert(0, project_root_dir) # to find patent_agent package
    # This is often needed if you run `python src/ui/cli.py` from within `patent_agent` directory
    # A better way for package execution is `python -m patent_agent.src.ui.cli` from the directory *containing* `patent_agent`
    from patent_agent.src.agent_core import handle_query
    from patent_agent.src.search_module import PatentSearchResult


def display_results(results: list[PatentSearchResult]):
    if not results:
        print("No patents found for your query.")
        return
    print("\n--- Search Results ---")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Patent ID: {result.patent_id}")
        print(f"  Title: {result.title}")
        print(f"  Abstract: {result.abstract[:200]}...") # Print first 200 chars of abstract
        print(f"  Publication Date: {result.publication_date}")
        print(f"  Assignee: {result.assignee}")
        print(f"  Relevance Score: {result.relevance_score:.2f}")
    print("\n--------------------")

def main():
    print("Welcome to the Patent Agent CLI!")
    print("You can search for patents using keywords.")
    
    # This is a simple way to adjust path for direct script execution.
    # It's often better to run as a module or ensure PYTHONPATH is set.
    # For the worker, this might not be an issue if it understands the project structure.
    # Adding parent of 'src' to path to allow 'from patent_agent.src...'
    # Assuming current file is patent_agent/src/ui/cli.py
    # parent_of_src = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # if parent_of_src not in sys.path:
    #    sys.path.insert(0, parent_of_src)

    while True:
        user_input = input("\nEnter your patent search query (or type 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            print("Exiting Patent Agent CLI. Goodbye!")
            break
        
        if not user_input:
            print("Please enter a search query.")
            continue
            
        print(f"Searching for: '{user_input}'...")
        try:
            # For now, no filters are passed from CLI, this can be an enhancement
            results = handle_query(user_query=user_input) 
            display_results(results)
        except Exception as e:
            print(f"An error occurred: {e}")
            # Potentially log the error to a file or more detailed logging system
            # For now, just print to console
            # import traceback
            # traceback.print_exc()

if __name__ == '__main__':
    main()
