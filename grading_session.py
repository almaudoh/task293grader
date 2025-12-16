# grading_session.py
from typing import Dict, Any
import json
from datetime import datetime


class GradingSession:
    """Manages state for a single grading session"""

    def __init__(self, grading_id: str, workspace: str, logger):
        self.grading_id = grading_id
        self.workspace = workspace
        self.logger = logger
        self.results = {}
        self.start_time = datetime.now()
        self.end_time = None
        self.errors = []

    def add_result(self, key: str, value: Any):
        """Add a single result"""
        self.results[key] = value
        self.logger.info(f"Result added - {key}: {value}")

    def add_results(self, category: str, results: Any):
        """Add results for a category"""
        self.results[category] = results
        self.logger.info(f"Results added for category: {category}")

    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append({
            'timestamp': datetime.now().isoformat(),
            'error': error
        })
        self.logger.error(error)

    @property
    def all_results(self) -> Dict[str, Any]:
        """Get all results"""
        return self.results

    def finalize(self):
        """Finalize the grading session"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        self.results['_metadata'] = {
            'grading_id': self.grading_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': duration,
            'errors': self.errors
        }

    def to_json(self) -> str:
        """Convert session to JSON"""
        return json.dumps(self.results, indent=2, default=str)
