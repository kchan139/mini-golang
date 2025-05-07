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
        # 
        self.className = "MiniGoClass" # Tên class tổng của chương trình minigo
        self.astTree = None
        self.path = None
        self.emit = None
        self.function = None
        self.list_function = []
        self.arrayCell = None # Dùng để lưu kiểu của mảng khi duyệt vào 1 ArrayCell
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
        # Nơi được gọi để khởi tạo classCodeGen và bắt đầu sinh mã !!!
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
        self.emit.printout(self.emit.emitMETHOD("<init>", MType([], VoidType()), False, frame))  # Bắt đầu định nghĩa phương thức <init>
        # sinh ra mã => .method public <init>()V
        frame.enterScope(True)  # Mỗi hàm có 1 frame riêng, và mỗi frame có 1 scope riêng, nên dùng enterScope để vào scope của frame này

        # self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), "this", ClassType(self.className), frame.getStartLabel(), frame.getEndLabel(), frame))  # Tạo biến "this" trong phương thức <init>
        # sinh ra mã => .var 0 is this LMiniGoClass; from Label0 to Label1
        self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), "this", f"L{self.className};", frame.getStartLabel(), frame.getEndLabel(), frame))

        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))
        # sinh ra mã => Label0: (nơi body method bắt đầu)

        self.emit.printout(self.emit.emitREADVAR("this", ClassType(self.className), 0, frame)) 
        # sinh ra mã => aload_0 (đưa biến this vào stack)

        self.emit.printout(self.emit.emitINVOKESPECIAL(frame))
        # sinh ra mã => invokespecial java/lang/Object/<init>()V (gọi hàm khởi tạo của class cha là Object)  
     
        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        # sinh ra mã => Label1: (nơi body method kết thúc)


        self.emit.printout(self.emit.emitRETURN(VoidType(), frame))  
        # sinh ra mã => return (trả về từ hàm khởi tạo này)

        self.emit.printout(self.emit.emitENDMETHOD(frame))  
        # sinh ra mã limit stack 1, limit locals 1, end method (kết thúc định nghĩa phương thức <init>)

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

        # frame = Frame("<cinit>", VoidType())  
        # self.emit.printout(self.emit.emitMETHOD("<clinit>", MType([], VoidType()), True, frame)) 
        # frame.enterScope(True)  
        # self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))

        # env['frame'] = frame

        # #Trừ đoạn code dưới đây thì còn lại giống emitObjectInit:
        # self.visit(Block([
        #     #  Assign(#TODO ...) for item in ast.decl if isinstance(item, (VarDecl, ConstDecl))       => Block chứa danh sách các Assign
        # ]), env)
        # # Đoạn này nạp mấy biến/hằng toàn cục vào lớp MiniGoClass

        # self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        # self.emit.printout(self.emit.emitRETURN(VoidType(), frame))  
        # self.emit.printout(self.emit.emitENDMETHOD(frame))  
        # frame.exitScope()

    def visitProgram(self, ast: Program, c):
        # Biến c ban đầu là dãy Symbol "mem" ở hàm init() ở trên, chứa các hàm builtin của minigo.

        self.list_function = c + [Symbol(item.name, MType(list(map(lambda x: x.parType, item.params)), item.retType), CName(self.className)) for item in ast.decl if isinstance(item, FuncDecl)]
        # Đoạn này nạp mấy hàm vào list_function, biến tụi nó thành Symbol để quản lí
        
        env = {}
        env['env'] = [c]


        self.emit.printout(self.emit.emitPROLOG(self.className, "java.lang.Object"))
        # sinh ra mã => .source MiniGoClass.java
        #               .class public MiniGoClass
        #               .super java.lang.Object


        # Đoạn sau sinh mã cho khai báo biến và khai báo báo hàm:
        ## 1. Khai báo biến (duyệt trước vì hàm có thể dùng biến toàn cục, cập nhật biến/hằng toàn cục vào env)
        env = reduce(lambda a, x: self.visit(x, a) if isinstance(x, VarDecl) or  isinstance(x, ConstDecl) else a, ast.decl, env)

        ## 2. Khai báo hàm (gọi hàm visitFuncDecl cho từng hàm trong danh sách hàm trong ast.decl)
        reduce(lambda a, x: self.visit(x, a) if isinstance(x, FuncDecl) else a, ast.decl, env)



        # Gọi mấy hàm đã định nghĩa ở trên
        self.emitObjectInit()
        self.emitObjectCInit(ast, env)


        self.emit.printout(self.emit.emitEPILOG())
        #Không sinh ra mã gì cả, chỉ là kết thúc chương trình thôi


        return env
    
    def visitFuncDecl(self, ast: FuncCall, o: dict) -> dict:

        #Lưu function đang duyệt vào biến self.function để dùng sau
        self.function = ast

        frame = Frame(ast.name, ast.retType)

        #Với hàm main thì có params và return cố định như bên dưới, này được định nghĩa trong spec:
        isMain = ast.name == "main"
        if isMain:
            mtype = MType([ArrayType([None],StringType())], VoidType())
            ast.body = Block([] + ast.body.member)
        else:
            mtype = MType(list(map(lambda x: x.parType, ast.params)), ast.retType)
        

        env = o.copy()
        env['frame'] = frame
        self.emit.printout(self.emit.emitMETHOD(ast.name, mtype,True, frame))
        # sinh ra mã => .method public static main([Ljava/lang/String;)V đối với hàm main

        # Tiếp theo nhảy vào body hàm:
        frame.enterScope(True)
        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))
        env['env'] = [[]] + env['env']
        # Lưu ý: mình đang dùng field env của env để lưu reference.

        # Sinh mã VAR tùy vào hàm có phải main hay không, đồng thời cũng cập nhật biến env['env'] với các tham số của hàm:
        if isMain:
            self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), "args", ArrayType([None],StringType()), frame.getStartLabel(), frame.getEndLabel(), frame))
        else:
            env = reduce(lambda acc,e: self.visit(e,acc),ast.params,env)

        #Gọi hàm visitBlock, truyền env đã được cập nhật scope params.
        self.visit(ast.body,env)


        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))


        if type(ast.retType) is VoidType:
            self.emit.printout(self.emit.emitRETURN(VoidType(), frame)) 
        #Nếu trả về kiểu khác void thì hàm visitBlock đã sinh mã cho return rồi.

        self.emit.printout(self.emit.emitENDMETHOD(frame))


        frame.exitScope()
        # Kết thúc thân hàm


        return o

    def visitParamDecl(self, ast: ParamDecl, o: dict) -> dict:
        frame = o['frame']
        index = frame.getNewIndex()
        o['env'][0].append(Symbol(ast.parName, ast.parType, Index(index)))
        self.emit.printout(self.emit.emitVAR(index, ast.parName, ast.parType, frame.getStartLabel() ,frame.getEndLabel(), frame))     
        return o

    def visitVarDecl(self, ast: VarDecl, o: dict) -> dict:
        

        def create_init(varType: Type, o: dict):
            if type(varType) is IntType:
                return IntLiteral(0)
            elif type(varType) is FloatType:
                return FloatLiteral(0.0)
            elif type(varType) is StringType:
                return StringLiteral("\"\"")
            elif type(varType) is BoolType:
                return BooleanLiteral("false")
            elif type(varType) is ArrayType:
                # Not implementing array for level 1
                pass


        varInit = ast.varInit # Giá trị khởi tạo của biến
        varType = ast.varType # Kiểu của biến

        #Nếu không có giá trị khởi tạo thì tự động gán cho nó 0, 0.0, false, "",..tùy vào kiểu biến:
        # int -> 0, float -> 0.0, bool -> false, string -> "", array -> mảng chứa các giá trị "zero" tùy thuộc vào kiểu phần tử.
        if not varInit:
            varInit = create_init(varType, o)
            if type(varType) is ArrayType:
                varInit = ArrayLiteral(varType.dimens, varType.dimens, varInit)
            ast.varInit = varInit


            ast.varInit = varInit
        env = o.copy()
        env['frame'] = Frame("<template_VT>", VoidType()) 

        # Như đã nói trong lưu ý ở trên thì trường hợp dimension là Id hay biểu thức sẽ đc xử lí ở visitArrayLiteral và là dòng dưới đây
        rhsCode, rhsType = self.visit(varInit, env)

        #Trường hợp khai báo với giá trị nhưng không có kiẻu thì mình sẽ tự động gán kiểu cho nó dựa vào giá trị khởi tạo.
        if not varType:
            varType = rhsType

        if 'frame' not in o: # TH global var => biến khai báo toàn cục thì mình
            o['env'][0].append(Symbol(ast.varName, varType, CName(self.className)))
            self.emit.printout(self.emit.emitATTRIBUTE(ast.varName, varType, True, False, None))
        else:
            frame = o['frame']

            index = frame.getNewIndex()
            o['env'][0].append(Symbol(ast.varName, varType, Index(index))) # mỗi trường sẽ có 1 index riêng


            self.emit.printout(self.emit.emitVAR(index, ast.varName, varType, frame.getStartLabel(), frame.getEndLabel(), frame))  
            rhsCode, rhsType = self.visit(varInit, o)
            if type(varType) is FloatType and type(rhsType) is IntType:
                rhsCode = rhsCode + self.emit.emitI2F(frame)
                  
            self.emit.printout(rhsCode)
            self.emit.printout(self.emit.emitWRITEVAR(ast.varName, varType, index, frame)) # sinh mã gán giá trị vào biến                   
        return o
    
    def visitFuncCall(self, ast: FuncCall, o: dict) -> dict:
        sym = next(filter(lambda x: x.name == ast.funName, self.list_function), None)
        if o.get('stmt'):
            o["stmt"] = False
            params_code = "".join([self.visit(x, o)[0] for x in ast.args])
            self.emit.printout(params_code)
              
            self.emit.printout(self.emit.emitINVOKESTATIC(f"{sym.value.value}/{ast.funName}", sym.mtype, o['frame']))
            #Đã đặt đủ tham số vào stack rồi thì sinh mã gọi hàm thôi

            return o # trả về o luôn vì stmt luôn trả về void k cần quan tâm
        output = "".join([self.visit(x, o)[0] for x in ast.args])
        output += self.emit.emitINVOKESTATIC(f"{sym.value.value}/{ast.funName}", sym.mtype, o['frame'])

        # Vì funcall ở chỗ này là 1 biểu thức nên mình cần trả về giá trị kèm theo kiểu trả về luôn.
        return output, sym.mtype.rettype

    def visitBlock(self, ast: Block, o: dict) -> dict:
        env = o.copy()
        env['env'] = [[]] + env['env']
        env['frame'].enterScope(False)
        self.emit.printout(self.emit.emitLABEL(env['frame'].getStartLabel(), env['frame']))

        for item in ast.member:
            if type(item) is FuncCall:
                env["stmt"] = True
            #Cập nhật biến cờ trước khi visit vào hàm FuncCall, lát nữa duyệt vào trong sẽ tắt biến cờ này đi.
            env = self.visit(item, env)


        self.emit.printout(self.emit.emitLABEL(env['frame'].getEndLabel(), env['frame']))

        env['frame'].exitScope()
        return o
    
    def visitId(self, ast: Id, o: dict) -> dict:
        sym = next(filter(lambda x: x.name == ast.name, [j for i in o['env'] for j in i]), None)

        #Nếu Id này nằm ở vế trái phép gán
        if o.get('isLeft'):
            if type(sym.value) is Index: #Nếu Id là 1 tên trường của 1 object
                return self.emit.emitWRITEVAR(ast.name, sym.mtype, sym.value.value, o['frame']), sym.mtype
            else:         
                #Putstatic là ghi vào biến static,
                return self.emit.emitPUTSTATIC(f"{sym.value.value}/{ast.name}", sym.mtype, o['frame']), sym.mtype


        if type(sym.value) is Index: #Nếu Id là 1 tên trường của 1 object
            return self.emit.emitREADVAR(ast.name, sym.mtype, sym.value.value, o['frame']), sym.mtype
        else:         
            #Getstatic là đọc biến static,
            return self.emit.emitGETSTATIC(f"{sym.value.value}/{ast.name}", sym.mtype, o['frame']), sym.mtype

    def visitAssign(self, ast: Assign, o: dict) -> dict:

        #Xem thử là biến này đã được khai báo chưa, trong minigo nếu phép gán mà biến chưa được khai báo thì sẽ tự động khai báo nó luôn.
        if type(ast.lhs) is Id and not next(filter(lambda x: x.name == ast.lhs.name, [j for i in o['env'] for j in i]), None):
            return self.visit(VarDecl(ast.lhs.name, None, ast.rhs), o)
        

        rhsCode, rhsType = self.visit(ast.rhs, o)

        #Trước khi duyệt vế trái (có thể chạy vào hàm visitId ở trên) thì mình bật biến cờ isLeft, duyệt xong thì tắt nó đi.
        #Biến cờ này dùng để xác định xem mình đang ở vế trái hay vế phải của phép gán, từ đó mà sinh mã cho đúng.
        o['isLeft'] = True
        lhsCode, lhsType = self.visit(ast.lhs, o)
        o['isLeft'] = False

        if type(lhsType) is FloatType and type(rhsType) is IntType:
            rhsCode = rhsCode + self.emit.emitI2F(o['frame'])
        

        # Khúc array cell này task 3
        o['frame'].push() # Tăng kích thước stack lên 1 đơn vị, vì mình sẽ dùng stack để lưu trữ giá trị của biến này.
                
        # Not implementing array for level 1
        if type(ast.lhs) is ArrayCell:
            pass
        # access id
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
            return codeLeft + codeRight + self.emit.emitANDOP(frame), BoolType()  # Lấy này làm vd làm mấy cái ở trên

        # nối string string        
        if op in ['+'] and type(typeLeft) is StringType:
            return codeLeft + codeRight + self.emit.emitINVOKEVIRTUAL("java/lang/String/concat", MType([StringType()], StringType()), frame), StringType()
        if op in ['==', '!=', '<', '>', '>=', '<='] and type(typeLeft) is StringType:
            code = codeLeft + codeRight + self.emit.emitINVOKEVIRTUAL("java/lang/String/compareTo", MType([StringType()], IntType()), frame)
            code = code + self.emit.emitREOP(op, IntType(), frame)
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
    
    ## TODO END basic expression ------------------------------

    ## TODO array ------------------------------
    def visitArrayCell(self, ast: ArrayCell, o: dict) -> tuple[str, Type]:
        # Not implementing array for level 1
        pass

    def visitArrayLiteral(self, ast:ArrayLiteral , o: dict) -> tuple[str, Type]:
        # Not implementing array for level 1
        pass

    def visitConstDecl(self, ast:ConstDecl, o: dict) -> dict:
        return self.visit(VarDecl(ast.conName, ast.conType, ast.iniExpr), o)
    
    def visitArrayType(self, ast:ArrayType, o):
        # Not implementing array for level 1
        pass