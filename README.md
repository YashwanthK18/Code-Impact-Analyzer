# Code Impact Analyzer

A tool designed to analyze the impact of code modifications across repositories and codebases.

## Project Structure

```
.
├── analyzer/        # Core analysis package
│   └── __init__.py
├── tests/           # Unit and integration tests
├── examples/        # Sample use-case files and test datasets
├── main.py          # Main entry point
├── requirements.txt # Project dependencies
├── .gitignore       # Git ignore rules
├── .env.example     # Template for environment variables
└── README.md        # Project documentation
```

## Getting Started

### 1. Prerequisites
- Python 3.10+

### 2. Setup
Clone or navigate to the project directory:
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Running
```bash
python main.py
```
