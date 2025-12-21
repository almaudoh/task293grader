# config.py
from doctest import debug
import os
from dataclasses import dataclass
from typing import Union
from dotenv import load_dotenv
import yaml

load_dotenv('.env.grader')


@dataclass
class GraderConfig:
    """Central configuration for the automated grader"""
    # Mode: normal, interactive, debug
    MODE = 'normal'

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

    # Endpoint prefix, e.g. '/api/v1'
    ENDPOINT_PREFIX = ''

    # Expected API endpoints
    REQUIRED_ENDPOINTS = {
        "query": {
            "path": "/query",
            "props": ["query"],
            "mime_type": "application/json"
        },
        "upload": {
            "path": "/upload",
            "props": ["files"],
        },
        "health": {
            "path": "/health",
            "props": [],
        },
    }

    # Timeout settings (in seconds)
    CLONE_TIMEOUT = 60
    DEPENDENCY_INSTALL_TIMEOUT = 300
    APP_STARTUP_TIMEOUT = 60
    API_REQUEST_TIMEOUT = 30

    # Grading weights
    WEIGHTS = {
        'repository_setup': 15,
        'environment_config': 5,
        'dependencies': 10,
        'startup': 10,
        'upload': 25,
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

    # ChromaDB settings
    CHROMA_HOST = 'localhost'
    CHROMA_PORT = 8999

    @property
    def CHROMA_DB_HOST(self) -> str:
        scheme = 'http' if self.CHROMA_HOST == 'localhost' else 'https'
        return f'{scheme}://{self.CHROMA_HOST}:{self.CHROMA_PORT}'

    # Server settings
    SERVER_HOST = 'localhost'
    SERVER_PORT = 8998

    @property
    def SERVER_BASE_URL(self) -> str:
        scheme = 'http' if self.SERVER_HOST == 'localhost' else 'https'
        return f'{scheme}://{self.SERVER_HOST}:{self.SERVER_PORT}'

    # Additional .env settings for the application being graded.
    # Credentials
    TEST_HF_KEY = os.getenv('GRADER_HF_KEY', 'hf_test_key_placeholder')
    TEST_GEMINI_KEY = os.getenv('GRADER_GEMINI_KEY', 'gemini_test_key_placeholder')

    EMBED_MODEL_NAME = os.getenv('GRADER_EMBED_MODEL_NAME', 'sentence-transformers/all-MiniLM-L6-v2')
    LLM_MODEL_NAME = os.getenv('GRADER_LLM_MODEL_NAME', 'gemini-2.0-flash-exp')

    # Test data
    TEST_DATA_DIR = './test_data'

    CHUNK_LENGTH = int(os.getenv('GRADER_CHUNK_LENGTH', '512'))

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

    def override_from_yaml(self, yaml_path: str) -> None:
        """Apply configuration overrides from a YAML file."""
        if not os.path.isfile(yaml_path):
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        with open(yaml_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file) or {}

        if not isinstance(data, dict):
            raise ValueError("YAML config must be a mapping of keys to values")

        for key, value in data.items():
            attr = getattr(type(self), key, None)
            if isinstance(attr, property):
                raise ValueError(f"Cannot override read-only setting: {key}")

            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError(f"Unknown configuration key: {key}")
