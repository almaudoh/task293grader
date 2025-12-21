# scoring_engine.py
from typing import Dict, Any, Optional
from config import GraderConfig


class ScoringEngine:
    """Calculates scores and generates grades"""

    def __init__(self, logger, config: Optional[GraderConfig] = None):
        self.logger = logger
        self.config = config or GraderConfig()

    def calculate_repo_score(self, results: Dict[str, Any]) -> float:
        """Calculate repository setup score (15 points)"""
        score = 0.0
        max_score = self.config.WEIGHTS['repository_setup']

        # Accessible repository (5 points)
        if results.get('repository_accessible', False):
            score += 5

        # Correct structure - language detected and main file found (5 points)
        if results.get('language_detected') and results.get('main_file_found'):
            score += 5

        # Documentation - README exists (5 points)
        if results.get('has_readme', False):
            score += 5

        self.logger.info(f"Repository score: {score}/{max_score}")
        return score

    def calculate_env_score(self, results: Dict[str, Any]) -> float:
        """Calculate environment configuration score (15 points)"""
        score = 0.0
        max_score = self.config.WEIGHTS['environment_config']

        env_results = results.get('environment', {})

        # Has .env template (5 points)
        if env_results.get('has_env_template', False):
            score += 5

        # All required variables present (10 points)
        missing_vars = env_results.get('missing_variables', [])
        if not missing_vars:
            score += 10
        else:
            # Partial credit
            required_count = len(self.config.REQUIRED_ENV_VARS)
            missing_count = len(missing_vars)
            present_count = required_count - missing_count
            score += (present_count / required_count) * 10

        self.logger.info(f"Environment score: {score}/{max_score}")
        return score

    def calculate_dep_score(self, results: Dict[str, Any]) -> float:
        """Calculate dependency management score (10 points)"""
        score = 0.0
        max_score = self.config.WEIGHTS['dependencies']

        if results.get('dependencies_installed', False):
            score = max_score

        self.logger.info(f"Dependencies score: {score}/{max_score}")
        return score

    def calculate_startup_score(self, results: Dict[str, Any]) -> float:
        """Calculate application startup score (10 points)"""
        score = 0.0
        max_score = self.config.WEIGHTS['startup']

        if results.get('application_started', False):
            score = max_score

        self.logger.info(f"Startup score: {score}/{max_score}")
        return score

    def calculate_upload_score(self, results: Dict[str, Any]) -> float:
        """Calculate document upload score (15 points)"""
        score = 0.0
        max_score = self.config.WEIGHTS['upload']

        upload_results = results.get('upload', [])

        if not upload_results:
            self.logger.warning("No upload results found")
            return 0.0

        # Upload endpoint works (10 points)
        successful_uploads = sum(1 for r in upload_results if r.get('success', False))
        total_uploads = len(upload_results)

        if successful_uploads > 0:
            score += 10  # At least one upload worked

            # Documents processed correctly (5 points - bonus for all successful)
            if successful_uploads == total_uploads:
                score += 5
            else:
                # Partial credit
                score += (successful_uploads / total_uploads) * 5

        self.logger.info(f"Upload score: {score}/{max_score}")
        return score

    def calculate_query_score(self, results: Dict[str, Any]) -> float:
        """Calculate RAG query functionality score (25 points)"""
        score = 0.0
        max_score = self.config.WEIGHTS['query']

        query_results = results.get('queries', [])

        if not query_results:
            self.logger.warning("No query results found")
            return 0.0

        successful_queries = [r for r in query_results if r.get('success', False)]

        if not successful_queries:
            return 0.0

        # Query endpoint works (10 points)
        score += 10

        # Retrieves relevant context (8 points)
        queries_with_context = sum(1 for r in successful_queries if r.get('has_context', False))
        if queries_with_context > 0:
            context_score = (queries_with_context / len(successful_queries)) * 8
            score += context_score

        # Generates coherent answers (7 points)
        queries_with_answers = [r for r in successful_queries if r.get('has_answer', False)]

        if queries_with_answers:
            # Check relevance scores
            relevance_scores = [r.get('relevance_score', 0) for r in queries_with_answers
                                if 'relevance_score' in r]

            if relevance_scores:
                avg_relevance = sum(relevance_scores) / len(relevance_scores)
                answer_score = (avg_relevance / 100) * 7
                score += answer_score
            else:
                # Give partial credit if answers exist but no relevance score
                score += 4

        self.logger.info(f"Query score: {score}/{max_score}")
        return score

    def calculate_technical_score(self, results: Dict[str, Any]) -> float:
        """Calculate technical requirements score (10 points)"""
        score = 0.0
        max_score = self.config.WEIGHTS['technical']

        tech_results = results.get('technical', {})

        if not tech_results:
            self.logger.warning("No technical verification results found")
            return 0.0

        # Each requirement is worth 2 points
        requirements = [
            'semantic_chunking',
            'hf_embeddings',
            'chromadb_integration',
            'gemini_integration',
            'configurable_chunk'
        ]

        for req in requirements:
            if tech_results.get(req, False):
                score += 2

        self.logger.info(f"Technical score: {score}/{max_score}")
        return score

    def calculate_final_score(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final score with breakdown"""
        self.logger.info("Calculating final score")

        scores = {
            'repository_setup': self.calculate_repo_score(results),
            'environment_config': self.calculate_env_score(results),
            'dependencies': self.calculate_dep_score(results),
            'startup': self.calculate_startup_score(results),
            'upload': self.calculate_upload_score(results),
            'query': self.calculate_query_score(results),
            'technical': self.calculate_technical_score(results)
        }

        total_score = sum(scores.values())
        grade = self.assign_grade(total_score)

        self.logger.info(f"Final score: {total_score}/100 - Grade: {grade}")

        return {
            'total_score': total_score,
            'grade': grade,
            'breakdown': scores,
            'max_score': 100
        }

    def assign_grade(self, score: float) -> str:
        """Assign letter grade based on score"""
        for grade, threshold in sorted(
            self.config.GRADE_THRESHOLDS.items(), key=lambda x: x[1], reverse=True
        ):
            if score >= threshold:
                return grade
        return 'F'
