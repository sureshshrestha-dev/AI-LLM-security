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
}