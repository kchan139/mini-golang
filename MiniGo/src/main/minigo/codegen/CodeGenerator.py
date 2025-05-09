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
        self.arrayCell = None
        self.arrayCellType = None
        self.list_type = {}

    def init(self):
        mem = [
            Symbol("putInt", MType([IntType()], VoidType()), CName("io", True)),
            Symbol("putIntLn", MType([IntType()], VoidType()), CName("io", True)),
            Symbol("putFloat", MType([FloatType()], VoidType()), CName("io", True)),
            Symbol("putFloatLn", MType([FloatType()], VoidType()), CName("io", True)),
            Symbol("putString", MType([StringType()], VoidType()), CName("io", True)),
            Symbol("putStringLn", MType([StringType()], VoidType()), CName("io", True)),
            Symbol("putBool", MType([BoolType()], VoidType()), CName("io", True)),
            Symbol("putBoolLn", MType([BoolType()], VoidType()), CName("io", True)),
            Symbol("getInt", MType([], IntType()), CName("io", True)),
            Symbol("getFloat", MType([], FloatType()), CName("io", True)),
            Symbol("getBool", MType([], BoolType()), CName("io", True)),
            Symbol("getString", MType([], StringType()), CName("io", True)),
        ]
        return mem

    def gen(self, ast, dir_):
        gl = self.init()
        self.astTree = ast
        self.path = dir_
        self.emit = Emitter(dir_ + "/" + self.className + ".j")
        self.visit(ast, gl)

    ### Vì chương trình của mình sẽ xem như nằm trong 1 class duy nhất trong java, cụ thể là MiniGoClass
    ### Nên mình sẽ định nghĩa 2 phương thức <init> và <clinit> trong class này bằng 2 phương thức emitObjectInit và emitObjectCInit
    ### Phương thức <init> sẽ được gọi khi khởi tạo 1 object của class này, và <clinit> sẽ được gọi khi class này được load vào bộ nhớ

    ### Dưới đây là mã jasmin cho 2 phương thức này(LMiniGoClass - kí hiệu L dùng để tham chiếu đến class trong java):

                    # .method public <init>()V
                    # .var 0 is this LMiniGoClass; from Label0 to Label1 
                    # Label0:
                    # 	aload_0
                    # 	invokespecial java/lang/Object/<init>()V
                    # Label1:
                    # 	return
                    # .limit stack 1
                    # .limit locals 1
                    # .end method

                    # .method public static <clinit>()V
                    # Label0:
                    # Label2:
                    # 	invokestatic MiniGoClass/fint()I
                    # 	putstatic MiniGoClass/global I
                    # Label3:
                    # Label1:
                    # 	return
                    # .limit stack 2
                    # .limit locals 0
                    # .end method


    def emitObjectInit(self):
        frame = Frame("<init>", VoidType())  
        self.emit.printout(self.emit.emitMETHOD("<init>", MType([], VoidType()), False, frame))
        
        frame.enterScope(True)

        self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), "this", f"L{self.className};", frame.getStartLabel(), frame.getEndLabel(), frame))

        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))
        
        self.emit.printout(self.emit.emitREADVAR("this", ClassType(self.className), 0, frame)) 
        
        self.emit.printout(self.emit.emitINVOKESPECIAL(frame))
        
        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        
        self.emit.printout(self.emit.emitRETURN(VoidType(), frame))  

        self.emit.printout(self.emit.emitENDMETHOD(frame))  

        frame.exitScope()  

    def emitObjectCInit(self, ast: Program, env):
        frame = Frame("<clinit>", VoidType())  
        self.emit.printout(self.emit.emitMETHOD("<clinit>", MType([], VoidType()), True, frame)) 
        frame.enterScope(True)  
        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))

        env['frame'] = frame

        assignStmts = []
        for item in ast.decl:
            if isinstance(item, (VarDecl, ConstDecl)) and (item.varInit or item.iniExpr):
                assignStmts.append(Assign(Id(item.varName if isinstance(item, VarDecl) else item.conName), 
                                        item.varInit or item.iniExpr))
        self.visit(Block(assignStmts), env)

        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        self.emit.printout(self.emit.emitRETURN(VoidType(), frame))  
        self.emit.printout(self.emit.emitENDMETHOD(frame))  
        frame.exitScope()

    def visitProgram(self, ast: Program, c):
        self.list_function = c + [Symbol(item.name, MType(list(map(lambda x: x.parType, item.params)), item.retType), CName(self.className)) for item in ast.decl if isinstance(item, FuncDecl)]
        self.list_type = {x.name: x for x in ast.decl if isinstance(x, (Type, StructType, InterfaceType))}  # Added

        for item in ast.decl:
            if isinstance(item, MethodDecl):
                if item.recType.name in self.list_type:
                    self.list_type[item.recType.name].methods.append(item)
        
        env = {}
        env['env'] = [c]
        self.emit.printout(self.emit.emitPROLOG(self.className, "java.lang.Object"))
        # Process declarations
        env = reduce(lambda a, x: self.visit(x, a) if isinstance(x, (VarDecl, ConstDecl)) else a, ast.decl, env)
        reduce(lambda a, x: self.visit(x, a) if isinstance(x, FuncDecl) else a, ast.decl, env)
        
        self.emitObjectInit()
        self.emitObjectCInit(ast, env)
        self.emit.printout(self.emit.emitEPILOG())
        
        # Emit separate .j files for each struct
        for item in self.list_type.values():
            if isinstance(item, StructType):
                self.emit = Emitter(self.path + "/" + item.name + ".j")
                self.visit(item, {'env': env['env']})
        
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
    
    def visitConstDecl(self, ast:ConstDecl, o: dict) -> dict:
        return self.visit(VarDecl(ast.conName, ast.conType, ast.iniExpr), o)

    def visitVarDecl(self, ast: VarDecl, o: dict) -> dict:
        def create_init(varType: Type) -> Literal:
            if isinstance(varType, IntType):
                return IntLiteral(0)
            elif isinstance(varType, FloatType):
                return FloatLiteral(0.0)
            elif isinstance(varType, StringType):
                return StringLiteral("")
            elif isinstance(varType, BoolType):
                return BooleanLiteral(False)
            elif isinstance(varType, Id):  # Struct type
                struct_typ = self.list_type.get(varType.name, None)
                if struct_typ:
                    return StructLiteral(struct_typ.name, [(elem[0], create_init(elem[1])) for elem in struct_typ.elements])
            # Handle array initialization if needed
            return None  # Default case
            # Array default initialization handled below, not via recursive create_init for literals

        varInit = ast.varInit
        varType = ast.varType

        # If no initializer is provided and a type is specified (and it's not an ArrayType), create a default value for primitive types.
        # Array default initialization (allocation) is handled later based on varType if no varInit is present.
        if not varInit and varType and not isinstance(varType, ArrayType):
            varInit = create_init(varType)
            ast.varInit = varInit # Update the AST node for later processing if needed

        # Determine the variable's type if not explicitly provided but an initializer exists.
        inferredType = None
        if not varType and varInit:
            # Need to visit varInit to get its type for inference
            if 'frame' not in o:
                # Global variable: Visit varInit in a context without a local frame
                temp_env = {'env': o['env']}
                _, inferredType = self.visit(varInit, temp_env)
            else:
                # Local variable: Visit varInit in the current frame context
                _, inferredType = self.visit(varInit, o)

        # Use the inferred type if varType was not provided
        if not varType:
            varType = inferredType


        # Now handle code generation based on whether it's a global or local variable
        if 'frame' not in o:
            # Global variable declaration
            # Add the symbol to the global scope
            o['env'][0].append(Symbol(ast.varName, varType, CName(self.className)))
            # Emit code for the global attribute (field)
            self.emit.printout(self.emit.emitATTRIBUTE(ast.varName, varType, True, False, None))
            # Global variable initialization code (if any) is handled in emitObjectCInit.
        else:
            # Local variable declaration
            frame = o['frame']

            # Get a new index for the local variable
            index = frame.getNewIndex()
            # Add the symbol to the current local scope
            o['env'][0].append(Symbol(ast.varName, varType, Index(index)))
            # Emit code to declare the local variable
            self.emit.printout(self.emit.emitVAR(index, ast.varName, varType, frame.getStartLabel(), frame.getEndLabel(), frame))

            # Handle initialization if an initializer is provided or if it's an array type without an initializer
            if varInit:
                # Visit the initializer expression to get its code and type
                rhsCode, rhsType = self.visit(varInit, o)
                # Handle type conversion if necessary (e.g., Int to Float)
                if type(varType) is FloatType and type(rhsType) is IntType:
                    rhsCode += self.emit.emitI2F(frame)
                # Emit the code for the initializer expression
                self.emit.printout(rhsCode)
                # Emit code to write the value to the local variable
                self.emit.printout(self.emit.emitWRITEVAR(ast.varName, varType, index, frame))

            elif type(varType) is ArrayType:
                # Handle array declaration without explicit initialization (allocate the array)
                # Need to visit dimension expressions and emit array creation code
                dim_codes = []
                # Ensure dimens are treated as expressions to be visited
                # Assuming varType.dimens contains AST nodes for dimensions
                for dim_expr in varType.dimens:
                    # Visit dimension expressions in the current local frame context
                    dim_code, _ = self.visit(dim_expr, o)
                    dim_codes.append(dim_code)

                # Emit the dimension calculations onto the stack
                self.emit.printout("".join(dim_codes))

                # Emit code to create the array (single or multi-dimensional)
                if len(varType.dimens) == 1:
                    # Emit NEWARRAY for 1D array of primitive or object type
                    self.emit.printout(self.emit.emitNEWARRAY(varType.eleType, frame))
                else:
                    # Emit MULTIANEWARRAY for multi-dimensional arrays
                    self.emit.printout(self.emit.emitMULTIANEWARRAY(varType, frame))

                # Emit code to store the new array reference in the local variable
                self.emit.printout(self.emit.emitWRITEVAR(ast.varName, varType, index, frame))

        # Return the modified environment
        return o
    
    def visitFuncCall(self, ast, o):
        sym = next(filter(lambda x: x.name == ast.funName, self.list_function), None)
        
        if 'frame' not in o:
            temp_frame = Frame("<clinit>", VoidType())
            env = o.copy()
            env['frame'] = temp_frame
            output = "".join([str(self.visit(x, env)[0]) for x in ast.args])
            output += self.emit.emitINVOKESTATIC(f'{sym.value.value}/{ast.funName}', sym.mtype, temp_frame)
            return output, sym.mtype.rettype
        
        if o.get('stmt'):
            o['stmt'] = False
            self.emit.printout("".join([str(self.visit(x,o)[0]) for x in ast.args]))
            self.emit.printout(self.emit.emitINVOKESTATIC(f"{sym.value.value}/{ast.funName}", sym.mtype, o['frame']))
            return o
        
        output = "".join([str(self.visit(x, o)[0]) for x in ast.args])
        output += self.emit.emitINVOKESTATIC(f'{sym.value.value}/{ast.funName}', sym.mtype, o['frame'])
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
        sym = next(filter(lambda x: x.name == ast.name, [j for i in o['env'] for j in i]), None)

        if o.get('isLeft'):
            if type(sym.value) is Index:
                return self.emit.emitWRITEVAR(ast.name, sym.mtype, sym.value.value, o['frame']), sym.mtype
            else:         
                return self.emit.emitPUTSTATIC(f"{sym.value.value}/{ast.name}", sym.mtype, o['frame']), sym.mtype

        if type(sym.value) is Index:
            return self.emit.emitREADVAR(ast.name, sym.mtype, sym.value.value, o['frame']), sym.mtype
        else:         
            return self.emit.emitGETSTATIC(f"{sym.value.value}/{ast.name}", sym.mtype, o['frame']), sym.mtype

    def visitAssign(self, ast, o):
        if type(ast.lhs) is Id and not next(filter(lambda x: x.name == ast.lhs.name,[j for i in o['env'] for j in i]),None):
            return self.visitVarDecl(VarDecl(ast.lhs.name, self.visit(ast.rhs,o)[1],ast.rhs),o)
        
        rhsCode, rhsType = self.visit(ast.rhs, o)
        o['isLeft'] = True
        lhsCode, lhsType = self.visit(ast.lhs, o)
        o['isLeft'] = False

        if type(lhsType) is FloatType and type(rhsType) is IntType:
            rhsCode += self.emit.emitI2F(o['frame'])

        if type(ast.lhs) is ArrayCell:
            self.emit.printout(lhsCode)
            self.emit.printout(rhsCode)
            # Fix: Use the element type instead of the array indices
            if self.arrayCell is not None:
                # Need to emit ASTORE with the element type, not with the indices
                if isinstance(lhsType, ArrayType):
                    self.emit.printout(self.emit.emitASTORE(lhsType.eleType, o['frame']))
                else:
                    self.emit.printout(self.emit.emitASTORE(lhsType, o['frame']))
            else:
                store_type = lhsType.eleType if isinstance(lhsType, ArrayType) else lhsType
                self.emit.printout(self.emit.emitASTORE(store_type, o['frame']))
        elif type(ast.lhs) is FieldAccess:
            self.emit.printout(lhsCode)
            self.emit.printout(rhsCode)
            struct_name = self.visit(ast.lhs.receiver,o)[1].name
            self.emit.printout(self.emit.emitPUTFIELD(struct_name + '/' + ast.lhs.field,lhsType,o['frame']))
        else:
            self.emit.printout(rhsCode)
            self.emit.printout(lhsCode)
        
        # Reset arrayCell after use
        self.arrayCell = None
        return o

    def visitReturn(self, ast: Return, o: dict) -> dict:
        if ast.expr:
            exprCode, exprType = self.visit(ast.expr, o)
            self.emit.printout(exprCode)
            if type(exprType) is IntType and type(self.function.retType) is FloatType:
                self.emit.printout(self.emit.emitI2F(o['frame']))
            self.emit.printout(self.emit.emitRETURN(self.function.retType, o['frame']))
        else:
            self.emit.printout(self.emit.emitRETURN(VoidType(), o['frame']))
        return o

    ##  END decl ------------------------------




   ##  basic expression ------------------------------
    def visitBinaryOp(self, ast, o):
        op = ast.op
        frame = o['frame']
        codeL, typeL = self.visit(ast.left, o)
        codeR, typeR = self.visit(ast.right, o)

        # arithmetic +, - on ints/floats
        if op in ['+', '-'] and isinstance(typeL, (IntType, FloatType)):
            resultType = IntType() if isinstance(typeL, IntType) and isinstance(typeR, IntType) else FloatType()
            if isinstance(resultType, FloatType):
                if isinstance(typeL, IntType):
                    codeL += self.emit.emitI2F(frame)
                if isinstance(typeR, IntType):
                    codeR += self.emit.emitI2F(frame)
            return codeL + codeR + self.emit.emitADDOP(op, resultType, frame), resultType

        # multiplication/division
        if op in ['*', '/']:
            resultType = IntType() if isinstance(typeL, IntType) and isinstance(typeR, IntType) else FloatType()
            if isinstance(resultType, FloatType):
                if isinstance(typeL, IntType):
                    codeL += self.emit.emitI2F(frame)
                if isinstance(typeR, IntType):
                    codeR += self.emit.emitI2F(frame)
            return codeL + codeR + self.emit.emitMULOP(op, resultType, frame), resultType

        # modulo
        if op == '%':
            return codeL + codeR + self.emit.emitMOD(frame), IntType()

        # relational on ints/floats
        if op in ['==', '!=', '<', '>', '<=', '>='] and isinstance(typeL, (IntType, FloatType)):
            cmpType = IntType() if isinstance(typeL, IntType) and isinstance(typeR, IntType) else FloatType()
            return codeL + codeR + self.emit.emitREOP(op, cmpType, frame), BoolType()

        # logical
        if op == '||':
            return codeL + codeR + self.emit.emitOROP(frame), BoolType()
        if op == '&&':
            return codeL + codeR + self.emit.emitANDOP(frame), BoolType()

        # string concatenation
        if op == '+' and isinstance(typeL, StringType):
            mtype = MType([StringType()], StringType())
            return codeL + codeR + self.emit.emitINVOKEVIRTUAL('java/lang/String/concat', mtype, frame), StringType()

        # string comparisons
        if op in ['==', '!=', '<', '>', '<=', '>='] and isinstance(typeL, StringType):
            # call compareTo
            mtype = MType([StringType()], IntType())
            code = codeL + codeR + self.emit.emitINVOKEVIRTUAL('java/lang/String/compareTo', mtype, frame)
            # compare result to zero
            code += self.emit.emitPUSHICONST(0, frame)
            code += self.emit.emitREOP(op, IntType(), frame)
            return code, BoolType()

        # fallback (should not reach)
        return "", BoolType()
              
    def visitUnaryOp(self, ast: UnaryOp, o: dict) -> tuple[str, Type]:
        if ast.op == '!':
            code, type_return = self.visit(ast.body, o)
            return code + self.emit.emitNOT(BoolType(), o['frame']), BoolType()
        elif ast.op == '-':
            code, type_return = self.visit(ast.body, o)
            return code + self.emit.emitNEGOP(type_return, o['frame']), type_return


    def visitIntLiteral(self, ast: IntLiteral, o: dict) -> tuple[str, Type]:
        return self.emit.emitPUSHICONST(ast.value, o['frame']), IntType()
    
    def visitFloatLiteral(self, ast: FloatLiteral, o: dict) -> tuple[str, Type]:
        return self.emit.emitPUSHFCONST(ast.value, o['frame']), FloatType()
    
    def visitBooleanLiteral(self, ast: BooleanLiteral, o: dict) -> tuple[str, Type]:
        return self.emit.emitPUSHICONST(ast.value, o['frame']), BoolType()
    
    def visitStringLiteral(self, ast: StringLiteral, o: dict) -> tuple[str, Type]:
        return self.emit.emitPUSHCONST(ast.value, StringType(), o['frame']), StringType()
    
    ## END basic expression ------------------------------

    ## array ------------------------------
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
        retType = None
        if len(arrType.dimens) == len(ast.idx):
            retType = arrType.eleType
            if not o.get('isLeft'):
                codeGen += self.emit.emitALOAD(retType,o['frame'])
            else:
                o['frame'].maxOpStackSize = max(o['frame'].maxOpStackSize + curr_ope_max - curr_ope_begin,10000)
                self.arrayCell = ast.idx
        else:
            retType = ArrayType(arrType.dimens[len(ast.idx):],arrType.eleType)
            if not o.get('isLeft'):
                codeGen += self.emit.emitALOAD(retType, o['frame'])
            else:
                o['frame'].maxOpStackSize = max(o['frame'].maxOpStackSize + curr_ope_max - curr_ope_begin,10000)
                self.arrayCell = ast.idx
        return codeGen, retType

    def visitArrayLiteral(self, ast:ArrayLiteral , o: dict) -> tuple[str, Type]:

        def nested2recursive(dat: Union[Literal, list['NestedList']], o: dict) -> tuple[str, Type]:
            if not isinstance(dat,list): 
                return self.visit(dat, 0)
            frame = o['frame']
            codeGen = self.emit.emitPUSHCONST(len(dat), IntType(), frame)
            
            if not isinstance(dat[0],list):
                _, type_element_array = self.visit(dat[0], o)

                if type(type_element_array) in [IntType, BoolType, FloatType]:
                    codeGen += self.emit.emitNEWARRAY(type_element_array, frame)
                else:
                    codeGen += self.emit.emitANEWARRAY(type_element_array, frame)

                for idx, item in enumerate(dat):
                    codeGen += self.emit.emitDUP(frame)
                    codeGen += self.emit.emitPUSHCONST(idx, IntType(), frame)
                    itemCode, itemType = self.visit(item, o)
                    codeGen += itemCode
                    codeGen += self.emit.emitASTORE(type_element_array, frame)
                if isinstance(type_element_array, ArrayType):
                    new_dimens = [IntLiteral(len(dat))]
                    new_dimens.extend(type_element_array.dimens)
                    return codeGen, ArrayType(new_dimens, type_element_array.eleType)
                else:
                    return codeGen, ArrayType([IntLiteral(len(dat))], type_element_array)

            _, type_element_array = nested2recursive(dat[0], o)
            if type(type_element_array) in [IntType, BoolType, FloatType]:
                codeGen += self.emit.emitNEWARRAY(type_element_array, frame)
            else:
                codeGen += self.emit.emitANEWARRAY(type_element_array, frame)

            for idx, item in enumerate(dat):
                codeGen += self.emit.emitDUP(frame)
                codeGen += self.emit.emitPUSHCONST(idx, IntType(), frame)
                subArrayCode, _ = nested2recursive(item, o)
                codeGen += subArrayCode
                codeGen += self.emit.emitASTORE(type_element_array, frame)
            
            if isinstance(type_element_array, ArrayType):
                new_dimens = [IntLiteral(len(dat))]
                new_dimens.extend(type_element_array.dimens)
                return codeGen, ArrayType(new_dimens, type_element_array.eleType)
            else:
                return codeGen, ArrayType([IntLiteral(len(dat))], type_element_array)
        
        if type(ast.value) is ArrayType:
            return self.visit(ast.value, o)

        return nested2recursive(ast.value, o)
    
    def visitArrayType(self, ast:ArrayType, o):
        codeGen = ""
        for dimen in ast.dimens:
            dimen_code, _ = self.visit(dimen, o)
            codeGen += dimen_code
        codeGen += self.emit.emitMULTIANEWARRAY(ast, o['frame'])
        return codeGen, ast

    def visitStructType(self, ast, o):
        self.emit.printout(self.emit.emitPROLOG(self.struct.name, "java.lang.Object"))
        for item in self.list_type.values():
            if isinstance(item, InterfaceType) and self.checkType(item, ast, [(InterfaceType, StructType)]):
                self.emit.printout(self.emit.emitIMPLEMENT(item.name))

        for item in ast.elements:
            self.emit.printout(self.emit.emitATTRIBUTE(item[0], item[1], False, False, False))

        self.visit(MethodDecl(None, None, FuncDecl("<init>", [ParamDecl(item[0],item[1]) for item in ast.elements], VoidType(),
                            Block([Assign(FieldAccess(Id("this"),item[0]),Id(item[0])) for item in ast.elements]))), o)
        self.visit(MethodDecl(None, None, FuncDecl("<init>", [], VoidType(), Block([]))), o)
        for item in ast.methods: self.visit(item, o)
        self.emit.printout(self.emit.emitEPILOG())

    def visitFieldAccess(self, ast, o):
        newO = o.copy()
        newO['isLeft'] = False
        code, typ = self.visit(ast.receiver, newO)
        typ = self.list_type[typ.name]
        field = self.lookup(ast.field, typ.elements, lambda x: x[0])
        if o.get('isLeft'):
            return code, field[1]
        return code + self.emit.emitGETFIELD(typ.name + '/' + field[0], field[1], o['frame']), field[1]

    def visitStructLiteral(self, ast, c):
        frame = c[-1] if isinstance(c[-1], Frame) else c[-2]
        emitter = c[-2] if isinstance(c[-1], Frame) else c[-3]
        
        structName = ast.name
        code = emitter.emitNEW(structName)
        code = code + emitter.emitDUP()
        code = code + emitter.emitINVOKESPECIAL(structName + "/<init>", "()V")
        
        for idx, expr in enumerate(ast.fields):
            code = code + emitter.emitDUP()
            exprCode, exprType = self.visit(expr, c)
            code = code + exprCode
            
            fieldName = ast.fieldNames[idx].name
            
            code = code + emitter.emitPUTFIELD(structName, fieldName, self.getJVMType(exprType))
        
        return code, ast.structType

    def visitMethodDecl(self, ast, c):
        emitter = c[-1]
        frame = Frame(ast.name.name, self.getJVMType(ast.returnType))
        newContext = c + [frame]
        
        inType = [self.getJVMType(param.varType) for param in ast.param]
        paramsCode = "(" + "".join(inType) + ")"
        returnType = self.getJVMType(ast.returnType)
        methodCode = f"{ast.name.name}{paramsCode}{returnType}"
        
        emitter.printout(emitter.emitMETHOD(ast.name.name, methodCode, False, frame))
        emitter.printout(emitter.emitVAR(0, "this", emitter.className, frame.getStartLabel(), frame.getEndLabel(), frame))
        
        startParamIdx = 1
        for idx, param in enumerate(ast.param):
            paramType = self.getJVMType(param.varType)
            paramName = param.variable.name
            index = startParamIdx
            startParamIdx += 1 if paramType in ["I", "Z", "F"] else 2
            emitter.printout(emitter.emitVAR(index, paramName, paramType, frame.getStartLabel(), frame.getEndLabel(), frame))
        
        emitter.printout(emitter.emitLABEL(frame.getStartLabel(), frame))
        [self.visit(stmt, newContext) for stmt in ast.body]
        emitter.printout(emitter.emitLABEL(frame.getEndLabel(), frame))
        
        if type(ast.returnType) is VoidType:
            emitter.printout(emitter.emitRETURN(frame))
        
        emitter.printout(emitter.emitENDMETHOD(frame))

    def visitMethCall(self, ast, c):
        frame = c[-1] if isinstance(c[-1], Frame) else c[-2]
        emitter = c[-2] if isinstance(c[-1], Frame) else c[-3]
        
        objCode, objType = self.visit(ast.obj, c)
        
        argCode = ""
        inType = []
        for arg in ast.args:
            argExpr, argType = self.visit(arg, c)
            argCode = argCode + argExpr
            inType.append(self.getJVMType(argType))
        
        methodName = ast.method.name
        paramsCode = "(" + "".join(inType) + ")"
        returnType = None
        code = objCode + argCode + \
            emitter.emitINVOKEVIRTUAL(objType.name + "/" + methodName, paramsCode + self.getJVMType(returnType))
        
        return code, returnType
    
    def visitIf(self, ast, o):
        frame = o['frame']
        label_false = frame.getNewLabel()
        label_end_if = frame.getNewLabel()
        condCode, _ = self.visit(ast.expr, o)
        
        self.emit.printout(condCode)
        self.emit.printout(self.emit.emitIFFALSE(label_false,frame))
        self.visit(ast.thenStmt, o)
        self.emit.printout(self.emit.emitGOTO(label_end_if,frame))
        self.emit.printout(self.emit.emitLABEL(label_false,frame))

        if ast.elseStmt:
            self.visit(ast.elseStmt,o)
        self.emit.printout(self.emit.emitLABEL(label_end_if,frame))

        return o
    
    def visitPrototype(self, ast: Prototype, o: dict):
        raise NotImplementedError

    def visitIntType(self, ast: IntType, o: dict):
        raise NotImplementedError

    def visitFloatType(self, ast: FloatType, o: dict):
        raise NotImplementedError

    def visitBoolType(self, ast: BoolType, o: dict):
        raise NotImplementedError

    def visitStringType(self, ast: StringType, o: dict):
        raise NotImplementedError

    def visitVoidType(self, ast: VoidType, o: dict):
        raise NotImplementedError

    def visitInterfaceType(self, ast: InterfaceType, o: dict):
        raise NotImplementedError

    def visitForBasic(self, ast: ForBasic, o: dict):
        frame = o['frame']
        frame.enterLoop()
        
        continue_label = frame.getContinueLabel()
        break_label = frame.getBreakLabel()
        
        self.emit.printout(self.emit.emitLABEL(continue_label, frame))
        
        cond_code, _ = self.visit(ast.cond, o)
        self.emit.printout(cond_code)
        self.emit.printout(self.emit.emitIFFALSE(break_label, frame))
        
        self.visit(ast.loop, o)
        
        self.emit.printout(self.emit.emitGOTO(continue_label, frame))
        self.emit.printout(self.emit.emitLABEL(break_label, frame))
        
        frame.exitLoop()
        return o

    def visitForStep(self, ast: ForStep, o: dict):
        frame = o['frame']
        frame.enterLoop()

        o['env'] = [[]] + o['env']
        frame.enterScope(False)
        
        self.visit(ast.init, o)
        
        continue_label = frame.getNewLabel()
        body_label = frame.getNewLabel()
        update_label = frame.getNewLabel()
        break_label = frame.getBreakLabel()

        self.emit.printout(self.emit.emitLABEL(continue_label, frame))

        cond_code, _ = self.visit(ast.cond, o)
        self.emit.printout(cond_code)
        self.emit.printout(self.emit.emitIFFALSE(break_label, frame))

        # Loop body
        self.emit.printout(self.emit.emitLABEL(body_label, frame))
        self.visit(ast.loop, o)

        # Update statement part (where continue should jump)
        self.emit.printout(self.emit.emitLABEL(update_label, frame))
        self.visit(ast.upda, o) # Execute update statement

        # Jump back to condition check
        self.emit.printout(self.emit.emitGOTO(continue_label, frame))

        # End of loop
        self.emit.printout(self.emit.emitLABEL(break_label, frame))

        frame.exitScope()
        o['env'].pop(0)

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

    def visitNilLiteral(self, ast: NilLiteral, o: dict):
        frame = o['frame']
        return self.emit.emitPUSHNULL(frame), None
    
    def checkType(self, LSH_type, RHS_type, list_type_permission):
        if type(RHS_type) == StructType and RHS_type.name == "":
            if not type(LSH_type) in [Id, StructType, InterfaceType]: return False
            else: return True

        LSH_type = self.lookup(LSH_type.name, self.list_type.values(), lambda x: x.name) if isinstance(LSH_type, Id) else LSH_type
        RHS_type = self.lookup(RHS_type.name, self.list_type.values(), lambda x: x.name) if isinstance(RHS_type, Id) else RHS_type

        if (type(LSH_type), type(RHS_type)) in list_type_permission:
            if isinstance(LSH_type, InterfaceType) and isinstance(RHS_type, StructType):
                count = 0
                for proto in LSH_type.methods:
                    for meth in RHS_type.methods:
                        if proto.name == meth.fun.name and [type(x) for x in proto.params] == [type(x) for x in list(map(lambda x: x.parType, meth.fun.params))]:
                            type_proto = proto.retType
                            type_meth = meth.fun.retType
                            if type(type_proto) == type(type_meth):
                                if not type(type_proto) == Id:
                                    count += 1
                                else:
                                    if type_proto.name == type_meth.name:
                                        count += 1
                if count == len(LSH_type.methods):
                    return True
                else: return False
            return True
        if (type(LSH_type), type(RHS_type)) in [(StructType, StructType), (InterfaceType, InterfaceType)]:
            return LSH_type.name == RHS_type.name

        if isinstance(LSH_type, ArrayType) and isinstance(RHS_type, ArrayType):
            return self.checkType(LSH_type.eleType, RHS_type.eleType, [(FloatType, IntType)]) and LSH_type.dimens == RHS_type.dimens

        return type(LSH_type) == type(RHS_type)