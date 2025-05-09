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
            if isinstance(item, VarDecl) and item.varInit:
                assignStmts.append(Assign(Id(item.varName), item.varInit))
            elif isinstance(item, ConstDecl) and item.iniExpr:
                assignStmts.append(Assign(Id(item.conName), item.iniExpr))
        
        self.visit(Block(assignStmts), env)

        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        self.emit.printout(self.emit.emitRETURN(VoidType(), frame))  
        self.emit.printout(self.emit.emitENDMETHOD(frame))  
        frame.exitScope()

    def visitProgram(self, ast: Program, c):
        self.list_function = c + [Symbol(item.name, MType(list(map(lambda x: x.parType, item.params)), item.retType), CName(self.className)) for item in ast.decl if isinstance(item, FuncDecl)]

        env = {}
        env['env'] = [c]

        self.emit.printout(self.emit.emitPROLOG(self.className, "java.lang.Object"))
        
        env = reduce(lambda a, x: self.visit(x, a) if isinstance(x, VarDecl) or  isinstance(x, ConstDecl) else a, ast.decl, env)
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
    
    def visitConstDecl(self, ast:ConstDecl, o: dict) -> dict:
        return self.visit(VarDecl(ast.conName, ast.conType, ast.iniExpr), o)

    def visitVarDecl(self, ast: VarDecl, o: dict) -> dict:
        def create_init(varType: Type) -> Literal:
            if type(varType) is IntType:
                return IntLiteral(0)
            elif type(varType) is FloatType:
                return FloatLiteral(0.0)
            elif type(varType) is StringType:
                return StringLiteral("")
            elif type(varType) is BoolType:
                return BooleanLiteral(False)
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
    
    def visitFuncCall(self, ast: FuncCall, o: dict) -> dict:
        sym = next(filter(lambda x: x.name == ast.funName, self.list_function), None)
        if o.get('stmt'):
            o["stmt"] = False
            params_code = "".join([self.visit(x, o)[0] for x in ast.args])
            self.emit.printout(params_code)      
            self.emit.printout(self.emit.emitINVOKESTATIC(f"{sym.value.value}/{ast.funName}", sym.mtype, o['frame']))
            
            return o
        
        output = "".join([self.visit(x, o)[0] for x in ast.args])
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

    def visitAssign(self, ast: Assign, o: dict) -> dict:
        if type(ast.lhs) is Id:
            sym = None
            for scope in o['env']:
                found_sym = next(filter(lambda x: x.name == ast.lhs.name, scope), None)
                if found_sym:
                    sym = found_sym
                    break

            if sym is None:
                new_var_decl = VarDecl(ast.lhs.name, None, ast.rhs)
                return self.visit(new_var_decl, o)

        rhsCode, rhsType = self.visit(ast.rhs, o)

        o['isLeft'] = True
        lhsCode, lhsType = self.visit(ast.lhs, o)
        o['isLeft'] = False

        if type(lhsType) is FloatType and type(rhsType) is IntType:
            rhsCode += self.emit.emitI2F(o['frame'])
        if type(ast.lhs) is ArrayCell:
            self.emit.printout(lhsCode)
            self.emit.printout(rhsCode)
            if self.arrayCell is None:
                store_type = lhsType.eleType if isinstance(lhsType, ArrayType) else lhsType
                self.emit.printout(self.emit.emitASTORE(store_type, o['frame']))
            else:
                self.emit.printout(self.emit.emitASTORE(self.arrayCell, o['frame']))
            self.arrayCell = None
        else:
            self.emit.printout(rhsCode)
            self.emit.printout(lhsCode)

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
                if type(typeRight) is IntType:
                    codeRight += self.emit.emitI2F(frame)
            return codeLeft + codeRight + self.emit.emitADDOP(op, typeReturn, frame), typeReturn
        if op in ['*', '/']:
            typeReturn = IntType() if type(typeLeft) is IntType and type(typeRight) is IntType else FloatType()
            if type(typeReturn) is FloatType:
                if type(typeLeft) is IntType:
                    codeLeft += self.emit.emitI2F(frame)
                if type(typeRight) is IntType:
                    codeRight += self.emit.emitI2F(frame)
            return codeLeft + codeRight + self.emit.emitMULOP(op, typeReturn, frame), typeReturn
        if op in ['%']:
            return codeLeft + codeRight + self.emit.emitMOD(frame), IntType()
        if op in ['==', '!=', '<', '>', '>=', '<='] and type(typeLeft) in [FloatType, IntType]:
            if type(typeLeft) is FloatType or type(typeRight) is FloatType:
                if type(typeLeft) is IntType:
                    codeLeft += self.emit.emitI2F(frame)
                if type(typeRight) is IntType:
                    codeRight += self.emit.emitI2F(frame)
                return codeLeft + codeRight + self.emit.emitREOP(op, FloatType(), frame), BoolType()
            else:
                return codeLeft + codeRight + self.emit.emitREOP(op, IntType(), frame), BoolType()
        if op in ['||']:
            return codeLeft + codeRight + self.emit.emitOROP(frame), BoolType()
        if op in ['&&']:
            return codeLeft + codeRight + self.emit.emitANDOP(frame), BoolType()

        if op in ['+'] and type(typeLeft) is StringType:
            return codeLeft + codeRight + self.emit.emitINVOKEVIRTUAL("java/lang/String/concat", MType([StringType()], StringType()), frame), StringType()

        if op in ['==', '!=', '<', '>', '>=', '<=',] and type(typeLeft) is StringType:
            code = codeLeft + codeRight + self.emit.emitINVOKEVIRTUAL("java/lang/String/compareTo", MType([StringType()], IntType()), frame)
            
            false_label = frame.getNewLabel()
            end_label = frame.getNewLabel()

            if op == "==":
                code += self.emit.emitIFICMPNE(false_label, o['frame'])
            elif op == "!=":
                code += self.emit.emitIFICMPEQ(false_label, o['frame'])
            elif op == "<":
                code += self.emit.emitIFICMPGE(false_label, o['frame'])
            elif op == "<=":
                code += self.emit.emitIFICMPGT(false_label, o['frame'])
            elif op == ">":
                code += self.emit.emitIFLE(false_label, o['frame'])
            elif op == ">=":
                code += self.emit.emitIFLT(false_label, o['frame'])

            frame.pop()
            
            code += self.emit.emitPUSHCONST("1", BoolType(), frame)[0]
            frame.push()
            
            code += self.emit.emitGOTO(end_label, frame)
            code += self.emit.emitLABEL(false_label, frame)

            code += self.emit.emitPUSHCONST("0", BoolType(), frame)[0]
            frame.push()
            
            code += self.emit.emitLABEL(end_label, frame)

            return code, BoolType()
              
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

    ## TODO array ------------------------------
    def visitArrayCell(self, ast: ArrayCell, o: dict) -> tuple[str, Type]:
        newO = o.copy()
        newO['isLeft'] = False
        codeGen, arrType = self.visit(ast.arr, newO)

        for idx, item in enumerate(ast.idx):
            codeGen += self.visit(item, newO)[0]
            if idx != len(ast.idx) - 1:
                codeGen += self.emit.emitALOAD(arrType, o['frame'])

        retType = None
        if len(arrType.dimens) == len(ast.idx):
            retType = arrType.eleType
            if not o.get('isLeft'):
                codeGen += self.emit.emitALOAD(retType, o['frame'])
            else:
                self.arrayCell = retType
        else:
            retType = ArrayType(arrType.dimens[len(ast.idx):], arrType.eleType)
            if not o.get('isLeft'):
                codeGen += self.emit.emitALOAD(retType, o['frame'])
            else:
                self.arrayCell = retType

        return codeGen, retType

    def visitArrayLiteral(self, ast: ArrayLiteral , o: dict) -> tuple[str, Type]:

        def nested_recursive(current_value, context: dict) -> tuple[str, Type]:
            if not isinstance(current_value, list):
                return self.visit(current_value, context)

            frame = context['frame']
            if not current_value:
                code_gen = self.emit.emitPUSHICONST(0, frame)
                element_type_for_newarray = ast.eleType
                
                if isinstance(element_type_for_newarray, (IntType, FloatType, BoolType)):
                    code_gen += self.emit.emitNEWARRAY(element_type_for_newarray, frame)
                else:
                    code_gen += self.emit.emitANEWARRAY(element_type_for_newarray, frame)

                return code_gen, ArrayType([0], element_type_for_newarray)

            code_gen = self.emit.emitPUSHICONST(len(current_value), frame)
            
            first_element = current_value[0]
            
            if not isinstance(first_element, list):
                _, type_of_elements = self.visit(first_element, context)

                if isinstance(type_of_elements, IntType):
                    code_gen += self.emit.emitNEWARRAY(type_of_elements, frame)
                elif isinstance(type_of_elements, FloatType):
                    code_gen += self.emit.emitNEWARRAY(type_of_elements, frame)
                elif isinstance(type_of_elements, BoolType):
                    code_gen += self.emit.emitNEWARRAY(type_of_elements, frame)
                else:
                    code_gen += self.emit.emitANEWARRAY(type_of_elements, frame)

                for idx, item in enumerate(current_value):
                    code_gen += self.emit.emitDUP(frame)
                    code_gen += self.emit.emitPUSHICONST(idx, frame)
                    item_code, item_type = self.visit(item, context)
                    code_gen += item_code
                    
                    if isinstance(type_of_elements, FloatType) and isinstance(item_type, IntType):
                        code_gen += self.emit.emitI2F(frame)
                    code_gen += self.emit.emitASTORE(type_of_elements, frame)
                
                return code_gen, ArrayType([len(current_value)], type_of_elements)
    
            else:
                _, type_of_inner_array = nested_recursive(first_element, context)

                code_gen += self.emit.emitANEWARRAY(type_of_inner_array, frame)

                for idx, sub_list in enumerate(current_value):
                    code_gen += self.emit.emitDUP(frame)
                    code_gen += self.emit.emitPUSHICONST(idx, frame)
                
                    sub_array_code, _ = nested_recursive(sub_list, context)
                    code_gen += sub_array_code
                    code_gen += self.emit.emitASTORE(type_of_inner_array, frame)
                
                final_dimensions = [len(current_value)]
                final_element_type = None

                if isinstance(type_of_inner_array, ArrayType):
                    final_dimensions.extend(type_of_inner_array.dimens)
                    final_element_type = type_of_inner_array.eleType
                else:
                    final_element_type = type_of_inner_array 
                    
                    
                return code_gen, ArrayType(final_dimensions, final_element_type)
        
        return nested_recursive(ast.value, o)

    
    def visitArrayType(self, ast:ArrayType, o):
        codeGen = ""
        for dimen in ast.dimens:
            dimen_code, _ = self.visit(dimen, o)
            codeGen += dimen_code
        codeGen += self.emit.emitMULTIANEWARRAY(ast, o['frame'])
        return codeGen, ast


    def visitStructType(self, ast, c):
        structName = ast.name.name
        emitter = Emitter(f"{structName}.j")
        
        c.append(emitter)
        
        emitter.printout(emitter.emitPROLOG(structName, "java/lang/Object"))
        
        for decl in ast.varDecls:
            emitter.printout(emitter.emitATTRIBUTE(decl.variable.name, self.getJVMType(decl.varType), False))
        
        emitter.printout(emitter.emitDEFAULT_CONSTRUCTOR(structName))
        
        for method in ast.methods:
            self.visit(method, c)
        
        emitter.printout(emitter.emitEPILOG())
        c.pop()

    def visitFieldAccess(self, ast, c):
        frame = c[-1] if isinstance(c[-1], Frame) else c[-2]
        emitter = c[-2] if isinstance(c[-1], Frame) else c[-3]
        
        code, typ = self.visit(ast.obj, c)
        fieldName = ast.fieldname.name
        fieldType = None
        structName = typ.name
        code = code + emitter.emitGETFIELD(structName, fieldName, self.getJVMType(fieldType))
        
        return code, fieldType

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