import os
import sys
from typing import List, Dict
import subprocess

try:
    from core.database import SessionLocal
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from core.database import SessionLocal

from sqlalchemy import text
from google.genai import types

# --- 1. SQL Injection Vulnerability ---

# VULNERABLE: Uses f-string formatting, allowing for SQL Injection.
def vulnerable_get_student_by_name(name: str) -> List[Dict]:
    """
    VULNERABLE: Gets student by name using an insecure f-string SQL query.
    An attacker can inject SQL commands via the 'name' parameter.
    Example exploit: name = "' or '1'='1"
    """
    print(f"Executing VULNERABLE search for student: {name}")
    db = SessionLocal()
    try:
        stmt = text(f"SELECT * FROM students WHERE LOWER(name) = '{name.lower()}'")
        result = db.execute(stmt)
        rows = [dict(r) for r in result.mappings().all()]
        return rows
    finally:
        db.close()

# SAFE: Uses parameterized queries, preventing SQL Injection.
def safe_get_student_by_name(name: str) -> List[Dict]:
    """
    SAFE: Gets student by name using a secure parameterized SQL query.
    This prevents SQL injection by separating the query logic from the data.
    """
    print(f"Executing SAFE search for student: {name}")
    db = SessionLocal()
    try:
        stmt = text("SELECT * FROM students WHERE LOWER(name) = LOWER(:name)")
        result = db.execute(stmt, {"name": name})
        rows = [dict(r) for r in result.mappings().all()]
        return rows
    finally:
        db.close()

# --- 2. Local File Inclusion (LFI) & Arbitrary Code Execution ---

# VULNERABLE: Reads any file on the filesystem with no restrictions.
def vulnerable_read_file(filepath: str) -> str:
    """
    VULNERABLE: Reads and returns the content of any file on the local filesystem.
    An attacker can use this to read sensitive files like '/etc/passwd' or '/proc/self/environ'.
    """
    print(f"Executing VULNERABLE file read for: {filepath}")
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# VULNERABLE: Executes arbitrary Python code.
def vulnerable_run_python_code(code_str: str) -> str:
    """
    VULNERABLE: Executes arbitrary Python code provided by the user.
    This is extremely insecure. An attacker can run any command.
    Example exploit: code_str = "import os; os.system('rm -rf /tmp/test')"
    """
    print(f"Executing VULNERABLE python code: {code_str}")
    try:
        with open("temp_exploit.py", "w") as f:
            f.write(code_str)
        result = subprocess.run(["python3", "temp_exploit.py"], capture_output=True, text=True)
        return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except Exception as e:
        return f"Error executing code: {e}"

# SAFE: Only lists files in a directory, no read/write/execute.
def safe_list_files(directory_path: str) -> List[str]:
    """
    SAFE: Lists files in a given directory. Scope is limited to a safe action.
    Includes basic validation.
    """
    print(f"Executing SAFE file list for: {directory_path}")
    if not os.path.isdir(directory_path):
        return ["Error: The specified path is not a valid directory."]
    # Add more security checks here in a real application (e.g., path traversal)
    return os.listdir(directory_path)

# --- 3. Sandboxed Code Execution ---

# SAFE: Executes code inside a temporary, isolated Docker container.
def sandboxed_run_python_code(code_str: str) -> str:
    """
    SAFE: Executes Python code inside a sandboxed Docker container.
    This prevents the code from accessing the host filesystem or network.
    """
    print(f"Executing SANDBOXED python code: {code_str}")
    try:
        # Use a temporary, throwaway container with no network and a read-only root filesystem
        docker_command = [
            "docker", "run",
            "--rm",  # Remove the container after it exits
            "--network", "none",  # Disable networking
            "--read-only", # Make the container's root filesystem read-only
            "python:3.11-slim",
            "python3", "-c", code_str
        ]
        result = subprocess.run(docker_command, capture_output=True, text=True, timeout=10)
        return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out after 10 seconds."
    except Exception as e:
        return f"Error creating sandbox: {e}"

# --- 4. Path Traversal Vulnerability ---

