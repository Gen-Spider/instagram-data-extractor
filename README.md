# Instagram Data Extractor

A Python-based Instagram data extraction tool that downloads user content, followers, following lists and creates an Instagram-like HTML/CSS/JS interface for data visualization.

## Features

- Extract Instagram user data and content
- Download followers and following lists
- Create interactive HTML/CSS/JS interface
- Support for multiple data formats
- Clean, organized data visualization

## Requirements

- Python 3.9 or higher (including Python 3.13)
- Valid Instagram account
- Internet connection

## Installation

### Quick Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/Gen-Spider/instagram-data-extractor.git
cd instagram-data-extractor

# Install using pip (supports Python 3.13)
pip install -e .
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/Gen-Spider/instagram-data-extractor.git
cd instagram-data-extractor

# Install dependencies
pip install -r requirements.txt
```

### Python 3.13 Compatibility

This project is fully compatible with Python 3.13. All dependencies have been updated to support the latest Python version:

- ✅ instagrapi ≥2.2.0 (Python 3.13 compatible)
- ✅ pillow ≥11.0.0 (Full Python 3.13 support)
- ✅ selenium ≥4.25.0 (Python 3.13 compatible)
- ✅ All other dependencies updated for compatibility

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Instagram credentials and preferences

## Usage

### Command Line
```bash
# Run the extractor
python instagram_extractor.py

# Or if installed via pip
instagram-extractor
```

### Python Script
```python
from instagram_extractor import InstagramExtractor

extractor = InstagramExtractor()
extractor.run()
```

## Development

### Setting up Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Type checking
mypy instagram_extractor.py
```

## Troubleshooting

### Python 3.13 Issues

If you encounter installation errors with Python 3.13, ensure you have the latest package versions:

```bash
# Update pip and build tools
pip install --upgrade pip setuptools wheel

# Install from updated requirements
pip install -r requirements.txt
```

### Common Issues

- **KeyError: '__version__'**: Update to newer package versions (fixed in this release)
- **Build wheel errors**: Ensure you're using pip ≥23.0 and setuptools ≥65.0
- **Instagram API errors**: Check your credentials and rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. Please respect Instagram's Terms of Service and rate limits.