from typing import List, Dict, Any # Ensure List, Dict, Any are imported
from patent_agent.src.search_module import search_patents, PatentSearchResult # Corrected import path

def handle_query(user_query: str, search_filters: Dict = None) -> List[PatentSearchResult]:
    """
    Handles a user's query by searching for patents.
    """
    print(f"Agent core handling query: '{user_query}', with filters: {search_filters}") # For debugging
    results = search_patents(query=user_query, filters=search_filters)
    return results

# Example usage (optional, for testing)
if __name__ == '__main__':
    test_query = "quantum computing"
    print(f"Testing agent_core with query: '{test_query}'")
    test_results = handle_query(user_query=test_query)
    if test_results:
        for result in test_results:
            print(f"  - ID: {result.patent_id}, Title: {result.title}, Score: {result.relevance_score}")
    else:
        print("No results found.")

    test_query_specific = "therapeutic"
    print(f"\nTesting agent_core with query: '{test_query_specific}'")
    test_results_specific = handle_query(user_query=test_query_specific)
    if test_results_specific:
        for result in test_results_specific:
            print(f"  - ID: {result.patent_id}, Title: {result.title}, Score: {result.relevance_score}")
    else:
        print("No results found for therapeutic.")

    test_query_none = "" # Test with empty query to get all mock results
    print(f"\nTesting agent_core with empty query:")
    test_results_none = handle_query(user_query=test_query_none)
    if test_results_none:
        for result in test_results_none:
            print(f"  - ID: {result.patent_id}, Title: {result.title}, Score: {result.relevance_score}")
    else:
        print("No results found for empty query.")
