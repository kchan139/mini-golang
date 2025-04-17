#!/bin/bash
export TERM=xterm

# ==================================================================
# Compiler Test Runner Script
# Purpose: Automated execution of compiler phase-specific test suites
# Platform Note: Use 'sed -i 's/\r$//' test.sh' when switching to Windows
# ==================================================================

# Script to generate, clear, and run compiler test suites
# Usage: ./test.sh {lexer|parser|ast|semantic|clean}

# Validate argument count
if [ "$#" -ne 1 ]; then
    echo "Error: Invalid number of arguments"
    echo "Usage: $0 {lexer|parser|ast|semantic|clean}"
    echo ""
    echo "Operations:"
    echo "  lexer    - Run lexical analysis test suite"
    echo "  parser   - Run syntax analysis test suite"
    echo "  ast      - Run abstract syntax tree generation tests"
    echo "  semantic - Run semantic analysis tests"
    echo "  codegen  - Run code generation tests"
    echo "  all      - Run all tests"
    echo "  clean    - Remove all test artifacts"
    exit 1
fi

# Define directory paths for test cases and expected outputs
INPUT="./test/testcases"  # Directory containing input test files
OUTPUT="./test/solutions"  # Directory containing expected outputs

python main.py gen && clear
# Process command line argument and execute the appropriate action
case "$1" in
    lexer)
        # Execute lexical analyzer tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Running lexical analysis tests..."
        python main.py test LexerSuite
        ;;
    parser)
        # Execute syntax analyzer tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Running syntax analysis tests..."
        python main.py test ParserSuite
        ;;
    ast)
        # Execute abstract syntax tree generation tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Running AST generation tests..."
        python main.py test ASTGenSuite
        ;;
    semantic)
        # Execute semantic analysis tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Running semantic analysis tests..."
        python main.py test CheckSuite
        ;;
    codegen)
        # Execute code generation tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "Running code generation tests..."
        python main.py test CodeGenSuite
        ;;
    all)
        # Execute all unit tests
        rm -f ${INPUT}/* 2>/dev/null
        rm -f ${OUTPUT}/* 2>/dev/null
        echo "<<< RUNNING ALL TESTS >>>"
        echo ""
        echo "Running lexical analysis tests..."
        python main.py test LexerSuite
        echo ""
        echo "Running syntax analysis tests..."
        python main.py test ParserSuite
        echo ""
        echo "Running AST generation tests..."
        python main.py test ASTGenSuite
        echo ""
        echo "Running semantic analysis tests..."
        python main.py test CheckSuite
        echo ""
        # echo "Running code generation tests..."
        # python main.py test CodeGenSuite
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
        echo "Usage: $0 {lexer|parser|ast|semantic|clean}"
        echo ""
        echo "Operations:"
        echo "  lexer    - Run lexical analysis test suite"
        echo "  parser   - Run syntax analysis test suite"
        echo "  ast      - Run abstract syntax tree generation tests"
        echo "  semantic - Run semantic analysis tests"
        echo "  codegen  - Run code generation tests"
        echo "  all      - Run all tests"
        echo "  clean    - Remove all test artifacts"
        exit 1
        ;;
esac