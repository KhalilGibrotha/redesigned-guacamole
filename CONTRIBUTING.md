# Contributing to Confluence Documentation Automation

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

This project follows a simple code of conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment

## How to Contribute

### Reporting Issues

1. Check existing issues first
2. Use the provided issue templates
3. Include relevant environment details
4. Provide clear reproduction steps

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run validation**
   ```bash
   make validate
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: clear description of changes"
   ```
6. **Push and create a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/confluence-automation.git
cd confluence-automation

# Install development tools
make install-tools

# Set up pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
make dev
```

## Quality Standards

### Before Submitting

- [ ] Code passes all linting checks (`make lint`)
- [ ] Security checks pass (`make security-check`)
- [ ] Templates validate (`make validate-templates`)
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive

### Coding Standards

- Follow existing YAML formatting
- Use 2-space indentation
- Keep lines under 120 characters
- Include descriptive comments
- Use semantic task names

### Testing

- Add tests for new functionality
- Ensure existing tests pass
- Include documentation updates
- Test with different Ansible versions if applicable

## Pull Request Process

1. **Description**: Clearly describe what your PR does
2. **Testing**: Include testing information
3. **Documentation**: Update relevant documentation
4. **Breaking Changes**: Call out any breaking changes
5. **Review**: Be responsive to review feedback

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Passes make validate
- [ ] Manual testing completed
- [ ] Added/updated tests

## Checklist
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## Areas for Contribution

### High Priority
- Bug fixes and security improvements
- Documentation enhancements
- Test coverage improvements
- CI/CD workflow enhancements

### Medium Priority
- New template features
- Additional validation rules
- Performance optimizations
- Integration examples

### Future Enhancements
- Multi-space Confluence support
- Advanced Molecule scenarios
- Template library expansion
- External integrations

## Development Guidelines

### File Organization
- Keep playbooks focused and modular
- Use descriptive variable names
- Organize templates logically
- Maintain consistent structure

### Documentation
- Update README for significant changes
- Include inline comments for complex logic
- Provide examples for new features
- Keep documentation current

### Security
- Never commit real credentials
- Use Ansible Vault for sensitive data
- Follow least-privilege principles
- Include security considerations in PRs

## Release Process

1. Version bumping follows semantic versioning
2. Changelog updates for all releases
3. Testing in multiple environments
4. Documentation updates
5. GitHub release creation

## Getting Help

- **Issues**: Use GitHub issues for bugs and questions
- **Discussions**: Use GitHub discussions for general questions
- **Documentation**: Check existing documentation first
- **Code Review**: Ask for specific feedback in PRs

## Recognition

Contributors will be:
- Listed in the project contributors
- Mentioned in release notes for significant contributions
- Credited in documentation updates

Thank you for contributing! 🎉
