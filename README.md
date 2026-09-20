# LLM & Agent Security Playground

This project is a hands-on learning environment designed to demonstrate common security vulnerabilities in applications that use Large Language Models (LLMs) and AI agents. It provides a FastAPI backend with a Gemini-powered agent that has several "tools" it can use, some of which are intentionally vulnerable.

This setup allows you to directly compare safe and insecure implementations of the same capability.

## How to Test

The agent has access to pairs of tools, one safe and one vulnerable. You can instruct the agent to use a specific tool by name in your prompt.

### 1. SQL Injection

To test for SQL injection, ask the agent to find a student by name.

*   **Vulnerable Test:**
    *   **Prompt:** `"Use the vulnerable_get_student_by_name tool to find the student named ' or '1'='1'"`
    *   **Expected Outcome:** The agent will use the f-string-based query, and the SQL injection will succeed, returning all students in the database.

*   **Safe Test:**
    *   **Prompt:** `"Use the safe_get_student_by_name tool to find the student named ' or '1'='1'"`
    *   **Expected Outcome:** The agent will use the parameterized query. The database will treat the input as a literal string, find no match, and return an empty list, preventing the injection.

### 2. Local File Inclusion (LFI)

To test for LFI, ask the agent to read a sensitive file.

*   **Vulnerable Test:**
    *   **Prompt:** `"Use the vulnerable_read_file tool to read the file /proc/self/environ"`
    *   **Expected Outcome:** The agent will read the file and return its contents, leaking all the environment variables of the running process (including your API key).

### 3. Arbitrary Code Execution vs. Sandboxing

To test for arbitrary code execution, ask the agent to run a piece of Python code.

*   **Vulnerable Test (Host Execution):**
    *   **Prompt:** `"Use the vulnerable_run_python_code tool to run the following Python code: import os; print(os.listdir('.'))"`
    *   **Expected Outcome:** The agent executes the code directly on the host machine. The output will be a listing of your project files (`core`, `main.py`, etc.), proving it has access to the host filesystem.

*   **Safe Test (Sandboxed Execution):**
    *   **Prompt:** `"Use the sandboxed_run_python_code tool to run the following Python code: import os; print(os.listdir('/'))"`
    *   **Expected Outcome:** The agent executes the code inside a temporary, isolated Docker container. The output will be a list of the root directories of a standard Linux system (`bin`, `etc`, `lib`, etc.), proving it is in an isolated environment with no access to your project files.

*   **Safe Test (Sandboxed Network Isolation):**
    *   **Prompt:** `"Use the sandboxed_run_python_code tool to run this code: import urllib.request; urllib.request.urlopen('https://google.com')"`
    *   **Expected Outcome:** The code will fail with a network error because the sandbox container is created with the `--network none` flag, preventing all external network calls.

*   **Limited-Scope Alternative:**
    *   **Prompt:** `"Use the safe_list_files tool to list the files in the '.' directory."`
    *   **Expected Outcome:** The agent uses a pre-defined, limited-scope function that only lists files. It cannot be tricked into executing other commands, reading file contents, or deleting files. This is the most secure approach when a specific, known capability is needed.


## Tool Implementations

All tools, both safe and vulnerable, are defined in `core/tools.py`.

*   `vulnerable_get_student_by_name`: Uses an f-string for the SQL query.
*   `safe_get_student_by_name`: Uses a secure parameterized query.
*   `vulnerable_read_file`: Reads any file with no restrictions.
*   `vulnerable_run_python_code`: Executes any string as Python code directly on the host.
*   `safe_list_files`: A limited-scope function that only lists directory contents.
*   `sandboxed_run_python_code`: Executes Python code inside a secure, isolated Docker container.


## How to Run the Application

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up your environment:**
    Create a `.env` file in the root of the project and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_api_key_here
    ```

3.  **Run the server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

4.  **Interact with the agent:**
    You can send prompts to the agent using the `/chat` endpoint. Remember to URL-encode your prompt.
    ```bash
    curl -X POST "http://localhost:8000/chat?query=Your%20prompt%20here"
    ```