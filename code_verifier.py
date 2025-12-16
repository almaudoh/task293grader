# code_verifier.py
import os
import re
from typing import Dict


class CodeVerifier:
    """Verifies technical requirements in code"""

    def __init__(self, logger):
        self.logger = logger

    def check_embedding_model(self, repo_path: str, model_name: str) -> bool:
        """Check if correct embedding model is used"""
        self.logger.info(f"Checking for embedding model: {model_name}")

        try:
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [
                    d for d in dirs
                    if d not in ['node_modules', 'venv', '__pycache__', '.git']
                ]

                for file in files:
                    if file.endswith(('.py', '.js', '.go', '.dart')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if model_name in content or 'all-MiniLM-L6-v2' in content:
                                    self.logger.info(f"Found embedding model reference in {file}")
                                    return True
                        except Exception:
                            continue

            self.logger.warning("Could not verify embedding model")
            return False

        except Exception as e:
            self.logger.error(f"Error checking embedding model: {e}")
            return False

    def check_chromadb_usage(self, repo_path: str) -> bool:
        """Check if ChromaDB is being used"""
        self.logger.info("Checking for ChromaDB integration")

        search_terms = ['chroma', 'chromadb', 'vector', 'collection']

        try:
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs
                           if d not in ['node_modules', 'venv', '__pycache__', '.git']]

                for file in files:
                    if file.endswith(('.py', '.js', '.go', '.dart')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                if any(term in content for term in search_terms):
                                    self.logger.info(f"Found ChromaDB usage in {file}")
                                    return True
                        except Exception:
                            continue

            self.logger.warning("Could not verify ChromaDB usage")
            return False

        except Exception as e:
            self.logger.error(f"Error checking ChromaDB: {e}")
            return False

    def check_gemini_usage(self, repo_path: str) -> bool:
        """Check if Gemini model is being used"""
        self.logger.info("Checking for Gemini integration")

        search_terms = ['gemini', 'google', 'generativeai']

        try:
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs
                           if d not in ['node_modules', 'venv', '__pycache__', '.git']]

                for file in files:
                    if file.endswith(('.py', '.js', '.go', '.dart')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                if any(term in content for term in search_terms):
                                    self.logger.info(f"Found Gemini usage in {file}")
                                    return True
                        except Exception:
                            continue

            self.logger.warning("Could not verify Gemini usage")
            return False

        except Exception as e:
            self.logger.error(f"Error checking Gemini: {e}")
            return False

    def check_chunk_config(self, repo_path: str) -> bool:
        """Check if chunk length is configurable"""
        self.logger.info("Checking for configurable chunk length")

        search_patterns = [
            r'CHUNK_LENGTH',
            r'chunk[_-]?length',
            r'chunk[_-]?size'
        ]

        try:
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs
                           if d not in ['node_modules', 'venv', '__pycache__', '.git']]

                for file in files:
                    if file.endswith(('.py', '.js', '.go', '.dart')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                for pattern in search_patterns:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        self.logger.info(f"Found chunk config in {file}")
                                        return True
                        except Exception:
                            continue

            self.logger.warning("Could not verify configurable chunk length")
            return False

        except Exception as e:
            self.logger.error(f"Error checking chunk config: {e}")
            return False

    def verify_technical_requirements(self, repo_path: str) -> Dict[str, bool]:
        """Verify all technical requirements"""
        self.logger.info("Verifying technical requirements")

        return {
            'semantic_chunking': self.check_chunk_config(repo_path),
            'hf_embeddings': self.check_embedding_model(repo_path, 'all-MiniLM-L6-v2'),
            'chromadb_integration': self.check_chromadb_usage(repo_path),
            'gemini_integration': self.check_gemini_usage(repo_path),
            'configurable_chunk': self.check_chunk_config(repo_path)
        }
