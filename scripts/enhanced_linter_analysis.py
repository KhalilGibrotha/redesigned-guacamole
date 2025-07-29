#!/usr/bin/env python3
"""
Enhanced Super Linter Analysis Script
Integrates with the existing Super Linter workflow to provide detailed analysis
of linting configurations, markdown patterns, and code quality metrics.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List


class SuperLinterAnalyzer:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.analysis_results = {
            "config_analysis": {},
            "markdown_analysis": {},
            "python_analysis": {},
            "ansible_analysis": {},
            "overall_health": {},
        }

    def analyze_autofix_changes(self) -> Dict[str, Any]:
        """Analyze auto-fixes applied by Super Linter"""
        print("🔧 Analyzing auto-fixes applied...")

        import subprocess

        try:
            # Check if there are any changes from auto-fix
            result = subprocess.run(["git", "diff", "--quiet"], capture_output=True)
            no_changes = result.returncode == 0

            if no_changes:
                return {"autofix_needed": False, "total_fixes": 0, "fixes_by_type": {}, "changed_files": []}

            # Get changed files
            changed_files_result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
            changed_files = (
                changed_files_result.stdout.strip().split("\n") if changed_files_result.stdout.strip() else []
            )

            # Count fixes by file type
            fixes_by_type = {"yaml": 0, "python": 0, "shell": 0, "markdown": 0, "json": 0, "ansible": 0}

            file_patterns = {
                "yaml": r"\.ya?ml$",
                "python": r"\.py$",
                "shell": r"\.sh$",
                "markdown": r"\.md$",
                "json": r"\.json$",
            }

            for file in changed_files:
                # Get change count for this file
                numstat_result = subprocess.run(["git", "diff", "--numstat", file], capture_output=True, text=True)
                if numstat_result.stdout:
                    parts = numstat_result.stdout.strip().split("\t")
                    if len(parts) >= 2:
                        try:
                            changes = int(parts[0]) + int(parts[1])
                        except ValueError:
                            changes = 1
                    else:
                        changes = 1
                else:
                    changes = 1

                # Categorize by file type
                for ftype, pattern in file_patterns.items():
                    if re.search(pattern, file):
                        fixes_by_type[ftype] += changes
                        break

                # Special handling for Ansible
                if re.search(r"(playbook|tasks|handlers|vars).*\.ya?ml$|site\.ya?ml$", file):
                    fixes_by_type["ansible"] += changes

            total_fixes = sum(fixes_by_type.values())

            return {
                "autofix_needed": True,
                "total_fixes": total_fixes,
                "fixes_by_type": fixes_by_type,
                "changed_files": changed_files,
                "changed_files_count": len(changed_files),
            }

        except Exception as e:
            print(f"⚠️ Error analyzing auto-fixes: {e}")
            return {
                "autofix_needed": False,
                "total_fixes": 0,
                "fixes_by_type": {},
                "changed_files": [],
                "error": str(e),
            }

    def analyze_linter_configurations(self) -> Dict[str, Any]:
        """Analyze linter configuration consistency and conflicts"""
        print("🔧 Analyzing linter configurations...")

        configs = {}
        conflicts = []
        recommendations = []

        # Check EditorConfig
        editorconfig_path = self.workspace_root / ".editorconfig"
        if editorconfig_path.exists():
            configs["editorconfig"] = self._parse_editorconfig(editorconfig_path)

        # Check Python configurations
        pyproject_path = self.workspace_root / "pyproject.toml"
        if pyproject_path.exists():
            configs["pyproject"] = self._parse_pyproject(pyproject_path)

        # Check flake8
        flake8_path = self.workspace_root / ".flake8"
        if flake8_path.exists():
            configs["flake8"] = self._parse_flake8(flake8_path)

        # Check markdownlint
        markdownlint_path = self.workspace_root / ".markdownlint.json"
        if markdownlint_path.exists():
            configs["markdownlint"] = self._parse_markdownlint(markdownlint_path)

        # Detect conflicts
        conflicts.extend(self._detect_line_length_conflicts(configs))
        conflicts.extend(self._detect_indentation_conflicts(configs))

        # Generate recommendations
        recommendations.extend(self._generate_config_recommendations(configs, conflicts))

        return {
            "configurations_found": list(configs.keys()),
            "total_conflicts": len(conflicts),
            "conflicts": conflicts,
            "recommendations": recommendations,
            "config_health_score": self._calculate_config_health_score(configs, conflicts),
        }

    def analyze_markdown_patterns(self) -> Dict[str, Any]:
        """Analyze markdown usage patterns and linting compatibility"""
        print("📝 Analyzing markdown patterns...")

        markdown_files = list(self.workspace_root.glob("**/*.md"))

        patterns = {
            "emoji_usage": 0,
            "html_elements": [],
            "long_lines": 0,
            "tables": 0,
            "code_blocks": 0,
            "template_variables": 0,
        }

        compatibility_issues = []
        total_files = len(markdown_files)

        for md_file in markdown_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                file_patterns = self._analyze_single_markdown_file(content)

                # Aggregate patterns
                for key in patterns:
                    if isinstance(patterns[key], int):
                        patterns[key] += file_patterns.get(key, 0)
                    elif isinstance(patterns[key], list):
                        patterns[key].extend(file_patterns.get(key, []))

                # Check compatibility with markdownlint config
                file_issues = self._check_markdown_compatibility(content, md_file)
                compatibility_issues.extend(file_issues)

            except Exception as e:
                print(f"⚠️ Error analyzing {md_file}: {e}")

        # Remove duplicates from HTML elements
        patterns["html_elements"] = list(set(patterns["html_elements"]))

        return {
            "total_files": total_files,
            "patterns": patterns,
            "compatibility_issues": len(compatibility_issues),
            "issue_details": compatibility_issues[:10],  # Limit for output
            "markdown_health_score": self._calculate_markdown_health_score(patterns, compatibility_issues),
        }

    def analyze_python_code_quality(self) -> Dict[str, Any]:
        """Analyze Python code quality and linting compliance"""
        print("🐍 Analyzing Python code quality...")

        python_files = list(self.workspace_root.glob("**/*.py"))

        metrics = {
            "total_files": len(python_files),
            "long_lines": 0,
            "complex_functions": 0,
            "missing_docstrings": 0,
            "import_issues": 0,
            "type_annotation_coverage": 0,
        }

        quality_issues = []

        for py_file in python_files:
            if any(skip in str(py_file) for skip in [".venv", "venv", "__pycache__", ".git"]):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                file_metrics = self._analyze_single_python_file(content, py_file)

                # Aggregate metrics
                for key in metrics:
                    if key != "total_files" and isinstance(metrics[key], int):
                        metrics[key] += file_metrics.get(key, 0)

                # Check quality issues
                file_issues = self._check_python_quality(content, py_file)
                quality_issues.extend(file_issues)

            except Exception as e:
                print(f"⚠️ Error analyzing {py_file}: {e}")

        metrics["total_files"] = len(
            [f for f in python_files if not any(skip in str(f) for skip in [".venv", "venv", "__pycache__", ".git"])]
        )

        return {
            "metrics": metrics,
            "quality_issues": len(quality_issues),
            "issue_details": quality_issues[:15],  # Limit for output
            "python_health_score": self._calculate_python_health_score(metrics, quality_issues),
        }

    def analyze_ansible_yaml_quality(self) -> Dict[str, Any]:
        """Analyze Ansible YAML files and general YAML quality"""
        print("🎭 Analyzing Ansible and YAML quality...")

        # Find all YAML files
        yaml_files = list(self.workspace_root.glob("**/*.yml")) + list(self.workspace_root.glob("**/*.yaml"))

        # Categorize YAML files
        ansible_files = []
        github_actions_files = []
        other_yaml_files = []

        for yaml_file in yaml_files:
            if any(skip in str(yaml_file) for skip in [".git", "__pycache__", ".venv", "venv"]):
                continue

            file_str = str(yaml_file)
            if (
                any(
                    indicator in file_str
                    for indicator in ["playbook", "tasks", "handlers", "vars", "inventory", "roles"]
                )
                or any(indicator in file_str for indicator in ["site.yml", "main.yml"])
                or "vars/" in file_str
            ):
                ansible_files.append(yaml_file)
            elif ".github/workflows" in file_str or ".github/actions" in file_str:
                github_actions_files.append(yaml_file)
            else:
                other_yaml_files.append(yaml_file)

        metrics = {
            "total_yaml_files": len(yaml_files),
            "ansible_files": len(ansible_files),
            "github_actions_files": len(github_actions_files),
            "other_yaml_files": len(other_yaml_files),
            "yaml_syntax_errors": 0,
            "ansible_best_practice_violations": 0,
            "long_yaml_files": 0,
            "complex_ansible_tasks": 0,
            "unsafe_yaml_patterns": 0,
            "missing_ansible_metadata": 0,
        }

        ansible_quality_issues = []
        yaml_syntax_issues = []

        # Analyze Ansible-specific files
        for ansible_file in ansible_files:
            try:
                content = ansible_file.read_text(encoding="utf-8")
                file_issues = self._analyze_single_ansible_file(content, ansible_file)

                # Aggregate metrics
                for key in [
                    "ansible_best_practice_violations",
                    "complex_ansible_tasks",
                    "unsafe_yaml_patterns",
                    "missing_ansible_metadata",
                ]:
                    metrics[key] += file_issues.get(key, 0)

                ansible_quality_issues.extend(file_issues.get("issues", []))

                # Check for long files (>200 lines)
                if len(content.split("\n")) > 200:
                    metrics["long_yaml_files"] += 1

            except Exception as e:
                print(f"⚠️ Error analyzing Ansible file {ansible_file}: {e}")
                metrics["yaml_syntax_errors"] += 1
                yaml_syntax_issues.append(f"{ansible_file}: {str(e)}")

        # Analyze all YAML files for syntax and general quality
        for yaml_file in yaml_files:
            if any(skip in str(yaml_file) for skip in [".git", "__pycache__", ".venv", "venv"]):
                continue

            try:
                content = yaml_file.read_text(encoding="utf-8")
                syntax_issues = self._check_yaml_syntax_quality(content, yaml_file)
                yaml_syntax_issues.extend(syntax_issues)

            except Exception as e:
                metrics["yaml_syntax_errors"] += 1
                yaml_syntax_issues.append(f"{yaml_file}: Encoding/read error - {str(e)}")

        metrics["yaml_syntax_errors"] = len(yaml_syntax_issues)

        return {
            "metrics": metrics,
            "ansible_files_analyzed": [str(f) for f in ansible_files[:10]],  # Sample for output
            "ansible_quality_issues": len(ansible_quality_issues),
            "ansible_issue_details": ansible_quality_issues[:10],  # Limit for output
            "yaml_syntax_issues": len(yaml_syntax_issues),
            "yaml_syntax_details": yaml_syntax_issues[:8],  # Limit for output
            "ansible_yaml_health_score": self._calculate_ansible_yaml_health_score(
                metrics, ansible_quality_issues, yaml_syntax_issues
            ),
        }

    def generate_github_summary(self) -> str:
        """Generate GitHub Step Summary markdown"""

        autofix_analysis = self.analysis_results["autofix_analysis"]
        config_analysis = self.analysis_results["config_analysis"]
        markdown_analysis = self.analysis_results["markdown_analysis"]
        python_analysis = self.analysis_results["python_analysis"]
        ansible_analysis = self.analysis_results["ansible_analysis"]

        summary = []

        # Header
        summary.append("## 🔍 Enhanced Super Linter Analysis")
        summary.append("")

        # Auto-fix Summary
        if autofix_analysis.get("autofix_needed"):
            summary.append("### 🤖 Auto-fixes Applied")
            total_fixes = autofix_analysis.get("total_fixes", 0)
            fixes_by_type = autofix_analysis.get("fixes_by_type", {})
            changed_files_count = autofix_analysis.get("changed_files_count", 0)

            summary.append(f"- **Total Changes**: {total_fixes} changes across {changed_files_count} files")

            # Show fixes by type
            if any(fixes_by_type.values()):
                summary.append("- **Fixes by Type**:")
                for ftype, count in fixes_by_type.items():
                    if count > 0:
                        emoji = {
                            "yaml": "📄",
                            "python": "🐍",
                            "shell": "🐚",
                            "markdown": "📝",
                            "json": "📋",
                            "ansible": "🎭",
                        }.get(ftype, "📄")
                        summary.append(f"  - {emoji} {ftype.title()}: {count} changes")
        else:
            summary.append("### ✅ No Auto-fixes Needed")
            summary.append("- **Code Quality**: All files already compliant with linting rules!")

        summary.append("")

        # Overall Health Score
        autofix_penalty = autofix_analysis.get("total_fixes", 0) * 1.5 if autofix_analysis.get("autofix_needed") else 0
        overall_score = (
            config_analysis.get("config_health_score", 0) * 0.20
            + markdown_analysis.get("markdown_health_score", 0) * 0.20
            + python_analysis.get("python_health_score", 0) * 0.25
            + ansible_analysis.get("ansible_yaml_health_score", 0) * 0.25
            + max(0, 100 - autofix_penalty) * 0.10
        )

        health_emoji = "🟢" if overall_score >= 85 else "🟡" if overall_score >= 70 else "🔴"
        summary.append(f"### {health_emoji} Overall Code Health: {overall_score:.1f}/100")
        summary.append("")

        # Configuration Analysis
        summary.append("### 🔧 Linter Configuration Analysis")
        summary.append(f"- **Configurations Found**: {', '.join(config_analysis.get('configurations_found', []))}")
        summary.append(f"- **Conflicts Detected**: {config_analysis.get('total_conflicts', 0)}")
        summary.append(f"- **Config Health**: {config_analysis.get('config_health_score', 0):.1f}/100")

        if config_analysis.get("conflicts"):
            summary.append("\n**Configuration Conflicts:**")
            for conflict in config_analysis["conflicts"][:3]:
                summary.append(f"- ⚠️ {conflict}")

        summary.append("")

        # Markdown Analysis
        summary.append("### 📝 Markdown Analysis")
        patterns = markdown_analysis.get("patterns", {})
        summary.append(f"- **Files Analyzed**: {markdown_analysis.get('total_files', 0)}")
        summary.append(f"- **Emoji Usage**: {patterns.get('emoji_usage', 0)} instances")
        summary.append(f"- **HTML Elements**: {len(patterns.get('html_elements', []))} types")
        summary.append(f"- **Code Blocks**: {patterns.get('code_blocks', 0)}")
        summary.append(f"- **Tables**: {patterns.get('tables', 0)}")
        summary.append(f"- **Compatibility Issues**: {markdown_analysis.get('compatibility_issues', 0)}")
        summary.append("")

        # Python Analysis
        summary.append("### 🐍 Python Code Quality")
        metrics = python_analysis.get("metrics", {})
        summary.append(f"- **Files Analyzed**: {metrics.get('total_files', 0)}")
        summary.append(f"- **Long Lines**: {metrics.get('long_lines', 0)}")
        summary.append(f"- **Complex Functions**: {metrics.get('complex_functions', 0)}")
        summary.append(f"- **Quality Issues**: {python_analysis.get('quality_issues', 0)}")
        summary.append("")

        # Ansible/YAML Analysis
        summary.append("### 🎭 Ansible & YAML Analysis")
        ansible_metrics = ansible_analysis.get("metrics", {})
        summary.append(f"- **Total YAML Files**: {ansible_metrics.get('total_yaml_files', 0)}")
        summary.append(f"- **Ansible Files**: {ansible_metrics.get('ansible_files', 0)}")
        summary.append(f"- **GitHub Actions Files**: {ansible_metrics.get('github_actions_files', 0)}")
        summary.append(f"- **YAML Syntax Errors**: {ansible_metrics.get('yaml_syntax_errors', 0)}")
        summary.append(
            f"- **Ansible Best Practice Violations**: {ansible_metrics.get('ansible_best_practice_violations', 0)}"
        )
        summary.append(f"- **Security/Safety Issues**: {ansible_metrics.get('unsafe_yaml_patterns', 0)}")
        summary.append("")

        # Recommendations
        recommendations = config_analysis.get("recommendations", [])
        if recommendations:
            summary.append("### 💡 Recommendations")
            for rec in recommendations[:5]:
                summary.append(f"- {rec}")
            summary.append("")

        # Summary table
        summary.append("### 📊 Health Summary")
        summary.append("| Category | Score | Status |")
        summary.append("|----------|-------|--------|")

        config_score = config_analysis.get("config_health_score", 0)
        config_status = "🟢 Excellent" if config_score >= 90 else "🟡 Good" if config_score >= 70 else "🔴 Needs Work"
        summary.append(f"| Configuration | {config_score:.1f}/100 | {config_status} |")

        markdown_score = markdown_analysis.get("markdown_health_score", 0)
        markdown_status = (
            "🟢 Excellent" if markdown_score >= 90 else "🟡 Good" if markdown_score >= 70 else "🔴 Needs Work"
        )
        summary.append(f"| Markdown | {markdown_score:.1f}/100 | {markdown_status} |")

        python_score = python_analysis.get("python_health_score", 0)
        python_status = "🟢 Excellent" if python_score >= 90 else "🟡 Good" if python_score >= 70 else "🔴 Needs Work"
        summary.append(f"| Python | {python_score:.1f}/100 | {python_status} |")

        ansible_score = ansible_analysis.get("ansible_yaml_health_score", 0)
        ansible_status = (
            "🟢 Excellent" if ansible_score >= 90 else "🟡 Good" if ansible_score >= 70 else "🔴 Needs Work"
        )
        summary.append(f"| Ansible/YAML | {ansible_score:.1f}/100 | {ansible_status} |")

        overall_status = "Excellent" if overall_score >= 85 else "Good" if overall_score >= 70 else "Needs Work"
        summary.append(f"| **Overall** | **{overall_score:.1f}/100** | **{health_emoji} {overall_status}** |")
        summary.append("")  # Add newline after table

        return "\n".join(summary)

    def _parse_editorconfig(self, path: Path) -> Dict[str, Any]:
        """Parse EditorConfig file"""
        try:
            content = path.read_text()
            # Simple parsing for key metrics
            python_line_length = None
            if "*.py]" in content:
                # Extract line length for Python files
                python_section = content.split("[*.py]")[1].split("[")[0]
                if "max_line_length" in python_section:
                    match = re.search(r"max_line_length\s*=\s*(\d+)", python_section)
                    if match:
                        python_line_length = int(match.group(1))

            return {"python_line_length": python_line_length, "has_python_config": "*.py]" in content}
        except Exception:
            return {}

    def _parse_pyproject(self, path: Path) -> Dict[str, Any]:
        """Parse pyproject.toml for tool configurations"""
        try:
            content = path.read_text()
            config = {}

            # Extract Black line length
            if "[tool.black]" in content:
                black_section = (
                    content.split("[tool.black]")[1].split("[tool.")[0]
                    if "[tool." in content.split("[tool.black]")[1]
                    else content.split("[tool.black]")[1]
                )
                match = re.search(r"line-length\s*=\s*(\d+)", black_section)
                if match:
                    config["black_line_length"] = int(match.group(1))

            # Check for other tools
            config["has_black"] = "[tool.black]" in content
            config["has_isort"] = "[tool.isort]" in content
            config["has_mypy"] = "[tool.mypy]" in content

            return config
        except Exception:
            return {}

    def _parse_flake8(self, path: Path) -> Dict[str, Any]:
        """Parse .flake8 configuration"""
        try:
            content = path.read_text()
            config = {}

            # Extract max line length
            match = re.search(r"max-line-length\s*=\s*(\d+)", content)
            if match:
                config["max_line_length"] = int(match.group(1))

            # Check for E133 in ignore list
            config["ignores_e133"] = "E133" in content

            return config
        except Exception:
            return {}

    def _parse_markdownlint(self, path: Path) -> Dict[str, Any]:
        """Parse markdownlint.json configuration"""
        try:
            with open(path) as f:
                config = json.load(f)

            md013 = config.get("MD013", {})
            return {
                "line_length": md013.get("line_length", 80),
                "allows_html": not config.get("MD033", True),
                "allows_multiple_h1": not config.get("MD025", True),
            }
        except Exception:
            return {}

    def _detect_line_length_conflicts(self, configs: Dict[str, Any]) -> List[str]:
        """Detect line length conflicts between tools"""
        conflicts = []
        line_lengths = {}

        if "editorconfig" in configs and configs["editorconfig"].get("python_line_length"):
            line_lengths["EditorConfig"] = configs["editorconfig"]["python_line_length"]

        if "pyproject" in configs and configs["pyproject"].get("black_line_length"):
            line_lengths["Black"] = configs["pyproject"]["black_line_length"]

        if "flake8" in configs and configs["flake8"].get("max_line_length"):
            line_lengths["flake8"] = configs["flake8"]["max_line_length"]

        # Check for conflicts
        if len(set(line_lengths.values())) > 1:
            conflicts.append(f"Line length mismatch: {line_lengths}")

        return conflicts

    def _detect_indentation_conflicts(self, configs: Dict[str, Any]) -> List[str]:
        """Detect indentation style conflicts"""
        # This would be expanded based on parsing more config details
        return []

    def _generate_config_recommendations(self, configs: Dict[str, Any], conflicts: List[str]) -> List[str]:
        """Generate configuration recommendations"""
        recommendations = []

        if conflicts:
            recommendations.append("🔧 Resolve line length conflicts by standardizing to 120 characters")

        if "flake8" in configs and not configs["flake8"].get("ignores_e133"):
            recommendations.append("🔧 Add E133 to flake8 ignore list for Black compatibility")

        if "markdownlint" in configs and configs["markdownlint"].get("line_length", 80) < 140:
            recommendations.append("📝 Consider increasing markdown line length to 180 for technical docs")

        return recommendations

    def _analyze_single_markdown_file(self, content: str) -> Dict[str, Any]:
        """Analyze patterns in a single markdown file"""
        patterns = {
            "emoji_usage": len(re.findall(r"[🚀📊🔍⚠️✅❌🎯📝🏗️🌐🔧🎉💾🔄📤📥🛡️☢️🔐🔒📋]", content)),
            "html_elements": re.findall(r"<(\w+)", content),
            "long_lines": len([line for line in content.split("\n") if len(line) > 180]),
            "tables": len(re.findall(r"\|.*\|", content)),
            "code_blocks": len(re.findall(r"```", content)) // 2,
            "template_variables": len(re.findall(r"\${[^}]+}", content)),
        }
        return patterns

    def _check_markdown_compatibility(self, content: str, file_path: Path) -> List[str]:
        """Check markdown compatibility with linting rules"""
        issues = []

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > 200:  # Very long lines
                issues.append(f"{file_path}:{i} - Line exceeds 200 characters ({len(line)})")

        return issues

    def _analyze_single_python_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        lines = content.split("\n")

        metrics = {
            "long_lines": len([line for line in lines if len(line) > 120]),
            "complex_functions": len(re.findall(r"def \w+.*:\s*\n(.*\n){20,}", content)),
            "missing_docstrings": len(re.findall(r'def \w+.*:\s*\n\s*[^"]', content)),
            "import_issues": 0,  # Would implement import analysis
            "type_annotation_coverage": 0,  # Would implement type annotation analysis
        }

        return metrics

    def _check_python_quality(self, content: str, file_path: Path) -> List[str]:
        """Check Python code quality issues"""
        issues = []

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > 130:  # Very long lines
                issues.append(f"{file_path}:{i} - Line exceeds 130 characters")

        return issues

    def _calculate_config_health_score(self, configs: Dict, conflicts: List) -> float:
        """Calculate configuration health score"""
        base_score = len(configs) * 20  # 20 points per config file
        conflict_penalty = len(conflicts) * 10
        return max(0, min(100, base_score - conflict_penalty))

    def _calculate_markdown_health_score(self, patterns: Dict, issues: List) -> float:
        """Calculate markdown health score"""
        base_score = 100
        issue_penalty = len(issues) * 2
        return max(0, min(100, base_score - issue_penalty))

    def _calculate_python_health_score(self, metrics: Dict, issues: List) -> float:
        """Calculate Python health score"""
        base_score = 100
        issue_penalty = len(issues) * 1.5
        line_penalty = metrics.get("long_lines", 0) * 0.5
        return max(0, min(100, base_score - issue_penalty - line_penalty))

    def _analyze_single_ansible_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Ansible YAML file for best practices"""
        issues = []
        metrics = {
            "ansible_best_practice_violations": 0,
            "complex_ansible_tasks": 0,
            "unsafe_yaml_patterns": 0,
            "missing_ansible_metadata": 0,
        }

        # Check for Ansible best practices
        if "hosts:" in content or "- hosts:" in content:
            # This looks like a playbook
            if "name:" not in content:
                issues.append(f"{file_path}: Playbook missing descriptive name")
                metrics["missing_ansible_metadata"] += 1

            # Check for become usage without explicit permissions
            if "become:" in content and "become_user:" not in content:
                issues.append(f"{file_path}: Using become without explicit become_user")
                metrics["ansible_best_practice_violations"] += 1

        # Check for complex tasks (very long task definitions)
        task_blocks = re.findall(r"- name:.*?(?=- name:|---|\Z)", content, re.DOTALL)
        for task in task_blocks:
            if len(task.split("\n")) > 15:  # Very long task
                metrics["complex_ansible_tasks"] += 1
                issues.append(f"{file_path}: Found overly complex task (>15 lines)")

        # Check for unsafe YAML patterns
        unsafe_patterns = [
            (r"{{.*\|.*shell.*}}", "Potential shell injection in template"),
            (r"shell:.*\$\{", "Potential variable injection in shell command"),
            (r"command:.*\|", "Piping in command module (use shell instead)"),
            (r"sudo:", "Using deprecated sudo (use become instead)"),
        ]

        for pattern, message in unsafe_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                metrics["unsafe_yaml_patterns"] += 1
                issues.append(f"{file_path}: {message}")

        # Check for missing documentation in vars files
        if "vars/" in str(file_path) or "variables" in str(file_path).lower():
            if not re.search(r"#.*[Dd]escription|#.*[Dd]oc|#.*[Pp]urpose", content):
                metrics["missing_ansible_metadata"] += 1
                issues.append(f"{file_path}: Variables file missing documentation comments")

        return {"issues": issues, **metrics}

    def _check_yaml_syntax_quality(self, content: str, file_path: Path) -> List[str]:
        """Check YAML syntax and quality issues"""
        issues = []

        try:
            import yaml

            # Try to parse the YAML
            yaml.safe_load(content)
        except ImportError:
            # YAML library not available, skip syntax check
            pass
        except Exception as e:
            # This catches both yaml.YAMLError and other parsing errors
            issues.append(f"{file_path}: YAML parsing error - {str(e)}")

        # Check for quality issues
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Very long lines in YAML
            if len(line) > 160:
                issues.append(f"{file_path}:{i}: Line exceeds 160 characters ({len(line)})")

            # Tabs in YAML (should use spaces)
            if "\t" in line:
                issues.append(f"{file_path}:{i}: Found tab character (use spaces instead)")

            # Trailing whitespace
            if line.endswith(" ") or line.endswith("\t"):
                issues.append(f"{file_path}:{i}: Trailing whitespace")

        # Check for inconsistent indentation
        indent_sizes = []
        for line in lines:
            if line.strip() and line.startswith(" "):
                leading_spaces = len(line) - len(line.lstrip(" "))
                if leading_spaces > 0:
                    indent_sizes.append(leading_spaces)

        if indent_sizes:
            # Find the most common indentation that's not a multiple of others
            from collections import Counter

            common_indents = Counter(indent_sizes).most_common(3)
            if len(common_indents) > 1:
                # Check if indentation is inconsistent
                base_indent = common_indents[0][0]
                for indent, count in common_indents[1:]:
                    if indent % base_indent != 0 and count > len(lines) * 0.1:  # 10% threshold
                        issues.append(
                            f"{file_path}: Inconsistent indentation detected ({base_indent} vs {indent} spaces)"
                        )
                        break

        return issues

    def _calculate_ansible_yaml_health_score(self, metrics: Dict, ansible_issues: List, yaml_issues: List) -> float:
        """Calculate Ansible/YAML health score"""
        base_score = 100

        # Penalties for different types of issues
        syntax_penalty = len(yaml_issues) * 5  # Syntax errors are serious
        ansible_violation_penalty = metrics.get("ansible_best_practice_violations", 0) * 3
        complexity_penalty = metrics.get("complex_ansible_tasks", 0) * 2
        unsafe_penalty = metrics.get("unsafe_yaml_patterns", 0) * 4  # Security issues are serious
        metadata_penalty = metrics.get("missing_ansible_metadata", 0) * 1

        total_penalty = (
            syntax_penalty + ansible_violation_penalty + complexity_penalty + unsafe_penalty + metadata_penalty
        )

        return max(0, min(100, base_score - total_penalty))

    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete analysis and return results"""
        print("🚀 Starting Enhanced Super Linter Analysis...")

        self.analysis_results["autofix_analysis"] = self.analyze_autofix_changes()
        self.analysis_results["config_analysis"] = self.analyze_linter_configurations()
        self.analysis_results["markdown_analysis"] = self.analyze_markdown_patterns()
        self.analysis_results["python_analysis"] = self.analyze_python_code_quality()
        self.analysis_results["ansible_analysis"] = self.analyze_ansible_yaml_quality()

        return self.analysis_results


def main():
    """Main function for GitHub Actions integration"""
    analyzer = SuperLinterAnalyzer()
    results = analyzer.run_full_analysis()

    # Generate GitHub Step Summary
    summary = analyzer.generate_github_summary()

    # Write to GitHub Step Summary
    github_summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if github_summary_file:
        with open(github_summary_file, "a") as f:
            f.write(summary)
        print("✅ Analysis added to GitHub Step Summary")
    else:
        print("📄 Analysis Results:")
        print(summary)

    # Output results as JSON for other steps
    print("\n📊 Detailed Results (JSON):")
    print(json.dumps(results, indent=2))

    # Set GitHub outputs for other steps
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        autofix_analysis = results.get("autofix_analysis", {})
        fixes_by_type = autofix_analysis.get("fixes_by_type", {})

        with open(github_output, "a") as f:
            # Enhanced analysis results
            f.write(f"analysis_results={json.dumps(results)}\n")

            # Autofix outputs (compatible with existing workflow)
            f.write(f"autofix_needed={str(autofix_analysis.get('autofix_needed', False)).lower()}\n")
            f.write(f"total_fixes={autofix_analysis.get('total_fixes', 0)}\n")
            f.write(f"yaml_fixes={fixes_by_type.get('yaml', 0)}\n")
            f.write(f"ansible_fixes={fixes_by_type.get('ansible', 0)}\n")
            f.write(f"python_fixes={fixes_by_type.get('python', 0)}\n")
            f.write(f"shell_fixes={fixes_by_type.get('shell', 0)}\n")
            f.write(f"markdown_fixes={fixes_by_type.get('markdown', 0)}\n")
            f.write(f"json_fixes={fixes_by_type.get('json', 0)}\n")

            # Health scores
            config_score = results.get("config_analysis", {}).get("config_health_score", 0)
            markdown_score = results.get("markdown_analysis", {}).get("markdown_health_score", 0)
            python_score = results.get("python_analysis", {}).get("python_health_score", 0)
            ansible_score = results.get("ansible_analysis", {}).get("ansible_yaml_health_score", 0)

            # Calculate overall score
            autofix_penalty = (
                autofix_analysis.get("total_fixes", 0) * 1.5 if autofix_analysis.get("autofix_needed") else 0
            )
            overall_score = (
                config_score * 0.20
                + markdown_score * 0.20
                + python_score * 0.25
                + ansible_score * 0.25
                + max(0, 100 - autofix_penalty) * 0.10
            )

            f.write(f"overall_health_score={overall_score:.1f}\n")
            f.write(f"config_health_score={config_score}\n")
            f.write(f"markdown_health_score={markdown_score}\n")
            f.write(f"python_health_score={python_score}\n")
            f.write(f"ansible_yaml_health_score={ansible_score}\n")

            # Ansible-specific outputs
            ansible_metrics = results.get("ansible_analysis", {}).get("metrics", {})
            f.write(f"ansible_files_count={ansible_metrics.get('ansible_files', 0)}\n")
            f.write(f"yaml_syntax_errors={ansible_metrics.get('yaml_syntax_errors', 0)}\n")
            f.write(f"ansible_violations={ansible_metrics.get('ansible_best_practice_violations', 0)}\n")
            f.write(f"ansible_security_issues={ansible_metrics.get('unsafe_yaml_patterns', 0)}\n")


if __name__ == "__main__":
    main()
