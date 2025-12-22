# dependency_manager.py
import os
import sys
import subprocess
from typing import Optional
from config import GraderConfig


class DependencyManager:
    """Manages dependency installation for different languages"""

    def __init__(self, logger, config: Optional[GraderConfig] = None):
        self.logger = logger
        self.config = config or GraderConfig()

    def _setup_venv(self, repo_path: str) -> Optional[str]:
        """Create virtual environment and return path to venv python executable"""
        venv_dir = os.path.join(repo_path, 'venv')

        # Create venv if it does not exist
        if not os.path.isdir(venv_dir):
            self.logger.info("Creating Python virtual environment")
            create_cmd = [sys.executable, '-m', 'venv', venv_dir]
            subprocess.run(
                create_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=self.config.DEPENDENCY_INSTALL_TIMEOUT,
                check=True,
            )

        # Resolve venv python
        if os.name == 'nt':
            venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe')
        else:
            venv_python = os.path.join(venv_dir, 'bin', 'python')

        # Upgrade pip first for reliability
        self.logger.info("Upgrading pip in virtual environment")
        upgrade_cmd = [venv_python, '-m', 'pip', 'install', '--upgrade', 'pip']
        subprocess.run(
            upgrade_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=self.config.DEPENDENCY_INSTALL_TIMEOUT,
            check=False,
        )

        return venv_python

    def _get_install_command(self, language: str, repo_path: str) -> Optional[list]:
        """Get install command for a language, handling venv for Python if needed"""
        lang_config = self.config.LANGUAGE_CONFIG[language]
        install_cmd = lang_config['install_command'].copy()

        # Handle venv for languages that support it (e.g., Python)
        options = lang_config.get('options', {})
        if options.get('use_venv') and language == 'python':
            venv_python = self._setup_venv(repo_path)
            # Replace pip command with venv python -m pip
            if install_cmd[0] == 'pip':
                install_cmd = [venv_python, '-m', 'pip'] + install_cmd[1:]

        return install_cmd

    def install_dependencies(self, repo_path: str, language: str) -> bool:
        """Install dependencies based on language"""
        self.logger.info(f"Installing dependencies for {language}")

        if language not in self.config.LANGUAGE_CONFIG:
            self.logger.error(f"Unsupported language: {language}")
            return False

        lang_config = self.config.LANGUAGE_CONFIG[language]
        dependency_file = lang_config['dependency_file']
        dep_file_path = os.path.join(repo_path, dependency_file)

        # Check if dependency file exists
        if not os.path.isfile(dep_file_path):
            self.logger.info(f"No {dependency_file} found, skipping installation")
            return True

        if os.path.getsize(dep_file_path) == 0:
            self.logger.info(f"Empty {dependency_file}, skipping installation")
            return True

        try:
            # Get the appropriate install command
            install_cmd = self._get_install_command(language, repo_path)

            self.logger.info(f"Running install command for {language}")
            result = subprocess.run(
                install_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=self.config.DEPENDENCY_INSTALL_TIMEOUT,
            )

            self.logger.info(f"result.stdout: {result.stdout}; result.stderr: {result.stderr}")

            if result.returncode == 0:
                self.logger.info("Dependencies installed successfully")
                self.logger.debug(f"Install output: {result.stdout}")
                return True

            # Handle specific error messages
            if 'Could not open requirements file' in (result.stderr or ''):
                self.logger.info(f"No {dependency_file} present; skipping dependency installation")
                return True

            self.logger.error(f"Dependency installation failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            self.logger.error("Dependency installation timeout")
            return False
        except FileNotFoundError:
            self.logger.error(f"Package manager not found for {language}")
            return False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Installation error: {e}")
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
