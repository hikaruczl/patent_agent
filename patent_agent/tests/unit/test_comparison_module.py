import unittest
import sys
import os

# Adjust path for imports - assuming tests are run from project root or PYTHONPATH is set
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
# from patent_agent.src.comparison_module import compare_patents, compare_patent_with_text, PatentComparisonResult
# The worker should ensure that the path is set up correctly for the below imports to work.
from patent_agent.src.comparison_module.api import compare_patents, compare_patent_with_text, PatentComparisonResult, MOCK_PATENT_DATABASE

class TestComparisonModule(unittest.TestCase):

    def test_compare_patents_found_similar(self):
        # US20230000001A1 (Quantum Computing) vs US20220000001A1 (Advanced Cooling) - Same Assignee
        result = compare_patents("US20230000001A1", "US20220000001A1")
        self.assertIsInstance(result, PatentComparisonResult)
        self.assertEqual(result.patent_a_id, "US20230000001A1")
        self.assertEqual(result.patent_b_id, "US20220000001A1")
        self.assertTrue(any("Same assignee: Tech Innovations Inc." in s for s in result.similarities))
        self.assertTrue(result.overall_similarity_score > 0) # Expect some similarity
        self.assertTrue(any("Common abstract keywords: cooling" in s for s in result.similarities))

    def test_compare_patents_found_different_assignee(self):
        # US20230000001A1 (Tech Innovations Inc.) vs US20230000002A1 (Pharma Solutions LLC)
        result = compare_patents("US20230000001A1", "US20230000002A1")
        self.assertIsInstance(result, PatentComparisonResult)
        self.assertTrue(any("Different assignees" in d for d in result.differences))
        # Check if score reflects no assignee bonus (or less score than same assignee)
        # This depends on the exact scoring logic, which might need refinement for robust testing here.

    def test_compare_patents_one_not_found(self):
        result = compare_patents("US20230000001A1", "NOT_AN_ID")
        self.assertIsInstance(result, PatentComparisonResult)
        self.assertEqual(result.overall_similarity_score, 0.0)
        self.assertTrue(any("Patent ID NOT_AN_ID not found" in s for s in result.similarities))

    def test_compare_patents_both_not_found(self):
        result = compare_patents("NOT_AN_ID_1", "NOT_AN_ID_2")
        self.assertIsInstance(result, PatentComparisonResult)
        self.assertEqual(result.overall_similarity_score, 0.0)
        self.assertTrue(any("Patent ID NOT_AN_ID_1 not found" in s for s in result.similarities))
        self.assertTrue(any("Patent ID NOT_AN_ID_2 not found" in s for s in result.similarities))
        
    def test_compare_patent_with_text_found(self):
        text = "This is a test about quantum computing and advanced cooling methods."
        result = compare_patent_with_text("US20230000001A1", text)
        self.assertIsInstance(result, PatentComparisonResult)
        self.assertEqual(result.patent_a_id, "US20230000001A1")
        self.assertEqual(result.patent_b_id, "CustomText")
        self.assertTrue(result.overall_similarity_score > 0)
        self.assertTrue(any("Common keywords with text: quantum, computing, cooling" in s for s in result.similarities) or \
                        any("Common keywords with text: computing, quantum, cooling" in s for s in result.similarities) or \
                        any("Common keywords with text: cooling, quantum, computing" in s for s in result.similarities) or \
                        any("Common keywords with text: quantum, cooling, computing" in s for s in result.similarities) or \
                        any("Common keywords with text: computing, cooling, quantum" in s for s in result.similarities) or \
                        any("Common keywords with text: cooling, computing, quantum" in s for s in result.similarities) )


    def test_compare_patent_with_text_not_found(self):
        text = "Some random text."
        result = compare_patent_with_text("NOT_AN_ID", text)
        self.assertIsInstance(result, PatentComparisonResult)
        self.assertEqual(result.overall_similarity_score, 0.0)
        self.assertTrue(any("Patent ID NOT_AN_ID not found" in s for s in result.similarities))

    # Add new test methods within the existing TestComparisonModule class:
    def test_compare_patents_claim_comparison_details(self):
        # US20230000001A1 (2 claims) vs US20220000001A1 (3 claims)
        result = compare_patents("US20230000001A1", "US20220000001A1")
        self.assertEqual(result.claim_comparison.get("patent_a_num_claims"), 2)
        self.assertEqual(result.claim_comparison.get("patent_b_num_claims"), 3)
        self.assertTrue(any("Different number of claims (A: 2, B: 3)" in d for d in result.differences))
        
        # Based on mock data: US20230000001A1 claims: "...cooling cycle...", "...phase change materials."
        # US20220000001A1 claims: "...heat sink...", "...fan...", "...thermoelectric cooler...phase change materials."
        # Common claim keywords could include "phase", "change", "materials" (if not stopwords)
        # The _get_words_from_text helper needs to be considered. "cooling" is in abstract, not claim of US20220000001A1.
        # "materials" and "phase" seem likely common based on mock data.
        self.assertIn("materials", result.claim_comparison.get("common_claim_keywords", []))
        self.assertIn("phase", result.claim_comparison.get("common_claim_keywords", []))
        self.assertTrue(any("Common claim keywords" in s for s in result.similarities))


    def test_compare_patents_ipc_comparison_details(self):
        # US20230000001A1 (G06N 10/00, H01L 39/00) vs US20220000001A1 (H01L 23/367, G06F 1/20)
        result = compare_patents("US20230000001A1", "US20220000001A1")
        self.assertCountEqual(result.ipc_comparison.get("patent_a_ipc", []), ["G06N 10/00", "H01L 39/00"])
        self.assertCountEqual(result.ipc_comparison.get("patent_b_ipc", []), ["H01L 23/367", "G06F 1/20"])
        self.assertEqual(result.ipc_comparison.get("common_ipc_codes", []), [])
        self.assertTrue(any("No common IPC codes found" in d for d in result.differences))

        # Test common main IPC groups
        # US20230000001A1 has main groups G06N, H01L.
        # US20230000002A1 has main groups G16H, G06N.
        # Common main group should be G06N.
        result_common_main_group = compare_patents("US20230000001A1", "US20230000002A1")
        self.assertIn("G06N", result_common_main_group.ipc_comparison.get("common_main_ipc_groups", []))
        self.assertTrue(any("Common main IPC groups: G06N" in s for s in result_common_main_group.similarities))
        # Check if score reflects this (simple check, assumes bonus is > 0)
        # This requires knowing a baseline score without this specific commonality.
        # For now, primarily test population of fields.

    def test_compare_patents_new_fields_populated(self):
        result = compare_patents("US20230000001A1", "US20230000002A1")
        self.assertIsNotNone(result.claim_comparison)
        self.assertIn("patent_a_num_claims", result.claim_comparison)
        self.assertIn("patent_b_num_claims", result.claim_comparison)
        self.assertIn("common_claim_keywords", result.claim_comparison)
        
        self.assertIsNotNone(result.ipc_comparison)
        self.assertIn("patent_a_ipc", result.ipc_comparison)
        self.assertIn("patent_b_ipc", result.ipc_comparison)
        self.assertIn("common_ipc_codes", result.ipc_comparison)
        self.assertIn("common_main_ipc_groups", result.ipc_comparison)

if __name__ == '__main__':
    unittest.main()
