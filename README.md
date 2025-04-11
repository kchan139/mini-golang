# MiniGo Programming Language

## Environment Setup

**Required**: Python 3.9.x - 3.12.x (3.12 recommended)

### Installation

#### Windows
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Compiler

Navigate to the source directory:
```bash
cd MiniGo/src
```

### Testing

#### Direct Commands
```bash
# Generate ANTLR files
python main.py gen

# Run test suites
python main.py test LexerSuite
python main.py test ParserSuite
python main.py test ASTGenSuite
python main.py test CheckSuite
```

#### Using Automation Script
```bash
# Make executable
chmod +x test.sh

# Run specific test suites
./test.sh lexer     # Lexer tests
./test.sh parser    # Parser tests
./test.sh ast       # AST Generation tests
./test.sh semantic  # Semantic Analysis tests
```

Note: The script will only execute tests if code generation succeeds.