from Utils import *
# from StaticCheck import *
# from StaticError import *
from Emitter import *
from Frame import Frame
from abc import ABC, abstractmethod
from functools import reduce
from Visitor import *
from AST import *

class CodeGenerator(BaseVisitor,Utils):
    def __init__(self):
        self.className = "MiniGoClass"
        self.astTree = None
        self.path = None
        self.emit = None
        self.function = None
        self.list_function = []

    def init(self):
        mem = [
            Symbol("putInt", MType([IntType()], VoidType()), CName("io", True)),
            Symbol("putIntLn", MType([IntType()], VoidType()), CName("io", True)),
            Symbol("putFloat", MType([FloatType()], VoidType()), CName("io", True)),
            Symbol("putFloatLn", MType([FloatType()], VoidType()), CName("io", True)),
           ## TODO implement
        ]
        return mem

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
        # self.visit(Block([## TODO implement for item in ast.decl if isinstance(item, VarDecl) and item.varInit]),env)
        
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

    ## TODO decl ------------------------------
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
            ## TODO implement
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
            self.emit.printout(## TODO implement))  
            rhsCode, rhsType = self.visit(varInit, o)
            if type(varType) is FloatType and type(rhsType) is IntType:
                ## TODO implement            
            self.emit.printout(rhsCode)
            self.emit.printout(self.emit.emitWRITEVAR(ast.varName, varType, index,  frame))                    
        return o
    
    def visitFuncCall(self, ast: FuncCall, o: dict) -> dict:
        sym = next(filter(lambda x: x.name == ast.funName, self.list_function),None)
        env = o.copy()
        if o.get('stmt'):
            env["stmt"] = False
            [## TODO implement]
            self.emit.printout(self.emit.emitINVOKESTATIC(f"{sym.value.value}/{ast.funName}",sym.mtype, o['frame']))
            return ## TODO implement
        output = "".join([str(self.visit(x, env)[0]) for x in ast.args])
        output += ## TODO implement
        return ## TODO implement

    def visitBlock(self, ast: Block, o: dict) -> dict:
        env = o.copy()
        env['env'] = [[]] + env['env']
        env['frame'].enterScope(False)
        self.emit.printout(self.emit.emitLABEL(## TODO implement))

        for item in ast.member:
            if type(item) is FuncCall:
                env["stmt"] = True
            env = self.visit(item, env)

        self.emit.printout(self.emit.emitLABEL(## TODO implement))
        env['frame'].exitScope()
        return o
    
    def visitId(self, ast: Id, o: dict) -> dict:
        sym = next(filter(lambda x: x.name == ast.name, [j for i in o['env'] for j in i]),None)
        if o.get('isLeft'):
            if type(sym.value) is Index:
                return self.emit.emitWRITEVAR(## TODO implement), sym.mtype
            else:         
                return self.emit.emitPUTSTATIC(## TODO implement),sym.mtype        
        if type(sym.value) is Index:
            return self.emit.emitREADVAR(## TODO implement),sym.mtype
        else:         
            return self.emit.emitGETSTATIC(## TODO implement),sym.mtype

    def visitAssign(self, ast: Assign, o: dict) -> dict:
        if type(ast.lhs) is Id and not next(filter(lambda x: ## TODO implement),None):
            return ## TODO implement
        rhsCode, rhsType = self.visit(ast.rhs, o)
        o['isLeft'] = True
        lhsCode, lhsType = self.visit(ast.lhs, o)
        o['isLeft'] = False

        if type(lhsType) is FloatType and type(rhsType) is IntType:
            ## TODO implement
        self.emit.printout(rhsCode)
        self.emit.printout(lhsCode)
        return o

    def visitReturn(self, ast: Return, o: dict) -> dict:
        if ast.expr:
            self.emit.printout(self.visit(ast.expr, o)[0])
        self.emit.printout(self.emit.emitRETURN(## TODO implement, o['frame']))
        return o

    ## TODO END decl ------------------------------

    ## TODO basic expression ------------------------------
    def visitBinaryOp(self, ast: BinaryOp, o: dict) -> tuple[str, Type]:
        op = ast.op
        frame = o['frame']
        codeLeft, typeLeft = self.visit(ast.left, o)
        codeRight, typeRight = self.visit(ast.right, o)
        if op in ['+', '-'] and type(typeLeft) in [FloatType, IntType]:
            typeReturn = IntType() if type(typeLeft) is IntType and type(typeRight) is IntType else FloatType()
            if type(typeReturn) is FloatType:
                if type(typeLeft) is IntType:
                    codeLeft += self.emit.emitI2F(frame)
                ## TODO implement
            return codeLeft + codeRight + ## TODO implement
        if op in ['*', '/']:
            typeReturn = ## TODO implement
            if type(typeReturn) is FloatType:
                if type(typeLeft) is IntType:
                    codeLeft += self.emit.emitI2F(frame)
                ## TODO implement
            return codeLeft + codeRight + ## TODO implement 
        if op in ['%']:
            return codeLeft + codeRight + ## TODO implement
        if op in ['==', '!=', '<', '>', '>=', '<='] and type(typeLeft) in [FloatType, IntType]:
            return codeLeft + codeRight + ## TODO implement
        if op in ['||']:
            return codeLeft + codeRight + ## TODO implement
        if op in ['&&']:
            return codeLeft + codeRight + self.emit.emitANDOP(frame), BoolType()  

        # string        
        if op in ['+', '-'] and type(typeLeft) in [StringType]:
            return codeLeft + codeRight + ## TODO implement, StringType()    
        if op in ['==', '!=', '<', '>', '>=', '<='] and type(typeLeft) in [StringType]:
            code = codeLeft + codeRight + ## TODO implement, frame)
            code = code + ## TODO implement + self.emit.emitREOP(op, IntType(), frame)
            return code, BoolType()    
              
    def visitUnaryOp(self, ast: UnaryOp, o: dict) -> tuple[str, Type]:
        if ast.op == '!':
            code, type_return = self.visit(ast.body, o)
            return code + self.emit.emitNOT(BoolType(), o['frame']), BoolType()

        ## TODO implement
    
    def visitIntLiteral(self, ast: IntLiteral, o: dict) -> tuple[str, Type]:
        return self.emit.emitPUSHICONST(ast.value, o['frame']), IntType()
    
    def visitFloatLiteral(self, ast: FloatLiteral, o: dict) -> tuple[str, Type]:
        ## TODO implement
    
    def visitBooleanLiteral(self, ast: BooleanLiteral, o: dict) -> tuple[str, Type]:
        ## TODO implement
    
    def visitStringLiteral(self, ast: StringLiteral, o: dict) -> tuple[str, Type]:
        ## TODO implement
    
    # TODO END basic expression ------------------------------