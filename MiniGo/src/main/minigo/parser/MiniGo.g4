// 2211649

grammar MiniGo;

@lexer::header {
from lexererr import *
}

@lexer::members {
def __init__(self, input=None, output:TextIO = sys.stdout):
    super().__init__(input, output)
    self.checkVersion("4.9.2")
    self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
    self._actions = None
    self._predicates = None
    self.prev_token_type = None  # Track previous token type

def emit(self):
    current_token_type = self.type
    
    # Handle NL case based on the actual previous token
    if current_token_type == self.NL:
        # Safely get previous token name
        prev_name = self.symbolicNames[self.prev_token_type] if (self.prev_token_type is not None and 0 <= self.prev_token_type < len(self.symbolicNames)) else "None"
        curr_name = self.symbolicNames[current_token_type]
        
        if self.shouldEmitSemicolon():
            token = super().emit()
            token.type = self.SEMICOLON
            token.text = ';'
            self.prev_token_type = token.type
            return token
        else:
            self.skip()
            return self.nextToken()
    
    # Handle all other token types
    token = super().emit()
    
    if current_token_type == self.UNCLOSE_STRING:
        result = token
        if result.text and result.text[-1] == '\n':
            result.text = result.text[0:-1]
        self.prev_token_type = current_token_type
        raise UncloseString(result.text)
        
    elif current_token_type == self.ILLEGAL_ESCAPE:
        result = token
        self.prev_token_type = current_token_type
        raise IllegalEscape(result.text)
        
    elif current_token_type == self.ERROR_CHAR:
        result = token
        self.prev_token_type = current_token_type
        raise ErrorToken(result.text)
        
    elif current_token_type == self.STRING_LIT:
        result = token
        self.prev_token_type = current_token_type
        return result
    
    # Update previous token type before returning
    self.prev_token_type = current_token_type
    return token

def shouldEmitSemicolon(self):
    return self.prev_token_type in {
        self.ID, self.INT_LIT, self.FLOAT_LIT, self.BOOL_LIT, self.STRING_LIT,
        self.INT, self.FLOAT, self.BOOLEAN, self.STRING, 
        self.NIL, self.RETURN, self.CONTINUE, self.BREAK,
        self.RIGHT_PAREN, self.RIGHT_BRACKET, self.RIGHT_BRACE
    }

}

options{
	language = Python3;
}


//////////////////////////////////
/////////// LEXER RULES //////////
//////////////////////////////////

//========== Fragments ==========//

