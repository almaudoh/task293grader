# config.py
import os
from dataclasses import dataclass


@dataclass
class GraderConfig:
    """Central configuration for the automated grader"""

    # Supported languages
    SUPPORTED_LANGUAGES = ['nodejs', 'python', 'golang', 'dart']

    # Required environment variables
    REQUIRED_ENV_VARS = [
        'HF_API_KEY',
        'EMBED_MODEL_NAME',
        'GEMINI_API_KEY',
        'LLM_MODEL_NAME',
        'CHROMA_DB_HOST',
        'RAG_DATA_DIR',
        'CHUNK_LENGTH',
        'PORT'
    ]

    # Expected API endpoints
    REQUIRED_ENDPOINTS = ['/query', '/upload', '/health']

    # Timeout settings (in seconds)
    CLONE_TIMEOUT = 60
    DEPENDENCY_INSTALL_TIMEOUT = 300
    APP_STARTUP_TIMEOUT = 60
    API_REQUEST_TIMEOUT = 30

    # Grading weights
    WEIGHTS = {
        'repository_setup': 15,
        'environment_config': 15,
        'dependencies': 10,
        'startup': 10,
        'upload': 15,
        'query': 25,
        'technical': 10
    }

    # Test queries with expected keywords
    TEST_QUERIES = [
        {
            'question': 'What is machine learning?',
            'expected_keywords': ['learning', 'data', 'algorithm', 'model', 'pattern']
        },
        {
            'question': 'Explain neural networks',
            'expected_keywords': ['neural', 'network', 'layer', 'neuron', 'weight']
        },
        {
            'question': 'What is the purpose of embeddings?',
            'expected_keywords': ['embedding', 'vector', 'representation', 'semantic']
        }
    ]

    # Test credentials
    TEST_HF_KEY = os.getenv('GRADER_HF_KEY', 'hf_test_key_placeholder')
    TEST_GEMINI_KEY = os.getenv('GRADER_GEMINI_KEY', 'gemini_test_key_placeholder')

    # ChromaDB settings
    CHROMA_HOST = 'localhost'
    CHROMA_PORT = 8000

    # Test data
    TEST_DATA_DIR = './grader_test_data'

    # Language-specific configurations
    LANGUAGE_CONFIG = {
        'nodejs': {
            'main_files': ['main.js', 'index.js', 'app.js', 'server.js'],
            'dependency_file': 'package.json',
            'install_command': ['npm', 'install'],
            'run_command': ['node']
        },
        'python': {
            'main_files': ['main.py', 'app.py', 'server.py'],
            'dependency_file': 'requirements.txt',
            'install_command': ['pip', 'install', '-r', 'requirements.txt'],
            'run_command': ['uvicorn', 'main:app', '--host', '0.0.0.0']
        },
        'golang': {
            'main_files': ['main.go'],
            'dependency_file': 'go.mod',
            'install_command': ['go', 'mod', 'download'],
            'run_command': ['go', 'run']
        },
        'dart': {
            'main_files': ['main.dart'],
            'dependency_file': 'pubspec.yaml',
            'install_command': ['dart', 'pub', 'get'],
            'run_command': ['dart', 'run']
        }
    }

    # Grade thresholds
    GRADE_THRESHOLDS = {
        'A': 90,
        'B': 80,
        'C': 70,
        'D': 60,
        'F': 0
    }
