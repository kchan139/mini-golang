#!/bin/bash

# ==================================================================
# Compiler Test Runner Script
# Purpose: Automated execution of compiler phase-specific test suites
# Platform Note: Use 'sed -i 's/\r$//' test.sh' when switching to Windows
# ==================================================================

# Script to generate, clear, and run compiler test suites
# Usage: ./test.sh {lexer|parser|ast|checker|clean}

# Validate argument count
if [ "$#" -ne 1 ]; then
    echo "Error: Invalid number of arguments"
    echo "Usage: $0 {lexer|parser|ast|checker|clean}"
    echo ""
    echo "Operations:"
    echo "  lexer   - Run lexical analysis test suite"
    echo "  parser  - Run syntax analysis test suite"
    echo "  ast     - Run abstract syntax tree generation tests"
    echo "  checker - Run semantic analysis tests"
    echo "  clean   - Remove all test artifacts"
    exit 1
fi

# Define directory paths for test cases and expected outputs
INPUT="./test/testcases"  # Directory containing input test files
OUTPUT="./test/solutions"  # Directory containing expected outputs

export ANTLR_JAR="antlr-4.9.2-complete.jar"
python main.py gen && clear

# Process command line argument and execute the appropriate action
case "$1" in
    lexer)
        # Generate and execute lexical analyzer tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Running lexical analysis tests..."
        python main.py test LexerSuite
        ;;
    parser)
        # Generate and execute syntax analyzer tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Running syntax analysis tests..."
        python main.py test ParserSuite
        ;;
    ast)
        # Generate and execute abstract syntax tree generation tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Running AST generation tests..."
        python main.py test ASTGenSuite
        ;;
    checker)
        # Generate and execute semantic analysis tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Running semantic analysis tests..."
        python main.py test CheckSuite
        ;;
    clean)
        # Remove all test artifacts from directories
        clear
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Test artifacts removed from:"
        echo "- ${INPUT}"
        echo "- ${OUTPUT}"
        ;;
    *)
        # Handle invalid arguments
        echo "Error: Invalid argument '$1'"
        echo "Usage: $0 {lexer|parser|ast|checker|clean}"
        echo ""
        echo "Operations:"
        echo "  lexer   - Run lexical analysis test suite"
        echo "  parser  - Run syntax analysis test suite"
        echo "  ast     - Run abstract syntax tree generation tests"
        echo "  checker - Run semantic analysis tests"
        echo "  clean   - Remove all test artifacts"
        exit 1
        ;;
esac