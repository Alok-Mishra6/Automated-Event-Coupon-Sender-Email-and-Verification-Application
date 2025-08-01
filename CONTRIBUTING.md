# Contributing to Event Ticket Management System

Thank you for your interest in contributing to the Event Ticket Management System! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Google Cloud Console account (for OAuth testing)
- Basic knowledge of Flask, HTML/CSS, and JavaScript

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/event-ticket-system.git
   cd event-ticket-system
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your development settings
   ```

4. **Run Setup**
   ```bash
   python setup.py
   ```

5. **Start Development Server**
   ```bash
   python app.py
   ```

## 🎯 How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 96]
- Python version: [e.g. 3.9.7]

**Additional context**
Any other context about the problem.
```

### Suggesting Features

Feature requests are welcome! Please provide:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach
- Any relevant examples or mockups

### Code Contributions

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run existing tests
   python test_encryption_service.py
   python test_email_service.py
   python test_csv_manager.py
   
   # Test the application manually
   python app.py
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use descriptive variable and function names

**Example:**
```python
def generate_encrypted_ticket(email: str, event_name: str) -> Dict[str, Any]:
    """
    Generate an encrypted ticket for the specified attendee.
    
    Args:
        email: Attendee's email address
        event_name: Name of the event
        
    Returns:
        Dictionary containing ticket data and QR code
    """
    # Implementation here
    pass
```

### JavaScript Code Style
- Use ES6+ features
- Use const/let instead of var
- Use meaningful function and variable names
- Add comments for complex logic

**Example:**
```javascript
const generateQRCode = async (ticketData) => {
    // Generate QR code from ticket data
    try {
        const qrCode = await createQRCode(ticketData);
        return qrCode;
    } catch (error) {
        console.error('QR code generation failed:', error);
        throw error;
    }
};
```

### HTML/CSS Standards
- Use semantic HTML5 elements
- Follow accessibility guidelines (WCAG 2.1)
- Use CSS custom properties for theming
- Mobile-first responsive design

### Commit Message Format

Use conventional commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): add Google OAuth integration
fix(scanner): resolve camera permission issues
docs(readme): update installation instructions
style(ui): improve dark theme consistency
```

## 🧪 Testing Guidelines

### Unit Tests
- Write tests for all new functions
- Aim for high code coverage
- Use descriptive test names
- Test both success and failure cases

### Integration Tests
- Test complete user workflows
- Verify API endpoints work correctly
- Test OAuth flow integration
- Validate email sending functionality

### Manual Testing Checklist
- [ ] User authentication works
- [ ] CSV upload and validation
- [ ] Ticket generation and email sending
- [ ] QR code scanning and verification
- [ ] Mobile responsiveness
- [ ] Error handling and user feedback

## 🔒 Security Considerations

### Sensitive Data
- Never commit real credentials or API keys
- Use environment variables for configuration
- Sanitize all user inputs
- Follow OWASP security guidelines

### Code Review Focus Areas
- Input validation and sanitization
- Authentication and authorization
- Data encryption and storage
- Error handling and logging

## 📚 Documentation

### Code Documentation
- Add docstrings to all functions and classes
- Include type hints
- Document complex algorithms
- Provide usage examples

### User Documentation
- Update README.md for new features
- Add troubleshooting information
- Include configuration examples
- Provide clear setup instructions

## 🎨 UI/UX Guidelines

### Design Principles
- Maintain consistency with existing dark theme
- Ensure accessibility compliance
- Optimize for mobile devices
- Provide clear user feedback

### Color Scheme
```css
:root {
    --bg-primary: #0a0a0a;
    --bg-secondary: #1a1a1a;
    --bg-tertiary: #2a2a2a;
    --accent-primary: #6366f1;
    --accent-secondary: #8b5cf6;
    --text-primary: #ffffff;
    --text-secondary: #a1a1aa;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
}
```

## 🚀 Release Process

### Version Numbering
We follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number bumped
- [ ] Changelog updated
- [ ] Security review completed

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Provide constructive feedback
- Focus on the code, not the person

### Communication
- Use clear, professional language
- Provide context and examples
- Be patient with questions
- Share knowledge and resources

## 📞 Getting Help

### Development Questions
- Check existing documentation first
- Search closed issues for similar problems
- Ask specific, detailed questions
- Provide relevant code examples

### Contact Information
- GitHub Issues: For bugs and feature requests
- GitHub Discussions: For general questions
- Email: For security-related concerns

## 🏆 Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Release notes for significant contributions
- GitHub contributors page

Thank you for contributing to making event management more secure and efficient! 🎫