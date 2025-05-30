import configparser
import os

# Determine the path to the config file relative to this script's location
# config_loader.py is in patent_agent/config/
# settings.ini will be in patent_agent/config/
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, 'settings.ini')

# Fallback for testing or if script is run from a different context
# This assumes 'patent_agent' is the root package directory in PYTHONPATH or CWD.
if not os.path.exists(CONFIG_FILE_PATH) and "patent_agent" in CONFIG_DIR:
    # Try path relative to 'patent_agent' directory if found in path
    try:
        import patent_agent
        package_root = os.path.dirname(patent_agent.__file__)
        CONFIG_FILE_PATH = os.path.join(package_root, 'config', 'settings.ini')
    except ImportError:
        pass # Keep original path if patent_agent package not found this way

# Ensure the path is absolute if it's still relative for some reason.
if not os.path.isabs(CONFIG_FILE_PATH):
    # This might happen if patent_agent package resolution above fails and CONFIG_DIR was relative.
    # This is a failsafe.
    CONFIG_FILE_PATH = os.path.abspath(os.path.join(os.getcwd(), 'config', 'settings.ini'))


def get_api_key(service_name: str) -> str | None:
    '''
    Reads an API key from the settings.ini file.
    Args:
        service_name: The name of the API key in the config file (e.g., PATENTSVIEW_API_KEY).
    Returns:
        The API key string if found, otherwise None.
    '''
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Check if the config file exists
    if not os.path.exists(CONFIG_FILE_PATH):
        # print(f"DEBUG: Config file not found at {CONFIG_FILE_PATH}")
        # Try to locate settings.ini.template to guide user
        template_path = CONFIG_FILE_PATH + ".template"
        if os.path.exists(template_path):
            print(f"INFO: Configuration file '{os.path.basename(CONFIG_FILE_PATH)}' not found in '{os.path.dirname(CONFIG_FILE_PATH)}'.")
            print(f"Please create it by copying the template '{os.path.basename(template_path)}' and filling in your API key if needed.")
        else:
            print(f"WARNING: Configuration file '{CONFIG_FILE_PATH}' not found, and no template available at that path.")
        return None
    
    try:
        config.read(CONFIG_FILE_PATH)
        api_key = config.get('API_KEYS', service_name, fallback=None)
        if api_key == 'your_api_key_here' or not api_key: # Check for placeholder or empty
            # print(f"DEBUG: API key for {service_name} is placeholder or empty in {CONFIG_FILE_PATH}.")
            return None
        # print(f"DEBUG: Loaded API key for {service_name}.")
        return api_key
    except configparser.Error as e:
        print(f"Error reading config file {CONFIG_FILE_PATH}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading config for {service_name}: {e}")
        return None

# Example usage (optional, for testing this script directly)
if __name__ == '__main__':
    print(f"Attempting to load config from: {CONFIG_FILE_PATH}")
    pv_key = get_api_key('PATENTSVIEW_API_KEY')
    if pv_key:
        print(f"PatentsView API Key: {pv_key}")
    else:
        print("PatentsView API Key not found or not set.")
