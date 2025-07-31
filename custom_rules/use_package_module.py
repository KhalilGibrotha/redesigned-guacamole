"""Custom rule to enforce the use of the 'package' module."""

from ansiblelint.rules import AnsibleLintRule


class UsePackageModuleRule(AnsibleLintRule):
    """Rule to enforce the use of the 'package' module."""

    id = "CUSTOM001"
    shortdesc = "Use package module instead of yum, apt, or dnf"
    description = (
        "Tasks should use the generic package module instead of yum, apt, or dnf "
        "for better portability across different Linux distributions."
    )
    severity = "MEDIUM"
    tags = ["portability", "modules", "best-practice"]
    version_added = "v1.0.0"

    def matchtask(self, task, file=None):
        """Check if a task uses yum, apt, or dnf instead of package."""
        # Get the module name from the task
        if hasattr(task, "action"):
            module_name = task.action
        else:
            # Fallback for different ansible-lint versions
            module_name = task.get("action", {}).get("__ansible_module__")

        # Check if the task uses a distribution-specific package manager
        return module_name in ["yum", "apt", "dnf", "zypper", "pacman"]
