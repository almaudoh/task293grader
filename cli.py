#!/usr/bin/env python3
import argparse
import sys
from automated_grader import AutomatedGrader


def main():
    parser = argparse.ArgumentParser(
        description='Automated Grader for RAG System Implementations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/student/rag-project
  %(prog)s --batch submissions.txt
  %(prog)s --url https://github.com/student/rag-project --output custom_report
"""
    )

    parser.add_argument(
        'url',
        nargs='?',
        help='GitHub repository URL to grade'
    )

    parser.add_argument(
        '--batch',
        '-b',
        help='File containing list of GitHub URLs (one per line)'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Output directory for reports (default: grading_reports)'
    )

    parser.add_argument(
        '--yaml-override',
        '-y',
        help='Path to YAML file with configuration overrides'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    if not args.url and not args.batch:
        parser.print_help()
        sys.exit(1)

    grader = AutomatedGrader()

    if args.yaml_override:
        try:
            grader.config.override_from_yaml(args.yaml_override)
        except (FileNotFoundError, ValueError, KeyError) as exc:
            print(f"❌ Error loading YAML overrides: {exc}")
            sys.exit(1)

    if args.batch:
        # Batch grading
        print(f"📚 Batch grading from {args.batch}")
        try:
            with open(args.batch, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            print(f"Found {len(urls)} submissions to grade\n")

            results = []
            for i, url in enumerate(urls, 1):
                print(f"\n{'='*80}")
                print(f"Grading submission {i}/{len(urls)}: {url}")
                print(f"{'='*80}\n")

                result = grader.grade_submission(url)
                results.append(result)

                if result['success']:
                    print(
                        f"✅ Grade: {result['scores']['grade']} "
                        f"({result['scores']['total_score']:.1f}/100)"
                    )
                else:
                    print(f"❌ Grading failed: {result.get('reason', 'Unknown error')}")

            # Summary
            print(f"\n{'='*80}")
            print("📊 BATCH GRADING SUMMARY")
            print(f"{'='*80}")

            successful = [r for r in results if r['success']]
            print(f"Total: {len(results)}")
            print(f"Successful: {len(successful)}")
            print(f"Failed: {len(results) - len(successful)}")

            if successful:
                grades = {}
                for result in successful:
                    grade = result['scores']['grade']
                    grades[grade] = grades.get(grade, 0) + 1

                print("\nGrade Distribution:")
                for grade in ['A', 'B', 'C', 'D', 'F']:
                    count = grades.get(grade, 0)
                    if count > 0:
                        print(f"  {grade}: {count}")

                avg_score = sum(r['scores']['total_score'] for r in successful) / len(successful)
                print(f"\nAverage Score: {avg_score:.1f}/100")

        except FileNotFoundError:
            print(f"❌ Error: File not found: {args.batch}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    else:
        # Single grading
        print(f"🎓 Grading submission: {args.url}\n")

        result = grader.grade_submission(args.url)

        if result['success']:
            print("\n✅ Grading Complete!")
            print(f"Grade: {result['scores']['grade']}")
            print(f"Score: {result['scores']['total_score']:.1f}/100")
            print("\n📄 Reports generated:")
            print(f"  HTML: {result['reports']['html']}")
            print(f"  JSON: {result['reports']['json']}")
        else:
            print("\n❌ Grading Failed")
            print(f"Reason: {result.get('reason', 'Unknown error')}")
            if 'reports' in result:
                print("\n📄 Partial report generated:")
                print(f"  HTML: {result['reports']['html']}")
            sys.exit(1)


if __name__ == '__main__':
    main()
