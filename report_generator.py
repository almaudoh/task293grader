# report_generator.py
from datetime import datetime
import os
from typing import Dict, Any, List
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape


class ReportGenerator:
    """Generates grading reports in various formats"""

    def __init__(self, logger):
        self.logger = logger
        self.env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            autoescape=select_autoescape(['html', 'xml']),
        )

    def generate_html_report(
        self,
        scores: Dict[str, Any],
        results: Dict[str, Any],
        grading_id: str,
    ) -> str:
        """Generate HTML report using Jinja2 template"""

        total_score = scores['total_score']
        grade = scores['grade']
        breakdown = scores['breakdown']

        grade_colors = {
            'A': '#4CAF50',
            'B': '#8BC34A',
            'C': '#FFC107',
            'D': '#FF9800',
            'F': '#F44336',
        }
        grade_color = grade_colors.get(grade, '#999')

        # Prepare breakdown render data to simplify template logic
        from config import GraderConfig
        breakdown_render: List[Dict[str, Any]] = []
        for category, score in breakdown.items():
            max_score = GraderConfig.WEIGHTS[category]
            percentage = (score / max_score * 100) if max_score > 0 else 0
            category_name = category.replace('_', ' ').title()
            breakdown_render.append({
                'category_name': category_name,
                'score': score,
                'max_score': max_score,
                'percentage': percentage,
            })

        # Derived values for sections
        env_results = results.get('environment', {})
        missing_vars = env_results.get('missing_variables', [])
        upload_results = results.get('upload', [])
        successful_uploads = sum(1 for r in upload_results if r.get('success'))
        query_results = results.get('queries', [])
        successful_queries = sum(1 for r in query_results if r.get('success'))
        tech_results = results.get('technical', {})
        tech_passed = sum(1 for v in tech_results.values() if v)
        tech_labels = {
            'semantic_chunking': 'Semantic Chunking',
            'hf_embeddings': 'HuggingFace Embeddings',
            'chromadb_integration': 'ChromaDB Integration',
            'gemini_integration': 'Gemini Integration',
            'configurable_chunk': 'Configurable Chunk Length',
        }

        template = self.env.get_template('report.html.j2')
        return template.render(
            grading_id=grading_id,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_score=total_score,
            grade=grade,
            grade_color=grade_color,
            breakdown_render=breakdown_render,
            results=results,
            env_results=env_results,
            missing_vars=missing_vars,
            upload_results=upload_results,
            successful_uploads=successful_uploads,
            query_results=query_results,
            successful_queries=successful_queries,
            tech_results=tech_results,
            tech_passed=tech_passed,
            tech_labels=tech_labels,
        )

    def generate_json_report(self, scores: Dict[str, Any], results: Dict[str, Any], grading_id: str) -> str:
        """Generate JSON report"""
        report = {
            'grading_id': grading_id,
            'timestamp': datetime.now().isoformat(),
            'scores': scores,
            'results': results
        }
        return json.dumps(report, indent=2, default=str)

    def save_report(self, content: str, filename: str):
        """Save report to file"""
        try:
            import os
            os.makedirs('grading_reports', exist_ok=True)
            filepath = os.path.join('grading_reports', filename)

            with open(filepath, 'w') as f:
                f.write(content)

            self.logger.info(f"Report saved to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            return None
