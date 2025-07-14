from ansiblelint.rules import AnsibleLintRule

class UsePackageModuleRule(AnsibleLintRule):
    id = 'CUSTOM001'
    shortdesc = 'Use package module instead of yum, apt, or dnf'
    description = (
        'Tasks should use the generic package module instead of yum, apt, or dnf '
        'for better portability.'
    )
    severity = 'MEDIUM'
    tags = ['portability', 'modules']

    def matchtask(self, file, task):
        module = task.get('action', {}).get('__ansible_module__')
        if module in ['yum', 'apt', 'dnf']:
            return True
        return False