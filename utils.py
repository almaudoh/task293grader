# utils.py
import os
import shutil
import logging
import uuid
import time
import socket
from datetime import datetime
from typing import Optional, Dict


def generate_unique_id() -> str:
    """Generate a unique identifier for grading session"""
    return f"grade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def setup_logger(grading_id: str) -> logging.Logger:
    """Setup logger for grading session"""
    logger = logging.getLogger(grading_id)
    logger.setLevel(logging.DEBUG)

    # Create logs directory if it doesn't exist
    os.makedirs('grading_logs', exist_ok=True)

    # File handler
    fh = logging.FileHandler(f'grading_logs/{grading_id}.log')
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def create_isolated_workspace(grading_id: str) -> str:
    """Create isolated workspace for grading"""
    workspace = f"./grading_workspace/{grading_id}"
    os.makedirs(workspace, exist_ok=True)
    return workspace


def cleanup_workspace(workspace: str):
    """Clean up workspace after grading"""
    try:
        if os.path.exists(workspace):
            shutil.rmtree(workspace)
    except Exception as e:
        logging.error(f"Failed to cleanup workspace {workspace}: {e}")


def is_port_open(host: str, port: int) -> bool:
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def wait_for_port(port: int, host: str = 'localhost', timeout: int = 60) -> bool:
    """Wait for a port to become available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_open(host, port):
            return True
        time.sleep(1)
    return False


def find_file(directory: str, filenames: list) -> Optional[str]:
    """Find first matching file in directory"""
    for filename in filenames:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            return filepath
    return None


def parse_env_file(filepath: str) -> Dict[str, str]:
    """Parse environment file and return key-value pairs"""
    env_vars = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        logging.error(f"Error parsing env file: {e}")
    return env_vars


def write_file(filepath: str, content: str):
    """Write content to file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)


def calculate_relevance(answer: str, keywords: list) -> float:
    """Calculate relevance score based on keyword presence"""
    if not answer:
        return 0.0

    answer_lower = answer.lower()
    matches = sum(1 for keyword in keywords if keyword.lower() in answer_lower)
    return (matches / len(keywords)) * 100 if keywords else 0.0


def strip_html_tags(text: str) -> str:
    """Strip HTML tags from text"""
    from html import unescape
    import re

    return unescape(re.sub(r'\n\s*\n', '\n', re.sub(r'<[^>]+>', '', text))).strip()
