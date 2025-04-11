from AST import * 
from Visitor import *
from Utils import Utils
from StaticError import *
from functools import reduce
from typing import List, Tuple, Union, Any
import inspect


class MType:
    def __init__(self, partype, rettype):
        self.partype = partype
        self.rettype = rettype

    def __str__(self):
        return "MType([" + ",".join(str(x) for x in self.partype) + "]," + str(self.rettype) + ")"


class Symbol:
    def __init__(self, name, mtype, value = None):
        self.name = name
        self.mtype = mtype
        self.value = value

    def __str__(self):
        return "Symbol(" + str(self.name) + "," + str(self.mtype) + ("" if self.value is None else "," + str(self.value)) + ")"


class StaticChecker(BaseVisitor,Utils):
    def __init__(self, ast):
        self.ast = ast
        self.list_type: List[Union[StructType, InterfaceType]] = []
        self.list_function = [
            FuncDecl("getInt", [], IntType(), Block([])),
            FuncDecl("putInt", [ParamDecl("i", IntType())], VoidType(), Block([])),
            FuncDecl("putIntLn", [ParamDecl("i", IntType())], VoidType(), Block([])),
            FuncDecl("getFloat", [], FloatType(), Block([])),
            FuncDecl("putFloat", [ParamDecl("f", FloatType())], VoidType(), Block([])),
            FuncDecl("putFloatLn", [ParamDecl("n", FloatType())], VoidType(), Block([])),
            FuncDecl("getBool", [], BoolType(), Block([])),
            FuncDecl("putBool", [ParamDecl("b", BoolType())], VoidType(), Block([])),
            FuncDecl("putBoolLn", [ParamDecl("b", BoolType())], VoidType(), Block([])),
            FuncDecl("getString", [], StringType(), Block([])),
            FuncDecl("putString", [ParamDecl("s", StringType())], VoidType(), Block([])),
            FuncDecl("putStringLn", [ParamDecl("s", StringType())], VoidType(), Block([])),
            FuncDecl("putLn", [], VoidType(), Block([]))
        ]
        self.function_current: FuncDecl = None
        self.loop_ctx = []

    def check(self):
        return self.visit(self.ast, [[]])
    
    def _check_type(self, LHS_type, RHS_type, allowed_pairs=None) -> bool:
        """
        Checks type compatibility between left-hand side and right-hand side types.
        
        Implements the following type compatibility rules:
        1. Exact type matches are compatible
        2. Types in allowed_pairs list are compatible (e.g., FloatType and IntType)
        3. Nil literals are compatible with struct and interface types
        4. Struct types implement interface types if they have all required methods
        5. Array types are compatible if dimensions match and element types are compatible
        6. Struct types are compatible only if they have the same name
        
        Args:
            LHS_type: The target type (type being assigned to)
            RHS_type: The source type (type being assigned from)
            allowed_pairs: List of tuples representing allowed type conversions
                        e.g., [(FloatType, IntType)] allows int to float conversion
        
        Returns:
            bool: True if types are compatible, False otherwise
        """
        allowed_pairs = allowed_pairs or []
        
        if isinstance(LHS_type, Id):
            LHS_type = self.lookup(LHS_type.name, self.list_type, lambda x: x.name) or LHS_type
        if isinstance(RHS_type, Id):
            RHS_type = self.lookup(RHS_type.name, self.list_type, lambda x: x.name) or RHS_type

        # Check allowed conversions
        if (type(LHS_type), type(RHS_type)) in allowed_pairs:
            return True
        
        # Handle nil literal
        if isinstance(RHS_type, StructType) and RHS_type.name == "":
            return isinstance(LHS_type, (Id, StructType, InterfaceType))
        
        # Handle struct/interface compatibility
        if isinstance(LHS_type, InterfaceType) and isinstance(RHS_type, StructType):
            return all(
                any(
                    method.fun.name == proto.name
                    and len(method.fun.params) == len(proto.params)
                    and all(self._check_type(proto.params[i], p.parType) for i, p in enumerate(method.fun.params))
                    and self._check_type(proto.retType, method.fun.retType)
                    for method in RHS_type.methods
                )
                for proto in LHS_type.methods
            )
        
        # Check array compatibility
        if isinstance(LHS_type, ArrayType) and isinstance(RHS_type, ArrayType):
            # Check if number of dimensions match
            if len(LHS_type.dimens) != len(RHS_type.dimens):
                return False
            
            # Check if dimension values match
            for i in range(len(LHS_type.dimens)):
                lhs_dim = LHS_type.dimens[i]
                rhs_dim = RHS_type.dimens[i]
                
                # Get dimension values
                lhs_val = lhs_dim.value if isinstance(lhs_dim, IntLiteral) else None
                rhs_val = rhs_dim.value if isinstance(rhs_dim, IntLiteral) else None
                
                # If both values are known and don't match, types are not compatible
                if lhs_val is not None and rhs_val is not None and lhs_val != rhs_val:
                    return False
            
            if (isinstance(LHS_type.eleType, FloatType) and isinstance(RHS_type.eleType, (IntType, FloatType))):
                return self._check_type(LHS_type.eleType, RHS_type.eleType, allowed_pairs)

            return type(LHS_type.eleType) == type(RHS_type.eleType) and LHS_type.eleType == RHS_type.eleType
            # return self._check_type(LHS_type.eleType, RHS_type.eleType, allowed_pairs)
        
        # Check struct name equivalence
        if isinstance(LHS_type, StructType) and isinstance(RHS_type, StructType):
            return LHS_type.name == RHS_type.name
        
        return type(LHS_type) == type(RHS_type)

    def visitProgram(self, ast: Program, _) -> List[List[Any]]:
        """
        class Program(AST):
            decl: List[Decl]
        """
        # First, collect all type declarations
        self.list_type = [decl for decl in ast.decl if isinstance(decl, (StructType, InterfaceType))]
        
        # Check for redeclared global names
        declared_names = set(func.name for func in self.list_function)
        for decl in ast.decl:
            name = None
            kind = None
            if isinstance(decl, (StructType, InterfaceType)):
                name = decl.name
                kind = Type()
            elif isinstance(decl, VarDecl):
                name = decl.varName
                kind = Variable()
            elif isinstance(decl, ConstDecl):
                name = decl.conName
                kind = Constant()
            elif isinstance(decl, FuncDecl):
                name = decl.name
                kind = Function()
                
            if name:
                if name in declared_names:
                    raise Redeclared(kind, name)
                declared_names.add(name)

        # Process type declarations
        self.list_type = reduce(
            lambda acc, decl: [self.visit(decl, acc)] + acc \
                if isinstance(decl, (StructType, InterfaceType)) else acc,
            ast.decl,
            []
        )

        # Process method declarations
        reduce(
            lambda _, decl: self.visit(decl, [[]]) if isinstance(decl, MethodDecl) else _,
            ast.decl, []
        )

        # Process function declarations
        self.list_function += [decl for decl in ast.decl if isinstance(decl, FuncDecl)]

        # Process other declarations
        env = [[]]
        reduce(
            lambda _, decl: self.visit(decl, env) \
                if isinstance(decl, (VarDecl, ConstDecl, FuncDecl)) else _, 
            ast.decl, []
        )
        return env

    def visitVarDecl(self, ast: VarDecl, c) -> Symbol:
        """
        class VarDecl(Decl,BlockMember):
            varName: str
            varType: Type # None if there is no type
            varInit: Expr # None if there is no initialization
        """
        current_scope = c[0]
        if self.lookup(ast.varName, current_scope, lambda x: x.name):
            raise Redeclared(Variable(), ast.varName)
        
        var_type = ast.varType
        if ast.varInit:
            init_type = self.visit(ast.varInit, c)
            if var_type:
                if not self._check_type(var_type, init_type, [(FloatType, IntType)]):
                    raise TypeMismatch(ast)
            else:
                var_type = init_type
        
        current_scope.append(Symbol(ast.varName, var_type))
        return Symbol(ast.varName, var_type)

    def visitConstDecl(self, ast: ConstDecl, c) -> Symbol:
        """
        class ConstDecl(Decl,BlockMember):
            conName: str
            conType: Type # None if there is no type 
            iniExpr: Expr
        """
        current_scope = c[0]
        if self.lookup(ast.conName, current_scope, lambda x: x.name):
            raise Redeclared(Constant(), ast.conName)
        
        init_type = self.visit(ast.iniExpr, c)
        const_type = ast.conType or init_type
        
        if not self._check_type(const_type, init_type):
            raise TypeMismatch(ast)
        
        current_scope.append(Symbol(ast.conName, const_type))
        return Symbol(ast.conName, const_type)
    
    def visitParamDecl(self, ast: ParamDecl, c: List[List[Symbol]]) -> Symbol:
        """
        class ParamDecl(Decl):
            parName: str
            parType: Type
        """
        current_scope = c[0]
        if self.lookup(ast.parName, current_scope, lambda x: x.name):
            raise Redeclared(Parameter(), ast.parName)
        
        init_type = self.visit(ast.parType, c)
        par_type = ast.parType or init_type
        
        if not self._check_type(par_type, init_type):
            raise TypeMismatch(ast)
        
        current_scope.append(Symbol(ast.parName, par_type))
        return Symbol(ast.parName, par_type)
    

    def visitFuncDecl(self, ast: FuncDecl, c) -> Symbol:
        """
        class FuncDecl(Decl):
            name: str
            params: List[ParamDecl]
            retType: Type # VoidType if there is no return type
            body: Block
        """
        # Check redeclaration in current scope
        current_scope = c[0]
        if self.lookup(ast.name, current_scope, lambda x: x.name):
            raise Redeclared(Function(), ast.name)
        
        # Create function type with evaluated array dimensions
        param_types = []
        param_scope = []
        for param in ast.params:
            param_sym = self.visit(param, [param_scope] + c)
            param_scope.append(param_sym)
            param_types.append(param_sym.mtype)
        
        func_type = MType(param_types, ast.retType)
        current_scope.append(Symbol(ast.name, func_type))
        
        # Check body
        self.function_current = ast
        body_env = [param_scope] + c
        self.visit(ast.body, body_env)
        self.function_current = None
        
        return Symbol(ast.name, func_type)

    def visitMethodDecl(self, ast: MethodDecl, c: List[List[Symbol]]) -> Symbol:
        """
        class MethodDecl(Decl):
            receiver: str
            recType: Type 
            fun: FuncDecl
        """
        rec_type = self.lookup(ast.recType.name, self.list_type, lambda x: x.name)
        if not rec_type:
            raise Undeclared(Type(), ast.recType.name)
        
        if not isinstance(rec_type, StructType):
            raise TypeMismatch(ast)
        
        if any(method.fun.name == ast.fun.name for method in rec_type.methods):
            raise Redeclared(Method(), ast.fun.name)
        
        if any(field_name == ast.fun.name for field_name, _ in rec_type.elements):
            raise Redeclared(Method(), ast.fun.name)
        
        method_scope = []
        method_scope.append(Symbol(ast.receiver, rec_type))
        
        param_types = []
        seen_param_names = set()
        
        for param in ast.fun.params:
            # Check for parameter name conflicts with other parameters
            if param.parName in seen_param_names:
                raise Redeclared(Parameter(), param.parName)
            seen_param_names.add(param.parName)
            
            param_type = self.visit(param.parType, c)
            param_types.append(param_type)
            # Parameters should shadow receiver with the same name
            method_scope = [sym for sym in method_scope if sym.name != param.parName] + [Symbol(param.parName, param_type)]
        
        meth_type = MType(param_types, ast.fun.retType)
        rec_type.methods.append(ast)
        
        prev_func = self.function_current
        self.function_current = ast.fun
        
        body_env = [method_scope] + c
        self.visit(ast.fun.body, body_env)
        
        self.function_current = prev_func
        
        return Symbol(ast.fun.name, meth_type)

    def visitPrototype(self, ast: Prototype, c: List[Prototype]) -> Prototype:
        """
        class Prototype(AST):
            name: str
            params: List[Type]
            retType: Type # VoidType if there is no return type
        """
        res = self.lookup(ast.name, c, lambda x: x.name)
        if not res is None:
            raise Redeclared(Prototype(), ast.name)
        return ast
    
    def visitIntType(self, ast: IntType, _) -> Type: 
        return ast
    
    def visitFloatType(self, ast: FloatType, _)-> Type: 
        return ast
    
    def visitBoolType(self, ast: BoolType, _)-> Type: 
        return ast
    
    def visitStringType(self, ast: StringType, _) -> Type: 
        return ast
    
    def visitVoidType(self, ast: VoidType, _) -> Type: 
        return ast
    
    def visitArrayType(self, ast: ArrayType, c: List[List[Symbol]]) -> ArrayType:
        """
        class ArrayType(Type):
            dimens: List[Expr]
            eleType: Type
        """
        evaluated_dims = []
        for dim in ast.dimens:
            dim_val = self._compute_constant_value(dim, c)
            evaluated_dims.append(dim_val)
        ast.dimens = [IntLiteral(d) for d in evaluated_dims]
        
        # Check element type exists
        if isinstance(ast.eleType, Id):
            resolved = self.lookup(ast.eleType.name, self.list_type, lambda x: x.name)
            if not resolved:
                raise Undeclared(Type(), ast.eleType.name)
            ast.eleType = resolved
        return ast

    def visitStructType(self, ast: StructType, c: List[Union[StructType, InterfaceType]]) -> StructType:
        """
        class StructType(Type):
            name: str
            elements: List[Tuple[str,Type]]
            methods: List[MethodDecl]
        """
        existing = self.lookup(ast.name, c, lambda x: x.name)
        if existing:
            raise Redeclared(Type(), ast.name)
        
        seen = set()
        for field_name, _ in ast.elements:
            if field_name in seen:
                raise Redeclared(Field(), field_name)
            seen.add(field_name)
        
        new_elements = []
        for (name, typ) in ast.elements:
            resolved_type = self.visit(typ, c)
            new_elements.append((name, resolved_type))
        ast.elements = new_elements
        return ast

    def visitInterfaceType(self, ast: InterfaceType, c : List[Union[StructType, InterfaceType]]) -> InterfaceType:
        """
        class InterfaceType(Type):
            name: str
            methods: List[Prototype]
        """
        res = self.lookup(ast.name, c, lambda x: x.name)
        if not res is None:
            raise Redeclared(Prototype(), ast.name)
        ast.methods = reduce(lambda acc,ele: [self.visit(ele,acc)] + acc , ast.methods , [])
        return ast
    
    def visitBlock(self, ast: Block, c: List[List[Symbol]]) -> None:
        """
        class Block(Stmt):
            member: List[BlockMember]
        """
        new_env = [[]] + c
        for member in ast.member:
            if isinstance(member, MethCall):
                ret_type = self.visit(member, new_env)
                if not isinstance(ret_type, VoidType):
                    raise TypeMismatch(member)
            else:
                self.visit(member, new_env)
        return new_env
 
    def visitAssign(self, ast: Assign, c) -> None:
        """
        class Assign(Stmt):
            lhs: LHS
            rhs: Expr # if assign operator is +=, rhs is BinaryOp(+,lhs,rhs), similar to -=,*=,/=,%=
        """
        # If lhs is an Id, it might be an implicit declaration
        if isinstance(ast.lhs, Id):
            id_name = ast.lhs.name
            current_scope = c[0]
            
            if not self.lookup(id_name, current_scope, lambda x: x.name):
                rhs_type = self.visit(ast.rhs, c)
                current_scope.append(Symbol(id_name, rhs_type))
                return
        
        lhs_type = self.visit(ast.lhs, c)
        rhs_type = self.visit(ast.rhs, c)
        
        allowed = [(FloatType, IntType), (ArrayType, ArrayType), (InterfaceType, StructType)]
        if not self._check_type(lhs_type, rhs_type, allowed):
            raise TypeMismatch(ast)
   
    def visitIf(self, ast: If, c) -> None:
        """
        class If(Stmt):
            expr: Expr
            thenStmt: Stmt
            elseStmt: Stmt # None if there is no else
        """
        cond_type = self.visit(ast.expr, c)
        if not isinstance(cond_type, BoolType):
            raise TypeMismatch(ast)
        
        self.visit(ast.thenStmt, c)
        if ast.elseStmt:
            self.visit(ast.elseStmt, c)
    
    def visitForBasic(self, ast: ForBasic, c) -> None:
        """
        class ForBasic(Stmt):
            cond: Expr
            loop: Block
        """
        cond_type = self.visit(ast.cond, c)
        if not isinstance(cond_type, BoolType):
            raise TypeMismatch(ast)
        self.visit(ast.loop, c)
 
    def visitForStep(self, ast: ForStep, c) -> None:
        """
        class ForStep(Stmt):
            init: Stmt
            cond: Expr
            upda: Assign
            loop: Block
        """
        loop_env = [[]] + c
        self.visit(ast.init, loop_env)

        cond_type = self.visit(ast.cond, loop_env)
        if not isinstance(cond_type, BoolType):
            raise TypeMismatch(ast)
        
        self.visit(ast.upda, loop_env)
        # Manage loop context for break/continue
        self.loop_ctx.append(True)

        for member in ast.loop.member:
            self.visit(member, loop_env)

        self.loop_ctx.pop()
        return None

    def visitForEach(self, ast: ForEach, c: List[List[Symbol]]) -> None:
        """
        class ForEach(Stmt):
            idx: Id
            value: Id
            arr: Expr
            loop: Block
        """
        arr_type = self.visit(ast.arr, c)
        if not isinstance(arr_type, ArrayType):
            raise TypeMismatch(ast)
        
        loop_scope = [[]] + c
        
        idx_symbol = Symbol(ast.idx.name, IntType())
        if self.lookup(idx_symbol.name, loop_scope[0], lambda x: x.name):
            raise Redeclared(Variable(), idx_symbol.name)
        loop_scope[0].append(idx_symbol)
        
        value_type = ArrayType(arr_type.dimens[1:], arr_type.eleType) \
            if len(arr_type.dimens) > 1 else arr_type.eleType
            
        # Find the value symbol in the current or parent scopes
        value_sym = None
        for scope in c:
            value_sym = self.lookup(ast.value.name, scope, lambda x: x.name)
            if value_sym:
                break
        
        if value_sym:
            # Check if the value's type is compatible with the array element type
            if not self._check_type(value_sym.mtype, value_type):
                raise TypeMismatch(ast)
        else:
            val_symbol = Symbol(ast.value.name, value_type)
            if self.lookup(val_symbol.name, loop_scope[0], lambda x: x.name):
                raise Redeclared(Variable(), val_symbol.name)
            loop_scope[0].append(val_symbol)
        
        # Manage loop context for break/continue
        self.loop_ctx.append(True)
        
        for member in ast.loop.member:
            self.visit(member, loop_scope)
        
        self.loop_ctx.pop()
        return None

    def visitContinue(self, *_) -> None:
        return None

    def visitBreak(self, *_) -> None:
        return None

    def visitReturn(self, ast: Return, c) -> None:
        """
        class Return(Stmt):
            expr: Expr # None if there is no expr
        """
        if self.function_current is None:
            raise TypeMismatch(ast)
        
        if ast.expr:
            expr_type = self.visit(ast.expr, c)
            
            # Special handling for array literals to check dimension consistency
            if isinstance(ast.expr, ArrayLiteral):
                if ast.expr.dimens and isinstance(ast.expr.dimens[0], Id):
                    dim_id = ast.expr.dimens[0].name
                    dim_value = None
                    
                    for scope in c:
                        for sym in scope:
                            if sym.name == dim_id and hasattr(sym, 'value') and sym.value is not None:
                                dim_value = sym.value
                                break
                    
                    if dim_value is None and self.function_current and self.function_current.body:
                        for stmt in self.function_current.body.member:
                            if isinstance(stmt, ConstDecl) and stmt.conName == dim_id:
                                if isinstance(stmt.iniExpr, IntLiteral):
                                    dim_value = stmt.iniExpr.value
                                    break
                    
                    # Check global constants as a fallback
                    if dim_value is None:
                        for decl in self.ast.decl:
                            if isinstance(decl, ConstDecl) and decl.conName == dim_id:
                                if isinstance(decl.iniExpr, IntLiteral):
                                    dim_value = decl.iniExpr.value
                                    break
                    
                    # Verify that the array literal has the correct number of elements
                    if dim_value is not None and dim_value != len(ast.expr.value):
                        raise TypeMismatch(ast)
            
            if not self._check_type(self.function_current.retType, expr_type):
                raise TypeMismatch(ast)
        else:
            if not isinstance(self.function_current.retType, VoidType):
                raise TypeMismatch(ast)

    def visitBinaryOp(self, ast: BinaryOp, c) -> Type:
        """
        class BinaryOp(Expr):
            op: str
            left: Expr
            right: Expr
        """
        left_type = self.visit(ast.left, c)
        right_type = self.visit(ast.right, c)
        
        if ast.op == '+':
            if isinstance(left_type, StringType) and isinstance(right_type, StringType):
                return StringType()
            elif isinstance(left_type, (IntType, FloatType)) and self._check_type(left_type, right_type, [(FloatType, IntType)]):
                return FloatType() if FloatType in (type(left_type), type(right_type)) else IntType()
        
        if ast.op in ['-', '*', '/']:
            if isinstance(left_type, (IntType, FloatType)) and self._check_type(left_type, right_type, [(FloatType, IntType)]):
                return FloatType() if FloatType in (type(left_type), type(right_type)) else IntType()
            
        if ast.op in ['%']:
            if self._check_type(left_type, right_type, [(FloatType, IntType)]):
                if isinstance(left_type,(FloatType, IntType)):
                    return IntType()
        
        if ast.op in ['<', '>', '<=', '>=']:
            if self._check_type(left_type, right_type, [(FloatType, IntType)]) and isinstance(left_type, (IntType, FloatType)):
                return BoolType()
        
        if ast.op in ['==', '!=']:
            if self._check_type(left_type, right_type):
                return BoolType()
        
        if ast.op in ['&&', '||']:
            if isinstance(left_type, BoolType) and isinstance(right_type, BoolType):
                return BoolType()
        
        raise TypeMismatch(ast)
    
    def visitUnaryOp(self, ast: UnaryOp, c) -> Type:
        """
        class UnaryOp(Expr):
            op: str
            body: Expr
        """
        body_type = self.visit(ast.body, c)

        if ast.op == '-' and isinstance(body_type, (IntType, FloatType)):
            return body_type
        if ast.op == '!' and isinstance(body_type, BoolType):
            return BoolType()
        
        raise TypeMismatch(ast)
    
    def visitFuncCall(self, ast: FuncCall, c) -> Type:
        """
        class FuncCall(Expr,Stmt):
            funName: str
            args: List[Expr] # [] if there is no arg 
        """
        func_sym = self.lookup(ast.funName, self.list_function, lambda x: x.name)
        if not func_sym:
            raise Undeclared(Function(), ast.funName)
        
        if c and c[0]:
            symbol = self.lookup(ast.funName, c[0], lambda x: x.name)
            if symbol and not isinstance(symbol.mtype, MType):
                raise Undeclared(Function(), ast.funName)
        
        if len(ast.args) != len(func_sym.params):
            raise TypeMismatch(ast)
        
        for arg, param in zip(ast.args, func_sym.params):
            arg_type = self.visit(arg, c)
            if not self._check_type(param.parType, arg_type):
                raise TypeMismatch(ast)
        
        return func_sym.retType

    def visitMethCall(self, ast: MethCall, c: List[List[Symbol]]) -> Type:
        """
        class MethCall(Expr,Stmt):
            receiver: Expr
            metName: str
            args: List[Expr]
        """
        receiver_type = self.visit(ast.receiver, c)
        
        # Resolve receiver type if it's an Id
        if isinstance(receiver_type, Id):
            resolved_type = self.lookup(receiver_type.name, self.list_type, lambda x: x.name)
            if resolved_type:
                receiver_type = resolved_type
            else:
                raise Undeclared(Type(), receiver_type.name)
        
        if not isinstance(receiver_type, (StructType, InterfaceType)):
            raise TypeMismatch(ast)
        
        # Lookup method in struct or interface
        method = None
        if isinstance(receiver_type, StructType):
            method = self.lookup(ast.metName, receiver_type.methods, lambda x: x.fun.name)
            if not method:
                raise Undeclared(Method(), ast.metName)
        else:  # InterfaceType
            method = self.lookup(ast.metName, receiver_type.methods, lambda x: x.name)
            if not method:
                raise Undeclared(Method(), ast.metName)
        
        
        # Extract function declaration or prototype
        if isinstance(receiver_type, StructType):
            func_decl = method.fun
            expected_params = func_decl.params
            return_type = func_decl.retType
        else:  # InterfaceType
            prototype = method
            expected_params = [ParamDecl(f"param_{i}", param) for i, param in enumerate(prototype.params)]
            return_type = prototype.retType
        
        # Check argument count
        if len(ast.args) != len(expected_params):
            raise TypeMismatch(ast)
        
        # Check each argument type matches parameter
        for arg, param in zip(ast.args, expected_params):
            arg_type = self.visit(arg, c)
            param_type = param.parType
            if not self._check_type(param_type, arg_type, allowed_pairs=[]):
                raise TypeMismatch(ast)
        
        return return_type

    def visitId(self, ast: Id, c: List[List[Symbol]]) -> Type:
        """
        class Id(Type,LHS):
            name: str
        """
        is_return_expr = False
        for frame in inspect.stack():
            if frame.function == 'visitReturn' and 'ast' in frame.frame.f_locals:
                if frame.frame.f_locals['ast'].expr == ast:
                    is_return_expr = True
                    break
        
        type_decl = self.lookup(ast.name, self.list_type, lambda x: x.name)
        if type_decl:
            if is_return_expr:
                raise Undeclared(Identifier(), ast.name)
            return type_decl

        for scope in c:
            symbol = self.lookup(ast.name, scope, lambda x: x.name) 
            if symbol and not isinstance(symbol.mtype, MType):
                return symbol.mtype
        raise Undeclared(Identifier(), ast.name)
    
    def visitArrayCell(self, ast: ArrayCell, c: List[List[Symbol]]) -> Type:
        """
        class ArrayCell(LHS):
            arr: Expr
            idx: List[Expr]
        """
        arr_type = self.visit(ast.arr, c)

        if not isinstance(arr_type, ArrayType):
            raise TypeMismatch(ast)

        for index_expr in ast.idx:
            index_type = self.visit(index_expr, c)
            if not self._check_type(index_type, IntType()):
                raise TypeMismatch(ast)

        accessed_dims = len(ast.idx)
        total_dims = len(arr_type.dimens)

        if accessed_dims == total_dims:
            return arr_type.eleType
        if accessed_dims < total_dims:
            remaining_dims = arr_type.dimens[accessed_dims:]
            return ArrayType(remaining_dims, arr_type.eleType)
            
        raise TypeMismatch(ast)
    
    def visitFieldAccess(self, ast: FieldAccess, c: List[List[Symbol]]) -> Type:
        """
        class FieldAccess(LHS):
            receiver: Expr
            field: str
        """
        receiver_type = self.visit(ast.receiver, c)
    
        if isinstance(receiver_type, Id):
            resolved_type = self.lookup(receiver_type.name, self.list_type, lambda x: x.name)
            if resolved_type is None:
                raise Undeclared(Type(), receiver_type.name)
            receiver_type = resolved_type
        
        if not isinstance(receiver_type, StructType):
            raise TypeMismatch(ast)
        
        for field_name, field_type in receiver_type.elements:
            if field_name == ast.field:
                return field_type
    
        raise Undeclared(Field(), ast.field)

    def visitArrayLiteral(self, ast: ArrayLiteral, c: List[List[Symbol]]) -> Type:
        """
        NestedList = Union[PrimLit, List['NestedList']]
        class ArrayLiteral(Literal):
            dimens:List[Expr]
            eleType: Type
            value: NestedList
        """
        # Check each dimension expression is an integer
        for dim_expr in ast.dimens:
            dim_type = self.visit(dim_expr, c)
            if not isinstance(dim_type, IntType):
                raise TypeMismatch(ast)
            
        # For the first dimension, check if it matches the number of elements
        if ast.dimens and len(ast.dimens) > 0:
            first_dim = ast.dimens[0]
            try:
                dim_value = self._compute_constant_value(first_dim, c)
                if dim_value != len(ast.value):
                    raise TypeMismatch(ast)
            except:
                pass
        
        # Validate elements against the declared element type
        def validate_elements(elements, ele_type):
            for elem in elements:
                if isinstance(elem, list):
                    if not isinstance(ele_type, ArrayType):
                        raise TypeMismatch(ast)
                    validate_elements(elem, ele_type.eleType)
                else:
                    elem_type = self.visit(elem, c)
                    if not self._check_type(ele_type, elem_type, [(FloatType, IntType)]):
                        raise TypeMismatch(ast)
        
        validate_elements(ast.value, ast.eleType)
        
        return ArrayType([dim for dim in ast.dimens], ast.eleType)

    def visitStructLiteral(self, ast: StructLiteral, c: List[List[Symbol]]) -> Type:
        """
        class StructLiteral(Literal):
            name:str
            elements: List[Tuple[str,Expr]] # [] if there is no elements
        """
        struct_type = self.lookup(ast.name, self.list_type, lambda x: x.name)
        if not struct_type or not isinstance(struct_type, StructType):
            raise Undeclared(Type(), ast.name)
        
        # Check all fields are present and types match
        field_map = {name: typ for name, typ in struct_type.elements}
        for field_name, expr in ast.elements:
            if field_name not in field_map:
                raise Undeclared(Field(), field_name)
            expr_type = self.visit(expr, c)
            if not self._check_type(field_map[field_name], expr_type):
                raise TypeMismatch(ast)
        return struct_type

    def visitIntLiteral(self, *_) -> Type:
        """
        class IntLiteral(PrimLit):
            value:int
        """
        return IntType()

    def visitFloatLiteral(self, *_) -> Type:
        """
        class FloatLiteral(PrimLit):
            value:float
        """
        return FloatType()
    
    def visitStringLiteral(self, *_) -> Type:
        """
        class StringLiteral(PrimLit):
            value:str
        """
        return StringType()
    
    def visitBooleanLiteral(self, *_) -> Type:
        """
        class BooleanLiteral(PrimLit):
            value:bool
        """
        return BoolType()

    def visitNilLiteral(self, *_) -> Type:
        return StructType("", [], [])
    
    def _compute_constant_value(self, node: AST, c: List[List[Symbol]]) -> int:
        """
        Evaluates constant expressions at compile time.
        
        Used primarily for array dimensions and constant initialization.
        Supports integer literals, constant identifiers, basic arithmetic operations,
        and comparison operations.
        
        Throws Undeclared error if a referenced identifier isn't found or doesn't
        have a constant value.
        
        Args:
            node: AST node representing the expression to evaluate
            c: List of symbol tables representing the current scope hierarchy
            
        Returns:
            int: The evaluated integer value of the expression
            
        Raises:
            Undeclared: If an identifier in the expression cannot be resolved
        """
        if isinstance(node, IntLiteral):
            return node.value
        
        if isinstance(node, Id):
            for scope in c:
                sym = self.lookup(node.name, scope, lambda x: x.name)
                if sym and isinstance(sym.mtype, IntType) and sym.value is not None:
                    return sym.value
            
            for decl in self.ast.decl:
                if isinstance(decl, ConstDecl) and decl.conName == node.name:
                    if isinstance(decl.iniExpr, IntLiteral):
                        return decl.iniExpr.value
                        
            raise Undeclared(Identifier(), node.name)
        
        if isinstance(node, BinaryOp):
            left = self._compute_constant_value(node.left, c)
            right = self._compute_constant_value(node.right, c)
            op = node.op
            if op == '+': return left + right
            elif op == '-': return left - right
            elif op == '*': return left * right
            elif op == '/': return left / right
            elif op == '%': return left % right
            elif op == '<': return left < right
            elif op == '>': return left > right
            elif op == '<=': return left <= right
            elif op == '>=': return left >= right
            elif op == '==': return left == right
            elif op == '!=': return left != right

        if isinstance(node, UnaryOp) and node.op == '-':
            return -self._compute_constant_value(node.body, c)

        return 0