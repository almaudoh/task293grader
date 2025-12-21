# app_runner.py
import subprocess
import requests
from typing import Optional
from config import GraderConfig
from utils import wait_for_port


class ApplicationRunner:
    """Manages application startup and health checks"""

    def __init__(self, logger, config: Optional[GraderConfig] = None):
        self.logger = logger
        self.config = config or GraderConfig()

    def start_application(
        self, repo_path: str, language: str, main_file: str, port: Optional[int] = None
    ) -> Optional[subprocess.Popen]:
        """Start the application"""
        self.logger.info(f"Starting {language} application")

        if language not in self.config.LANGUAGE_CONFIG:
            self.logger.error(f"Unsupported language: {language}")
            return None

        run_cmd = self.config.LANGUAGE_CONFIG[language]['run_command'].copy()

        # Adjust command based on language
        if language == 'nodejs':
            run_cmd.append(main_file)
        elif language == 'python':
            port = port or self.config.SERVER_PORT
            run_cmd.extend(['--port', str(port)])
        elif language == 'golang':
            run_cmd.append(main_file)
        elif language == 'dart':
            run_cmd.append(main_file)

        try:
            process = subprocess.Popen(
                run_cmd,
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.logger.info(f"Application process started (PID: {process.pid})")
            return process

        except Exception as e:
            self.logger.error(f"Failed to start application: {e}")
            return None

    def wait_for_startup(self, port: Optional[int] = None, timeout: Optional[int] = None) -> bool:
        """Wait for application to start"""
        if timeout is None:
            timeout = self.config.APP_STARTUP_TIMEOUT

        if port is None:
            port = self.config.SERVER_PORT

        self.logger.info(f"Waiting for application on port {port}")

        if wait_for_port(port, timeout=timeout):
            self.logger.info("Application is responding")
            return True

        self.logger.error("Application failed to start within timeout")
        return False

    def check_health_endpoint(self) -> bool:
        """Check if health endpoint responds"""
        health_url = f"{self.config.SERVER_BASE_URL}{self.config.ENDPOINT_PREFIX}" \
                     f"{self.config.REQUIRED_ENDPOINTS['health']['path']}"

        try:
            self.logger.info(f"Checking health endpoint: {health_url}")
            response = requests.get(
                health_url,
                timeout=self.config.API_REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                self.logger.info("Health check passed")
                return True
            else:
                self.logger.warning(f"Health check returned status {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def stop_application(self, process: subprocess.Popen):
        """Stop the application"""
        if process:
            try:
                self.logger.info(f"Stopping application (PID: {process.pid})")
                process.terminate()

                # Wait up to 10 seconds for graceful shutdown
                try:
                    process.wait(timeout=10)
                    self.logger.info("Application stopped gracefully")
                except subprocess.TimeoutExpired:
                    self.logger.warning("Force killing application")
                    process.kill()
                    process.wait()

            except Exception as e:
                self.logger.error(f"Error stopping application: {e}")