# SAFE: Uses pathlib to resolve paths and prevent traversal attacks.
def safe_read_document(filename: str) -> str:
    """
    SAFE: Reads a file only from within the 'documents' directory.
    Uses pathlib to resolve the path and prevent directory traversal attacks.
    """
    print(f"Executing SAFE document read for: {filename}")
    try:
        base_dir = os.path.abspath("documents")
        target_path = os.path.abspath(os.path.join(base_dir, filename))

        # Security Check: Ensure the resolved path is still within the base directory
        if not target_path.startswith(base_dir):
            return "Error: Path traversal attempt detected."

        with open(target_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: The specified document was not found."
    except Exception as e:
        return f"Error reading document: {e}"

# --- 5. Server-Side Request Forgery (SSRF) ---
import requests
import ipaddress
import socket
from urllib.parse import urlparse

# VULNERABLE: Fetches any URL provided, including internal and metadata IPs.
def vulnerable_fetch_webpage(url: str) -> str:
    """
    VULNERABLE: Fetches the content of any URL.
    An attacker can use this to scan internal networks or access cloud metadata services.
    Example exploit: url = "http://169.254.169.254/latest/meta-data/"
    """
    print(f"Executing VULNERABLE webpage fetch for: {url}")
    try:
        response = requests.get(url, timeout=3)
        return response.text[:500] # Return first 500 chars
    except Exception as e:
        return f"Error fetching URL: {e}"

# SAFE: Validates the URL to ensure it's not an internal or reserved IP.
def safe_fetch_webpage(url: str) -> str:
    """
    SAFE: Fetches a URL after validating it doesn't point to a private or reserved IP address.
    This prevents SSRF attacks.
    """
    print(f"Executing SAFE webpage fetch for: {url}")
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ('http', 'https'):
            return "Error: Invalid URL scheme. Only http and https are allowed."

        hostname = parsed_url.hostname
        if not hostname:
            return "Error: Invalid hostname."

        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)

        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return f"Error: SSRF attempt blocked. The IP {ip_str} is a non-public address."

        response = requests.get(url, timeout=3)
        return response.text[:500] # Return first 500 chars
    except socket.gaierror:
        return "Error: Could not resolve hostname."
    except Exception as e:
        return f"Error fetching URL: {e}"





# --- Gemini Tool Declarations ---

ALL_TOOLS = types.Tool(
    function_declarations=[
        # Vulnerable SQLi Tool
        types.FunctionDeclaration(
            name="vulnerable_get_student_by_name",
            description="VULNERABLE: Gets student by name using an insecure f-string SQL query.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"name": types.Schema(type="STRING")},
                required=["name"],
            ),
        ),
        # Safe SQLi Tool
        types.FunctionDeclaration(
            name="safe_get_student_by_name",
            description="SAFE: Gets student by name using a secure parameterized SQL query.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"name": types.Schema(type="STRING")},
                required=["name"],
            ),
        ),
        # Vulnerable File Read Tool
        types.FunctionDeclaration(
            name="vulnerable_read_file",
            description="VULNERABLE: Reads and returns the content of any file on the local filesystem.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"filepath": types.Schema(type="STRING")},
                required=["filepath"],
            ),
        ),
        # Vulnerable Code Execution Tool
        types.FunctionDeclaration(
            name="vulnerable_run_python_code",
            description="VULNERABLE: Executes arbitrary Python code provided by the user.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"code_str": types.Schema(type="STRING")},
                required=["code_str"],
            ),
        ),
        # Safe File Listing Tool
        types.FunctionDeclaration(
            name="safe_list_files",
            description="SAFE: Lists files in a given directory. Scope is limited to a safe action.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"directory_path": types.Schema(type="STRING")},
                required=["directory_path"],
            ),
        ),
        # Sandboxed Code Execution Tool
        types.FunctionDeclaration(
            name="sandboxed_run_python_code",
            description="SAFE: Executes Python code inside a sandboxed Docker container.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"code_str": types.Schema(type="STRING")},
                required=["code_str"],
            ),
        ),
        # Safe Document Reading Tool (Path Traversal Safe)
        types.FunctionDeclaration(
            name="safe_read_document",
            description="SAFE: Reads a file only from within the 'documents' directory, preventing path traversal.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"filename": types.Schema(type="STRING")},
                required=["filename"],
            ),
        ),
        # Vulnerable SSRF Tool
        types.FunctionDeclaration(
            name="vulnerable_fetch_webpage",
            description="VULNERABLE: Fetches the content of any URL, allowing SSRF.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"url": types.Schema(type="STRING")},
                required=["url"],
            ),
        ),
        # Safe SSRF Tool
        types.FunctionDeclaration(
            name="safe_fetch_webpage",
            description="SAFE: Fetches a URL after validating it's not a private or reserved IP.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"url": types.Schema(type="STRING")},
                required=["url"],
            ),
        ),
    ]
)

# Mapping tool names to functions for easy execution
TOOL_FUNCTION_MAP = {
    "vulnerable_get_student_by_name": vulnerable_get_student_by_name,
    "safe_get_student_by_name": safe_get_student_by_name,
    "vulnerable_read_file": vulnerable_read_file,
    "vulnerable_run_python_code": vulnerable_run_python_code,
    "safe_list_files": safe_list_files,
    "sandboxed_run_python_code": sandboxed_run_python_code,
    "safe_read_document": safe_read_document,
    "vulnerable_fetch_webpage": vulnerable_fetch_webpage,
    "safe_fetch_webpage": safe_fetch_webpage,
}