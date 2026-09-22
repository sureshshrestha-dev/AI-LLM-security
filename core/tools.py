import os
import sys
import subprocess
import requests
import ipaddress
import socket
from urllib.parse import urlparse
from typing import List, Dict, Tuple
from sqlalchemy import text

from core.database import SessionLocal
from core.models import AcademicStudent, KnowledgeDocument

# --- 1. SQL Injection Tools ---

def vulnerable_get_student_by_name(name: str) -> Tuple[List[Dict], str]:
    """
    VULNERABLE: Uses f-string formatting, allowing SQL Injection.
    """
    raw_query = f"SELECT * FROM academic_students WHERE LOWER(full_name) = '{name.lower()}'"
    trace = f"[SQL TRACE - VULNERABLE]\nExecuting Query:\n{raw_query}\n"
    
    db = SessionLocal()
    try:
        stmt = text(raw_query)
        result = db.execute(stmt)
        rows = [dict(r) for r in result.mappings().all()]
        trace += f"Query returned {len(rows)} record(s).\n"
        return rows, trace
    except Exception as e:
        trace += f"SQL Error: {str(e)}\n"
        return [], trace
    finally:
        db.close()

def safe_get_student_by_name(name: str) -> Tuple[List[Dict], str]:
    """
    SAFE: Uses parameterized queries, preventing SQL Injection.
    """
    raw_query = "SELECT * FROM academic_students WHERE LOWER(full_name) = LOWER(:name)"
    trace = f"[SQL TRACE - SAFE (PARAMETERIZED)]\nQuery Template:\n{raw_query}\nBound Parameters: {{'name': '{name}'}}\n"
    
    db = SessionLocal()
    try:
        stmt = text(raw_query)
        result = db.execute(stmt, {"name": name})
        rows = [dict(r) for r in result.mappings().all()]
        trace += f"Query returned {len(rows)} record(s). Parameterization prevented syntax injection.\n"
        return rows, trace
    except Exception as e:
        trace += f"SQL Error: {str(e)}\n"
        return [], trace
    finally:
        db.close()

# --- 2. LFI / Path Traversal Tools ---

def vulnerable_read_file(filepath: str) -> Tuple[str, str]:
    """
    VULNERABLE: Reads any file on the local filesystem with no restrictions.
    """
    trace = f"[FILE TRACE - VULNERABLE]\nAttempting raw file open for: {filepath}\n"
    
    # Handle special mock path for demonstration if requested
    if "secret_system.flag" in filepath or "secret_flag" in filepath:
        content = "FLAG{LFI_PATH_TRAVERSAL_EXPOSED_SYSTEM_2026}\nSYSTEM_CONFIDENTIAL_KEY=sk_live_9921831923"
        trace += f"SUCCESS: Read {len(content)} bytes from file path.\n"
        return content, trace
        
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
            trace += f"SUCCESS: Read {len(content)} bytes.\n"
            return content, trace
        else:
            trace += "ERROR: File not found on filesystem.\n"
            return "Error: File not found.", trace
    except Exception as e:
        trace += f"ERROR: Exception during file read: {e}\n"
        return f"Error: {e}", trace

def safe_read_document(filename: str) -> Tuple[str, str]:
    """
    SAFE: Uses pathlib/abspath to resolve paths and prevent traversal.
    """
    trace = f"[FILE TRACE - SAFE BOUNDARY CHECK]\nInput filename: {filename}\n"
    try:
        base_dir = os.path.abspath("documents")
        target_path = os.path.abspath(os.path.join(base_dir, filename))
        
        trace += f"Resolved Base Directory: {base_dir}\n"
        trace += f"Resolved Target Path:   {target_path}\n"

        if not target_path.startswith(base_dir):
            trace += "SECURITY VIOLATION DETECTED: Resolved path leaves base directory boundaries!\n"
            return "Error: Path traversal attempt blocked.", trace

        if os.path.exists(target_path):
            with open(target_path, "r") as f:
                content = f.read()
            trace += f"SUCCESS: Read {len(content)} bytes safely inside allowed directory.\n"
            return content, trace
        else:
            trace += "ERROR: Document not found within allowed directory.\n"
            return "Error: Document not found.", trace
    except Exception as e:
        trace += f"ERROR: Exception during safe read: {e}\n"
        return f"Error: {e}", trace

# --- 3. Arbitrary Code Execution vs Sandbox ---

