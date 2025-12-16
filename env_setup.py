# env_setup.py
import os
from config import GraderConfig
from utils import write_file
import shutil


class EnvironmentSetup:
    """Sets up test environment for grading"""

    def __init__(self, logger):
        self.logger = logger
        self.config = GraderConfig()

    def create_env_file(self, repo_path: str) -> bool:
        """Create .env file with test credentials"""
        try:
            self.logger.info("Creating .env file")

            env_content = f"""# Grader-generated test environment
HF_API_KEY={self.config.TEST_HF_KEY}
EMBED_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
GEMINI_API_KEY={self.config.TEST_GEMINI_KEY}
LLM_MODEL_NAME=gemini-2.0-flash-exp
CHROMA_DB_HOST={self.config.CHROMA_HOST}:{self.config.CHROMA_PORT}
RAG_DATA_DIR=./test_data
CHUNK_LENGTH=512
PORT=8080
"""

            env_path = os.path.join(repo_path, '.env')
            write_file(env_path, env_content)

            self.logger.info(".env file created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create .env file: {e}")
            return False

    def setup_test_data_directory(self, repo_path: str) -> bool:
        """Create test data directory"""
        try:
            test_data_dir = os.path.join(repo_path, 'test_data')
            os.makedirs(test_data_dir, exist_ok=True)
            self.logger.info(f"Test data directory created: {test_data_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create test data directory: {e}")
            return False

    def prepare_sample_documents(self, repo_path: str) -> list:
        """Copy sample documents into the test environment"""
        source_docs_dir = 'sample_documents'
        test_data_dir = os.path.join(repo_path, 'test_data')
        documents = []

        try:
            if not os.path.isdir(source_docs_dir):
                self.logger.error(f"Source documents directory not found: {source_docs_dir}")
                return []

            for filename in os.listdir(source_docs_dir):
                source_path = os.path.join(source_docs_dir, filename)
                dest_path = os.path.join(test_data_dir, filename)
                if os.path.isfile(source_path):
                    shutil.copy(source_path, dest_path)
                    documents.append(dest_path)

            self.logger.info(f"Copied {len(documents)} test documents to {test_data_dir}")
            return documents

        except Exception as e:
            self.logger.error(f"Failed to prepare sample documents: {e}")
            return []
