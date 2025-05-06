'''
 *   @author Nguyen Hua Phung
 *   @version 1.0
 *   23/10/2015
 *   This file provides a simple version of code generator
 *
'''
from AST import *
from Utils import *
from Visitor import *
from StaticCheck import *
from StaticError import *
from Frame import Frame
from Emitter import Emitter
from abc import ABC, abstractmethod
from functools import reduce


class Val(ABC):
    pass

class Index(Val):
    def __init__(self, value):
        #value: Int

        self.value = value

class CName(Val):
    def __init__(self, value,isStatic=True):
        #value: String
        self.isStatic = isStatic
        self.value = value

class ClassType(Type):
    def __init__(self, name):
        #value: Id
        self.name = name


class CodeGenerator(BaseVisitor,Utils):
    def __init__(self):
        self.className = "MiniGoClass"
        self.astTree = None
        self.path = None
        self.emit = None
        self.function = None
        self.list_function = []

    def init(self):
        return [
            Symbol("getInt", MType(list(), IntType()), CName("io",True)),
            Symbol("putInt", MType([IntType()], VoidType()), CName("io",True)),
            Symbol("putIntLn", MType([IntType()], VoidType()), CName("io",True)),
            Symbol("getFloat", MType([], FloatType()), CName("io",True)),
            Symbol("putFloat", MType([FloatType()], VoidType()), CName("io",True)),
            Symbol("putFloatLn", MType([FloatType()], VoidType()), CName("io",True)),
            Symbol("putBool", MType([BoolType()], VoidType()), CName("io",True)),
            Symbol("putBoolLn", MType([BoolType()], VoidType()), CName("io",True)),
            Symbol("putString", MType([StringType()], VoidType()), CName("io",True)),
            Symbol("putStringLn", MType([StringType()], VoidType()), CName("io",True)),
            Symbol("putLn", MType([], VoidType()), CName("io",True)),
        ]

    def gen(self, ast, dir_):
        gl = self.init()
        self.astTree = ast
        self.path = dir_
        self.emit = Emitter(dir_ + "/" + self.className + ".j")
        self.visit(ast, gl)
       
        
    def emitObjectInit(self):
        frame = Frame("<init>", VoidType())  
        self.emit.printout(self.emit.emitMETHOD("<init>", MType([], VoidType()), False, frame))  # Bắt đầu định nghĩa phương thức <init>
        frame.enterScope(True)  
        self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), "this", ClassType(self.className), frame.getStartLabel(), frame.getEndLabel(), frame))  # Tạo biến "this" trong phương thức <init>
        
        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))
        self.emit.printout(self.emit.emitREADVAR("this", ClassType(self.className), 0, frame))  
        self.emit.printout(self.emit.emitINVOKESPECIAL(frame))  
    
        
        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        self.emit.printout(self.emit.emitRETURN(VoidType(), frame))  
        self.emit.printout(self.emit.emitENDMETHOD(frame))  
        frame.exitScope()  

    def emitObjectCInit(self, ast: Program, env):
        frame = Frame("<cinit>", VoidType())  
        self.emit.printout(self.emit.emitMETHOD("<clinit>", MType([], VoidType()), True, frame)) 
        frame.enterScope(True)  
        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))

        env['frame'] = frame
        for item in ast.decl:
            if isinstance(item, VarDecl) and item.varInit:
                self.visit(item, env)
        
        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        self.emit.printout(self.emit.emitRETURN(VoidType(), frame))  
        self.emit.printout(self.emit.emitENDMETHOD(frame))  
        frame.exitScope()

    def visitProgram(self, ast: Program, c):
        self.list_function = c + [Symbol(item.name, MType(list(map(lambda x: x.parType, item.params)), item.retType), CName(self.className)) for item in ast.decl if isinstance(item, FuncDecl)]
        env ={}
        env['env'] = [c]
        self.emit.printout(self.emit.emitPROLOG(self.className, "java.lang.Object"))
        env = reduce(lambda a, x: self.visit(x, a) if isinstance(x, VarDecl) else a, ast.decl, env)
        reduce(lambda a, x: self.visit(x, a) if isinstance(x, FuncDecl) else a, ast.decl, env)
        self.emitObjectInit()
        self.emitObjectCInit(ast, env)
        self.emit.printout(self.emit.emitEPILOG())
        return env

    def visitFuncDecl(self, ast: FuncCall, o: dict) -> dict:
        self.function = ast
        frame = Frame(ast.name, ast.retType)
        isMain = ast.name == "main"
        if isMain:
            mtype = MType([ArrayType([None],StringType())], VoidType())
            ast.body = Block([] + ast.body.member)
        else:
            mtype = MType(list(map(lambda x: x.parType, ast.params)), ast.retType)
        
        env = o.copy()
        env['frame'] = frame
        self.emit.printout(self.emit.emitMETHOD(ast.name, mtype,True, frame))
        frame.enterScope(True)
        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))
        env['env'] = [[]] + env['env']
        if isMain:
            self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), "args", ArrayType([None],StringType()), frame.getStartLabel(), frame.getEndLabel(), frame))
        else:
            env = reduce(lambda acc,e: self.visit(e,acc),ast.params,env)
        self.visit(ast.body,env)
        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        if type(ast.retType) is VoidType:
            self.emit.printout(self.emit.emitRETURN(VoidType(), frame)) 
        self.emit.printout(self.emit.emitENDMETHOD(frame))
        frame.exitScope()
        return o

    def visitParamDecl(self, ast: ParamDecl, o: dict) -> dict:
        frame = o['frame']
        index = frame.getNewIndex()
        o['env'][0].append(Symbol(ast.parName, ast.parType, Index(index)))
        self.emit.printout(self.emit.emitVAR(index, ast.parName, ast.parType, frame.getStartLabel() ,frame.getEndLabel(), frame))     
        return o

    def visitVarDecl(self, ast: VarDecl, o: dict) -> dict:
        varInit = ast.varInit
        varType = ast.varType

        if not varInit:
            if type(varType) is IntType:
                varInit = IntLiteral(0)
            elif type(varType) is FloatType:
                varInit = FloatLiteral(0.0)
            elif type(varType) is BoolType:
                varInit = BooleanLiteral(False)
            elif type(varType) is StringType:
                varInit = StringLiteral("")
            ast.varInit = varInit

        env = o.copy()
        env['frame'] = Frame("<template_VT>", VoidType()) 
        rhsCode, rhsType = self.visit(varInit, env)
        if not varType:
            varType = rhsType

        if 'frame' not in o: # global var
            o['env'][0].append(Symbol(ast.varName, varType, CName(self.className)))
            self.emit.printout(self.emit.emitATTRIBUTE(ast.varName, varType, True, False, None))
        else:
            frame = o['frame']
            index = frame.getNewIndex()
            o['env'][0].append(Symbol(ast.varName, varType, Index(index)))
            self.emit.printout(self.emit.emitVAR(index, ast.varName, varType, frame.getStartLabel(), frame.getEndLabel(), frame))
            rhsCode, rhsType = self.visit(varInit, o)
            if type(varType) is FloatType and type(rhsType) is IntType:
                rhsCode += self.emit.emitI2F(frame)       
            self.emit.printout(rhsCode)
            self.emit.printout(self.emit.emitWRITEVAR(ast.varName, varType, index,  frame))                    
        return o
    
    def visitFuncCall(self, ast: FuncCall, o: dict) -> dict:
        sym = next(filter(lambda x: x.name == ast.funName, self.list_function),None)
        env = o.copy()
        if o.get('stmt'):
            env["stmt"] = False
            [self.emit.printout(self.visit(arg, env)[0]) for arg in ast.args]
            self.emit.printout(self.emit.emitINVOKESTATIC(f"{sym.value.value}/{ast.funName}",sym.mtype, o['frame']))
            return o
        output = "".join([str(self.visit(x, env)[0]) for x in ast.args])
        output += self.emit.emitINVOKESTATIC(f"{sym.value.value}/{ast.funName}", sym.mtype, o['frame'])
        return output, sym.mtype.rettype

    def visitBlock(self, ast: Block, o: dict) -> dict:
        env = o.copy()
        env['env'] = [[]] + env['env']
        env['frame'].enterScope(False)
        self.emit.printout(self.emit.emitLABEL(env['frame'].getStartLabel(), env['frame']))

        for item in ast.member:
            if type(item) is FuncCall:
                env["stmt"] = True
            env = self.visit(item, env)

        self.emit.printout(self.emit.emitLABEL(env['frame'].getEndLabel(), env['frame']))
        env['frame'].exitScope()
        return o
    
    def visitId(self, ast: Id, o: dict) -> dict:
        sym = next(filter(lambda x: x.name == ast.name, [j for i in o['env'] for j in i]),None)
        if o.get('isLeft'):
            if type(sym.value) is Index:
                return self.emit.emitWRITEVAR(ast.name, sym.mtype, sym.value.value, o['frame']), sym.mtype
            else:         
                return self.emit.emitPUTSTATIC(f"{self.className}/{ast.name}", sym.mtype, o['frame']), sym.mtype   
        if type(sym.value) is Index:
            return self.emit.emitREADVAR(ast.name, sym.mtype, sym.value.value, o['frame']), sym.mtype
        else:         
            return self.emit.emitGETSTATIC(f"{self.className}/{ast.name}", sym.mtype, o['frame']), sym.mtype

    def visitAssign(self, ast: Assign, o: dict) -> dict:
        if type(ast.lhs) is Id and not \
            next(filter(lambda x: x.name == ast.lhs.name, [j for i in o['env'] for j in i]), None):
                return o
        
        rhsCode, rhsType = self.visit(ast.rhs, o)
        o['isLeft'] = True
        lhsCode, lhsType = self.visit(ast.lhs, o)
        o['isLeft'] = False

        if type(lhsType) is FloatType and type(rhsType) is IntType:
            rhsCode += self.emit.emitI2F(o['frame'])

        self.emit.printout(rhsCode)
        self.emit.printout(lhsCode)
        return o

    def visitReturn(self, ast: Return, o: dict) -> dict:
        if ast.expr:
            self.emit.printout(self.visit(ast.expr, o)[0])
        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        return o

    ## END decl ------------------------------

    ## basic expression ------------------------------
    def visitBinaryOp(self, ast: BinaryOp, o: dict):
        leftCode, leftType = self.visit(ast.left, o)
        rightCode, rightType = self.visit(ast.right, o)
        op = ast.op
        frame = o['frame']

        # Implicit int-to-float promotion if needed
        if isinstance(leftType, FloatType) and isinstance(rightType, IntType):
            rightCode += self.emit.emitI2F(frame)
            rightType = FloatType()

        elif isinstance(leftType, IntType) and isinstance(rightType, FloatType):
            leftCode += self.emit.emitI2F(frame)
            leftType = FloatType()

        if op in ['+', '-', '*', '/']:
            if isinstance(leftType, IntType) and isinstance(rightType, IntType):
                code = leftCode + rightCode + self.emit.emitADDOP(op, IntType(), frame)
                return code, IntType()
            else:
                code = leftCode + rightCode + self.emit.emitADDOP(op, FloatType(), frame)
                return code, FloatType()
            
        elif op in ['%', '&&', '||']:
            code = leftCode + rightCode + self.emit.emitREOP(op, IntType(), frame)
            return code, IntType()
        
        elif op in ['==', '!=', '<', '<=', '>', '>=']:
            if isinstance(leftType, FloatType) or isinstance(rightType, FloatType):
                code = leftCode + rightCode + self.emit.emitREOP(op, FloatType(), frame)
            else:
                code = leftCode + rightCode + self.emit.emitREOP(op, IntType(), frame)
            return code, BoolType()
              
    def visitUnaryOp(self, ast: UnaryOp, o: dict) -> tuple[str, Type]:
        if ast.op == '!':
            code, type_return = self.visit(ast.body, o)
            return code + self.emit.emitNOT(BoolType(), o['frame']), BoolType()

        if ast.op == '-':
            code, type_return = self.visit(ast.body, o)
            if isinstance(type_return, IntType):
                return code + self.emit.emitNEGOP(IntType(), o['frame']), IntType()
            else:
                return code + self.emit.emitNEGOP(FloatType(), o['frame']), FloatType()
    
    def visitIntLiteral(self, ast: IntLiteral, o: dict) -> tuple[str, Type]:
        return self.emit.emitPUSHICONST(ast.value, o['frame']), IntType()
    
    def visitFloatLiteral(self, ast: FloatLiteral, o: dict) -> tuple[str, Type]:
        return self.emit.emitPUSHFCONST(ast.value, o['frame']), FloatType()
    
    def visitBooleanLiteral(self, ast: BooleanLiteral, o: dict) -> tuple[str, Type]:
        return self.emit.emitPUSHICONST(1 if ast.value else 0, o['frame']), BoolType()
    
    def visitStringLiteral(self, ast: StringLiteral, o: dict) -> tuple[str, Type]:
        return self.emit.emitPUSHCONST(ast.value, StringType(), o['frame']), StringType()
    
    # END basic expression ------------------------------