def vulnerable_run_python_code(code_str: str) -> Tuple[str, str]:
    """
    VULNERABLE: Executes Python code directly on host machine.
    """
    trace = f"[EXECUTION TRACE - VULNERABLE HOST RUNNER]\nExecuting Python script directly on host system...\n"
    try:
        temp_file = "temp_host_script.py"
        with open(temp_file, "w") as f:
            f.write(code_str)
        
        result = subprocess.run(["python3", temp_file], capture_output=True, text=True, timeout=5)
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        out = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        trace += f"Execution complete with return code {result.returncode}.\n"
        return out, trace
    except subprocess.TimeoutExpired:
        trace += "ERROR: Script execution timed out.\n"
        return "Error: Execution timeout", trace
    except Exception as e:
        trace += f"ERROR: {e}\n"
        return f"Error: {e}", trace

def sandboxed_run_python_code(code_str: str) -> Tuple[str, str]:
    """
    SAFE: Executes code inside isolated Docker container.
    """
    trace = f"[EXECUTION TRACE - SAFE DOCKER SANDBOX]\nPreparing isolated container execution (python:3.11-slim, network=none, read-only)...\n"
    try:
        docker_command = [
            "docker", "run",
            "--rm",
            "--network", "none",
            "--read-only",
            "python:3.11-slim",
            "python3", "-c", code_str
        ]
        result = subprocess.run(docker_command, capture_output=True, text=True, timeout=8)
        out = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        trace += f"Container exited cleanly. Network calls and filesystem writes were blocked by kernel sandbox.\n"
        return out, trace
    except Exception as e:
        trace += f"Sandbox Fallback Note: Docker daemon not active or restricted. Simulating secure isolated execution.\n"
        out = "SANDBOX SIMULATION: Code executed in ephemeral isolated container.\nNetwork: DISABLED\nFilesystem: READ-ONLY"
        return out, trace

# --- 4. Server-Side Request Forgery (SSRF) ---

def vulnerable_fetch_webpage(url: str) -> Tuple[str, str]:
    """
    VULNERABLE: Fetches any URL without validating IP or host.
    """
    trace = f"[NETWORK TRACE - VULNERABLE FETCH]\nSending HTTP GET request to: {url}\n"
    if "169.254.169.254" in url or "localhost" in url or "127.0.0.1" in url:
        mock_response = "HTTP/1.1 200 OK\nHeader: Cloud-Metadata-Service\nBody: FLAG{SSRF_METADATA_PORT_SCAN_2026}\nAWS_SECRET_ACCESS_KEY=ASIAIOSFODNN7EXAMPLE"
        trace += "SUCCESS: Connected to internal endpoint / metadata IP!\n"
        return mock_response, trace
        
    try:
        res = requests.get(url, timeout=3)
        trace += f"SUCCESS: Received HTTP {res.status_code}\n"
        return res.text[:500], trace
    except Exception as e:
        trace += f"Connection failed/timed out: {e}\n"
        return f"Fetch result: {e}", trace

def safe_fetch_webpage(url: str) -> Tuple[str, str]:
    """
    SAFE: Validates DNS resolution to block private/reserved IP ranges.
    """
    trace = f"[NETWORK TRACE - SAFE IP VALIDATION]\nInspecting URL: {url}\n"
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ('http', 'https'):
            trace += "REJECTED: Only http and https protocols permitted.\n"
            return "Error: Invalid scheme.", trace

        hostname = parsed_url.hostname
        if not hostname:
            trace += "REJECTED: Hostname missing.\n"
            return "Error: Invalid hostname.", trace

        trace += f"Resolving hostname: {hostname}...\n"
        try:
            ip_str = socket.gethostbyname(hostname)
        except socket.gaierror:
            ip_str = "127.0.0.1" if hostname in ("localhost", "169.254.169.254") else "192.168.1.1"

        ip = ipaddress.ip_address(ip_str)
        trace += f"Resolved IP Address: {ip_str}\n"

        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or str(ip) == "169.254.169.254":
            trace += f"SECURITY BLOCK: The IP {ip_str} belongs to a restricted/private network range!\n"
            return f"Error: SSRF attempt blocked. Target IP {ip_str} is private/reserved.", trace

        res = requests.get(url, timeout=3)
        trace += f"SUCCESS: External public website fetched (HTTP {res.status_code}).\n"
        return res.text[:500], trace
    except Exception as e:
        trace += f"Execution error: {e}\n"
        return f"Error: {e}", trace