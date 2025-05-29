import unittest
import sys
import os

# Adjust path for imports
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from patent_agent.src.writing_module.api import generate_patent_section, summarize_patent, PatentDraftSection, MOCK_PATENT_DATABASE

class TestWritingModule(unittest.TestCase):

    def test_generate_patent_section_abstract(self):
        prompt = "generate abstract about AI drug discovery"
        result = generate_patent_section(prompt)
        self.assertIsInstance(result, PatentDraftSection)
        self.assertEqual(result.section_title, "Abstract")
        self.assertIn("AI drug discovery", result.content) # Check if keywords are used
        self.assertGreater(result.confidence_score, 0.2)

    def test_generate_patent_section_background(self):
        prompt = "generate background for synthetic biology"
        result = generate_patent_section(prompt)
        self.assertEqual(result.section_title, "Background of the Invention")
        self.assertIn("synthetic biology", result.content)

    def test_generate_patent_section_summary(self):
        prompt = "write a brief summary of a patent on biodegradable plastics"
        result = generate_patent_section(prompt)
        self.assertEqual(result.section_title, "Summary of the Invention")
        self.assertIn("biodegradable plastics", result.content)

    def test_generate_patent_section_claims_no_existing(self):
        prompt = "generate claims for a new type of solar panel"
        result = generate_patent_section(prompt)
        self.assertEqual(result.section_title, "Claims")
        self.assertIn("solar panel", result.content)
        self.assertIn("1. A", result.content) # Check for basic claim structure

    def test_generate_patent_section_claims_with_existing(self):
        prompt = "generate claims for enhanced battery, further comprising a new electrode"
        existing_claims = ["1. A battery system comprising an anode and a cathode."]
        result = generate_patent_section(prompt, existing_claims=existing_claims)
        self.assertEqual(result.section_title, "Claims")
        self.assertIn("2. The battery system of claim 1", result.content) # Corrected expected claim number and dependency text
        self.assertIn("new electrode", result.content.lower())

    def test_generate_patent_section_unknown(self):
        prompt = "tell me about nanotechnology" # Not a specific section generation
        result = generate_patent_section(prompt)
        self.assertEqual(result.section_title, "General Section")
        self.assertIn("nanotechnology", result.content)


    def test_summarize_patent_found_long_abstract(self):
        # US20230000001A1 abstract is longer than 50 chars for test
        summary = summarize_patent("US20230000001A1", target_length=50)
        self.assertTrue(len(summary) <= 50 + 3) # 3 for "..."
        self.assertTrue(summary.endswith("..."))
        # Check if some keywords from original abstract are present
        original_abstract_keywords = MOCK_PATENT_DATABASE["US20230000001A1"]["abstract"].lower().split()
        summary_keywords = summary.lower().split()
        # Ensure at least one non-trivial word from original abstract is in summary
        self.assertTrue(any(word in summary_keywords for word in original_abstract_keywords if len(word) > 3))


    def test_summarize_patent_found_short_abstract(self):
        # Add a mock patent with short abstract if needed, or use one if it exists
        # For now, let's assume US20220000001A1's abstract is short enough if target_length is large
        short_abstract = MOCK_PATENT_DATABASE["US20220000001A1"]["abstract"]
        summary = summarize_patent("US20220000001A1", target_length=len(short_abstract) + 10)
        self.assertEqual(summary, short_abstract) # No "..."
        self.assertFalse(summary.endswith("..."))

    def test_summarize_patent_not_found(self):
        summary = summarize_patent("NOT_AN_ID")
        self.assertIn("not found", summary)
        
    def test_summarize_patent_empty_abstract(self):
        # Temporarily add a mock patent with an empty abstract for this test
        original_patent_data = MOCK_PATENT_DATABASE.get("TEMP_EMPTY_ID")
        MOCK_PATENT_DATABASE["TEMP_EMPTY_ID"] = {"patent_id": "TEMP_EMPTY_ID", "title": "Test Empty", "abstract": " "}
        summary = summarize_patent("TEMP_EMPTY_ID", target_length=50)
        self.assertEqual(summary, "No abstract content available to summarize.")
        # Clean up: remove or restore if it was modified
        if original_patent_data is None: # if it did not exist before
            if "TEMP_EMPTY_ID" in MOCK_PATENT_DATABASE: # Ensure it was added before trying to delete
                 del MOCK_PATENT_DATABASE["TEMP_EMPTY_ID"]
        else: # If it somehow existed, restore it
             MOCK_PATENT_DATABASE["TEMP_EMPTY_ID"] = original_patent_data


if __name__ == '__main__':
    unittest.main()
