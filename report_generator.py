# report_generator.py
from datetime import datetime
from typing import Dict, Any
import json


class ReportGenerator:
    """Generates grading reports in various formats"""

    def __init__(self, logger):
        self.logger = logger

    def generate_html_report(self, scores: Dict[str, Any], results: Dict[str, Any], grading_id: str) -> str:
        """Generate HTML report"""

        total_score = scores['total_score']
        grade = scores['grade']
        breakdown = scores['breakdown']

        # Determine grade color
        grade_colors = {
            'A': '#4CAF50',
            'B': '#8BC34A',
            'C': '#FFC107',
            'D': '#FF9800',
            'F': '#F44336'
        }
        grade_color = grade_colors.get(grade, '#999')

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG System Grading Report - {grading_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .summary-card {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .grade-badge {{
            display: inline-block;
            padding: 10px 30px;
            border-radius: 50px;
            color: white;
            font-size: 48px;
            font-weight: bold;
            background-color: {grade_color};
        }}
        .breakdown {{
            margin: 30px 0;
        }}
        .breakdown-item {{
            margin: 15px 0;
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
        }}
        .breakdown-item h4 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .progress-bar {{
            background: #e0e0e0;
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        .details {{
            margin: 30px 0;
        }}
        .detail-section {{
            margin: 20px 0;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        .detail-header {{
            background: #f5f5f5;
            padding: 15px;
            font-weight: bold;
            cursor: pointer;
            user-select: none;
        }}
        .detail-header:hover {{
            background: #e0e0e0;
        }}
        .detail-content {{
            padding: 15px;
            display: none;
        }}
        .detail-content.show {{
            display: block;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status-success {{
            background: #E8F5E9;
            color: #2E7D32;
        }}
        .status-failure {{
            background: #FFEBEE;
            color: #C62828;
        }}
        .status-warning {{
            background: #FFF3E0;
            color: #EF6C00;
        }}
        pre {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .metadata {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 14px;
            color: #666;
        }}
    </style>
    <script>
        function toggleSection(id) {{
            const content = document.getElementById(id);
            content.classList.toggle('show');
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>🎓 RAG System Automated Grading Report</h1>

        <div class="metadata">
            <strong>Grading ID:</strong> {grading_id}<br>
            <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            <strong>Repository:</strong> {results.get('repository_url', 'N/A')}
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Final Grade</h3>
                <div class="value">
                    <span class="grade-badge">{grade}</span>
                </div>
            </div>
            <div class="summary-card">
                <h3>Total Score</h3>
                <div class="value">{total_score:.1f}/100</div>
            </div>
            <div class="summary-card">
                <h3>Language</h3>
                <div class="value" style="font-size: 24px;">{results.get('language_detected', 'N/A')}</div>
            </div>
        </div>

        <div class="breakdown">
            <h2>📊 Score Breakdown</h2>
"""

        # Add breakdown items
        for category, score in breakdown.items():
            from config import GraderConfig
            max_score = GraderConfig.WEIGHTS[category]
            percentage = (score / max_score * 100) if max_score > 0 else 0

            category_name = category.replace('_', ' ').title()

            html += f"""
            <div class="breakdown-item">
                <h4>{category_name}</h4>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {percentage}%">
                        {score:.1f}/{max_score}
                    </div>
                </div>
            </div>
"""

        html += """
        </div>

        <div class="details">
            <h2>📝 Detailed Results</h2>
"""

        # Repository Details
        html += f"""
            <div class="detail-section">
                <div class="detail-header" onclick="toggleSection('repo-details')">
                    ▶ Repository Setup
                    <span class="status-badge {'status-success' if results.get('repository_accessible') else 'status-failure'}">
                        {'✓ Pass' if results.get('repository_accessible') else '✗ Fail'}
                    </span>
                </div>
                <div id="repo-details" class="detail-content">
                    <p><strong>Language Detected:</strong> {results.get('language_detected', 'None')}</p>
                    <p><strong>Main File Found:</strong> {'Yes' if results.get('main_file_found') else 'No'}</p>
                    <p><strong>README Present:</strong> {'Yes' if results.get('has_readme') else 'No'}</p>
                </div>
            </div>
"""

        # Environment Details
        env_results = results.get('environment', {})
        missing_vars = env_results.get('missing_variables', [])
        html += f"""
            <div class="detail-section">
                <div class="detail-header" onclick="toggleSection('env-details')">
                    ▶ Environment Configuration
                    <span class="status-badge {'status-success' if not missing_vars else 'status-warning'}">
                        {'✓ Complete' if not missing_vars else f'⚠ {len(missing_vars)} Missing'}
                    </span>
                </div>
                <div id="env-details" class="detail-content">
                    <p><strong>.env Template Present:</strong> {'Yes' if env_results.get('has_env_template') else 'No'}</p>
                    {f'<p><strong>Missing Variables:</strong> {", ".join(missing_vars)}</p>' if missing_vars else '<p>✓ All required variables documented</p>'}
                </div>
            </div>
"""

        # Upload Details
        upload_results = results.get('upload', [])
        successful_uploads = sum(1 for r in upload_results if r.get('success'))
        html += f"""
            <div class="detail-section">
                <div class="detail-header" onclick="toggleSection('upload-details')">
                    ▶ Document Upload Tests
                    <span class="status-badge {'status-success' if successful_uploads == len(upload_results) else 'status-warning'}">
                        {successful_uploads}/{len(upload_results)} Successful
                    </span>
                </div>
                <div id="upload-details" class="detail-content">
"""

        for upload in upload_results:
            status_class = 'status-success' if upload.get('success') else 'status-failure'
            html += f"""
                    <p>
                        <span class="status-badge {status_class}">
                            {'✓' if upload.get('success') else '✗'}
                        </span>
                        <strong>{upload.get('document')}:</strong> 
                        {upload.get('status_code', 'Error')}
                    </p>
"""

        html += """
                </div>
            </div>
"""

        # Query Details
        query_results = results.get('queries', [])
        successful_queries = sum(1 for r in query_results if r.get('success'))
        html += f"""
            <div class="detail-section">
                <div class="detail-header" onclick="toggleSection('query-details')">
                    ▶ RAG Query Tests
                    <span class="status-badge {'status-success' if successful_queries == len(query_results) else 'status-warning'}">
                        {successful_queries}/{len(query_results)} Successful
                    </span>
                </div>
                <div id="query-details" class="detail-content">
"""

        for query in query_results:
            status_class = 'status-success' if query.get('success') else 'status-failure'
            relevance = query.get('relevance_score', 0)

            html += f"""
                    <div style="margin: 15px 0; padding: 10px; background: #f9f9f9; border-radius: 4px;">
                        <p><strong>Query:</strong> {query.get('query')}</p>
                        <p>
                            <span class="status-badge {status_class}">
                                {'✓' if query.get('success') else '✗'}
                            </span>
                            Status: {query.get('status_code', 'Error')}
                        </p>
                        {f'<p><strong>Relevance Score:</strong> {relevance:.1f}%</p>' if 'relevance_score' in query else ''}
                        <p><strong>Has Context:</strong> {'Yes' if query.get('has_context') else 'No'}</p>
                        <p><strong>Has Answer:</strong> {'Yes' if query.get('has_answer') else 'No'}</p>
                    </div>
"""

        html += """
                </div>
            </div>
"""

        # Technical Requirements
        tech_results = results.get('technical', {})
        tech_passed = sum(1 for v in tech_results.values() if v)
        html += f"""
            <div class="detail-section">
                <div class="detail-header" onclick="toggleSection('tech-details')">
                    ▶ Technical Requirements
                    <span class="status-badge {'status-success' if tech_passed == len(tech_results) else 'status-warning'}">
                        {tech_passed}/{len(tech_results)} Verified
                    </span>
                </div>
                <div id="tech-details" class="detail-content">
"""

        tech_labels = {
            'semantic_chunking': 'Semantic Chunking',
            'hf_embeddings': 'HuggingFace Embeddings',
            'chromadb_integration': 'ChromaDB Integration',
            'gemini_integration': 'Gemini Integration',
            'configurable_chunk': 'Configurable Chunk Length'
        }

        for key, label in tech_labels.items():
            verified = tech_results.get(key, False)
            status_class = 'status-success' if verified else 'status-failure'
            html += f"""
                    <p>
                        <span class="status-badge {status_class}">
                            {'✓' if verified else '✗'}
                        </span>
                        {label}
                    </p>
"""

        html += """
                </div>
            </div>
        </div>

        <div style="margin-top: 40px; padding: 20px; background: #E3F2FD; border-radius: 8px;">
            <h3>📌 Summary</h3>
"""

        if grade in ['A', 'B']:
            html += f"""
            <p>✅ <strong>Excellent work!</strong> The RAG system implementation meets all or most requirements with a grade of <strong>{grade}</strong>.</p>
"""
        elif grade == 'C':
            html += f"""
            <p>⚠️ <strong>Good effort!</strong> The implementation is functional but has room for improvement. Grade: <strong>{grade}</strong></p>
"""
        else:
            html += f"""
            <p>❌ <strong>Needs improvement.</strong> Several requirements were not met. Grade: <strong>{grade}</strong></p>
            <p>Please review the detailed feedback above and address the failing components.</p>
"""

        html += """
        </div>
    </div>
</body>
</html>
"""

        return html

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
