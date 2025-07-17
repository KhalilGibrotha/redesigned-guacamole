# Contributing to Confluence Documentation Publisher

Thank you for your interest in contributing! This project provides reusable GitHub Actions workflows for publishing documentation to Confluence.

## Code of Conduct

This project follows a simple code of conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment

## How to Contribute

### Reporting Issues

1. Check existing issues first
2. Use the provided issue templates
3. Include relevant environment details (Python version, Confluence setup, etc.)
4. Provide clear reproduction steps

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test your changes**
   ```bash
   # Test Python script locally
   python scripts/confluence_publisher.py --dry-run --docs-dir docs --vars-file docs/vars.yaml
   
   # Run linting
   yamllint .
   python -m flake8 scripts/
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: clear description of changes"
   ```
6. **Push and create a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/redesigned-guacamole.git
cd redesigned-guacamole

# Install Python dependencies
pip install -r requirements.txt

# Install development tools (optional)
pip install flake8 black

# Test the confluence publisher
python scripts/confluence_publisher.py --help
```

## Quality Standards

### Before Submitting

- [ ] Python code passes linting (`python -m flake8 scripts/`)
- [ ] YAML files validate (`yamllint .`)
- [ ] Confluence publisher works in dry-run mode
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive

### Coding Standards

**Python Code:**
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include docstrings for functions and classes
- Handle errors gracefully

**YAML Files:**
- Use 2-space indentation
- Keep lines under 120 characters
- Include descriptive comments
- Follow GitHub Actions best practices

**Documentation:**
- Update README.md for user-facing changes
- Include examples for new features
- Use clear, concise language

### Testing

- Test Python scripts with `--dry-run` mode
- Validate YAML frontmatter formats
- Test with different file structures
- Include example documentation files

## Pull Request Process

1. **Description**: Clearly describe what your PR does
2. **Testing**: Include testing information and screenshots if applicable
3. **Documentation**: Update relevant documentation
4. **Breaking Changes**: Call out any breaking changes
5. **Review**: Be responsive to review feedback

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (Python script, workflows)
- [ ] New feature (publishing functionality, workflow enhancements)
- [ ] Documentation update
- [ ] Workflow improvement

## Testing
- [ ] Python script tested with `--dry-run`
- [ ] YAML files pass validation
- [ ] Manual testing completed
- [ ] Works with sample documentation

## Checklist
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Follows repository patterns
```

## Areas for Contribution

### High Priority
- Bug fixes in Python publisher script
- GitHub Actions workflow improvements
- Documentation and example enhancements
- Error handling and logging improvements

### Medium Priority
- Additional file format support
- Enhanced Jinja2 template features
- Confluence API improvements
- Publishing report enhancements

### Future Enhancements
- Multi-space Confluence support
- Advanced template library
- Integration with other documentation tools
- Performance optimizations

## Development Guidelines

### File Organization
- Keep Python scripts modular and well-documented
- Use descriptive variable names and function names
- Organize workflows logically
- Maintain consistent code style

### Documentation
- Update README.md for user-facing changes
- Include docstrings in Python code
- Provide examples for new features
- Keep usage examples current

### Security
- Never commit real credentials
- Use GitHub secrets properly
- Follow least-privilege principles
- Include security considerations in PRs

## Release Process

1. Version updates follow semantic versioning
2. Test workflows with multiple repository setups
3. Update documentation and examples
4. Create GitHub release with changelog

## Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for general questions
- **Documentation**: Check README.md and docs/ folder first
- **Code Review**: Ask for specific feedback in PRs

## Recognition

Contributors will be:
- Listed in the project contributors
- Mentioned in release notes for significant contributions
- Credited in documentation updates

Thank you for contributing! 🎉
