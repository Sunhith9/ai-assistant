"""
code_tool.py
Code execution agent - runs Python code snippets safely in an isolated
subprocess with a timeout, so it can't hang or crash the main assistant.
Free, fully local, no API needed.
"""

import subprocess
import sys
import tempfile
import os


def run_python_code(code: str, timeout_seconds: int = 10) -> str:
    """Execute a Python code snippet in an isolated subprocess and return
    its printed output. Use print() in the code to see results.
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if error:
            return f"Code ran with errors:\n{error}\n\nOutput so far:\n{output}"

        return output if output else "Code ran successfully with no printed output."

    except subprocess.TimeoutExpired:
        return f"Code execution timed out after {timeout_seconds} seconds (possible infinite loop)."
    except Exception as e:
        return f"Code execution agent error: {e}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)