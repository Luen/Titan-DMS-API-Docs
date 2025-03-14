# Titan DMS API Documentation

This repository contains automatically generated documentation for the Titan DMS API. The documentation is generated using a Python script that scrapes the official Titan DMS Developer Portal.

## Features

- Comprehensive API documentation for all Titan DMS endpoints
- JSON and Markdown formats
- Automatically generated and updated
- Includes:
  - API descriptions
  - Endpoints
  - Request/Response formats
  - Operation details
  - Example responses

## APIs Covered

1. Accounting Api
2. Appraisal Api
3. CRM Api
4. Part Order
5. Service Api
6. Sundry Api
7. Vehicle Deal Api
8. Vehicle Stock
9. Vehicle Stock Card

## Getting Started

### Prerequisites

- Python 3.7+
- Playwright
- dotenv

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Titan-DMS-API-Docs.git
cd Titan-DMS-API-Docs
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with your Titan DMS API credentials:
```
TITAN_API_USERNAME=your_username
TITAN_API_PASSWORD=your_password
```

### Usage

Run the documentation generator:
```bash
python main.py
```

This will:
1. Log into the Titan DMS Developer Portal
2. Scrape all API documentation
3. Generate both JSON and Markdown files with timestamps

## Documentation Format

The documentation is generated in two formats:

1. **Markdown (.md)**: Human-readable format with proper formatting and structure
2. **JSON (.json)**: Machine-readable format for programmatic access

### Markdown Structure

```markdown
# Titan DMS API Documentation

## [API Name]
**Type:** [API Type]
**Description:** [API Description]
**URL:** [API URL]

### Operations
#### [Method] [Operation Name]
[Operation Description]
**Endpoint:** [Endpoint URL]
**Response:** [JSON Response Example]
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Titan DMS for providing the API documentation
- The Playwright team for the excellent browser automation tool
