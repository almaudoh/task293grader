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

    def install_dependencies(self, repo_path: str, language: str) -> bool:
        """Install dependencies based on language"""
        self.logger.info(f"Installing dependencies for {language}")

        if language not in self.config.LANGUAGE_CONFIG:
            self.logger.error(f"Unsupported language: {language}")
            return False

        try:
            if language == 'python':
                # @todo: How can we make this more generic?

                if self.config.LANGUAGE_CONFIG['python'].get('options', {}).get('use_venv', False):
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
                        executable = os.path.join(venv_dir, 'Scripts', 'python.exe')
                    else:
                        executable = os.path.join(venv_dir, 'bin', 'python')

                else:
                    executable = sys.executable

                # Upgrade pip first for reliability
                self.logger.info("Upgrading pip in virtual environment")
                upgrade_cmd = [executable, '-m', 'pip', 'install', '--upgrade', 'pip']
                subprocess.run(
                    upgrade_cmd,
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=self.config.DEPENDENCY_INSTALL_TIMEOUT,
                    check=False,
                )

                # Requirements installation
                base_dependency_path = self.config.LANGUAGE_CONFIG['python']['dependency_file']
                req_file = os.path.join(repo_path, base_dependency_path)
                if not os.path.isfile(req_file):
                    self.logger.info("No requirements.txt found, skipping installation")
                    return True

                if os.path.getsize(req_file) == 0:
                    self.logger.info("Empty requirements.txt, skipping installation")
                    return True

                self.logger.info("Installing Python dependencies in python environment")
                install_cmd = [executable, '-m', 'pip', 'install', '-r', base_dependency_path]
                result = subprocess.run(
                    install_cmd,
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=self.config.DEPENDENCY_INSTALL_TIMEOUT,
                )

                if result.returncode == 0:
                    self.logger.info("Python dependencies installed in venv")
                    self.logger.debug(f"Install output: {result.stdout}")
                    return True

                if 'Could not open requirements file' in (result.stderr or ''):
                    self.logger.info("No requirements.txt present; skipping dependency installation")
                    return True

                self.logger.error(f"Dependency installation failed: {result.stderr}")
                return False

            # Non-Python languages use configured install command
            self.logger.info(f"Running install command for {language}")
            install_cmd = self.config.LANGUAGE_CONFIG[language]['install_command']
            result = subprocess.run(
                install_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=self.config.DEPENDENCY_INSTALL_TIMEOUT,
            )

            if result.returncode == 0:
                self.logger.info("Dependencies installed successfully")
                self.logger.debug(f"Install output: {result.stdout}")
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
