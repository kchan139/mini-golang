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
        self.className = 'MiniGoClass'
        self.list_function = []
        self.list_type = {}
        self.function = None
        self.astTree = None
        self.struct = None
        self.path = None
        self.emit = None

    def initialize(self):
        mem = [
            Symbol('putInt',     MType([IntType()], VoidType()),    CName('io', True)),
            Symbol('putIntLn',   MType([IntType()], VoidType()),    CName('io', True)),
            Symbol('putFloat',   MType([FloatType()], VoidType()),  CName('io', True)),
            Symbol('putFloatLn', MType([FloatType()], VoidType()),  CName('io', True)),
            Symbol('getInt',     MType([], IntType()),              CName('io',True)),
            Symbol('getFloat',   MType([], FloatType()),            CName('io', True)),
            Symbol('getBool',    MType([], BoolType()),             CName('io', True)),
            Symbol('putBool',    MType([BoolType()], VoidType()),   CName('io', True)),
            Symbol('putBoolLn',  MType([BoolType()], VoidType()),   CName('io', True)),
            Symbol('getString',  MType([], StringType()),           CName('io', True)),
            Symbol('putString',  MType([StringType()], VoidType()), CName('io', True)),
            Symbol('putStringLn',MType([StringType()], VoidType()), CName('io', True)),
            Symbol('putLn',      MType([], VoidType()),             CName('io', True))
        ]
        return mem

    def gen(self, ast, dir_):
        gl = self.initialize()
        self.astTree = ast
        self.path = dir_
        self.emit = Emitter(dir_ + '/' + self.className + '.j')
        self.visit(ast, gl)

    def emitObjectInit(self):
        frame = Frame('<init>', VoidType())
        self.emit.printout(self.emit.emitMETHOD('<init>', MType([], VoidType()), False))

        frame.enterScope(True)
        self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), 'this', Id(self.className), frame.getStartLabel(), frame.getEndLabel(), frame))

        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))
        self.emit.printout(self.emit.emitREADVAR('this', Id(self.className), 0, frame))
        self.emit.printout(self.emit.emitINVOKESPECIAL(frame))

        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        self.emit.printout(self.emit.emitRETURN(VoidType(), frame))
        self.emit.printout(self.emit.emitENDMETHOD(frame))

        frame.exitScope()

    def emitObjectCInit(self, ast: Program, env):
        frame = Frame('<cinit>', VoidType())
        
        self.emit.printout(self.emit.emitMETHOD('<clinit>', MType([], VoidType()), True))
        frame.enterScope(True)
        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))
        
        env['frame'] = frame
        
        var_initializations = [
            Assign(Id(item.varName), item.varInit) 
            for item in ast.decl 
            if isinstance(item, VarDecl) and item.varInit
        ]
        
        const_initializations = [
            Assign(Id(item.conName), item.iniExpr) 
            for item in ast.decl 
            if isinstance(item, ConstDecl) and item.iniExpr
        ]
        
        if var_initializations:
            self.visit(Block(var_initializations), env)
        if const_initializations:
            self.visit(Block(const_initializations), env)
        
        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        self.emit.printout(self.emit.emitRETURN(VoidType(), frame))
        self.emit.printout(self.emit.emitENDMETHOD(frame))
        
        frame.exitScope()

    def visitProgram(self, ast: Program, c):
        self.list_function = c + \
            [Symbol(item.name, MType(list(map(lambda x: x.parType, item.params)), item.retType), 
                CName(self.className)) for item in ast.decl if isinstance(item, FuncDecl)]
        self.list_type = {x.name: x for x in ast.decl if isinstance(x, Type)}
        
        for item in ast.decl:
            if isinstance(item, MethodDecl):
                self.list_type[item.recType.name].methods.append(item)
        
        env = {'env': [c]}
        self.emit.printout(self.emit.emitPROLOG(self.className, 'java.lang.Object'))
        
        env = reduce(lambda a, x: self.visit(x, a) if isinstance(x, VarDecl) or isinstance(x, ConstDecl) else a, 
                    ast.decl, env)
        reduce(lambda a, x: self.visit(x, a) if isinstance(x, FuncDecl) else a, ast.decl, env)
        
        self.emitObjectInit()
        self.emitObjectCInit(ast, env)
        self.emit.printout(self.emit.emitEPILOG())
        
        for item in self.list_type.values():
            self.struct = item
            self.emit = Emitter(self.path + '/' + item.name + '.j')
            self.visit(item, {'env': env['env']})
        
        return env

    def visitFuncDecl(self, ast, o):
        self.function = ast
        frame = Frame(ast.name, ast.retType)
        isMain = ast.name == 'main'
        
        mtype = MType([ArrayType([None], StringType())], VoidType()) if isMain else \
                MType(list(map(lambda x: x.parType, ast.params)), ast.retType)
        
        env = o.copy()
        env['frame'] = frame
        self.emit.printout(self.emit.emitMETHOD(ast.name, mtype, True))
        
        frame.enterScope(True)
        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))
        env['env'] = [[]] + env['env']
        
        if isMain:
            self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), 'args', 
                            ArrayType([None], StringType()), 
                            frame.getStartLabel(), frame.getEndLabel(), frame))
        else:
            env = reduce(lambda acc, e: self.visit(e, acc), ast.params, env)
        
        self.visit(ast.body, env)
        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        
        if isinstance(ast.retType, VoidType):
            self.emit.printout(self.emit.emitRETURN(VoidType(), frame))
            
        self.emit.printout(self.emit.emitENDMETHOD(frame))
        frame.exitScope()
        
        return o

    def visitParamDecl(self, ast, o):
        frame = o['frame']
        index = frame.getNewIndex()
        o['env'][0].append(Symbol(ast.parName, ast.parType, Index(index)))
        
        self.emit.printout(self.emit.emitVAR(
            index, 
            ast.parName, 
            ast.parType, 
            frame.getStartLabel(), 
            frame.getEndLabel(), 
            frame
        ))
        return o

    def visitVarDecl(self, ast, o):
        def _create_init(varType, o):
            if isinstance(varType, IntType):
                return IntLiteral(0)
            elif isinstance(varType, FloatType):
                return FloatLiteral(0.0)
            elif isinstance(varType, StringType):
                return StringLiteral('\"\"')
            elif isinstance(varType, BoolType):
                return BooleanLiteral('false')
            elif isinstance(varType, Id):
                struct_typ = self.list_type[varType.name]
                return StructLiteral(struct_typ.name, [(x[0], _create_init(x[1], o)) for x in struct_typ.elements])
        
        varInit = ast.varInit
        varType = ast.varType
        
        if not varInit:
            varInit = _create_init(varType, o)
            if isinstance(varType, ArrayType):
                varInit = ArrayLiteral(varType.dimens, varType.eleType, varType)
            ast.varInit = varInit

        env = o.copy()
        env['frame'] = Frame('<template_KC>', VoidType())
        rhsCode, rhsType = self.visit(varInit, env)
        
        if not varType:
            varType = rhsType
        if isinstance(varType, Id):
            varType = Id(varType.name)
            
        if 'frame' not in o:  # global var
            o['env'][0].append(Symbol(ast.varName, varType, CName(self.className)))
            self.emit.printout(self.emit.emitATTRIBUTE(ast.varName, varType, True, False, None))
        else:
            frame = o['frame']
            index = frame.getNewIndex()
            o['env'][0].append(Symbol(ast.varName, varType, Index(index)))
            self.emit.printout(self.emit.emitVAR(index, ast.varName, varType, 
                            frame.getStartLabel(), frame.getEndLabel(), frame))
            
            rhsCode, rhsType = self.visit(varInit, o)
            if isinstance(varType, FloatType) and isinstance(rhsType, IntType):
                rhsCode += self.emit.emitI2F(frame)

            self.emit.printout(rhsCode)
            self.emit.printout(self.emit.emitWRITEVAR(ast.varName, varType, index, frame))
            
        return o
    
    def visitConstDecl(self, ast, o):
        return self.visit(VarDecl(ast.conName, ast.conType, ast.iniExpr), o)
    
    def visitFuncCall(self, ast, o):
        sym = next(filter(lambda x: x.name == ast.funName, self.list_function), None)
        
        if o.get('stmt'):
            o['stmt'] = False
            self.emit.printout(''.join([str(self.visit(x, o)[0]) for x in ast.args]))
            self.emit.printout(self.emit.emitINVOKESTATIC(f'{sym.value.value}/{ast.funName}', sym.mtype, o['frame']))
            return o
        
        output = ''.join([str(self.visit(x, o.copy())[0]) for x in ast.args])
        output += self.emit.emitINVOKESTATIC(f'{sym.value.value}/{ast.funName}', sym.mtype, o['frame'])
        return output, sym.mtype.rettype

    def visitBlock(self, ast, o):
        env = o.copy()
        env['env'] = [[]] + env['env']
        env['frame'].enterScope(False)
        self.emit.printout(self.emit.emitLABEL(env['frame'].getStartLabel(), env['frame']))

        for item in ast.member:
            if isinstance(item, (FuncCall, MethCall)):
                env['stmt'] = True
            env = self.visit(item, env)

        self.emit.printout(self.emit.emitLABEL(env['frame'].getEndLabel(), env['frame']))
        env['frame'].exitScope()
        return o

    def visitId(self, ast, o):
        sym = next(filter(lambda x: x.name == ast.name, [j for i in o['env'] for j in i]), None)
        
        if sym is None:
            return (self.emit.emitWRITEVAR('this', Id(self.struct.name), 0, o['frame']) if o.get('isLeft') else 
                    self.emit.emitREADVAR('this', Id(self.struct.name), 0, o['frame'])), Id(self.struct.name)
        
        if o.get('isLeft'):
            return ((self.emit.emitWRITEVAR(sym.name, sym.mtype, sym.value.value, o['frame']) 
                    if isinstance(sym.value, Index) else
                    self.emit.emitPUTSTATIC(f'{sym.value.value}/{sym.name}', sym.mtype, o['frame'])), 
                    sym.mtype)
        
        return ((self.emit.emitREADVAR(sym.name, sym.mtype, sym.value.value, o['frame']) 
                if isinstance(sym.value, Index) else
                self.emit.emitGETSTATIC(f'{sym.value.value}/{sym.name}', sym.mtype, o['frame'])), 
                sym.mtype)

    def visitAssign(self, ast, o):
        if isinstance(ast.lhs, Id) and not next(filter(lambda x: x.name == ast.lhs.name, 
                                                    [j for i in o['env'] for j in i]), None):
            return self.visitVarDecl(VarDecl(ast.lhs.name, self.visit(ast.rhs, o)[1], ast.rhs), o)
        
        rhsCode, rhsType = self.visit(ast.rhs, o)
        
        o['isLeft'] = True
        lhsCode, lhsType = self.visit(ast.lhs, o)
        o['isLeft'] = False

        if isinstance(lhsType, FloatType) and isinstance(rhsType, IntType):
            rhsCode += self.emit.emitI2F(o['frame'])

        if isinstance(ast.lhs, ArrayCell):
            self.emit.printout(lhsCode)
            self.emit.printout(rhsCode)
            self.emit.printout(self.emit.emitASTORE(lhsType, o['frame']))
        elif isinstance(ast.lhs, FieldAccess):
            self.emit.printout(lhsCode)
            self.emit.printout(rhsCode)
            struct_name = self.visit(ast.lhs.receiver, o)[1].name
            self.emit.printout(self.emit.emitPUTFIELD(f'{struct_name}/{ast.lhs.field}', lhsType, o['frame']))
        else:
            self.emit.printout(rhsCode)
            self.emit.printout(lhsCode)
            
        return o

    def visitReturn(self, ast, o):
        if ast.expr:
            self.emit.printout(self.visit(ast.expr, o)[0])
        self.emit.printout(self.emit.emitRETURN(self.visit(ast.expr, o)[1] if ast.expr else VoidType(), o['frame']))
        return o

    def visitArrayCell(self, ast, o):
        newO = o.copy()
        newO['isLeft'] = False
        curr_ope_begin = o['frame'].currOpStackSize
        codeGen, arrType = self.visit(ast.arr, newO)
        
        curr_ope_max = 0
        for idx, val in enumerate(ast.idx):
            codeGen += self.visit(val, newO)[0]
            curr_ope_max = max(curr_ope_begin, o['frame'].currOpStackSize)
            if idx != len(ast.idx) - 1:
                codeGen += self.emit.emitALOAD(arrType, o['frame'])
        
        if len(arrType.dimens) == len(ast.idx):
            retType = arrType.eleType
            if not o.get('isLeft'):
                codeGen += self.emit.emitALOAD(retType, o['frame'])
            else:
                o['frame'].maxOpStackSize = max(o['frame'].maxOpStackSize + curr_ope_max - curr_ope_begin, 16384)
                self.arrayCell = ast.idx
        else:
            retType = ArrayType(arrType.dimens[len(ast.idx):], arrType.eleType)
            if not o.get('isLeft'):
                codeGen += self.emit.emitALOAD(retType, o['frame'])
            else:
                o['frame'].maxOpStackSize = max(o['frame'].maxOpStackSize + curr_ope_max - curr_ope_begin, 16384)
                self.arrayCell = ast.idx
                
        return codeGen, retType
    
    def visitArrayLiteral(self, ast, o):
        def _process_array(data, o):
            if not isinstance(data, list):
                return self.visit(data, o)

            frame = o['frame']
            length = len(data)
            code = self.emit.emitPUSHCONST(length, IntType(), frame)
            
            if not isinstance(data[0], list):
                # One-dimensional array case
                result, elem_type = self.visit(data[0], o)
                is_primitive = type(elem_type) in [IntType, FloatType, BoolType]
                code += self.emit.emitNEWARRAY(elem_type, frame) if is_primitive else self.emit.emitANEWARRAY(elem_type, frame)
                
                for idx, item in enumerate(data):
                    code += self.emit.emitDUP(frame)
                    code += self.emit.emitPUSHCONST(idx, IntType(), frame)
                    code += self.visit(item, o)[0]
                    code += self.emit.emitASTORE(elem_type, frame)
                    
                return code, ArrayType([IntLiteral(length)], elem_type)
            
            # Multi-dimensional array case
            _, elem_type = _process_array(data[0], o)
            code += self.emit.emitANEWARRAY(elem_type, frame)
            
            for idx, item in enumerate(data):
                item_code, item_type = _process_array(item, o)
                code += self.emit.emitDUP(frame)
                code += self.emit.emitPUSHCONST(idx, IntType(), frame)
                code += item_code
                code += self.emit.emitASTORE(item_type, frame)
                
            return code, ArrayType([IntLiteral(length)] + elem_type.dimens, elem_type.eleType)
        
        if isinstance(ast.value, ArrayType):
            return self.visit(ast.value, o)
        return _process_array(ast.value, o)

    def visitBinaryOp(self, ast, o):
        op = ast.op
        frame = o['frame']
        codeLeft, typeLeft = self.visit(ast.left, o)
        codeRight, typeRight = self.visit(ast.right, o)
        if op in ['+', '-'] and type(typeLeft) in [FloatType, IntType]:
            typeReturn = IntType() if type(typeLeft) is IntType and type(typeRight) is IntType else FloatType()
            if type(typeReturn) is FloatType:
                if type(typeLeft) is IntType:
                    codeLeft += self.emit.emitI2F(frame)
                if type(typeRight) is IntType:
                    codeRight += self.emit.emitI2F(frame)
            return codeLeft + codeRight + self.emit.emitADDOP(op,typeReturn, frame), typeReturn
        elif op in ['*', '/']:
            typeReturn = IntType() if type(typeLeft) is IntType and type(typeRight) is IntType else FloatType()

            if type(typeReturn) is FloatType:
                if type(typeLeft) is IntType:
                    codeLeft += self.emit.emitI2F(frame)
                if type(typeRight) is IntType:
                    codeRight += self.emit.emitI2F(frame)
            return codeLeft + codeRight + self.emit.emitMULOP(op, typeReturn,frame), typeReturn
        elif op in ['%']:
            return codeLeft + codeRight + self.emit.emitMOD(frame), IntType()
        elif op in ['==', '!=', '<', '>', '>=', '<='] and type(typeLeft) in [FloatType, IntType]:
            return codeLeft + codeRight + self.emit.emitREOP(op, IntType() if type(typeLeft) is IntType and type(typeRight) is IntType else FloatType(),frame), BoolType()
        elif op in ['||']:
            return codeLeft + codeRight + self.emit.emitOROP(frame), BoolType()
        elif op in ['&&']:
            return codeLeft + codeRight + self.emit.emitANDOP(frame), BoolType()

        if op in ['+', '-'] and type(typeLeft) in [StringType]:
            funtyp = MType([StringType()], StringType())
            return codeLeft + codeRight + self.emit.emitINVOKEVIRTUAL('java/lang/String/concat',funtyp,frame), StringType()
        elif op in ['==', '!=', '<', '>', '>=', '<='] and type(typeLeft) in [StringType]:
            funtyp = MType([StringType()], IntType())
            code = codeLeft + codeRight + self.emit.emitINVOKEVIRTUAL('java/lang/String/compareTo',funtyp, frame)
            code = code + self.emit.emitPUSHICONST(0,frame) + self.emit.emitREOP(op, IntType(),frame)
            return code, BoolType()

    def visitUnaryOp(self, ast, o):
        if ast.op == '!':
            code, type_return = self.visit(ast.body, o)
            return code + self.emit.emitNOT(BoolType(), o['frame']), BoolType()

        elif ast.op == '-':
            code, type_return = self.visit(ast.body, o)
            return code + self.emit.emitNEGOP(IntType() if type(type_return) is IntType else FloatType(), o['frame']), type_return

    def visitIntLiteral(self, ast, o):
        return self.emit.emitPUSHICONST(ast.value, o['frame']), IntType()

    def visitFloatLiteral(self, ast, o):
        return self.emit.emitPUSHFCONST(str(ast.value),o['frame']), FloatType()

    def visitBooleanLiteral(self, ast, o):
        return self.emit.emitPUSHCONST(str(ast.value).lower(),BoolType(),o['frame']), BoolType()

    def visitStringLiteral(self, ast, o):
        return self.emit.emitPUSHCONST('\"' + ast.value[1:-1] + '\"',StringType(),o['frame']), StringType()

    def visitArrayType(self, ast, o):
        codeGen = ''
        codeGen = reduce(lambda acc,ele:acc + self.visit(ele, o)[0] ,ast.dimens, codeGen)
        codeGen += self.emit.emitMULTIANEWARRAY(ast, o['frame'])
        return codeGen, ast

    def visitIf(self, ast, o):
        frame = o['frame']
        label_false = frame.getNewLabel()
        label_end = frame.getNewLabel()
        
        # Process condition
        cond_code, _ = self.visit(ast.expr, o)
        self.emit.printout(cond_code)
        self.emit.printout(self.emit.emitIFFALSE(label_false, frame))
        
        # Then branch
        self.visit(ast.thenStmt, o)
        self.emit.printout(self.emit.emitGOTO(label_end, frame))
        
        # Else branch
        self.emit.printout(self.emit.emitLABEL(label_false, frame))
        if ast.elseStmt:
            self.visit(ast.elseStmt, o)
            
        # End of if statement
        self.emit.printout(self.emit.emitLABEL(label_end, frame))
        return o

    def visitForBasic(self, ast, o):
        frame = o['frame']
        frame.enterLoop()
        
        label_break = frame.getBreakLabel()
        label_continue = frame.getContinueLabel()
        
        self.emit.printout(self.emit.emitLABEL(label_continue, frame))
        self.emit.printout(self.visit(ast.cond, o)[0])
        self.emit.printout(self.emit.emitIFFALSE(label_break, frame))
        
        self.visit(ast.loop, o)
        
        self.emit.printout(self.emit.emitGOTO(label_continue, frame))
        self.emit.printout(self.emit.emitLABEL(label_break, frame))
        
        frame.exitLoop()
        return o

    def visitForStep(self, ast, o):
        env = o.copy()
        env['env'] = [[]] + env['env']
        frame = env['frame']
        
        frame.enterLoop()
        label_begin = frame.getNewLabel()
        label_break = frame.getBreakLabel()
        label_continue = frame.getContinueLabel()
        
        self.visit(ast.init, env)
        self.emit.printout(self.emit.emitLABEL(label_begin, frame))
        self.emit.printout(self.visit(ast.cond, env)[0])
        self.emit.printout(self.emit.emitIFFALSE(label_break, frame))
        
        self.visit(ast.loop, env)
        
        self.emit.printout(self.emit.emitLABEL(label_continue, frame))
        self.visit(ast.upda, env)
        self.emit.printout(self.emit.emitGOTO(label_begin, frame))
        
        self.emit.printout(self.emit.emitLABEL(label_break, frame))
        frame.exitLoop()
        
        return o

    def visitForEach(self, ast, o):
        return o

    def visitContinue(self, ast, o):
        self.emit.printout(self.emit.emitGOTO(o['frame'].getContinueLabel(),o['frame']))
        return o

    def visitBreak(self, ast, o):
        self.emit.printout(self.emit.emitGOTO(o['frame'].getBreakLabel(),o['frame']))
        return o

    def visitFieldAccess(self, ast, o):
        ctx = o.copy()
        ctx['isLeft'] = False
        
        code, typ = self.visit(ast.receiver, ctx)
        typ = self.list_type[typ.name]
        field = self.lookup(ast.field, typ.elements, lambda x: x[0])
        field_type = field[1]
        
        if o.get('isLeft'):
            return code, field_type
        
        field_access = self.emit.emitGETFIELD(f'{typ.name}/{field[0]}', field_type, o['frame'])
        return code + field_access, field_type

    def visitMethCall(self, ast, o):
        code, typ = self.visit(ast.receiver, o)
        typ = self.list_type[typ.name] if typ.name != '' else StructType('', [], [])
        is_stmt = o.pop('stmt', False)
        
        # Generate code for arguments
        for item in ast.args:
            code += self.visit(item, o)[0]
        
        # Handle method call based on type
        if isinstance(typ, StructType):
            method = self.lookup(ast.metName, typ.methods, lambda x: x.fun.name)
            mtype = MType([item.parType for item in method.fun.params], method.fun.retType)
            returnTyp = method.fun.retType
            code += self.emit.emitINVOKEVIRTUAL(f'{typ.name}/{method.fun.name}', mtype, o['frame'])
        elif isinstance(typ, InterfaceType):
            method = self.lookup(ast.metName, typ.methods, lambda x: x.name)
            mtype = MType([item for item in method.params], method.retType)
            returnTyp = method.retType
            code += self.emit.emitINVOKEINTERFACE(f'{typ.name}/{method.name}', mtype, o['frame'])
        
        # Handle statement or expression
        if is_stmt:
            self.emit.printout(code)
            return o
        return code, returnTyp

    def visitStructLiteral(self, ast, o):
        frame = o['frame']
        code = self.emit.emitNEW(ast.name, frame)
        code += self.emit.emitDUP(frame)
        
        types = []
        for _, expr in ast.elements:
            expr_code, expr_type = self.visit(expr, o)
            code += expr_code
            types.append(expr_type)
        
        constructor_sig = MType(types, VoidType())
        code += self.emit.emitINVOKESPECIAL(frame, f'{ast.name}/<init>', constructor_sig)
        
        return code, Id(ast.name)

    def visitNilLiteral(self, ast, o):
        return self.emit.emitPUSHNULL(o['frame']), Id('')

    def visitStructType(self, ast, o):
        self.emit.printout(self.emit.emitPROLOG(self.struct.name, 'java.lang.Object'))
        
        # Emit interface implementations
        for item in self.list_type.values():
            if isinstance(item, InterfaceType) and self._isTypeCompatible(item, ast, [(InterfaceType, StructType)]):
                self.emit.printout(self.emit.emitIMPLEMENT(item.name))

        # Emit attributes
        for name, typ in ast.elements:
            self.emit.printout(self.emit.emitATTRIBUTE(name, typ, False, False, False))

        # Generate constructor with parameters
        parameterized_constructor = MethodDecl(
            None, None, 
            FuncDecl(
                '<init>',
                [ParamDecl(name, typ) for name, typ in ast.elements],
                VoidType(),
                Block([Assign(FieldAccess(Id('this'), name), Id(name)) for name, typ in ast.elements])
            )
        )
        self.visit(parameterized_constructor, o)
        
        # Generate default constructor
        default_constructor = MethodDecl(None, None, FuncDecl('<init>', [], VoidType(), Block([])))
        self.visit(default_constructor, o)
        
        # Visit all methods
        for method in ast.methods:
            self.visit(method, o)
            
        self.emit.printout(self.emit.emitEPILOG())

    def visitMethodDecl(self, ast, o):
        self.function = ast.fun
        frame = Frame(ast.fun.name, ast.fun.retType)
        param_types = [param.parType for param in ast.fun.params]
        mtype = MType(param_types, ast.fun.retType)

        env = o.copy()
        env['frame'] = frame
        self.emit.printout(self.emit.emitMETHOD(ast.fun.name, mtype, False))
        
        frame.enterScope(True)
        idx_this = frame.getNewIndex()
        struct_type = Id(self.struct.name)
        self.emit.printout(self.emit.emitVAR(
            idx_this, 'this', struct_type, 
            frame.getStartLabel(), frame.getEndLabel(), frame
        ))

        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))
        
        if ast.receiver is None:
            self.emit.printout(self.emit.emitREADVAR('this', struct_type, idx_this, frame))
            self.emit.printout(self.emit.emitINVOKESPECIAL(frame))

        env['env'] = [[]] + env['env']
        
        # Process parameters
        for param in ast.fun.params:
            env = self.visit(param, env)

        self.visit(ast.fun.body, env)

        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        if type(ast.fun.retType) is VoidType:
            self.emit.printout(self.emit.emitRETURN(VoidType(),frame))
        self.emit.printout(self.emit.emitENDMETHOD(frame))
        frame.exitScope()
        return o

    def visitInterfaceType(self, ast, o):
        self.emit.printout(self.emit.emitPROLOG(ast.name, 'java.lang.Object', True))
        
        for item in ast.methods:
            mtype = MType(item.params, item.retType)
            self.emit.printout(self.emit.emitMETHOD(item.name, mtype, False, abstract=True))
            self.emit.printout(self.emit.emitENDMETHOD(False))
        
        self.emit.printout(self.emit.emitEPILOG())

    def _isTypeCompatible(self, target_type, source_type, allowed_type_pairs):
        # Special case for empty struct literal
        if isinstance(source_type, StructType) and source_type.name == '':
            return isinstance(target_type, (Id, StructType, InterfaceType))

        # Resolve Id references to actual types
        if isinstance(target_type, Id):
            target_type = self.lookup(target_type.name, self.list_type.values(), lambda x: x.name)
        if isinstance(source_type, Id):
            source_type = self.lookup(source_type.name, self.list_type.values(), lambda x: x.name)

        # Check if the type pair is in the allowed list
        if (type(target_type), type(source_type)) in allowed_type_pairs:
            # Special case for interface implementation checking
            if isinstance(target_type, InterfaceType) and isinstance(source_type, StructType):
                methods_matched = 0
                for interface_method in target_type.methods:
                    for struct_method in source_type.methods:
                        if interface_method.name == struct_method.fun.name:
                            # Check parameter types match
                            interface_param_types = [type(x) for x in interface_method.params]
                            struct_param_types = [type(x.parType) for x in struct_method.fun.params]
                            
                            if interface_param_types == struct_param_types:
                                type_interface = interface_method.retType
                                type_struct = struct_method.fun.retType
                                
                                # Check return types match
                                if type(type_interface) == type(type_struct):
                                    if not isinstance(type_interface, Id) or type_interface.name == type_struct.name:
                                        methods_matched += 1
                
                return methods_matched == len(target_type.methods)
            return True
        
        # Check for same type with same name
        if (isinstance(target_type, StructType) and isinstance(source_type, StructType)) or \
        (isinstance(target_type, InterfaceType) and isinstance(source_type, InterfaceType)):
            return target_type.name == source_type.name

        # Check array types recursively
        if isinstance(target_type, ArrayType) and isinstance(source_type, ArrayType):
            return self.isTypeCompatible(target_type.eleType, source_type.eleType, [(FloatType, IntType)]) and \
                target_type.dimens == source_type.dimens

        # Default: check for exact type match
        return type(target_type) == type(source_type)