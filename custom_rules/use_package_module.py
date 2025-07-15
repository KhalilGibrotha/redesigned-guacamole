from ansiblelint.rules import AnsibleLintRule

class UsePackageModuleRule(AnsibleLintRule):
    """Rule to enforce the use of the 'package' module."""
    id = 'CUSTOM001'
    shortdesc = 'Use package module instead of yum, apt, or dnf'
    description = (
        'Tasks should use the generic package module instead of yum, apt, or dnf '
        'for better portability.'
    )
    severity = 'MEDIUM'
    tags = ['portability', 'modules']

    def matchtask(self, file, task):
        """Check if a task uses yum, apt, or dnf instead of package."""
        module = task.get('action', {}).get('__ansible_module__')
        return module in ['yum', 'apt', 'dnf']