import sys,os,traceback
sys.path.append('./test/')
import subprocess
import unittest
from antlr4 import *

#Make sure that ANTLR_JAR is set to antlr-4.9.2-complete.jar
ANTLR_JAR = os.environ.get('ANTLR_JAR')
TARGET = '../target/main/minigo/parser' if os.name == 'posix' else os.path.normpath('../target/')
locpath = ['./main/minigo/parser/','./main/minigo/astgen/','./main/minigo/utils/','./main/minigo/checker/']
for p in locpath:
    if not p in sys.path:
        sys.path.append(p)

def main(argv):
    global ANTLR_JAR, TARGET
    if len(argv) < 1:
        printUsage()
    elif argv[0] == 'gen':
        subprocess.run(["java","-jar",ANTLR_JAR,"-o","../target","-no-listener","-visitor","main/minigo/parser/MiniGo.g4"])
    elif argv[0] == 'clean':
        subprocess.run(["rm","-rf","../target/main"])
    elif argv[0] == 'test':
        if not './main/minigo/parser/' in sys.path:
            sys.path.append('./main/minigo/parser/')
        if os.path.isdir(TARGET) and not TARGET in sys.path:
            sys.path.append(TARGET)
        if len(argv) < 2:
            printUsage()
        elif argv[1] == 'LexerSuite':
            from LexerSuite import LexerSuite
            suite = unittest.TestLoader().loadTestsFromTestCase(LexerSuite)
            success = test(suite)
            if not success:
                sys.exit(1)
        elif argv[1] == 'ParserSuite':
            from ParserSuite import ParserSuite
            suite = unittest.TestLoader().loadTestsFromTestCase(ParserSuite)
            success = test(suite)
            if not success:
                sys.exit(1)
        elif argv[1] == 'ASTGenSuite':
            from ASTGenSuite import ASTGenSuite
            suite = unittest.TestLoader().loadTestsFromTestCase(ASTGenSuite)
            success = test(suite)
            if not success:
                sys.exit(1)
        elif argv[1] == 'CheckSuite':
            from CheckSuite import CheckSuite
            suite = unittest.TestLoader().loadTestsFromTestCase(CheckSuite)
            success = test(suite)
            if not success:
                sys.exit(1)
        else:
            printUsage()
    else:
        printUsage()
    

def test(suite):
    from pprint import pprint
    from io import StringIO
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    result = runner.run(suite)
    print('Tests run ', result.testsRun)
    print('Errors ', len(result.errors))
    print('Failures ', len(result.failures))
    
    # Print out error details
    if result.errors:
        print("\n===== ERRORS =====")
        for i, (test, error) in enumerate(result.errors):
            print(f"\nError {i+1}: {test}")
            print(error)
    
    # Print out failure details
    if result.failures:
        print("\n===== FAILURES =====")
        for i, (test, failure) in enumerate(result.failures):
            print(f"\nFailure {i+1}: {test}")
            print(failure)
    
    stream.seek(0)
    print('Test output\n', stream.read())
    
    # Return success status to caller
    return result.wasSuccessful()

def printUsage():
    print("python3 run.py gen")
    print("python3 run.py test LexerSuite")
    print("python3 run.py test ParserSuite")
    print("python3 run.py test ASTGenSuite")
    print("python3 run.py test CheckSuite")

if __name__ == "__main__":
   main(sys.argv[1:])