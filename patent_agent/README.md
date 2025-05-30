# Patent Agent Project

This project is developing an intelligent agent designed to streamline and assist with a variety of patent-related tasks. The goal is to provide users with tools for effective patent searching, in-depth comparison of patent documents, and assistance in drafting new patent applications.

## Project Goals

*   **Patent Search**: Allow users to search for existing patents using keywords, patent numbers, classifications, etc.
*   **Patent Comparison**: Provide tools to compare two or more patents, highlighting similarities and differences in claims, specifications, and drawings.
*   **Patent Writing Assistance**: Offer AI-powered assistance for drafting various sections of a patent application, such as claims, abstract, and detailed description.
*   **Intelligent Query Handling**: Develop a core agent logic that can understand user queries and delegate tasks to the appropriate modules.

## Architecture Overview

The project is structured into several key modules:

*   **`src/agent_core/`**: Contains the central logic for the agent. It processes user queries and coordinates tasks between other modules.
*   **`src/search_module/`**: Responsible for handling patent searches. It now interfaces with the live PatentsView API to fetch real-time patent data.
*   **`src/comparison_module/`**: (Future) Will contain tools for comparing patent documents. Currently implements mock data comparison of abstracts, assignees, claims structure, and IPC codes.
*   **`src/writing_module/`**: (Future) Will house functionalities for AI-assisted patent drafting.
*   **`src/ui/`**: Provides user interfaces for interacting with the agent. Currently, a Command-Line Interface (CLI) is available.
*   **`config/`**: (Future) For project configuration files (e.g., API keys, database settings).
*   **`data/`**: (Future) For storing local data, cached results, etc.
*   **`docs/`**: For detailed documentation.
*   **`tests/`**: Contains unit and integration tests for the project.

## Getting Started

### Prerequisites

*   Python 3.8+

### Setup

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2.  (Optional) Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install dependencies:
    The project now uses external libraries listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
4. Configure API Keys (Optional):
   The project uses a configuration file to manage API keys. To set up your API keys:
   a. Navigate to the `patent_agent/config/` directory.
   b. Copy the template file `settings.ini.template` to a new file named `settings.ini`.
      ```bash
      cp settings.ini.template settings.ini
      ```
   c. Edit `settings.ini` with your actual API key(s) if you have them. For the PatentsView API, a key is optional for basic public access but recommended for higher query rates.

   **Important**: The `settings.ini` file is included in `.gitignore` and should not be committed to version control as it may contain sensitive information.

### Running the Command-Line Interface (CLI)

The CLI allows you to interact with the patent agent for searching, comparing patents, generating patent document sections, and summarizing patents.

### Available Commands

*   `search <query_terms>`: Searches for patents using the PatentsView API based on the provided query terms.
    *   Example: `search AI in medical diagnosis`
*   `compare <patent_id_1> <patent_id_2>`: Compares two patents using their IDs (currently uses internal mock data for demonstration). The comparison analyzes:
    *   Common keywords in abstracts.
    *   Assignee information.
    *   Number of claims and common keywords in claims.
    *   Common International Patent Classification (IPC) codes and main groups.
    *   Example: `compare US20230000001A1 CN100000000A`
*   `compare_text <patent_id> <text_to_compare>`: Compares a patent (from mock data) with arbitrary text.
    *   Example: `compare_text US20230000001A1 This text describes a novel cooling system.`
*   `generate <section_type> about <topic_keywords>`: Generates a boilerplate section for a patent document.
    *   Supported section types: `abstract`, `background`, `summary`, `claims`.
    *   Example: `generate abstract about advanced battery technology`
*   `summarize <patent_id>`: Summarizes the abstract of a patent (uses internal mock data).
    *   Example: `summarize US20230000001A1`
*   `exit`: Quits the CLI.

To run the CLI:
Navigate to the root directory of the `patent_agent` project (the one containing the `src` directory, not the outer repo root if they are different). Then execute:

```bash
python -m src.ui.cli
```
Alternatively, from the `patent_agent/src/ui/` directory:
```bash
python cli.py 
```
*(Note: Running `cli.py` directly might require `PYTHONPATH` adjustments if not run as part of a module. The `python -m src.ui.cli` command from the `patent_agent` directory is generally more robust for package structures.)*

You will be prompted to enter your search queries. Type `exit` to quit the CLI.

### Running Unit Tests

Unit tests are implemented using Python's `unittest` module.

To run all unit tests:
Navigate to the root directory of the `patent_agent` project. Then execute:

```bash
python -m unittest discover tests
```
Or, to run a specific test file:
```bash
python -m unittest tests.unit.test_search_module
```

## API Usage and Configuration

### PatentsView API
The patent search functionality currently uses the public PatentsView API. This API is generally accessible without an API key for basic use. If you have an API key for PatentsView (e.g., for higher rate limits), you can add it to the `config/settings.ini` file.

### Configuration File (`config/settings.ini`)
API keys and other sensitive configurations are managed through a configuration file located at `patent_agent/config/settings.ini`.

To set up your configuration:
1.  Go to the `patent_agent/config/` directory.
2.  Copy `settings.ini.template` to `settings.ini`.
3.  Open `settings.ini` in a text editor.
4.  Under the `[API_KEYS]` section, replace `your_api_key_here` with your actual API key for the respective service (e.g., `PATENTSVIEW_API_KEY`).
    ```ini
    [API_KEYS]
    PATENTSVIEW_API_KEY = your_actual_key_here_if_you_have_one
    ```
5.  Save the file. The application will automatically try to load the keys from this file. If a key is not found or the file doesn't exist, functionalities requiring that key might be limited or use public access modes if available.

The `settings.ini` file is ignored by Git (see `.gitignore`) to prevent accidental sharing of sensitive keys. Always ensure this file is kept private.

## Contributing
(Future) Details on how to contribute to the project will be added here.

## License
(Future) Specify project license (e.g., MIT, Apache 2.0).
