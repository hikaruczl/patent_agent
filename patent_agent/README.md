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
*   **`src/search_module/`**: Responsible for handling patent searches. It interfaces with patent databases (currently mock, to be integrated with actual APIs).
*   **`src/comparison_module/`**: (Future) Will contain tools for comparing patent documents.
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
3.  Currently, there are no external dependencies to install for the basic mock functionality. If dependencies are added later, they will be listed in a `requirements.txt` file.

### Running the Command-Line Interface (CLI)

The CLI allows you to interact with the patent agent for searching patents.

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

## Contributing
(Future) Details on how to contribute to the project will be added here.

## License
(Future) Specify project license (e.g., MIT, Apache 2.0).
