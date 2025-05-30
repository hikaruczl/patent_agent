import unittest
from unittest.mock import patch, MagicMock # Ensure MagicMock is imported
import sys
import os

# Adjust path for imports
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from patent_agent.src.agent_core import process_command
# Import result types for type checking if needed, though mocks will be primary
from patent_agent.src.search_module import PatentSearchResult
from patent_agent.src.comparison_module import PatentComparisonResult
from patent_agent.src.writing_module import PatentDraftSection


class TestAgentCore(unittest.TestCase):

    @patch('patent_agent.src.agent_core.core.search_patents')
    def test_process_command_search_valid(self, mock_search_patents):
        mock_search_patents.return_value = [PatentSearchResult(patent_id="123", title="Test")]
        result = process_command("search AI ethics")
        mock_search_patents.assert_called_once_with(query="AI ethics", filters=None)
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], PatentSearchResult)

    def test_process_command_search_invalid(self):
        result = process_command("search") # No query
        self.assertIsInstance(result, str)
        self.assertIn("requires query terms", result)

    @patch('patent_agent.src.agent_core.core.compare_patents')
    def test_process_command_compare_valid(self, mock_compare_patents):
        mock_compare_patents.return_value = PatentComparisonResult("id1", "id2", [], [], 0.5)
        result = process_command("compare US123 CN456")
        mock_compare_patents.assert_called_once_with(patent_id_a="US123", patent_id_b="CN456")
        self.assertIsInstance(result, PatentComparisonResult)

    def test_process_command_compare_invalid(self):
        result = process_command("compare US123") # Needs two IDs
        self.assertIsInstance(result, str)
        self.assertIn("requires two patent IDs", result)

    @patch('patent_agent.src.agent_core.core.compare_patent_with_text')
    def test_process_command_compare_text_valid(self, mock_compare_text):
        mock_compare_text.return_value = PatentComparisonResult("id1", "CustomText", [], [], 0.3)
        result = process_command("compare_text US123 some example text here")
        mock_compare_text.assert_called_once_with(patent_id="US123", text_to_compare="some example text here")
        self.assertIsInstance(result, PatentComparisonResult)

    def test_process_command_compare_text_invalid(self):
        result = process_command("compare_text US123") # Needs text
        self.assertIsInstance(result, str)
        self.assertIn("requires a patent ID and text", result)

    @patch('patent_agent.src.agent_core.core.generate_patent_section')
    def test_process_command_generate_valid(self, mock_generate_section):
        mock_generate_section.return_value = PatentDraftSection("Abstract", "Content", 0.5)
        result = process_command("generate abstract about machine learning")
        mock_generate_section.assert_called_once_with(prompt="generate abstract about machine learning", existing_claims=None)
        self.assertIsInstance(result, PatentDraftSection)

    def test_process_command_generate_invalid_format(self):
        result = process_command("generate abstract machine learning") # Missing "about"
        self.assertIsInstance(result, str)
        self.assertIn("generate <section_type> about <topic_keywords>", result)
        
    def test_process_command_generate_missing_topic(self):
        result = process_command("generate abstract about") # Missing topic
        self.assertIsInstance(result, str)
        self.assertIn("generate <section_type> about <topic_keywords>", result)


    @patch('patent_agent.src.agent_core.core.summarize_patent')
    def test_process_command_summarize_valid(self, mock_summarize_patent):
        mock_summarize_patent.return_value = "This is a summary."
        result = process_command("summarize US123")
        mock_summarize_patent.assert_called_once_with(patent_id="US123")
        self.assertEqual(result, "This is a summary.")

    def test_process_command_summarize_invalid(self):
        result = process_command("summarize") # No ID
        self.assertIsInstance(result, str)
        self.assertIn("requires one patent ID", result)
        
    def test_process_command_unknown(self):
        result = process_command("invent a new gadget")
        self.assertIsInstance(result, str)
        self.assertIn("Unknown command: 'invent'", result)

    def test_process_command_no_command(self):
        result = process_command("    ") # Empty or whitespace
        self.assertIsInstance(result, str)
        self.assertIn("No command entered", result)

    # Add new test methods within the existing TestAgentCore class:
    def test_process_command_search_empty_query_terms(self):
        result = process_command("search      ") # Query terms are whitespace
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Error: Search query terms cannot be empty."))

    def test_process_command_compare_text_empty_text(self):
        result = process_command("compare_text US123   ") # Text for comparison is whitespace
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Error: Text for comparison cannot be empty."))

    def test_process_command_generate_invalid_section_type(self):
        result = process_command("generate invention_details about AI")
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Error: Unsupported section type 'invention_details'."))
        self.assertIn("Supported types are: abstract, background, summary, claims", result)

    def test_process_command_generate_empty_topic(self):
        result = process_command("generate abstract about    ")
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Error: Topic keywords for generation cannot be empty."))

    # Add tests for correct error messages for other commands too if not covered by existing tests
    def test_process_command_search_no_args(self): # This is same as test_process_command_search_invalid
        result = process_command("search")
        self.assertTrue(result.startswith("Error: Search command requires query terms."))

    def test_process_command_compare_not_enough_args(self): # This is same as test_process_command_compare_invalid
        result = process_command("compare id1")
        self.assertTrue(result.startswith("Error: Compare command requires exactly two patent IDs."))
    
    def test_process_command_compare_too_many_args(self): # Assuming it takes exactly two
        result = process_command("compare id1 id2 id3")
        self.assertTrue(result.startswith("Error: Compare command requires exactly two patent IDs."))

    def test_process_command_compare_text_no_text(self): # This is same as test_process_command_compare_text_invalid
        result = process_command("compare_text id1")
        self.assertTrue(result.startswith("Error: Compare_text command requires a patent ID and text."))

    def test_process_command_generate_malformed(self): # This is same as test_process_command_generate_invalid_format
        result = process_command("generate abstract AI") # Missing "about"
        self.assertTrue(result.startswith("Error: Generate command format is"))
    
    def test_process_command_summarize_no_id(self): # This is same as test_process_command_summarize_invalid
        result = process_command("summarize")
        self.assertTrue(result.startswith("Error: Summarize command requires exactly one patent ID."))

    def test_process_command_summarize_too_many_ids(self):
        result = process_command("summarize id1 id2")
        self.assertTrue(result.startswith("Error: Summarize command requires exactly one patent ID."))

if __name__ == '__main__':
    unittest.main()
