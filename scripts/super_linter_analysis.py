#!/usr/bin/env python3
"""
Super Linter Analysis Script
Analyzes Super Linter results and provides comprehensive quality reporting.
"""

import glob
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


class SuperLinterAnalyzer:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.results = {"checks": {}, "summary": {}, "health_score": 0}

    def get_linter_status(self, linter_name: str, log_pattern: Optional[str] = None) -> Dict[str, Any]:
        """Get status for a specific linter"""
        status = {"enabled": True, "errors": 0, "warnings": 0, "files_checked": 0, "status": "✅ PASS", "details": ""}

        # Check if Super Linter log files exist
        if log_pattern:
            log_files = glob.glob(log_pattern, recursive=True)
            if log_files:
                for log_file in log_files:
                    try:
                        with open(log_file, "r") as f:
                            content = f.read()
                            # Parse errors/warnings from log
                            errors = len(re.findall(r"ERROR|FAIL|CRITICAL", content, re.IGNORECASE))
                            warnings = len(re.findall(r"WARNING|WARN", content, re.IGNORECASE))

                            status["errors"] += errors
                            status["warnings"] += warnings

                            if errors > 0:
                                status["status"] = "❌ FAIL"
                                status["details"] = f"{errors} errors"
                            elif warnings > 0:
                                status["status"] = "⚠️ WARN"
                                status["details"] = f"{warnings} warnings"
                    except Exception as e:
                        status["details"] = f"Error reading log: {str(e)}"

        return status

    def analyze_yaml_files(self) -> Dict[str, Any]:
        """Analyze YAML files"""
        yaml_files = list(self.workspace_root.glob("**/*.yml")) + list(self.workspace_root.glob("**/*.yaml"))
        yaml_files = [f for f in yaml_files if not any(skip in str(f) for skip in [".git", ".venv", "node_modules"])]

        errors = 0
        warnings = 0

        for yaml_file in yaml_files:
            try:
                content = yaml_file.read_text()
                # Basic YAML quality checks
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if len(line) > 160:
                        warnings += 1
                    if "\t" in line:
                        errors += 1
            except Exception:
                errors += 1

        status = "✅ PASS"
        details = f"{len(yaml_files)} files"
        if errors > 0:
            status = "❌ FAIL"
            details = f"{errors} errors, {len(yaml_files)} files"
        elif warnings > 0:
            status = "⚠️ WARN"
            details = f"{warnings} warnings, {len(yaml_files)} files"

        return {
            "enabled": True,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(yaml_files),
            "status": status,
            "details": details,
        }

    def analyze_ansible_files(self) -> Dict[str, Any]:
        """Analyze Ansible files"""
        ansible_files = []
        for pattern in ["**/playbook*.yml", "**/site.yml", "**/main.yml", "playbooks/**/*.yml", "roles/**/*.yml"]:
            ansible_files.extend(list(self.workspace_root.glob(pattern)))

        # Remove duplicates and filter out excluded paths
        ansible_files = list(set([f for f in ansible_files if not any(skip in str(f) for skip in [".git", ".venv"])]))

        errors = 0
        warnings = 0

        for ansible_file in ansible_files:
            try:
                content = ansible_file.read_text()
                # Check for Ansible best practices
                if "hosts:" in content and "name:" not in content:
                    warnings += 1
                if "sudo:" in content:
                    warnings += 1
                if re.search(r"{{.*\|.*shell.*}}", content):
                    errors += 1
            except Exception:
                errors += 1

        status = "✅ PASS"
        details = f"{len(ansible_files)} files"
        if errors > 0:
            status = "❌ FAIL"
            details = f"{errors} errors, {len(ansible_files)} files"
        elif warnings > 0:
            status = "⚠️ WARN"
            details = f"{warnings} warnings, {len(ansible_files)} files"

        return {
            "enabled": len(ansible_files) > 0,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(ansible_files),
            "status": status,
            "details": details,
        }

    def analyze_python_files(self) -> Dict[str, Any]:
        """Analyze Python files"""
        python_files = list(self.workspace_root.glob("**/*.py"))
        python_files = [f for f in python_files if not any(skip in str(f) for skip in [".git", ".venv", "__pycache__"])]

        errors = 0
        warnings = 0

        for py_file in python_files:
            try:
                content = py_file.read_text()
                lines = content.split("\n")
                for line in lines:
                    if len(line) > 120:
                        warnings += 1
                    if re.search(r"print\s*\(.*\)", line) and "debug" not in line.lower():
                        warnings += 1
            except Exception:
                errors += 1

        status = "✅ PASS"
        details = f"{len(python_files)} files"
        if errors > 0:
            status = "❌ FAIL"
            details = f"{errors} errors, {len(python_files)} files"
        elif warnings > 0:
            status = "⚠️ WARN"
            details = f"{warnings} warnings, {len(python_files)} files"

        return {
            "enabled": len(python_files) > 0,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(python_files),
            "status": status,
            "details": details,
        }

    def analyze_shell_files(self) -> Dict[str, Any]:
        """Analyze shell script files"""
        shell_files = []
        for pattern in ["**/*.sh", "**/*.bash"]:
            shell_files.extend(list(self.workspace_root.glob(pattern)))

        shell_files = [f for f in shell_files if not any(skip in str(f) for skip in [".git", ".venv"])]

        errors = 0
        warnings = 0

        # Try to use shellcheck if available
        for shell_file in shell_files:
            try:
                result = subprocess.run(
                    ["shellcheck", "-f", "json", str(shell_file)], capture_output=True, text=True, timeout=10
                )
                if result.stdout:
                    issues = json.loads(result.stdout)
                    for issue in issues:
                        if issue.get("level") == "error":
                            errors += 1
                        else:
                            warnings += 1
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
                # Fallback to basic analysis if shellcheck not available
                try:
                    content = shell_file.read_text()
                    if "rm -rf" in content and "$" in content:
                        warnings += 1
                    if re.search(r"\$\w+", content) and '"' not in content:
                        warnings += 1
                except Exception:
                    errors += 1

        status = "✅ PASS"
        details = f"{len(shell_files)} files"
        if errors > 0:
            status = "❌ FAIL"
            details = f"{errors} errors, {len(shell_files)} files"
        elif warnings > 0:
            status = "⚠️ WARN"
            details = f"{warnings} warnings, {len(shell_files)} files"

        return {
            "enabled": len(shell_files) > 0,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(shell_files),
            "status": status,
            "details": details,
        }

    def analyze_markdown_files(self) -> Dict[str, Any]:
        """Analyze Markdown files"""
        md_files = list(self.workspace_root.glob("**/*.md"))
        md_files = [f for f in md_files if not any(skip in str(f) for skip in [".git", ".venv"])]

        errors = 0
        warnings = 0

        for md_file in md_files:
            try:
                content = md_file.read_text()
                lines = content.split("\n")
                for line in lines:
                    if len(line) > 200:
                        warnings += 1
                    if re.search(r"<script|<iframe|javascript:", line, re.IGNORECASE):
                        errors += 1
            except Exception:
                errors += 1

        status = "✅ PASS"
        details = f"{len(md_files)} files"
        if errors > 0:
            status = "❌ FAIL"
            details = f"{errors} errors, {len(md_files)} files"
        elif warnings > 0:
            status = "⚠️ WARN"
            details = f"{warnings} warnings, {len(md_files)} files"

        return {
            "enabled": len(md_files) > 0,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(md_files),
            "status": status,
            "details": details,
        }

    def analyze_json_files(self) -> Dict[str, Any]:
        """Analyze JSON files"""
        json_files = list(self.workspace_root.glob("**/*.json"))
        json_files = [f for f in json_files if not any(skip in str(f) for skip in [".git", ".venv", "node_modules"])]

        errors = 0
        warnings = 0

        for json_file in json_files:
            try:
                with open(json_file, "r") as f:
                    json.load(f)
            except json.JSONDecodeError:
                errors += 1
            except Exception:
                errors += 1

        status = "✅ PASS"
        details = f"{len(json_files)} files"
        if errors > 0:
            status = "❌ FAIL"
            details = f"{errors} errors, {len(json_files)} files"

        return {
            "enabled": len(json_files) > 0,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(json_files),
            "status": status,
            "details": details,
        }

    def analyze_docker_files(self) -> Dict[str, Any]:
        """Analyze Dockerfile and Docker Compose files"""
        docker_files = []
        for pattern in [
            "**/Dockerfile*",
            "**/*dockerfile*",
            "**/*.docker",
            "**/docker-compose*.yml",
            "**/compose*.yml",
        ]:
            docker_files.extend(list(self.workspace_root.glob(pattern)))

        docker_files = [f for f in docker_files if not any(skip in str(f) for skip in [".git", ".venv"])]

        errors = 0
        warnings = 0

        for docker_file in docker_files:
            try:
                content = docker_file.read_text()
                # Basic Docker best practices
                if "FROM" in content and "latest" in content:
                    warnings += 1
                if "ADD" in content and "http" in content:
                    warnings += 1
                if "sudo" in content:
                    warnings += 1
            except Exception:
                errors += 1

        status = "✅ PASS"
        details = f"{len(docker_files)} files"
        if errors > 0:
            status = "❌ FAIL"
            details = f"{errors} errors, {len(docker_files)} files"
        elif warnings > 0:
            status = "⚠️ WARN"
            details = f"{warnings} warnings, {len(docker_files)} files"

        return {
            "enabled": len(docker_files) > 0,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(docker_files),
            "status": status,
            "details": details,
        }

    def analyze_terraform_files(self) -> Dict[str, Any]:
        """Analyze Terraform files"""
        tf_files = []
        for pattern in ["**/*.tf", "**/*.tfvars", "**/*.hcl"]:
            tf_files.extend(list(self.workspace_root.glob(pattern)))

        tf_files = [f for f in tf_files if not any(skip in str(f) for skip in [".git", ".venv"])]

        errors = 0
        warnings = 0

        for tf_file in tf_files:
            try:
                content = tf_file.read_text()
                # Basic Terraform checks
                if "resource" in content and "name" not in content:
                    warnings += 1
            except Exception:
                errors += 1

        status = "✅ PASS"
        details = f"{len(tf_files)} files"
        if errors > 0:
            status = "❌ FAIL"
            details = f"{errors} errors, {len(tf_files)} files"
        elif warnings > 0:
            status = "⚠️ WARN"
            details = f"{warnings} warnings, {len(tf_files)} files"

        return {
            "enabled": len(tf_files) > 0,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(tf_files),
            "status": status,
            "details": details,
        }

    def check_security_scan(self) -> Dict[str, Any]:
        """Check for security issues"""
        errors = 0
        warnings = 0

        # Check for common security issues
        all_files = []
        for pattern in ["**/*.py", "**/*.js", "**/*.yml", "**/*.yaml", "**/*.sh"]:
            all_files.extend(list(self.workspace_root.glob(pattern)))

        all_files = [f for f in all_files if not any(skip in str(f) for skip in [".git", ".venv", "node_modules"])]

        for file_path in all_files:
            try:
                content = file_path.read_text()
                # Check for secrets/credentials
                secret_patterns = [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][^"\']+["\']',
                ]
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        warnings += 1
                        break
            except Exception:
                pass

        status = "✅ PASS"
        details = f"{len(all_files)} files scanned"
        if errors > 0:
            status = "❌ FAIL"
            details = f"{errors} security issues"
        elif warnings > 0:
            status = "⚠️ WARN"
            details = f"{warnings} potential issues"

        return {
            "enabled": True,
            "errors": errors,
            "warnings": warnings,
            "files_checked": len(all_files),
            "status": status,
            "details": details,
        }

    def run_analysis(self) -> Dict[str, Any]:
        """Run complete analysis"""
        print("🔍 Starting Super Linter Analysis...")

        # Run all checks
        checks = {
            "YAML Linting": self.analyze_yaml_files(),
            "Ansible Linting": self.analyze_ansible_files(),
            "Python Linting": self.analyze_python_files(),
            "Shell Script Check": self.analyze_shell_files(),
            "Markdown Linting": self.analyze_markdown_files(),
            "JSON Validation": self.analyze_json_files(),
            "Docker Linting": self.analyze_docker_files(),
            "Terraform Linting": self.analyze_terraform_files(),
            "Security Scan": self.check_security_scan(),
        }

        # Calculate summary
        total_errors = sum(check["errors"] for check in checks.values())
        total_warnings = sum(check["warnings"] for check in checks.values())
        total_files = sum(check["files_checked"] for check in checks.values())
        enabled_checks = sum(1 for check in checks.values() if check["enabled"])
        passed_checks = sum(1 for check in checks.values() if check["status"] == "✅ PASS" and check["enabled"])

        # Calculate health score
        if enabled_checks == 0:
            health_score = 100
        else:
            base_score = (passed_checks / enabled_checks) * 100
            error_penalty = min(total_errors * 5, 50)
            warning_penalty = min(total_warnings * 2, 30)
            health_score = max(0, base_score - error_penalty - warning_penalty)

        summary = {
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "total_files": total_files,
            "enabled_checks": enabled_checks,
            "passed_checks": passed_checks,
            "health_score": round(health_score, 1),
        }

        self.results = {"checks": checks, "summary": summary, "health_score": health_score}

        return self.results

    def generate_github_summary(self) -> str:
        """Generate GitHub Step Summary markdown"""
        checks = self.results["checks"]
        summary = self.results["summary"]

        lines = []
        lines.append("## 🔍 Super Linter Analysis Results")
        lines.append("")

        # Overall health score
        health_score = summary["health_score"]
        health_emoji = "🟢" if health_score >= 85 else "🟡" if health_score >= 70 else "🔴"
        lines.append(f"### {health_emoji} Overall Health Score: {health_score}/100")
        lines.append("")

        # Results table
        lines.append("### 📋 Linting Results")
        lines.append("")
        lines.append("| Linter | Status | Details | Files |")
        lines.append("|--------|--------|---------|-------|")

        for check_name, check_data in checks.items():
            if check_data["enabled"]:
                status = check_data["status"]
                details = check_data["details"]
                files = check_data["files_checked"]
                lines.append(f"| {check_name} | {status} | {details} | {files} |")
            else:
                lines.append(f"| {check_name} | ⏭️ SKIP | No files found | 0 |")

        lines.append("")

        # Summary statistics
        lines.append("### 📊 Summary Statistics")
        lines.append(f"- **Total Files Checked**: {summary['total_files']}")
        lines.append(f"- **Active Linters**: {summary['enabled_checks']}")
        lines.append(f"- **Passed Checks**: {summary['passed_checks']}/{summary['enabled_checks']}")
        lines.append(f"- **Total Errors**: {summary['total_errors']}")
        lines.append(f"- **Total Warnings**: {summary['total_warnings']}")
        lines.append("")

        # Status indicator
        if summary["total_errors"] == 0 and summary["total_warnings"] == 0:
            lines.append("🎉 **Excellent! No issues found.**")
        elif summary["total_errors"] == 0:
            lines.append(f"⚠️ **Good! Only {summary['total_warnings']} warnings found.**")
        else:
            lines.append(
                f"❌ **Issues found: {summary['total_errors']} errors, {summary['total_warnings']} warnings.**"
            )

        return "\n".join(lines)

    def set_github_outputs(self):
        """Set GitHub Actions outputs"""
        github_output = os.getenv("GITHUB_OUTPUT")
        if not github_output:
            return

        summary = self.results["summary"]
        checks = self.results["checks"]

        with open(github_output, "a") as f:
            f.write(f"health_score={summary['health_score']}\n")
            f.write(f"total_errors={summary['total_errors']}\n")
            f.write(f"total_warnings={summary['total_warnings']}\n")
            f.write(f"total_files={summary['total_files']}\n")
            f.write(f"passed_checks={summary['passed_checks']}\n")
            f.write(f"enabled_checks={summary['enabled_checks']}\n")

            # Individual check results
            for check_name, check_data in checks.items():
                safe_name = check_name.lower().replace(" ", "_").replace("-", "_")
                f.write(f"{safe_name}_status={check_data['status']}\n")
                f.write(f"{safe_name}_errors={check_data['errors']}\n")
                f.write(f"{safe_name}_warnings={check_data['warnings']}\n")
                f.write(f"{safe_name}_files={check_data['files_checked']}\n")


def main():
    """Main function"""
    analyzer = SuperLinterAnalyzer()
    results = analyzer.run_analysis()

    # Generate and display summary
    summary = analyzer.generate_github_summary()
    print(summary)

    # Write to GitHub Step Summary
    github_summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if github_summary_file:
        with open(github_summary_file, "a") as f:
            f.write("\n" + summary + "\n")
        print("✅ Summary added to GitHub Step Summary")

    # Set GitHub Actions outputs
    analyzer.set_github_outputs()
    print("✅ GitHub Actions outputs set")

    # Print JSON results for debugging
    print("\n📊 Detailed Results:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
