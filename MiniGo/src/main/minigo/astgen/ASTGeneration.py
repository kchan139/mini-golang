from MiniGoVisitor import MiniGoVisitor
from MiniGoParser import MiniGoParser
from AST import *

def castToInt(num_str: str) -> int:
    """
    This method casts INT_LIT string to number
    """
    if num_str.startswith("0x") or num_str.startswith("0X"):
        return int(num_str, 16)
    elif num_str.startswith("0o") or num_str.startswith("0O"):
        return int(num_str, 8)
    elif num_str.startswith("0b") or num_str.startswith("0B"):
        return int(num_str, 2)
    else:
        return int(num_str)


class ASTGeneration(MiniGoVisitor):
    """
    This class implements the visitor pattern for generating an 
    Abstract Syntax Tree (AST) for a MiniGo program.
    """

    # //========== 4. Type and Value ==========//
    def visitPrimitiveType(self, ctx: MiniGoParser.ProgramContext):
        """
        primitiveType
            : INT 
            | FLOAT 
            | BOOLEAN 
            | STRING
            ;
        """
        if ctx.INT():
            return IntType()
        if ctx.FLOAT():
            return FloatType()
        if ctx.BOOLEAN():
            return BoolType()
        if ctx.STRING():
            return StringType()
        else:
            return None
    
    def visitArrayType(self, ctx: MiniGoParser.ArrayTypeContext):
        """
        arrayType
            : arrayAccessList (primitiveType | ID)
            ;
        """
        dimens = self.visit(ctx.arrayAccessList())
        ele_type = None
        if ctx.ID():
            ele_type = Id(ctx.ID().getText())
        else:
            ele_type = self.visit(ctx.primitiveType())
        return ArrayType(dimens, ele_type)
    
    def visitArrayAccessParam(self, ctx: MiniGoParser.ProgramContext):
        """
        arrayAccessParam
            : INT_LIT | ID
            ;
        """
        if ctx.INT_LIT():
            num = castToInt(ctx.INT_LIT().getText())
            return [IntLiteral(num)]
        if ctx.ID():
            return [Id(ctx.ID().getText())]
        else:
            return []
        

    def visitStructType(self, ctx: MiniGoParser.StructTypeContext):
        """
        structType
            : STRUCT LEFT_BRACE manyFieldDecl RIGHT_BRACE
            ;
        """
        field_decls = self.visit(ctx.manyFieldDecl())
        
        elements = []
        methods = []
        
        for field_decl in field_decls:
            if isinstance(field_decl, tuple):
                elements.append((field_decl[0].name, field_decl[1]))
            else:
                methods.append(field_decl)
        
        return StructType("", elements, methods)

    
    def visitManyFieldDecl(self, ctx: MiniGoParser.ProgramContext):
        """
        manyFieldDecl
            : fieldDecl manyFieldDeclTail
            ;
        """
        list_field_decl = [self.visit(ctx.fieldDecl())] + self.visit(ctx.manyFieldDeclTail())
        return list_field_decl
    
    def visitManyFieldDeclTail(self, ctx: MiniGoParser.ProgramContext):
        """
        manyFieldDeclTail
            : fieldDecl manyFieldDeclTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            return [self.visit(ctx.fieldDecl())] + self.visit(ctx.manyFieldDeclTail())
        return []
    
    def visitFieldDecl(self, ctx: MiniGoParser.ProgramContext):
        """
        fieldDecl
            : ID typeSpec optionalSemicolon
            | methodDecl
            ;
        """
        if ctx.ID():
            field_id = Id(ctx.ID().getText())
            field_type = self.visit(ctx.typeSpec())
            return (field_id, field_type)
        if ctx.methodDecl():
            return self.visit(ctx.methodDecl())
        else:
            return None
        
    def visitTypeSpec(self, ctx: MiniGoParser.TypeSpecContext):
        """
        typeSpec
            : primitiveType 
            | arrayType 
            | structType 
            | interfaceType
            | ID
            ;
        """
        if ctx.primitiveType():
            return self.visit(ctx.primitiveType())
        if ctx.arrayType():
            return self.visit(ctx.arrayType())
        if ctx.structType():
            return self.visit(ctx.structType())
        if ctx.interfaceType():
            return self.visit(ctx.interfaceType())
        if ctx.ID():
            return Id(ctx.ID().getText())
        else:
            return None


    def visitOptionalTypeSpec(self, ctx: MiniGoParser.OptionalTypeSpecContext):
        """
        optionalTypeSpec
            : typeSpec | 
            ;
        """
        if ctx.typeSpec():
            return self.visit(ctx.typeSpec())
        else:
            return VoidType()


    def visitInterfaceType(self, ctx: MiniGoParser.InterfaceTypeContext):
        """
        interfaceType
            : INTERFACE LEFT_BRACE manyInterfaceContent RIGHT_BRACE
            ;
        """
        methods = self.visit(ctx.manyInterfaceContent())
        # Filter to include only Prototype objects
        methods = [m for m in methods if isinstance(m, Prototype)]
        return InterfaceType("", methods)


    def visitManyInterfaceContent(self, ctx: MiniGoParser.ManyInterfaceContentContext):
        """
        manyInterfaceContent
            : interfaceContent manyInterfaceContentTail
            ;
        """
        list_interface_content = [self.visit(ctx.interfaceContent())] + self.visit(ctx.manyInterfaceContentTail())
        return list_interface_content


    def visitManyInterfaceContentTail(self, ctx: MiniGoParser.ManyInterfaceContentTailContext):
        """
        manyInterfaceContentTail
            : interfaceContent manyInterfaceContentTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            return [self.visit(ctx.interfaceContent())] + self.visit(ctx.manyInterfaceContentTail())
        return []


    def visitInterfaceContent(self, ctx: MiniGoParser.InterfaceContentContext):
        """
        interfaceContent
            : interfaceMethod | stmt
            ;
        """
        if ctx.interfaceMethod():
            return self.visit(ctx.interfaceMethod())
        if ctx.stmt():
            return self.visit(ctx.stmt())
        else:
            return None



    #========== 5. Variables, Constants and Functions ==========
    
    def visitBlock(self, ctx: MiniGoParser.BlockContext):
        """
        block
            : LEFT_BRACE manyBlockContent RIGHT_BRACE optionalSemicolon
            ;
        """
        return Block(self.visit(ctx.manyBlockContent()))

    
    def visitManyBlockContent(self, ctx: MiniGoParser.ManyBlockContentContext):
        """
        manyBlockContent
            : blockContent manyBlockContentTail
            ;
        """
        list_block_content = [self.visit(ctx.blockContent())] + self.visit(ctx.manyBlockContentTail())
        return list_block_content

    
    def visitManyBlockContentTail(self, ctx: MiniGoParser.ManyBlockContentTailContext):
        """
        manyBlockContentTail
            : blockContent manyBlockContentTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            return [self.visit(ctx.blockContent())] + self.visit(ctx.manyBlockContentTail())
        return []

    
    def visitBlockContent(self, ctx: MiniGoParser.BlockContentContext):
        """
        blockContent
            : stmt | block
            ;
        """
        if ctx.stmt():
            return self.visit(ctx.stmt())
        if ctx.block():
            return self.visit(ctx.block())
        else:
            return None

    
    def visitVarDecl(self, ctx: MiniGoParser.VarDeclContext):
        """
        varDecl
            : VAR ID typeSpec ASSIGN expr SEMICOLON - 1
            | VAR ID ASSIGN expr SEMICOLON          - 2
            | VAR ID typeSpec SEMICOLON             - 3
            ;
        """
        var_id = ctx.ID().getText()
        var_type = None
        var_expr = None
        if ctx.typeSpec():
            var_type = self.visit(ctx.typeSpec())
        if ctx.expr():
            var_expr = self.visit(ctx.expr())
        
        return VarDecl(var_id,var_type, var_expr)

    
    def visitConstDecl(self, ctx: MiniGoParser.ConstDeclContext):
        """
        constDecl
            : CONST ID ASSIGN expr SEMICOLON
            ;
        """
        const_id = ctx.ID().getText()
        const_type = None
        const_expr = self.visit(ctx.expr())
        
        return ConstDecl(const_id, const_type, const_expr)

    
    def visitFuncDecl(self, ctx: MiniGoParser.FuncDeclContext):
        """
        funcDecl
            : FUNC ID LEFT_PAREN paramList RIGHT_PAREN optionalTypeSpec block SEMICOLON
            ;
        """
        func_id = ctx.ID().getText()
        func_paramlist = self.visit(ctx.paramList())
        func_type = self.visit(ctx.optionalTypeSpec())
        func_body = self.visit(ctx.block())
        return FuncDecl(func_id, func_paramlist, func_type, func_body)

    
    def visitMethodDecl(self, ctx: MiniGoParser.MethodDeclContext):
        """
        methodDecl
            : FUNC LEFT_PAREN ID ID RIGHT_PAREN ID LEFT_PAREN paramList RIGHT_PAREN optionalTypeSpec block SEMICOLON
            ;
        """
        receiver_id = ctx.ID(0).getText()
        receiver_type = Id(ctx.ID(1).getText())
        method_id = ctx.ID(2).getText()
        method_paramlist = self.visit(ctx.paramList())
        method_type = self.visit(ctx.optionalTypeSpec())
        method_body = self.visit(ctx.block())

        return MethodDecl(
            receiver_id, 
            receiver_type, 
            FuncDecl(method_id, method_paramlist, method_type, method_body)
        )

    
    def visitTypeDecl(self, ctx: MiniGoParser.TypeDeclContext):
        """
        typeDecl
            : TYPE ID typeSpec SEMICOLON
            ;
        """
        type_name = ctx.ID().getText()
        type_spec = self.visit(ctx.typeSpec())
        
        if isinstance(type_spec, StructType) or isinstance(type_spec, InterfaceType):
            type_spec.name = type_name
            return type_spec
        else:
            return type_spec

    
    def visitInterfaceMethod(self, ctx: MiniGoParser.InterfaceMethodContext):
        """
        interfaceMethod
            : ID LEFT_PAREN paramList RIGHT_PAREN optionalTypeSpec SEMICOLON
            ;
        """
        method_name = ctx.ID().getText()
        param_decls = self.visit(ctx.paramList())
        return_type = self.visit(ctx.optionalTypeSpec())
        
        # Extract parameter types from the parameter declarations
        param_types = [param.parType for param in param_decls]
        
        # Return a Prototype representing this interface method
        return Prototype(method_name, param_types, return_type)

    
    def visitParamList(self, ctx: MiniGoParser.ParamListContext):
        """
        paramList
            : param paramListTail |
            ;
        """
        if ctx.getChildCount() > 0:
            list_param = [self.visit(ctx.param())] + self.visit(ctx.paramListTail())
            return [i for j in list_param for i in j]
        else:
            return []

    
    def visitParamListTail(self, ctx: MiniGoParser.ParamListTailContext):
        """
        paramListTail
            : COMMA param paramListTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            return [self.visit(ctx.param())] + self.visit(ctx.paramListTail())
        return []

    
    def visitParam(self, ctx: MiniGoParser.ParamContext):
        """
        param
            : idList typeSpec
            ;
        """
        param_id_list = self.visit(ctx.idList())
        param_type = self.visit(ctx.typeSpec())
        return [ParamDecl(param_id, param_type) for param_id in param_id_list]

    
    def visitIdList(self, ctx: MiniGoParser.IdListContext):
        """
        idList
            : ID idListTail
            ;
        """
        list_id = [ctx.ID().getText()] + self.visit(ctx.idListTail())
        return list_id

    
    def visitIdListTail(self, ctx: MiniGoParser.IdListTailContext):
        """
        idListTail
            : COMMA ID idListTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            return [ctx.ID().getText()] + self.visit(ctx.idListTail())
        return []



    #========== 6. Expressions ==========
    
    def visitExpr(self, ctx: MiniGoParser.ExprContext):
        """
        expr
            : expr OR expr1 
            | expr1
            ;
        """
        if ctx.OR():
            or_op = ctx.OR().getText()
            left = self.visit(ctx.expr())
            right = self.visit(ctx.expr1())
            return BinaryOp(or_op, left, right)
        else:
            return self.visit(ctx.expr1()) 

    
    def visitExpr1(self, ctx: MiniGoParser.Expr1Context):
        """
        expr1
            : expr1 AND expr2 
            | expr2
            ;
        """
        if ctx.AND():
            and_op = ctx.AND().getText()
            left = self.visit(ctx.expr1())
            right = self.visit(ctx.expr2())
            return BinaryOp(and_op, left, right)
        else:
            return self.visit(ctx.expr2())

    
    def visitExpr2(self, ctx: MiniGoParser.Expr2Context):
        """
        expr2
            : expr2 (EQUAL | NOT_EQUAL | LESS | LESS_EQUAL | GREATER | GREATER_EQUAL) expr3 
            | expr3
            ;
        """
        if ctx.getChildCount() > 1:
            op = ctx.getChild(1).getText()
            left = self.visit(ctx.expr2())
            right = self.visit(ctx.expr3())
            return BinaryOp(op, left, right)
        else:
            return self.visit(ctx.expr3())

    
    def visitExpr3(self, ctx: MiniGoParser.Expr3Context):
        """
        expr3
            : expr3 (PLUS | MINUS) expr4 
            | expr4
            ;
        """
        if ctx.getChildCount() > 1:
            op = ctx.getChild(1).getText()
            left = self.visit(ctx.expr3())
            right = self.visit(ctx.expr4())
            return BinaryOp(op, left, right)
        else:
            return self.visit(ctx.expr4())

    
    def visitExpr4(self, ctx: MiniGoParser.Expr4Context):
        """
        expr4
            : expr4 (MULT | DIV | MOD) expr5 
            | expr5
            ;
        """
        if ctx.getChildCount() > 1:
            op = ctx.getChild(1).getText()
            left = self.visit(ctx.expr4())
            right = self.visit(ctx.expr5())
            return BinaryOp(op, left, right)
        else:
            return self.visit(ctx.expr5())

    
    def visitExpr5(self, ctx: MiniGoParser.Expr5Context):
        """
        expr5
            : unaryOperator expr5 
            | expr6
            ;
        """
        if ctx.getChildCount() > 1:
            un_op = self.visit(ctx.unaryOperator())
            un_body = self.visit(ctx.expr5())
            return UnaryOp(un_op, un_body)
        if ctx.expr6():
            return self.visit(ctx.expr6())
        else:
            return None

    
    def visitUnaryOperator(self, ctx: MiniGoParser.UnaryOperatorContext):
        """
        unaryOperator
            : MINUS 
            | NOT
            ;
        """
        if ctx.MINUS():
            return ctx.MINUS().getText()
        if ctx.NOT():
            return ctx.NOT().getText()
        else:
            return None

    
    def visitExpr6(self, ctx: MiniGoParser.Expr6Context):
        """
        expr6
            : expr6 (
                DOT (ID | funcCall) 
                | LEFT_BRACKET expr RIGHT_BRACKET
                | LEFT_BRACE expr RIGHT_BRACE
            )
            | expr7
            ;
        """
        if ctx.getChildCount() > 1:
            obj = self.visit(ctx.expr6())
            
            if ctx.DOT():
                # If there's a DOT, check if ID or funcCall follows
                if ctx.ID():
                    field_id = ctx.ID().getText()
                    return FieldAccess(obj, field_id)
                elif ctx.funcCall():
                    # Handle method call properly
                    func_ctx = ctx.funcCall()
                    func_id = func_ctx.ID().getText()
                    func_args = self.visit(func_ctx.exprList())
                    return MethCall(obj, func_id, func_args)
            elif ctx.LEFT_BRACKET():
                arr_idx = self.visit(ctx.expr())
                if isinstance(obj, ArrayCell):
                    # Fix: append to list instead of adding IntLiterals
                    return ArrayCell(obj.arr, obj.idx + [arr_idx])
                else:
                    return ArrayCell(obj, [arr_idx])
            elif ctx.LEFT_BRACE():
                return self.visit(ctx.expr())
        if ctx.expr7():
            return self.visit(ctx.expr7())
        else:
            return None

    
    def visitExpr7(self, ctx: MiniGoParser.Expr7Context):
        """
        expr7
            : ID 
            | literal 
            | LEFT_PAREN expr RIGHT_PAREN 
            | funcCall
            ;
        """
        if ctx.ID():
            return Id(ctx.ID().getText())
        if ctx.literal():
            return self.visit(ctx.literal())
        if ctx.expr():
            return self.visit(ctx.expr())
        if ctx.funcCall():
            return self.visit(ctx.funcCall())
        else:
            return None

    
    def visitLiteral(self, ctx: MiniGoParser.LiteralContext):
        """
        literal
            : INT_LIT 
            | FLOAT_LIT 
            | STRING_LIT 
            | BOOL_LIT 
            | NIL 
            | arrayLit 
            | structLit
            ;
        """
        if ctx.INT_LIT():
            num = castToInt(ctx.INT_LIT().getText())
            return IntLiteral(num)
        if ctx.FLOAT_LIT():
            return FloatLiteral(float(ctx.FLOAT_LIT().getText()))
        if ctx.STRING_LIT():
            return StringLiteral(ctx.STRING_LIT().getText())
        if ctx.BOOL_LIT():
            return BooleanLiteral(ctx.BOOL_LIT().getText().capitalize())
        if ctx.NIL():
            return NilLiteral()
        if ctx.arrayLit():
            return self.visit(ctx.arrayLit())
        if ctx.structLit():
            return self.visit(ctx.structLit())

    
    def visitArrayLit(self, ctx: MiniGoParser.ArrayLitContext):
        """
        arrayLit
            : arrayAccessList (primitiveType | ID) LEFT_BRACE arrayElementListList RIGHT_BRACE
            ;
        """
        arr_dim = self.visit(ctx.arrayAccessList())
        arr_type = None
        if ctx.ID():
            arr_type = Id(ctx.ID().getText())
        else:
            arr_type = self.visit(ctx.primitiveType())
        arr_val = self.visit(ctx.arrayElementListList())
        return ArrayLiteral(arr_dim, arr_type, arr_val)

    def visitArrayAccessList(self, ctx: MiniGoParser.ArrayElementListListContext):
        """arrayAccessList
            : LEFT_BRACKET arrayAccessParam RIGHT_BRACKET arrayAccessListTail
            ;
        """
        list_arr_access = [self.visit(ctx.arrayAccessParam())] + self.visit(ctx.arrayAccessListTail())
        return [i for j in list_arr_access for i in j]

    def visitArrayAccessListTail(self, ctx: MiniGoParser.ArrayElementListListContext):
        """
        arrayAccessListTail
            : LEFT_BRACKET arrayAccessParam RIGHT_BRACKET arrayAccessListTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            return [self.visit(ctx.arrayAccessParam())] + self.visit(ctx.arrayAccessListTail())
        return []

    
    def visitArrayElementListList(self, ctx: MiniGoParser.ArrayElementListListContext):
        """
        arrayElementListList
            : arrayElementList arrayElementListListTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            list_list_arr_elem = [self.visit(ctx.arrayElementList())] + self.visit(ctx.arrayElementListListTail())
            return [i for j in list_list_arr_elem for i in j]
        else:
            return []

    
    def visitArrayElementListListTail(self, ctx: MiniGoParser.ArrayElementListListTailContext):
        """
        arrayElementListListTail
            : COMMA arrayElementList arrayElementListListTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            return [self.visit(ctx.arrayElementList())] + self.visit(ctx.arrayElementListListTail())
        return []

    
    def visitArrayElementList(self, ctx: MiniGoParser.ArrayElementListContext):
        """
        arrayElementList
            : arrayElement arrayElementListTail
            ;
        """
        list_arr_elem = [self.visit(ctx.arrayElement())] + self.visit(ctx.arrayElementListTail())
        return list_arr_elem

    
    def visitArrayElementListTail(self, ctx: MiniGoParser.ArrayElementListTailContext):
        """
        arrayElementListTail
            : COMMA arrayElement arrayElementListTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            return [self.visit(ctx.arrayElement())] + self.visit(ctx.arrayElementListTail())
        return []

    
    def visitArrayElement(self, ctx: MiniGoParser.ArrayElementContext):
        """
        arrayElement
            : INT_LIT | FLOAT_LIT | STRING_LIT | BOOL_LIT | NIL | ID
            | LEFT_BRACE arrayElementList RIGHT_BRACE
            | ID LEFT_BRACE structMemberList RIGHT_BRACE
            ;
        """
        if ctx.INT_LIT():
            num = castToInt(ctx.INT_LIT().getText())
            return IntLiteral(num)
        if ctx.FLOAT_LIT():
            return FloatLiteral(float(ctx.FLOAT_LIT().getText()))
        if ctx.STRING_LIT():
            return StringLiteral(ctx.STRING_LIT().getText()[1:-1])
        if ctx.BOOL_LIT():
            return BooleanLiteral(ctx.BOOL_LIT().getText().capitalize())
        if ctx.NIL():
            return NilLiteral()
        if ctx.ID() and not ctx.LEFT_BRACE():
            return Id(ctx.ID().getText())
        if not ctx.ID() and ctx.LEFT_BRACE():
            return self.visit(ctx.arrayElementList())
        if ctx.ID() and ctx.LEFT_BRACE():
            struct_id = ctx.ID().getText()
            struct_elem = self.visit(ctx.structMemberList())
            return StructLiteral(struct_id, struct_elem)
        else:
            return None
        
    
    def visitStructLit(self, ctx: MiniGoParser.StructLitContext):
        """
        structLit
            : ID LEFT_BRACE structMemberList RIGHT_BRACE
            ;
        """
        struct_id = ctx.ID().getText()
        struct_elem = self.visit(ctx.structMemberList())
        return StructLiteral(struct_id, struct_elem)

    
    def visitStructMemberList(self, ctx: MiniGoParser.StructMemberListContext):
        """
        structMemberList
            : structMember structMemberListTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            list_struct_mem = [self.visit(ctx.structMember())] + self.visit(ctx.structMemberListTail())
            return [i for j in list_struct_mem for i in j]
        else:
            return []

    
    def visitStructMemberListTail(self, ctx: MiniGoParser.StructMemberListTailContext):
        """
        structMemberListTail
            : COMMA structMember structMemberListTail |
            ;
        """
        if ctx.getChildCount() > 0:
            return [self.visit(ctx.structMember())] + self.visit(ctx.structMemberListTail())
        return []

    
    def visitStructMember(self, ctx: MiniGoParser.StructMemberContext):
        """
        structMember
            : ID COLON expr
            ;
        """
        field_id = ctx.ID().getText()
        field_val = self.visit(ctx.expr())
        return [(field_id, field_val)]
    
    def visitFuncCall(self, ctx: MiniGoParser.FuncCallContext):
        """
        funcCall
            : ID LEFT_PAREN exprList RIGHT_PAREN optionalSemicolon
            ;
        """
        func_id = ctx.ID().getText()
        func_expr_list = self.visit(ctx.exprList())
        return FuncCall(func_id,func_expr_list)

    
    def visitMethodCall(self, ctx: MiniGoParser.MethodCallContext):
        """
        methodCall
            : ID DOT (expr | assignStmt) optionalSemicolon
            ;
        """
        receiver = Id(ctx.ID().getText())
        
        if ctx.expr():
            expression = self.visit(ctx.expr())
            if isinstance(expression, FuncCall):
                method_name = expression.funName
                args = expression.args
                return MethCall(receiver, method_name, args)
            else:
                return FieldAccess(receiver, str(expression))
        else:
            return self.visit(ctx.assignStmt())
        
    
    def visitExprList(self, ctx: MiniGoParser.ExprListContext):
        """
        exprList
            : expr exprListTail | 
            ;
        """
        if ctx.getChildCount() > 0:
            expr_list = [self.visit(ctx.expr())]
            tail_list = self.visit(ctx.exprListTail())
            return expr_list + tail_list
        else:
            return []

    def visitExprListTail(self, ctx: MiniGoParser.ExprListTailContext):
        """
        exprListTail
            : COMMA expr exprListTail |
            ;
        """
        if ctx.getChildCount() > 0:
            expr_list = [self.visit(ctx.expr())]
            tail_list = self.visit(ctx.exprListTail())
            return expr_list + tail_list
        return []


    #========== 7. Variable, Constant Declaration Statement ==========
    
    def visitStmt(self, ctx: MiniGoParser.StmtContext):
        """
        stmt
            : decl
            | assignStmt
            | ifStmt
            | forStmt
            | breakStmt
            | continueStmt
            | callStmt
            | returnStmt
            ;
        """
        if ctx.decl():
            return self.visit(ctx.decl())
        if ctx.assignStmt():
            return self.visit(ctx.assignStmt())
        if ctx.ifStmt():
            return self.visit(ctx.ifStmt())
        if ctx.forStmt():
            return self.visit(ctx.forStmt())
        if ctx.breakStmt():
            return self.visit(ctx.breakStmt())
        if ctx.continueStmt():
            return self.visit(ctx.continueStmt())
        if ctx.callStmt():
            return self.visit(ctx.callStmt())
        if ctx.returnStmt():
            return self.visit(ctx.returnStmt())
        else:
            return None

    
    def visitAssignStmt(self, ctx: MiniGoParser.AssignStmtContext):
        """
        assignStmt
            : lhs (COLON_ASSIGN | PLUS_ASSIGN | MINUS_ASSIGN | MULT_ASSIGN | DIV_ASSIGN | MOD_ASSIGN) expr optionalSemicolon
            ;
        """
        lhs = self.visit(ctx.lhs())
        assign_op = ctx.getChild(1).getText()
        assigned_expr = self.visit(ctx.expr())

        if assign_op != '=' and assign_op != ':=':
            assigned_expr = BinaryOp(assign_op[:-1], lhs, assigned_expr)
            
        return Assign(lhs, assigned_expr)

    
    def visitLhs(self, ctx: MiniGoParser.LhsContext):
        """
        lhs
            : ID
            | arrayAccess
            | fieldAccess
            | lhs DOT ID
            | lhs DOT arrayAccess
            | lhs DOT fieldAccess
            ;
        """
        if ctx.ID() and ctx.getChildCount() == 1:
            return Id(ctx.ID().getText())
        if ctx.arrayAccess() and ctx.getChildCount() == 1:
            return self.visit(ctx.arrayAccess())
        if ctx.fieldAccess() and ctx.getChildCount() == 1:
            return self.visit(ctx.fieldAccess())
        
        if ctx.lhs():
            lhs_obj = self.visit(ctx.lhs())
            
            if ctx.ID():
                field_name = ctx.ID().getText()
                return FieldAccess(lhs_obj, field_name)
            
            elif ctx.arrayAccess():
                array_access = self.visit(ctx.arrayAccess())
                if isinstance(array_access, ArrayCell):
                    return ArrayCell(
                        FieldAccess(
                            lhs_obj, 
                            array_access.arr.name if isinstance(array_access.arr, Id) else "array"
                        ), 
                        array_access.idx
                    )
            
            elif ctx.fieldAccess():
                field_access = self.visit(ctx.fieldAccess())
                return FieldAccess(
                    FieldAccess(
                        lhs_obj, 
                        field_access.receiver.name if isinstance(field_access.receiver, Id) else "field"
                    ),
                    field_access.field
                )
        
        return None


    
    def visitArrayAccess(self, ctx: MiniGoParser.ArrayAccessContext):
        """
        arrayAccess
            : ID arrayDim
            ;
        """
        arr_id = Id(ctx.ID().getText())
        arr_dim = self.visit(ctx.arrayDim())
        
        return ArrayCell(arr_id, arr_dim)


    def visitArrayDim(self, ctx: MiniGoParser.ArrayDimContext):
        """
        arrayDim
            : arrayDim LEFT_BRACKET expr RIGHT_BRACKET
            | LEFT_BRACKET expr RIGHT_BRACKET
            ;
        """
        if ctx.arrayDim():
            prev_dims = self.visit(ctx.arrayDim())
            curr_expr = self.visit(ctx.expr())
            return prev_dims + [curr_expr]
        else:
            return [self.visit(ctx.expr())]


    def visitFieldAccess(self, ctx: MiniGoParser.FieldAccessContext):
        """
        fieldAccess
            : ID DOT ID fieldAccess
            | dim
            ;
        """
        if ctx.ID():
            base_obj = Id(ctx.ID(0).getText())
            field_name = ctx.ID(1).getText()
            field_access = FieldAccess(base_obj, field_name)
            
            if ctx.fieldAccess():
                further_access = self.visit(ctx.fieldAccess())
                
                if isinstance(further_access, IntLiteral):
                    return ArrayCell(field_access, [further_access])
                elif isinstance(further_access, FieldAccess):
                    return FieldAccess(field_access, further_access.field)
                else:
                    return FieldAccess(field_access, str(further_access))
            
            return field_access
        if ctx.dim():
            return self.visit(ctx.dim())
        else:
            return None


    def visitDim(self, ctx: MiniGoParser.DimContext):
        """
        dim
            : LEFT_BRACKET INT_LIT RIGHT_BRACKET
            ;
        """
        int_lit_text = ctx.INT_LIT().getText()
        int_value = castToInt(int_lit_text)
        
        return IntLiteral(int_value)

    
    def visitIfStmt(self, ctx: MiniGoParser.IfStmtContext):
        """
        ifStmt
            : IF LEFT_PAREN expr RIGHT_PAREN ifElseBlock optionalElseBlock
            ;
        """
        condition = self.visit(ctx.expr())
        then_stmt = self.visit(ctx.ifElseBlock())
        else_stmt = self.visit(ctx.optionalElseBlock())
        
        return If(condition, then_stmt, else_stmt)


    def visitIfElseBlock(self, ctx: MiniGoParser.IfElseBlockContext):
        """
        ifElseBlock
            : block | ifStmt
            ;
        """
        if ctx.block():
            return self.visit(ctx.block())
        if ctx.ifStmt():
            return self.visit(ctx.ifStmt())
        else:
            return None


    def visitOptionalElseBlock(self, ctx: MiniGoParser.OptionalElseBlockContext):
        """
        optionalElseBlock
            : ELSE ifElseBlock |
            ;
        """
        if ctx.getChildCount() > 0:
            return self.visit(ctx.ifElseBlock())
        else:
            return None


    def visitForStmt(self, ctx: MiniGoParser.ForStmtContext):
        """
        forStmt
            : FOR (forClause | rangeClause) block
            ;
        """
        loop_body = self.visit(ctx.block())
        
        if ctx.forClause():
            for_clause_result = self.visit(ctx.forClause())
            
            if isinstance(for_clause_result, tuple):
                init, cond, update = for_clause_result
                return ForStep(init, cond, update, loop_body)
            else:
                return ForBasic(for_clause_result, loop_body)
                
        else:
            range_clause_result = self.visit(ctx.rangeClause())
            
            if isinstance(range_clause_result, tuple):
                idx, val, arr = range_clause_result
                return ForEach(idx, val, arr, loop_body)
            else:
                return ForBasic(range_clause_result, loop_body)


    def visitForClause(self, ctx: MiniGoParser.ForClauseContext):
        """
        forClause
            : (assignStmt | varDecl)? expr? SEMICOLON assignStmt?
            ;
        """
        init_stmt = None
        condition = None
        update_stmt = None
        
        if ctx.assignStmt() and ctx.getChild(0) == ctx.assignStmt(0):
            init_stmt = self.visit(ctx.assignStmt(0))
        elif ctx.varDecl():
            init_stmt = self.visit(ctx.varDecl())
        
        # Check for condition expression
        if ctx.expr():
            condition = self.visit(ctx.expr())
        else:
            condition = BooleanLiteral(True)
            
        for i in range(ctx.getChildCount()):
            if ctx.getChild(i) == ctx.SEMICOLON() and i+1 < ctx.getChildCount():
                for j in range(i+1, ctx.getChildCount()):
                    if ctx.getChild(j) == ctx.assignStmt(0) or (
                        ctx.assignStmt(1) and ctx.getChild(j) == ctx.assignStmt(1)
                    ):
                        update_idx = 1 if ctx.assignStmt(1) and ctx.getChild(j) == ctx.assignStmt(1) else 0
                        update_stmt = self.visit(ctx.assignStmt(update_idx))
                        break
        
        if init_stmt is not None or update_stmt is not None:
            return (init_stmt, condition, update_stmt)
        
        return condition


    def visitRangeClause(self, ctx: MiniGoParser.RangeClauseContext):
        """
        rangeClause
            : ID COMMA ID COLON_ASSIGN RANGE expr 
            | expr
            ;
        """
        if ctx.COMMA():
            idx_id = Id(ctx.ID(0).getText())
            val_id = Id(ctx.ID(1).getText())
            array_expr = self.visit(ctx.expr())
            return (idx_id, val_id, array_expr)
        
        if ctx.expr():
            return self.visit(ctx.expr())
        else:
            return None
    
    def visitBreakStmt(self, ctx: MiniGoParser.BreakStmtContext):
        """
        breakStmt
            : BREAK SEMICOLON
            ;
        """
        return Break()

    
    def visitContinueStmt(self, ctx: MiniGoParser.ContinueStmtContext):
        """
        continueStmt
            : CONTINUE SEMICOLON
            ;
        """
        return Continue()

    
    def visitReturnStmt(self, ctx: MiniGoParser.ReturnStmtContext):
        """
        returnStmt
            : RETURN expr? SEMICOLON
            ;
        """
        return_expr = None
        if ctx.expr():
            return_expr = self.visit(ctx.expr())
            
        return Return(return_expr)

    
    def visitCallStmt(self, ctx: MiniGoParser.CallStmtContext):
        """
        callStmt
            : expr SEMICOLON
            ;
        """
        return self.visit(ctx.expr())


    
    # //========== TOP-LEVEL DECLARATIONS ==========//
    def visitProgram(self, ctx: MiniGoParser.ProgramContext):
        """
        program
            : decl_stmt+ EOF
            ;
        """
        list_decl_stmt = [self.visit(i) for i in ctx.decl_stmt()]
        return Program(list_decl_stmt)
    
    def visitDecl_stmt(self, ctx: MiniGoParser.Decl_stmtContext):
        """
        decl_stmt
            : decl | stmt
            ;
        """
        if ctx.decl():
            return self.visit(ctx.decl())
        if ctx.stmt():
            return self.visit(ctx.stmt())
        else:
            return None

    def visitDecl(self, ctx: MiniGoParser.DeclContext):
        """
        decl
            : constDecl 
            | varDecl 
            | typeDecl 
            | funcDecl 
            | methodDecl
            | mainFunction
            ;
        """
        if ctx.constDecl():
            return self.visit(ctx.constDecl())
        if ctx.varDecl():
            return self.visit(ctx.varDecl())
        if ctx.typeDecl():
            return self.visit(ctx.typeDecl())
        if ctx.funcDecl():
            return self.visit(ctx.funcDecl())
        if ctx.methodDecl():
            return self.visit(ctx.methodDecl())
        return self.visit(ctx.mainFunction())
    
    def visitMainFunction(self, ctx: MiniGoParser.MainFunctionContext):
        """
        mainFunction
            : FUNC 'main' LEFT_PAREN RIGHT_PAREN block
            ;
        """
        main_id = 'main'
        main_paramlist = []
        main_type = VoidType()
        main_body = self.visit(ctx.block())
        
        return FuncDecl(main_id, main_paramlist, main_type, main_body)