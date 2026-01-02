# automated_grader.py
import os
from time import time
from typing import Dict, Any, Optional
from copy import deepcopy
from grading_session import GradingSession
from repo_analyzer import RepositoryAnalyzer
from env_setup import EnvironmentSetup
from dependency_manager import DependencyManager
from app_runner import ApplicationRunner
from functional_tester import FunctionalTester
from code_verifier import CodeVerifier
from scoring_engine import ScoringEngine
from report_generator import ReportGenerator
from utils import (
    generate_unique_id,
    setup_logger,
    create_isolated_workspace,
    cleanup_workspace,
    parse_env_file,
)
from config import GraderConfig


class AutomatedGrader:
    """Main orchestrator for automated grading"""
    def __init__(self, config_overrides: Optional[Dict[str, Any]] = None):
        self.config = GraderConfig()
        if config_overrides:
            for key, value in config_overrides.items():
                setattr(self.config, key, value)

    def grade_submission(
        self,
        github_url: str,
        config_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Grade a single submission"""

        # Initialize session
        grading_id = generate_unique_id()
        workspace = create_isolated_workspace(grading_id)
        logger = setup_logger(grading_id)
        session = GradingSession(grading_id, workspace, logger)

        # Prepare configuration (allow per-call overrides without mutating base)
        local_config = deepcopy(self.config)
        if config_overrides:
            for key, value in config_overrides.items():
                setattr(local_config, key, value)

        logger.info("=" * 80)
        logger.info(f"Starting automated grading session: {grading_id}")
        logger.info(f"Repository: {github_url}")
        logger.info("=" * 80)

        process = None
        repo_path = None

        try:
            session.add_result('repository_url', github_url)

            # Step 1: Clone and analyze repository
            logger.info("\n[STEP 1/11] Cloning and analyzing repository...")
            analyzer = RepositoryAnalyzer(logger, config=local_config)

            repo_path = analyzer.clone_repository(github_url, os.path.join(workspace, 'repo'))

            if not repo_path:
                session.add_error("Failed to clone repository")
                return self._generate_failure_report(session, "Repository clone failed")

            session.add_result('repository_accessible', True)

            # Detect language
            language = analyzer.detect_language(repo_path)
            if not language:
                session.add_error("Could not detect programming language")
                return self._generate_failure_report(session, "Language detection failed")

            session.add_result('language_detected', language)

            # Find main file
            main_file = analyzer.find_main_file(repo_path, language)
            if not main_file:
                session.add_error("Main entry file not found")
                return self._generate_failure_report(session, "Main file not found")

            session.add_result('main_file_found', True)
            session.add_result('main_file', main_file)

            # Check for README
            has_readme = analyzer.check_readme(repo_path)
            session.add_result('has_readme', has_readme)

            # Step 2: Validate environment configuration
            logger.info("\n[STEP 2/11] Validating environment configuration...")
            has_env_template = analyzer.check_env_template(repo_path)

            missing_vars = []
            if has_env_template:
                env_file = None
                for name in ['.env.example', '.env.template', '.env.sample']:
                    path = os.path.join(repo_path, name)
                    if os.path.exists(path):
                        env_file = path
                        break

                if env_file:
                    env_vars = parse_env_file(env_file)
                    missing_vars = [var for var in local_config.REQUIRED_ENV_VARS
                                    if var not in env_vars]
            else:
                missing_vars = local_config.REQUIRED_ENV_VARS

            session.add_results('environment', {
                'has_env_template': has_env_template,
                'missing_variables': missing_vars
            })

            # Step 3: Setup test environment
            logger.info("\n[STEP 3/11] Setting up test environment...")
            env_setup = EnvironmentSetup(logger, config=local_config)

            if not env_setup.create_env_file(repo_path):
                session.add_error("Failed to create .env file")
                return self._generate_failure_report(session, "Environment setup failed")

            env_setup.setup_test_data_directory(repo_path)
            test_documents = env_setup.prepare_sample_documents(repo_path)

            if not test_documents:
                session.add_error("Failed to create test documents")
                return self._generate_failure_report(session, "Test data setup failed")

            # Step 4: Install dependencies
            logger.info("\n[STEP 4/11] Installing dependencies...")
            dep_manager = DependencyManager(logger, config=local_config)

            dep_success = dep_manager.install_dependencies(repo_path, language)
            session.add_result('dependencies_installed', dep_success)

            if not dep_success:
                session.add_error("Dependency installation failed")
                return self._generate_failure_report(session, "Dependency installation failed")

            # Step 5: Start application
            logger.info("\n[STEP 5/11] Starting application...")
            app_runner = ApplicationRunner(logger, config=local_config)

            process = app_runner.start_application(
                repo_path, language, main_file, self.config.SERVER_PORT
            )

            if not process:
                session.add_error("Failed to start application")
                return self._generate_failure_report(session, "Application start failed")

            # Wait for startup
            startup_success = app_runner.wait_for_startup()

            if not startup_success:
                session.add_error("Application did not start within timeout")
                return self._generate_failure_report(
                    session, "Application startup timeout", process
                )

            # Check health endpoint
            health_ok = app_runner.check_health_endpoint()
            session.add_result('application_started', health_ok)

            if not health_ok:
                logger.warning("Health check failed, but continuing tests...")

            # Step 6: Test document upload
            logger.info("\n[STEP 6/11] Testing document upload...")
            tester = FunctionalTester(logger, config=local_config)

            context = f"test-{int(time())}"
            upload_results = tester.test_document_upload(test_documents, context=context)
            session.add_results('upload', upload_results)

            # Step 7: Test RAG queries
            logger.info("\n[STEP 7/11] Testing RAG query functionality...")
            query_results = tester.test_rag_queries(context=context)
            session.add_results('queries', query_results)

            # Step 8: Verify technical requirements
            logger.info("\n[STEP 8/11] Verifying technical requirements...")
            verifier = CodeVerifier(logger)

            tech_results = verifier.verify_technical_requirements(repo_path)
            session.add_results('technical', tech_results)

            # Step 9: Calculate scores
            logger.info("\n[STEP 9/11] Calculating scores...")
            scorer = ScoringEngine(logger)

            final_scores = scorer.calculate_final_score(session.all_results)

            # Step 10: Generate reports
            logger.info("\n[STEP 10/11] Generating reports...")
            reporter = ReportGenerator(logger)

            html_report = reporter.generate_html_report(
                final_scores,
                session.all_results,
                grading_id,
            )
            json_report = reporter.generate_json_report(
                final_scores,
                session.all_results,
                grading_id,
            )

            html_path = reporter.save_report(html_report, f'{grading_id}.html')
            json_path = reporter.save_report(json_report, f'{grading_id}.json')

            # Step 11: Cleanup
            logger.info("\n[STEP 11/11] Cleaning up...")

            if local_config.MODE in ['interactive', 'debug']:
                # Wait for user response before terminating application.
                while True:
                    user_input = input("Type 'exit' to terminate the grading session and cleanup: ")
                    if user_input.strip().lower() == 'exit':
                        break

            if process:
                app_runner.stop_application(process)

            session.finalize()

            logger.info("=" * 80)
            logger.info("Grading complete!")
            logger.info(f"Final Score: {final_scores['total_score']:.1f}/100")
            logger.info(f"Grade: {final_scores['grade']}")
            logger.info(f"HTML Report: {html_path}")
            logger.info(f"JSON Report: {json_path}")
            logger.info("=" * 80)

            return {
                'success': True,
                'grading_id': grading_id,
                'scores': final_scores,
                'reports': {
                    'html': html_path,
                    'json': json_path
                }
            }

        except Exception as e:
            logger.error(f"Grading error: {e}", exc_info=True)
            session.add_error(str(e))

            if process:
                try:
                    ApplicationRunner(logger).stop_application(process)
                except Exception:
                    pass

            return self._generate_error_report(session, str(e))

        finally:
            # Always cleanup workspace
            if workspace and os.path.exists(workspace):
                logger.info("Cleaning up workspace...")
                cleanup_workspace(workspace)

    def _generate_failure_report(
        self,
        session: GradingSession,
        reason: str,
        process=None,
    ) -> Dict[str, Any]:
        """Generate report for failed grading"""
        if process:
            try:
                ApplicationRunner(session.logger).stop_application(process)
            except Exception:
                pass

        session.add_error(reason)
        session.finalize()

        scorer = ScoringEngine(session.logger)
        final_scores = scorer.calculate_final_score(session.all_results)

        reporter = ReportGenerator(session.logger)
        html_report = reporter.generate_html_report(
            final_scores,
            session.all_results,
            session.grading_id,
        )
        json_report = reporter.generate_json_report(
            final_scores,
            session.all_results,
            session.grading_id,
        )

        html_path = reporter.save_report(html_report, f'{session.grading_id}.html')
        json_path = reporter.save_report(json_report, f'{session.grading_id}.json')

        return {
            'success': False,
            'grading_id': session.grading_id,
            'reason': reason,
            'scores': final_scores,
            'reports': {
                'html': html_path,
                'json': json_path
            }
        }

    def _generate_error_report(self, session: GradingSession, error: str) -> Dict[str, Any]:
        """Generate report for grading errors"""
        return self._generate_failure_report(session, f"Error: {error}")
