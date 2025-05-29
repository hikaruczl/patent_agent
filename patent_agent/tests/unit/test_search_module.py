import unittest
import sys
import os

# Adjust path to import from the project's src directory
# Assuming this test script is in patent_agent/tests/unit/
# We want to add the directory containing 'patent_agent' to sys.path
# current_dir = os.path.dirname(os.path.abspath(__file__)) # patent_agent/tests/unit
# project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir))) # Directory containing patent_agent
# sys.path.insert(0, project_root_dir)
# This setup allows 'from patent_agent.src...' imports

# A more robust way if tests are run with `python -m unittest discover` from the project root:
# The project root (containing the 'patent_agent' directory) should be in PYTHONPATH or be the CWD.
# Then, imports like `from patent_agent.src.search_module...` should work.

try:
    from patent_agent.src.search_module import search_patents, PatentSearchResult
except ImportError:
    # Fallback for simpler execution environments or if the above isn't set up
    # This adds the 'patent_agent' directory itself to the path, to allow 'from src...'
    # This is a bit fragile and depends on CWD.
    # Example: if CWD is 'patent_agent_project' which contains 'patent_agent' directory
    # Then sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) might work
    # For now, assuming PYTHONPATH or similar is configured for test discovery.
    # Worker should handle this.
    # Let's add a more direct path adjustment for the worker if it runs the script directly.
    # This assumes the script is at patent_agent/tests/unit/test_search_module.py
    # We need to go up three levels to get to the directory containing 'patent_agent'
    # then add 'patent_agent' to the path, or just add the root 'patent_agent' to path to use 'from src...'.
    
    # Get the absolute path to the 'patent_agent' directory
    # current_script_path = os.path.abspath(__file__) # .../patent_agent/tests/unit/test_search_module.py
    # unit_tests_dir = os.path.dirname(current_script_path) # .../patent_agent/tests/unit
    # tests_dir = os.path.dirname(unit_tests_dir) # .../patent_agent/tests
    # src_dir_level = os.path.dirname(tests_dir) # .../patent_agent
    # project_root = os.path.dirname(src_dir_level) # .../ (directory containing patent_agent)
    
    # If 'patent_agent' is the root of the project for Python's perspective:
    patent_agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'patent_agent'))
    # This path is if the tests are run from within the 'tests/unit' directory.
    # A more common setup is to run tests from the root directory of the 'patent_agent' package.
    # sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) # Adds 'patent_agent' to path
    
    # Let's assume the structure is:
    # repo_root/
    #   patent_agent/  <-- This is a package
    #     src/
    #     tests/
    # If running `python -m unittest discover` from `repo_root`, then imports should work.
    # If the worker needs explicit path, this is one way:
    # This adds the directory containing 'patent_agent' to sys.path
    # This should be the 'repo_root' if the structure is repo_root/patent_agent
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))) 
    from patent_agent.src.search_module import search_patents, PatentSearchResult


class TestSearchModule(unittest.TestCase):

    def test_search_patents_no_query(self):
        results = search_patents(query="")
        self.assertEqual(len(results), 3)
        expected_ids = ["US20230000001A1", "US20230000002A1", "CN100000000A"]
        returned_ids = [result.patent_id for result in results]
        self.assertCountEqual(returned_ids, expected_ids) # Use assertCountEqual for lists where order doesn't matter

    def test_search_patents_with_query_found(self):
        # Test for "Quantum"
        results_quantum = search_patents(query="Quantum")
        self.assertEqual(len(results_quantum), 1)
        self.assertIn("Quantum Computing Method", results_quantum[0].title)
        self.assertEqual(results_quantum[0].patent_id, "US20230000001A1")

        # Test for "AI-Powered" (in title)
        results_ai_title = search_patents(query="AI-Powered")
        self.assertEqual(len(results_ai_title), 1)
        self.assertIn("AI-Powered Drug Discovery Platform", results_ai_title[0].title)
        self.assertEqual(results_ai_title[0].patent_id, "US20230000002A1")
        
        # Test for "therapeutic" (in title of another patent)
        results_therapeutic = search_patents(query="therapeutic")
        self.assertEqual(len(results_therapeutic), 1)
        self.assertIn("Method for preparing a therapeutic composition", results_therapeutic[0].title)
        self.assertEqual(results_therapeutic[0].patent_id, "CN100000000A")

        # Test for "method" (in abstract or title of multiple patents)
        # "Novel Quantum Computing Method"
        # "AI-Powered Drug Discovery Platform" -> abstract: "Utilizing machine learning to accelerate the identification of potential drug candidates."
        # "Method for preparing a therapeutic composition" -> abstract: "The invention discloses a method for preparing a therapeutic composition..."
        # The current search_patents implementation searches title OR abstract.
        # "Novel Quantum Computing Method" (title)
        # "Method for preparing a therapeutic composition" (title + abstract)
        results_method = search_patents(query="method")
        # Based on the mock data:
        # 1. "Novel Quantum Computing Method" (title contains "Method")
        # 2. "AI-Powered Drug Discovery Platform" (abstract does not contain "method")
        # 3. "Method for preparing a therapeutic composition" (title and abstract contain "method")
        # So, two results are expected.
        self.assertEqual(len(results_method), 2) 
        ids_method = [result.patent_id for result in results_method]
        self.assertIn("US20230000001A1", ids_method) # For "Novel Quantum Computing Method"
        self.assertIn("CN100000000A", ids_method)  # For "Method for preparing a therapeutic composition"


    def test_search_patents_with_query_not_found(self):
        results = search_patents(query="NonExistentTerm123XYZ")
        self.assertEqual(len(results), 0)

    def test_search_patents_case_insensitivity(self):
        results_lower = search_patents(query="quantum") # Lowercase
        self.assertEqual(len(results_lower), 1)
        self.assertIn("Quantum Computing Method", results_lower[0].title)

        results_upper = search_patents(query="METHOD") # Uppercase
        # This should also find 2 results, same as "method" due to case-insensitivity
        self.assertEqual(len(results_upper), 2)


    # The mock search_patents currently only filters by query text, not by structured filters.
    # This test reflects that; if filter logic were added, this test would need to change.
    def test_search_patents_filters_currently_ignored_by_mock(self):
        results = search_patents(query="Quantum", filters={"assignee": "SomeCorp", "publication_date_from": "2023-01-01"})
        self.assertEqual(len(results), 1) # Still finds the "Quantum" patent
        self.assertIn("Quantum Computing Method", results[0].title)
        # This test just confirms current mock behavior. Real implementation would use filters.

if __name__ == '__main__':
    unittest.main()
