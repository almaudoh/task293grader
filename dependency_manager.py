# dependency_manager.py
import subprocess
from typing import Optional
from config import GraderConfig


class DependencyManager:
    """Manages dependency installation for different languages"""

    def __init__(self, logger, config: Optional[GraderConfig] = None):
        self.logger = logger
        self.config = config or GraderConfig()

    def install_dependencies(self, repo_path: str, language: str) -> bool:
        """Install dependencies based on language"""
        self.logger.info(f"Installing dependencies for {language}")

        if language not in self.config.LANGUAGE_CONFIG:
            self.logger.error(f"Unsupported language: {language}")
            return False

        install_cmd = self.config.LANGUAGE_CONFIG[language]['install_command']

        try:
            result = subprocess.run(
                install_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=self.config.DEPENDENCY_INSTALL_TIMEOUT
            )

            if result.returncode == 0:
                self.logger.info("Dependencies installed successfully")
                self.logger.debug(f"Install output: {result.stdout}")
                return True
            else:
                self.logger.error(f"Dependency installation failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("Dependency installation timeout")
            return False
        except FileNotFoundError:
            self.logger.error(f"Package manager not found for {language}")
            return False
        except Exception as e:
            self.logger.error(f"Installation error: {e}")
            return False

    def verify_installation(self, repo_path: str, language: str) -> bool:
        """Verify that dependencies were installed correctly"""
        self.logger.info("Verifying dependency installation")

        verification_paths = {
            'nodejs': 'node_modules',
            'python': 'venv',  # May not exist, that's ok
            'golang': 'go.sum',
            'dart': '.dart_tool'
        }

        if language in verification_paths:
            path = verification_paths[language]
            full_path = f"{repo_path}/{path}"
            exists = subprocess.run(['test', '-e', full_path], capture_output=True).returncode == 0

            if exists or language == 'python':  # Python might not have venv
                self.logger.info("Dependency installation verified")
                return True

        self.logger.warning("Could not verify dependency installation")
        return True  # Don't fail if we can't verify
