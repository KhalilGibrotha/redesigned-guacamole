#!/usr/bin/env python3
"""
Generate a comprehensive summary from all SARIF reports.

This script processes SARIF files from various security and linting tools
and generates a markdown summary for GitHub Actions.
"""

import json
import os
import glob
import sys


def parse_sarif(file_path):
    """
    Parse a SARIF file and return formatted markdown content and issue count.
    
    Args:
        file_path (str): Path to the SARIF file
        
    Returns:
        tuple: (formatted_markdown_string, total_issue_count)
    """
    if not os.path.exists(file_path):
        return "| N/A | No report found | This scan may have failed to produce a report. | N/A |\n", 0

    report_md = ""
    results = {}
    total_issues = 0
    
    try:
        with open(file_path) as f:
            sarif_data = json.load(f)
            for run in sarif_data.get('runs', []):
                for result in run.get('results', []):
                    total_issues += 1
                    rule_id = result.get('ruleId', 'unknown')
                    message = result.get('message', {}).get('text', 'No description available')
                    level = result.get('level', 'warning').upper()
                    key = (level, rule_id, message)
                    results[key] = results.get(key, 0) + 1
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        return f"| ERROR | PARSE_ERROR | Failed to parse SARIF file: {str(e)} | N/A |\n", 0
    
    if not results:
        report_md += "| ✅ | None | No issues found! | 0 |\n"
    else:
        for (level, rule, msg), count in sorted(results.items()):
            # Escape markdown special characters in message
            msg_escaped = msg.replace('|', '\\|').replace('\n', ' ').replace('\r', '')
            report_md += f'| {level} | `{rule}` | {msg_escaped} | {count} |\n'
    
    return report_md, total_issues


def main():
    """Main function to generate the comprehensive SARIF report summary."""
    # Get environment variables
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if not summary_file:
        print("ERROR: GITHUB_STEP_SUMMARY environment variable not set")
        sys.exit(1)
    
    reports_dir = './reports'
    overall_total = 0

    # Define all the reports to process
    all_reports = {
        "Trivy Vulnerability Scan": os.path.join(reports_dir, 'trivy-results', 'trivy-results.sarif'),
        "Ansible Lint": os.path.join(reports_dir, 'ansible-lint-results', 'ansible-lint-results.sarif')
        # Add other tools here as you generate more SARIF files
    }
    
    print(f"Processing {len(all_reports)} report types...")
    print(f"Reports directory: {reports_dir}")
    print(f"Summary will be written to: {summary_file}")
    
    # Check if reports directory exists
    if not os.path.exists(reports_dir):
        print(f"WARNING: Reports directory '{reports_dir}' does not exist")
        with open(summary_file, 'a') as f:
            f.write('## ⚠️ No Reports Found\n')
            f.write('The reports directory was not found. This may indicate that the scanning jobs failed to run or produce artifacts.\n\n')
        return
    
    # Process each report
    for tool_name, report_path in all_reports.items():
        print(f"Processing {tool_name} report: {report_path}")
        
        with open(summary_file, 'a') as f:
            f.write(f'## {tool_name} Report\n')
            f.write('| Severity | Rule ID | Description | Total |\n')
            f.write('|----------|---------|-------------|-------|\n')
        
        report_content, issue_count = parse_sarif(report_path)
        overall_total += issue_count
        
        with open(summary_file, 'a') as f:
            f.write(report_content)
            f.write('\n')
        
        print(f"  - Found {issue_count} issues in {tool_name}")

    # Final summary
    with open(summary_file, 'a') as f:
        f.write('---\n')
        f.write(f'### Grand Total of All Issues Found: {overall_total}\n')
    
    print(f"Summary generation complete. Total issues across all tools: {overall_total}")


if __name__ == "__main__":
    main()
