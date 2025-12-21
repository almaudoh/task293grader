# repo_analyzer.py
import os
import subprocess
from typing import Optional
from config import GraderConfig


class RepositoryAnalyzer:
    """Analyzes repository structure and detects language"""

    def __init__(self, logger, config: Optional[GraderConfig] = None):
        self.logger = logger
        self.config = config or GraderConfig()

    def clone_repository(self, github_url: str, destination: str) -> Optional[str]:
        """Clone GitHub repository"""
        try:
            self.logger.info(f"Cloning repository: {github_url}")
            result = subprocess.run(
                ['git', 'clone', github_url, destination],
                capture_output=True,
                text=True,
                timeout=self.config.CLONE_TIMEOUT
            )

            if result.returncode == 0:
                self.logger.info("Repository cloned successfully")
                return destination
            else:
                self.logger.error(f"Clone failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            self.logger.error("Repository clone timeout")
            return None
        except Exception as e:
            self.logger.error(f"Clone error: {e}")
            return None

    def detect_language(self, repo_path: str) -> Optional[str]:
        """Detect programming language from dependency files"""
        self.logger.info("Detecting programming language")

        for lang, config in self.config.LANGUAGE_CONFIG.items():
            dep_file = os.path.join(repo_path, config['dependency_file'])
            if os.path.exists(dep_file):
                self.logger.info(f"Detected language: {lang}")
                return lang

        self.logger.error("Could not detect programming language")
        return None

    def find_main_file(self, repo_path: str, language: str) -> Optional[str]:
        """Find main entry file"""
        self.logger.info(f"Looking for main file for {language}")

        if language not in self.config.LANGUAGE_CONFIG:
            return None

        main_files = self.config.LANGUAGE_CONFIG[language]['main_files']

        for main_file in main_files:
            filepath = os.path.join(repo_path, main_file)
            if os.path.exists(filepath):
                self.logger.info(f"Found main file: {main_file}")
                return main_file

        self.logger.error("Main file not found")
        return None

    def find_dependency_file(self, repo_path: str, language: str) -> Optional[str]:
        """Find dependency file"""
        if language not in self.config.LANGUAGE_CONFIG:
            return None

        dep_file = self.config.LANGUAGE_CONFIG[language]['dependency_file']
        filepath = os.path.join(repo_path, dep_file)

        return filepath if os.path.exists(filepath) else None

    def check_env_template(self, repo_path: str) -> bool:
        """Check if .env template exists"""
        env_files = ['.env.example', '.env.template', '.env.sample']
        for env_file in env_files:
            if os.path.exists(os.path.join(repo_path, env_file)):
                self.logger.info(f"Found env template: {env_file}")
                return True

        self.logger.warning("No .env template found")
        return False

    def check_readme(self, repo_path: str) -> bool:
        """Check if README exists"""
        readme_files = ['README.md', 'README.txt', 'README']
        for readme in readme_files:
            if os.path.exists(os.path.join(repo_path, readme)):
                return True
        return False
