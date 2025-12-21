# functional_tester.py
import json
import os
import requests
import time
from typing import Dict, List, Any, Optional
from config import GraderConfig
from utils import calculate_relevance, strip_html_tags


class FunctionalTester:
    """Tests RAG system functionality"""

    def __init__(self, logger, config: Optional[GraderConfig] = None):
        self.logger = logger
        self.config = config or GraderConfig()

    def test_document_upload(self, documents: List[str]) -> List[Dict[str, Any]]:
        """Test document upload functionality"""
        self.logger.info("Testing document upload")
        results = []

        for doc_path in documents:
            try:
                self.logger.info(f"Uploading document: {doc_path}")

                with open(doc_path, 'rb') as f:
                    files = {
                        self.config.REQUIRED_ENDPOINTS['upload']['props'][0]:
                        (doc_path.split('/')[-1], f, 'text/plain')
                    }

                    response = requests.post(
                        f"{self.config.SERVER_BASE_URL}{self.config.ENDPOINT_PREFIX}"
                        f"{self.config.REQUIRED_ENDPOINTS['upload']['path']}",
                        files=files,
                        timeout=self.config.API_REQUEST_TIMEOUT
                    )

                success = response.status_code in [200, 201]

                result = {
                    'document': doc_path.split('/')[-1],
                    'success': success,
                    'status_code': response.status_code
                }

                if success:
                    try:
                        result['response'] = response.json()
                    except Exception:
                        result['response'] = response.text
                else:
                    result['error'] = response.text
                    self.logger.error(
                        f"Upload failed with status {response.status_code}:"
                        f" {strip_html_tags(response.text)}"
                    )

                results.append(result)
                self.logger.info(f"Upload {'succeeded' if success else 'failed'}: {doc_path}:"
                                 f" {json.dumps(result)}")

                # Small delay between uploads
                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Upload error for {doc_path}: {e}")
                results.append({
                    'document': doc_path.split('/')[-1],
                    'success': False,
                    'error': str(e)
                })

        success_count = sum(1 for r in results if r['success'])
        self.logger.info(f"Upload test complete: {success_count}/{len(documents)} successful")

        return results

    def test_query_endpoint(self, query: str) -> Dict[str, Any]:
        """Test a single query"""
        try:
            self.logger.info(f"Testing query: {query}")

            response = requests.post(
                f"{self.config.SERVER_BASE_URL}{self.config.ENDPOINT_PREFIX}"
                f"{self.config.REQUIRED_ENDPOINTS['query']['path']}",
                json={self.config.REQUIRED_ENDPOINTS['query']['props'][0]: query},
                timeout=self.config.API_REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()

                # Check for expected response structure
                context_keys = ['context', 'retrieved_chunks', 'chunks', 'documents']
                has_context = any(key in data for key in context_keys)
                answer_keys = ['answer', 'response', 'result']
                has_answer = any(key in data for key in answer_keys)

                # Extract answer text
                answer_text = ''
                for key in ['answer', 'response', 'result', 'text']:
                    if key in data:
                        answer_text = str(data[key])
                        break

                return {
                    'success': True,
                    'status_code': response.status_code,
                    'has_context': has_context,
                    'has_answer': has_answer,
                    'answer_text': answer_text,
                    'response_data': data
                }
            else:
                self.logger.error(
                    f"Query failed with status {response.status_code}:"
                    f" {strip_html_tags(response.text)}"
                )
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }

        except Exception as e:
            self.logger.error(f"Query test error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def test_rag_queries(self) -> List[Dict[str, Any]]:
        """Test RAG query functionality with multiple queries"""
        self.logger.info("Testing RAG queries")
        results = []

        for test_query in self.config.TEST_QUERIES:
            query_text = test_query['question']
            expected_keywords = test_query['expected_keywords']

            result = self.test_query_endpoint(query_text)
            result['query'] = query_text

            # Calculate relevance if we got an answer
            if result.get('success') and result.get('answer_text'):
                relevance = calculate_relevance(result['answer_text'], expected_keywords)
                result['relevance_score'] = relevance
                result['expected_keywords'] = expected_keywords

                self.logger.info(f"Query relevance score: {relevance:.1f}%")

            results.append(result)

            # Small delay between queries
            time.sleep(1)

        success_count = sum(1 for r in results if r.get('success'))
        self.logger.info(f"Query test complete: {success_count}/{len(results)} successful")

        return results

    def test_semantic_chunking(self, repo_path: str) -> bool:
        """Check if semantic chunking is implemented"""
        self.logger.info("Checking for semantic chunking implementation")

        search_terms = ['chunk', 'semantic', 'split', 'segment']

        try:
            # Search in common file locations
            excluded_dirs = {'node_modules', 'venv', '__pycache__', '.git'}
            for root, dirs, files in os.walk(repo_path):
                # Skip node_modules, venv, etc.
                dirs[:] = [d for d in dirs if d not in excluded_dirs]

                for file in files:
                    if file.endswith(('.py', '.js', '.go', '.dart')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                if any(term in content for term in search_terms):
                                    self.logger.info(f"Found chunking implementation in {file}")
                                    return True
                        except Exception:
                            continue

            self.logger.warning("Could not verify semantic chunking implementation")
            return False

        except Exception as e:
            self.logger.error(f"Error checking semantic chunking: {e}")
            return False
