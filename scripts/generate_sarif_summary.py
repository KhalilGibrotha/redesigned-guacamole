#!/usr/bin/env python3
"""
Enhanced SARIF Report Summary Generator for GitHub Actions

This script processes SARIF (Static Analysis Results Interchange Format) files
and generates comprehensive markdown summaries for GitHub Actions workflow summaries.
"""

import json
import os
import glob
import sys
import logging
from typing import Tuple


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def escape_markdown(text: str) -> str:
    """Escape special markdown characters to prevent formatting issues."""
    if not isinstance(text, str):
        text = str(text)
    
    escape_chars = ['|', '*', '_', '`', '\\', '[', ']', '(', ')', '#', '+', '-', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def validate_file_path(file_path: str) -> bool:
    """Validate that the file path exists and is accessible."""
    if not file_path:
        return False
    
    try:
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK)
    except (OSError, TypeError):
        return False


def load_sarif_data(file_path: str) -> Tuple[dict, str]:
    """Load and validate SARIF data from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sarif_data = json.load(f)

        if not isinstance(sarif_data, dict):
            return {}, "SARIF file is not a valid JSON object"

        runs = sarif_data.get('runs', [])
        if not isinstance(runs, list):
            return {}, "SARIF 'runs' field is not an array"

        return sarif_data, ""

    except json.JSONDecodeError as e:
        return {}, f"Failed to parse JSON: {e}"
    except (OSError, IOError) as e:
        return {}, f"Failed to read file: {e}"


def process_sarif_results(sarif_data: dict) -> Tuple[dict, int]:
    """Process SARIF results and group them."""
    results = {}
    total_issues = 0

    runs = sarif_data.get('runs', [])
    for run_idx, run in enumerate(runs):
        if not isinstance(run, dict):
            logger.warning(f"Skipping invalid run {run_idx}")
            continue

        run_results = run.get('results', [])
        if not isinstance(run_results, list):
            logger.warning(f"Invalid results in run {run_idx}")
            continue

        for result in run_results:
            if not isinstance(result, dict):
                continue

            total_issues += 1
            rule_id = result.get('ruleId', 'unknown')

            # Handle different message formats in SARIF
            message_obj = result.get('message', {})
            if isinstance(message_obj, dict):
                message = message_obj.get('text', 'No description available')
            elif isinstance(message_obj, str):
                message = message_obj
            else:
                message = 'No description available'

            level = result.get('level', 'warning').upper()

            # Create unique key for grouping similar issues
            key = (level, str(rule_id), str(message))
            results[key] = results.get(key, 0) + 1

    return results, total_issues


def generate_report_content(results: dict) -> str:
    """Generate markdown report content from results."""
    if not results:
        return "| ✅ | None | No issues found! | 0 |\n"

    report_md = ""
    severity_order = {'ERROR': 0, 'WARNING': 1, 'INFO': 2, 'NOTE': 3}
    sorted_results = sorted(
        results.items(),
        key=lambda x: (severity_order.get(x[0][0], 999), x[0][1], x[0][2])
    )

    for (level, rule_id, message), count in sorted_results:
        escaped_rule = escape_markdown(rule_id)
        escaped_message = escape_markdown(message)
        report_md += f'| {level} | `{escaped_rule}` | {escaped_message} | {count} |\n'

    return report_md


def parse_sarif(file_path: str) -> Tuple[str, int]:
    """Parse a SARIF file and generate a markdown report."""
    if not validate_file_path(file_path):
        logger.warning(f"SARIF file not found: {file_path}")
        return "| ⚠️ | File Not Found | SARIF file not found or not accessible. | 0 |\n", 0

    # Check if file is empty
    try:
        if os.path.getsize(file_path) == 0:
            logger.warning(f"SARIF file is empty: {file_path}")
            return "| ⚠️ | Empty File | SARIF file exists but is empty. | 0 |\n", 0
    except OSError as e:
        logger.error(f"Error checking file size: {e}")
        return f"| ERROR | FILE_ERROR | Error accessing file: {escape_markdown(str(e))} | N/A |\n", 0

    # Load SARIF data
    sarif_data, error_msg = load_sarif_data(file_path)
    if error_msg:
        logger.error(f"Error loading {file_path}: {error_msg}")
        return f"| ERROR | INVALID_FORMAT | {escape_markdown(error_msg)} | N/A |\n", 0

    # Process results
    try:
        results, total_issues = process_sarif_results(sarif_data)
        report_content = generate_report_content(results)
        logger.info(f"Processed {file_path}: {total_issues} issues found")
        return report_content, total_issues
    except Exception as e:
        logger.error(f"Unexpected error parsing {file_path}: {e}")
        return f"| ERROR | UNKNOWN_ERROR | Unexpected error: {escape_markdown(str(e))} | N/A |\n", 0


def write_summary_section(summary_file: str, content: str) -> None:
    """Safely write content to the summary file."""
    try:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(content)
    except (OSError, IOError) as e:
        logger.error(f"Failed to write to summary file {summary_file}: {e}")
        raise


def main():
    """Main function to generate the comprehensive SARIF report summary."""
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if not summary_file:
        logger.error("GITHUB_STEP_SUMMARY environment variable not set")
        print("ERROR: GITHUB_STEP_SUMMARY environment variable not set", file=sys.stderr)
        sys.exit(1)

    reports_dir = './reports'
    logger.info("Starting SARIF summary generation")
    logger.info(f"Reports directory: {reports_dir}")
    logger.info(f"Summary will be written to: {summary_file}")

    # Discover SARIF reports
    all_reports = {}
    try:
        pattern = os.path.join(reports_dir, '**', '*.sarif')
        for report_path in glob.glob(pattern, recursive=True):
            dir_name = os.path.basename(os.path.dirname(report_path))
            name = dir_name.replace('-', ' ').replace('_', ' ').title()
            if name and validate_file_path(report_path):
                all_reports[name] = report_path
    except Exception as e:
        logger.error(f"Error discovering SARIF reports: {e}")

    logger.info(f"Found {len(all_reports)} valid report files")

    # Check if reports directory exists
    if not os.path.exists(reports_dir):
        logger.warning(f"Reports directory '{reports_dir}' does not exist")
        try:
            write_summary_section(summary_file,
                '## 📊 Security & Quality Reports Summary\n\n'
                '### ⚠️ No Reports Found\n\n'
                'The reports directory was not found. This may indicate:\n'
                '- No artifacts were generated by the scanning jobs\n'
                '- All scans passed without issues (no SARIF files created)\n'
                '- Artifact download failed or was skipped\n\n'
                '**This is often normal** - it means no security or linting issues were detected!\n\n'
            )
            logger.info("Summary generated with 'no reports found' message")
        except Exception as e:
            logger.error(f"Failed to write summary: {e}")
            sys.exit(1)
        return

    # Check if we found any valid SARIF files
    if not all_reports:
        logger.info("Reports directory exists but contains no valid SARIF files")
        try:
            all_files = glob.glob(os.path.join(reports_dir, '**', '*'), recursive=True)
            write_summary_section(summary_file,
                '## 📊 Security & Quality Reports Summary\n\n'
                '### ✅ No Issues Found\n\n'
                'Reports directory exists but no SARIF reports were found.\n'
                'This typically means all security and linting scans passed successfully!\n\n'
            )
            if len(all_files) > 0:
                write_summary_section(summary_file,
                    f'📁 **Files found in reports directory**: {len(all_files)}\n'
                    '(These may be log files or other artifacts)\n\n'
                )
            logger.info("Summary generated with 'no issues found' message")
        except Exception as e:
            logger.error(f"Failed to write summary: {e}")
            sys.exit(1)
        return

    # Process reports
    overall_total = 0
    try:
        write_summary_section(summary_file, '## 📊 Security & Quality Reports Summary\n\n')
        
        for tool_name, report_path in all_reports.items():
            logger.info(f"Processing {tool_name} report: {report_path}")

            write_summary_section(summary_file,
                f'### {tool_name} Report\n'
                '| Severity | Rule ID | Description | Total |\n'
                '|----------|---------|-------------|-------|\n'
            )

            report_content, issue_count = parse_sarif(report_path)
            overall_total += issue_count

            write_summary_section(summary_file, report_content + '\n')
            logger.info(f"Found {issue_count} issues in {tool_name}")

        # Final summary
        write_summary_section(summary_file, '\n---\n\n')
        if overall_total == 0:
            write_summary_section(summary_file,
                '### 🎉 Excellent! No Issues Found\n\n'
                'All security and quality scans completed successfully with no issues detected.\n'
            )
        else:
            write_summary_section(summary_file,
                f'### 📊 Total Issues Found: {overall_total}\n\n'
                'Please review the individual reports above for detailed information.\n'
            )

        logger.info(f"Summary generation complete. Total issues: {overall_total}")
        
    except Exception as e:
        logger.error(f"Failed to process reports: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Script starting...", file=sys.stderr)
    try:
        main()
        print("Script completed successfully", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Script failed with: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
