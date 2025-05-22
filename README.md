# MiniGo Programming Language Compiler

A compiler for the MiniGo programming language, implemented in Python using ANTLR for parsing. MiniGo is a simplified version of Go designed for educational purposes.

## Module Evaluation Results

* **Lexer**: 100/100 (100%)
* **Recognizer**: 98/100 (98%)
* **AST Generation**: 96/100 (96%)
* **Static Check**: 107/125 (85.6%)
* **Code Generation**: 100/101 (99,01%)
* **Optimization**: Not in course scope

### Overall: 95.25%

---

## Project Structure

```
└── kchan139-mini-golang/
├── MiniGo/
│   └── src/
│       ├── main.py               \# Main compiler script
│       ├── main/
│       │   └── minigo/
│       │       ├── astgen/       \# Abstract Syntax Tree generation
│       │       ├── checker/      \# Static checking (semantic analysis)
│       │       ├── codegen/      \# Code generation
│       │       ├── parser/       \# Lexer and Parser (ANTLR G4)
│       │       └── utils/        \# Utility modules (AST nodes, Visitor)
│       └── test/
│           ├── \*.py             \# Test suites (Lexer, Parser, AST, Check, CodeGen)
│           └── TestUtils.py      \# Test utilities
└── Specification/
    └── MiniGo Spec 1.0.2.pdf     \# MiniGo language specification
```

### Installation & Usage (Docker)

If you are already familiar with Docker, this is the recommended and easier setup method.

1.  **Build the Docker image:**

    ```bash
    docker compose up --build -d
    ```

2.  **Run commands inside the container:**

    ```bash
    # Enter an interactive shell in the container
    docker compose exec minigo bash

    # Inside the container, navigate to the source directory
    cd MiniGo/src

    # Now you can run the compiler commands (see Testing section)
    ./test.sh all
    ```

### Installation (Native)

#### Environment Setup

**Required**:
* Python >= 3.10 (3.12 recommended)
* Java Development Kit (JDK) (for ANTLR)

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

**Note:** Ensure the `ANTLR_JAR` environment variable is set to the path of the `antlr-4.9.2-complete.jar` file (e.g., `export ANTLR_JAR=/MiniGo/src/antlr-4.9.2-complete.jar`).

## Testing

### Using Bash Script (`test.sh`)

```bash
# Make the script executable
chmod +x test.sh

# Run specific test phases
./test.sh lexer     # Lexer tests
./test.sh parser    # Parser tests
./test.sh ast       # AST Generation tests
./test.sh semantic  # Semantic Analysis (Static Check) tests
./test.sh codegen   # Code Generation tests
./test.sh all       # Run all test suites sequentially
./test.sh clean     # Clean test artifacts (input/output files)
```

**Note:** The `test.sh` script first runs `python main.py gen` every time.

## Language Specification

For details about the MiniGo language syntax and semantics, refer to the [Specification](Specification).