## 1. Usage Example
```python
# example_usage.py
from automated_grader import AutomatedGrader

# Grade a single submission
grader = AutomatedGrader()

result = grader.grade_submission('https://github.com/student/rag-implementation')

print(f"Grade: {result['scores']['grade']}")
print(f"Score: {result['scores']['total_score']}/100")
print(f"Report: {result['reports']['html']}")
```

## 2. Batch Grading Script
```python
# batch_grade.py
import sys
from automated_grader import AutomatedGrader
import csv

def batch_grade(submissions_file, output_csv='results.csv'):
    """Grade multiple submissions and output results to CSV"""
    
    # Read submissions
    with open(submissions_file, 'r') as f:
        submissions = [line.strip() for line in f if line.strip()]
    
    grader = AutomatedGrader()
    results = []
    
    for i, url in enumerate(submissions, 1):
        print(f"\nGrading {i}/{len(submissions)}: {url}")
        
        result = grader.grade_submission(url)
        
        results.append({
            'url': url,
            'grade': result['scores']['grade'] if result['success'] else 'F',
            'score': result['scores']['total_score'] if result['success'] else 0,
            'success': result['success'],
            'html_report': result['reports']['html'] if 'reports' in result else ''
        })
    
    # Write to CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'grade', 'score', 'success', 'html_report'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Results written to {output_csv}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python batch_grade.py <submissions_file> [output_csv]")
        sys.exit(1)
    
    submissions_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else 'results.csv'
    
    batch_grade(submissions_file, output_csv)
```

This complete implementation provides a robust, production-ready automated grader for RAG system implementations. The system is modular, well-logged, and generates comprehensive HTML and JSON reports for each submission.