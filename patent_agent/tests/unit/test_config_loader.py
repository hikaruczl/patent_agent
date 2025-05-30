# patent_agent/tests/unit/test_config_loader.py
import unittest
from unittest.mock import patch, mock_open, MagicMock
import os

# Adjust path for import - Worker should ensure this works
# This assumes that the tests are run from a context where 'patent_agent' package is discoverable
from patent_agent.config.config_loader import get_api_key, CONFIG_FILE_PATH

class TestConfigLoader(unittest.TestCase):

    @patch('patent_agent.config.config_loader.os.path.exists')
    def test_get_api_key_file_not_exists(self, mock_exists):
        mock_exists.return_value = False
        # Mock the os.path.exists for the template file as well if it's checked
        with patch('builtins.print') as mock_print: # Suppress print statements during test
            self.assertIsNone(get_api_key('PATENTSVIEW_API_KEY'))
        # Check if it tried the correct file path for existence
        mock_exists.assert_any_call(CONFIG_FILE_PATH)


    @patch('patent_agent.config.config_loader.os.path.exists')
    @patch('patent_agent.config.config_loader.configparser.ConfigParser')
    def test_get_api_key_found(self, mock_config_parser, mock_exists):
        mock_exists.return_value = True
        mock_parser_instance = MagicMock()
        # Simulating the behavior of configparser's get method
        def get_side_effect(section, key, fallback=None):
            if section == 'API_KEYS' and key == 'PATENTSVIEW_API_KEY':
                return 'test_key_123'
            return fallback
        mock_parser_instance.get = MagicMock(side_effect=get_side_effect)
        mock_config_parser.return_value = mock_parser_instance
        
        self.assertEqual(get_api_key('PATENTSVIEW_API_KEY'), 'test_key_123')
        mock_parser_instance.read.assert_called_with(CONFIG_FILE_PATH)
        mock_parser_instance.get.assert_called_with('API_KEYS', 'PATENTSVIEW_API_KEY', fallback=None)

    @patch('patent_agent.config.config_loader.os.path.exists')
    @patch('patent_agent.config.config_loader.configparser.ConfigParser')
    def test_get_api_key_not_found_in_file(self, mock_config_parser, mock_exists):
        mock_exists.return_value = True
        mock_parser_instance = MagicMock()
        mock_parser_instance.get.return_value = None # Simulate key not present
        mock_config_parser.return_value = mock_parser_instance

        self.assertIsNone(get_api_key('NON_EXISTENT_KEY'))
        mock_parser_instance.get.assert_called_with('API_KEYS', 'NON_EXISTENT_KEY', fallback=None)

    @patch('patent_agent.config.config_loader.os.path.exists')
    @patch('patent_agent.config.config_loader.configparser.ConfigParser')
    def test_get_api_key_is_placeholder(self, mock_config_parser, mock_exists):
        mock_exists.return_value = True
        mock_parser_instance = MagicMock()
        # Simulating the behavior of configparser's get method
        def get_side_effect(section, key, fallback=None):
            if section == 'API_KEYS' and key == 'PATENTSVIEW_API_KEY':
                return 'your_api_key_here'
            return fallback
        mock_parser_instance.get = MagicMock(side_effect=get_side_effect)
        mock_config_parser.return_value = mock_parser_instance

        self.assertIsNone(get_api_key('PATENTSVIEW_API_KEY'))

    @patch('patent_agent.config.config_loader.os.path.exists')
    @patch('patent_agent.config.config_loader.configparser.ConfigParser')
    def test_get_api_key_config_parser_error_on_read(self, mock_config_parser, mock_exists):
        mock_exists.return_value = True
        mock_parser_instance = MagicMock()
        mock_parser_instance.read.side_effect = Exception("Fake parsing error") # Simulate error during read
        mock_config_parser.return_value = mock_parser_instance
        
        with patch('builtins.print') as mock_print:
            self.assertIsNone(get_api_key('PATENTSVIEW_API_KEY'))
            self.assertTrue(any("Error reading config file" in call.args[0] for call in mock_print.call_args_list if call.args))

    @patch('patent_agent.config.config_loader.os.path.exists')
    @patch('patent_agent.config.config_loader.configparser.ConfigParser')
    def test_get_api_key_unexpected_error(self, mock_config_parser, mock_exists):
        mock_exists.return_value = True
        mock_parser_instance = MagicMock()
        # Simulate an error other than configparser.Error during .get()
        mock_parser_instance.get.side_effect = Exception("Unexpected problem")
        mock_config_parser.return_value = mock_parser_instance

        with patch('builtins.print') as mock_print:
            self.assertIsNone(get_api_key('PATENTSVIEW_API_KEY'))
            self.assertTrue(any("An unexpected error occurred" in call.args[0] for call in mock_print.call_args_list if call.args))

if __name__ == '__main__':
    unittest.main()
