# MiniGo Programming Language

## Setup Guide

### Environment Requirements
- **Python Version**: 3.9.x - 3.12.x (Recommended: 3.12)

#### Setup Steps

##### Windows
1. Install Python from official website
2. Open Command Prompt
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

##### macOS/Linux
```bash
# Install Python via Homebrew (macOS) or package manager (Linux)
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Navigate to the assignment source directory:
```bash
cd 'Assignment 1/src'
```

#### Generate ANTLR Files and Run Tests
You have two options to run the tests:

**Option 1: Manual Commands**
- Generate ANTLR Files
```bash
python main.py gen
```
- Run Lexer Tests
```bash
python main.py test LexerSuite
```
- Run Parser Tests
```bash
python main.py test ParserSuite
```

- Run AST Generation Tests
```bash
python main.py test ASTGenSuite
```

- Run Semantic Analysis Tests
```bash
python main.py test CheckSuite
```

**Option 2: Use the Helper Script test.sh**
A shell script (`test.sh`) has been added at the repository root to automate these tasks. It accepts a parameter to choose the test suite. The script runs the file-generation command and, only if that succeeds, clears the screen and runs the chosen tests.

- Make the Script Executable
```bash
chmod +x test.sh
```
- Run Lexer Tests
```bash
./test.sh lexer
```
- Run Parser Tests
```bash
./test.sh parser
```
- Run AST Generation Tests
```bash
./test.sh ast
```
- Run Semantic Analysis Tests
```bash
./test.sh semantic
```

Note: If any error occurs during the python main.py gen step, the script will stop and the test suite command will not be executed.