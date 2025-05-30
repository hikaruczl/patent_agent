import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, field # Ensure dataclass is imported
from patent_agent.config import get_api_key # Import the API key loader

# Definition of PatentSearchResult (should already exist)
@dataclass
class PatentSearchResult:
    patent_id: str
    title: str
    abstract: Optional[str] = None
    publication_date: Optional[str] = None
    assignee: Optional[str] = None # Changed to Optional, can be a list of strings too
    relevance_score: float = 0.0
    # Add a URL field if available and useful
    patent_url: Optional[str] = None


PATENTSVIEW_API_URL = "https://search.patentsview.org/api/v1/patent/query"
# Default fields to retrieve from PatentsView API
DEFAULT_FIELDS = [
    "patent_number", 
    "patent_title", 
    "patent_abstract", 
    "patent_date", 
    "assignee_organization", # For organizations
    "inventor_last_name", # Example if you want inventor info
    "cpc_subsection_title" # Example CPC classification
]

def search_patents(query: str, filters: Optional[Dict] = None, max_results: int = 10) -> List[PatentSearchResult]:
    results = []
    if not query and not filters: # Avoid empty queries to API
        print("Search query or filters must be provided.")
        return results

    # Construct the query payload for PatentsView API
    # Simple query: search the query string in patent title or abstract
    # For more complex queries based on filters, this logic would need expansion
    
    query_conditions = []
    if query:
        query_conditions.extend([
            {"_text_any": {"patent_title": query}},
            {"_text_any": {"patent_abstract": query}}
        ])
    
    # Example of how filters might be incorporated (very basic)
    if filters:
        if "assignee" in filters and filters["assignee"]: # Ensure filter value is not empty
            query_conditions.append({"_text_any": {"assignee_organization": filters["assignee"]}})
        if "publication_date_from" in filters and filters["publication_date_from"]: # Date format YYYY-MM-DD
             query_conditions.append({"_gte": {"patent_date": filters["publication_date_from"]}})
        # Add more filter handling here if needed

    if not query_conditions:
        print("No valid query conditions constructed. Please provide a query or valid filters.")
        return results

    # Main query structure: uses "_or" for query terms, and "_and" for combining with filters implicitly if multiple conditions
    # For simplicity here, let's assume filters are also part of an OR condition if query is present,
    # or stand alone if no general query term. A more robust filter integration is needed for complex logic.
    # This example will make all conditions ORed together.
    
    # A slightly better structure for query + filters could be:
    # q_obj = {"_and": []}
    # query_or_conditions = []
    # if query:
    #   query_or_conditions.extend([{"_text_any":{"patent_title":query}}, {"_text_any":{"patent_abstract":query}}])
    # if query_or_conditions:
    #   q_obj["_and"].append({"_or": query_or_conditions})
    # filter_and_conditions = []
    # if filters:
    #    if "assignee" in filters: filter_and_conditions.append({"_text_any":{"assignee_organization": filters["assignee"]}})
    #    # ... other filters
    # if filter_and_conditions:
    #   q_obj["_and"].extend(filter_and_conditions)
    # search_query_payload = {"q": q_obj, "f": DEFAULT_FIELDS, "o": {"per_page": max_results}}
    
    # Using the simpler OR for all specified query/filter terms for now:
    search_query_payload = {"q": {"_or": query_conditions}, "f": DEFAULT_FIELDS, "o": {"per_page": max_results}}

    # Get API key and add to payload if available
    api_key = get_api_key('PATENTSVIEW_API_KEY')
    if api_key:
        search_query_payload["key"] = api_key # Add key to payload if present
        print("INFO: Using configured PatentsView API Key.") # Changed DEBUG to INFO
    else:
        print("INFO: No PatentsView API Key found or configured. Using public access.") # Changed DEBUG to INFO


    try:
        print(f"Querying PatentsView API with payload: {json.dumps(search_query_payload)}")
        response = requests.post(PATENTSVIEW_API_URL, json=search_query_payload, timeout=20) # Increased timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        data = response.json()
        
        # Check structure of 'data' and 'count' based on actual API response
        # PatentsView API returns 'count' at the top level of the patent list object (e.g., data['patents'][0]['count'] is not correct)
        # The total number of patents found is in 'total_patent_count' at the root.
        # The count of patents *in the current response page* is implicitly len(data.get("patents", []))
        
        if data.get("patents") is None or data.get("total_patent_count", 0) == 0:
            print("No patents found for the query based on API response (total_patent_count is 0 or patents array is null).")
            return results

        for patent_data_item in data.get("patents", []): # data.get("patents") is a list of dicts
            if not patent_data_item: continue # Should not happen if API is well-behaved

            # Extracting assignee information
            # In PatentsView, assignee_organization is typically a list of strings.
            assignees_list = patent_data_item.get("assignee_organization")
            assignee_str = None
            if isinstance(assignees_list, list) and assignees_list:
                assignee_str = ", ".join(filter(None, assignees_list)) # Filter out None or empty strings
            elif isinstance(assignees_list, str): # Handle if it's unexpectedly a string
                assignee_str = assignees_list
            
            # Constructing URL to Google Patents (PatentsView doesn't directly provide this)
            patent_id = patent_data_item.get("patent_number")
            google_patent_url = f"https://patents.google.com/patent/{patent_id}/en" if patent_id else None

            result = PatentSearchResult(
                patent_id=patent_id,
                title=patent_data_item.get("patent_title"),
                abstract=patent_data_item.get("patent_abstract"),
                publication_date=patent_data_item.get("patent_date"),
                assignee=assignee_str,
                relevance_score=1.0, # Default score as API doesn't rank general queries
                patent_url=google_patent_url
            )
            results.append(result)
            # max_results is handled by "per_page" in API query options, so no need to break early here
            # unless we want to limit further than what API returned in one page.
        
        print(f"Found {data.get('total_patent_count', 0)} total patents. Returning up to {len(results)} results from this page.")

    except requests.exceptions.Timeout:
        print(f"API request timed out after 20 seconds.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status: {http_err.response.status_code if http_err.response else 'N/A'}")
        if http_err.response is not None:
             print(f"Response body: {http_err.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error calling PatentsView API: {e}")
    except json.JSONDecodeError:
        # response might not be defined if error occurred before request was made (e.g. DNS failure)
        resp_text = response.text if 'response' in locals() and hasattr(response, 'text') else 'Unknown response text'
        print(f"Error decoding JSON response from API. Response text: {resp_text}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        # import traceback # Uncomment for debugging if needed
        # traceback.print_exc()

    return results