fragment EscapeChar
    :
    '\\' [rnt'\\"] | ~[\n'\\"]
    ;
fragment StringContent
    : EscapeChar | ~["\\\r\n]
    ;
fragment Digit
    : [0-9]
    ;
fragment Letter
    : [a-zA-Z]
    ;
fragment ScientificNotation
    : [eE] [+-]? Digit+
    ;


//========== 3.1. Characters Set ==========//

NL
    : '\r'? '\n'
    ;

WS 
    : [ \t\r\f]+ -> skip // skip spaces, tabs, carriage returns
    ;


//=========== 3.2. Program Comment ===========//

LINE_COMMENT
    : '//' ~[\r\n]*-> skip
    ; 

BLOCK_COMMENT
    : '/*' (BLOCK_COMMENT | .)*? '*/'-> skip
    ;


// =========== 3.3. Tokens Set ===========//

// 3.3.2. Keywords
IF
    : 'if'
    ;
ELSE
    : 'else'
    ;
FOR
    : 'for'
    ;
RETURN
    : 'return'
    ;
FUNC
    : 'func'
    ;
TYPE
    : 'type'
    ;
STRUCT
    : 'struct'
    ;
INTERFACE
    : 'interface'
    ;
STRING
    : 'string'
    ;
INT
    : 'int'
    ;
FLOAT
    : 'float'
    ;
BOOLEAN
    : 'boolean'
    ;
CONST
    : 'const'
    ;
VAR
    : 'var'
    ;
CONTINUE
    : 'continue'
    ;
BREAK
    : 'break'
    ;
RANGE
    : 'range'
    ;
NIL
    : 'nil'
    ;

// 3.3.3. Operators
// Arithmetic
PLUS
    : '+'
    ;
MINUS
    : '-'
    ;
MULT
    : '*'
    ;
DIV
    : '/'
    ;
MOD
    : '%'
    ;

// Relational
EQUAL
    : '=='
    ;
NOT_EQUAL
    : '!='
    ;
LESS
    : '<'
    ;
LESS_EQUAL
    : '<='
    ;
GREATER
    : '>'
    ;
GREATER_EQUAL
    : '>='
    ;

// Logical
AND
    : '&&'
    ;
OR
    : '||'
    ;
NOT
    : '!'
    ;

// Assignment
ASSIGN
    : '='
    ;
COLON_ASSIGN
    : ':='
    ;
PLUS_ASSIGN
    : '+='
    ;
MINUS_ASSIGN
    : '-='
    ;
MULT_ASSIGN
    : '*='
    ;
DIV_ASSIGN
    : '/='
    ;
MOD_ASSIGN
    : '%='
    ;


// Dot
DOT
    : '.'
    ;

// 3.3.4. Separators
LEFT_BRACKET
    : '['
    ;
RIGHT_BRACKET
    : ']'
    ;
LEFT_PAREN
    : '('
    ;
RIGHT_PAREN
    : ')'
    ;
LEFT_BRACE
    : '{'
    ;
RIGHT_BRACE
    : '}'
    ;
SEMICOLON
    : ';'
    ;
COLON
    : ':'
    ;
COMMA
    : ','
    ;

// 3.3.5 Literals
// Integer Literals
INT_LIT
    : '0'                             // Zero
    | [1-9] Digit*                    // Decimal
    | '0'[bB] [0-1]+                  // Binary
    | '0'[oO] [0-7]+                  // Octal
    | '0'[xX] (Digit | [a-fA-F])+     // Hex
    ;

// Floating point Literals
FLOAT_LIT
    : Digit+ '.' Digit* ScientificNotation?
    ;

// Boolean Literals
BOOL_LIT
    : TRUE | FALSE
    ;
TRUE
    : 'true'
    ;
FALSE
    : 'false'
    ;

// Nil Literal
NIL_LIT
    : NIL
    ;

// String Literals
UNCLOSE_STRING
    : '"' StringContent* ([\r\n] | EOF)
    ;
ILLEGAL_ESCAPE
    : '"' StringContent* '\\' ~[ntr'\\"]
    ;
STRING_LIT
    : '"' StringContent* '"'
    ;

// 3.3.1. Idenfifiers
ID
    : (Letter | '_') (Letter | Digit | '_')*
    ;


// If nothing matches, it's an illegal character
ERROR_CHAR
    : .
    ;



/////////////////////////////////////////////
//////////////// PARSER RULES ///////////////
/////////////////////////////////////////////

//========== 4. Type and Value ==========//
primitiveType
    : INT 
    | FLOAT 
    | BOOLEAN 
    | STRING
    ;
arrayType
    : arrayAccessList (primitiveType | ID)
    ;
arrayAccessParam
    : INT_LIT | ID
    ;
structType
    : STRUCT LEFT_BRACE manyFieldDecl RIGHT_BRACE
    ;
manyFieldDecl
    : fieldDecl manyFieldDeclTail
    ;
manyFieldDeclTail
    : fieldDecl manyFieldDeclTail | 
    ;
fieldDecl
    : ID typeSpec optionalSemicolon
    | methodDecl
    ;
typeSpec
    : primitiveType 
    | arrayType 
    | structType 
    | interfaceType
    | ID
    ;
optionalTypeSpec
    : typeSpec | 
    ;
optionalSemicolon
    : SEMICOLON | 
    ;
interfaceType
    : INTERFACE LEFT_BRACE manyInterfaceContent RIGHT_BRACE
    ;
manyInterfaceContent
    : interfaceContent manyInterfaceContentTail
    ;
manyInterfaceContentTail
    : interfaceContent manyInterfaceContentTail | 
    ;
interfaceContent
    : interfaceMethod | stmt
    ;


//========== 5. Variables, Constants and Functions ==========//
block
    : LEFT_BRACE manyBlockContent RIGHT_BRACE optionalSemicolon
    ;
manyBlockContent
    : blockContent manyBlockContentTail
    ;
manyBlockContentTail
    : blockContent manyBlockContentTail |
    ;
blockContent
    : stmt | block
    ;
varDecl
    : VAR ID typeSpec ASSIGN expr SEMICOLON
    | VAR ID ASSIGN expr SEMICOLON
    | VAR ID typeSpec SEMICOLON
    ;
constDecl
    : CONST ID ASSIGN expr SEMICOLON
    ;
funcDecl
    : FUNC ID LEFT_PAREN paramList RIGHT_PAREN optionalTypeSpec block SEMICOLON
    ;
methodDecl
    : FUNC LEFT_PAREN ID ID RIGHT_PAREN ID LEFT_PAREN paramList RIGHT_PAREN optionalTypeSpec block SEMICOLON
    ;
typeDecl
    : TYPE ID typeSpec SEMICOLON
    ;
interfaceMethod
    : ID LEFT_PAREN paramList RIGHT_PAREN optionalTypeSpec SEMICOLON
    ;

paramList
    : param paramListTail |
    ;
paramListTail
    : COMMA param paramListTail | 
    ;
param
    : idList typeSpec
    ;
idList
    : ID idListTail
    ;
idListTail
    : COMMA ID idListTail | 
    ;


//========== 6. Expressions ==========//
expr
    : expr OR expr1 
    | expr1
    ;
expr1
    : expr1 AND expr2 
    | expr2
    ;
expr2
    : expr2 (EQUAL | NOT_EQUAL | LESS | LESS_EQUAL | GREATER | GREATER_EQUAL) expr3 
    | expr3
    ;
expr3
    : expr3 (PLUS | MINUS) expr4 
    | expr4
    ;
expr4
    : expr4 (MULT | DIV | MOD) expr5 
    | expr5
    ;
expr5
    : unaryOperator expr5 
    | expr6
    ;
unaryOperator
    : MINUS 
    | NOT
    ;
expr6
    : expr6 ( DOT 
        (ID | funcCall) 
        | LEFT_BRACKET expr RIGHT_BRACKET
        | LEFT_BRACE expr RIGHT_BRACE
        )
    | expr7
    ;
expr7
    : ID 
    | literal 
    | LEFT_PAREN expr RIGHT_PAREN 
    | funcCall
    ;

literal
    : INT_LIT 
    | FLOAT_LIT 
    | STRING_LIT 
    | BOOL_LIT 
    | NIL 
    | arrayLit 
    | structLit
    ;
arrayLit
    : arrayAccessList (primitiveType | ID) LEFT_BRACE arrayElementListList RIGHT_BRACE
    ;
arrayAccessList
    : LEFT_BRACKET arrayAccessParam RIGHT_BRACKET arrayAccessListTail
    ;
arrayAccessListTail
    : LEFT_BRACKET arrayAccessParam RIGHT_BRACKET arrayAccessListTail | 
    ;
arrayElementListList
    : arrayElementList arrayElementListListTail | 
    ;
arrayElementListListTail
    : COMMA arrayElementList arrayElementListListTail | 
    ;
arrayElementList
    : arrayElement arrayElementListTail
    ;
arrayElementListTail
    : COMMA arrayElement arrayElementListTail | 
    ;
arrayElement
    : INT_LIT | FLOAT_LIT | STRING_LIT | BOOL_LIT | NIL | ID
    | LEFT_BRACE arrayElementList RIGHT_BRACE
    | ID LEFT_BRACE structMemberList RIGHT_BRACE
    ;
structLit
    : ID LEFT_BRACE structMemberList RIGHT_BRACE
    ;

structMemberList
    : structMember structMemberListTail | 
    ;
structMemberListTail
    : COMMA structMember structMemberListTail |
    ;
structMember
    : ID COLON expr
    ;


funcCall
    : ID LEFT_PAREN exprList RIGHT_PAREN optionalSemicolon
    ;
methodCall
    : ID DOT (expr | assignStmt) optionalSemicolon
    ;
exprList
    : expr exprListTail | 
    ;
exprListTail
    : COMMA expr exprListTail |
    ;


//========== 7. Variable, Constant Declaration Statement ==========//
stmt: decl
    | assignStmt
    | ifStmt
    | forStmt
    | breakStmt
    | continueStmt
    | callStmt
    | returnStmt
    ;

assignStmt
    : lhs (COLON_ASSIGN | PLUS_ASSIGN | MINUS_ASSIGN | MULT_ASSIGN | DIV_ASSIGN | MOD_ASSIGN) expr optionalSemicolon
    ;
lhs
    : ID
    | arrayAccess
    | fieldAccess
    | lhs DOT ID
    | lhs DOT arrayAccess
    | lhs DOT fieldAccess
    ;
arrayAccess
    : ID arrayDim
    ;
arrayDim
    : arrayDim LEFT_BRACKET expr RIGHT_BRACKET
    | LEFT_BRACKET expr RIGHT_BRACKET
    ;
fieldAccess
    : ID DOT ID fieldAccess
    | dim
    ;
dim
    : LEFT_BRACKET INT_LIT RIGHT_BRACKET
    ;

ifStmt
    : IF LEFT_PAREN expr RIGHT_PAREN ifElseBlock optionalElseBlock
    ;
ifElseBlock
    : block | ifStmt
    ;
optionalElseBlock
    : ELSE ifElseBlock |
    ;

// for loop
forStmt
    : FOR (forClause | rangeClause) block
    ;
forClause
    : (assignStmt | varDecl)? expr? SEMICOLON assignStmt?
    ;
rangeClause
    : ID COMMA ID COLON_ASSIGN RANGE expr 
    | expr
    ;

breakStmt
    : BREAK SEMICOLON
    ;
continueStmt
    : CONTINUE SEMICOLON
    ;
returnStmt
    : RETURN expr? SEMICOLON
    ;
callStmt
    : expr SEMICOLON
    ;


//========== 9. Built-in Functions ==========//



//========== TOP-LEVEL DECLARATIONS ==========//
program
    : decl_stmt+ EOF
    ;
decl_stmt
    : decl | stmt
    ;
decl
    : constDecl 
    | varDecl 
    | typeDecl 
    | funcDecl 
    | methodDecl
    | mainFunction
    ;

mainFunction
    : FUNC 'main' LEFT_PAREN RIGHT_PAREN block
    ;