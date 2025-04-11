import unittest
from TestUtils import TestAST
from AST import *

class ASTGenSuite(unittest.TestCase):
    def test_201(self):
        input = """const KhoaPineapple = poo(1);"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[IntLiteral(1)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 201))

    def test_202(self):
        input = """const KhoaPineapple = poo(1.0,true,false,nil,\"KhoaPineapple\");"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[FloatLiteral(1.0),BooleanLiteral(True),BooleanLiteral(False),NilLiteral(),StringLiteral("\"KhoaPineapple\"")]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 202))

    def test_203(self):
        input = """const KhoaPineapple = poo(id);"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[Id("id")]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 203))

    def test_204(self):
        input = """const KhoaPineapple = poo(1+2-3&&5--1);"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[BinaryOp("&&", BinaryOp("-", BinaryOp("+", IntLiteral(1), IntLiteral(2)), IntLiteral(3)), BinaryOp("-", IntLiteral(5), UnaryOp("-",IntLiteral(1))))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 204))

    def test_205(self):
        input = """const KhoaPineapple = poo(a > b <= c);"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[BinaryOp("<=", BinaryOp(">", Id("a"), Id("b")), Id("c"))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 205))

    def test_206(self):
        input = """const KhoaPineapple = poo(a[2][3]);"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[ArrayCell(Id("a"),[IntLiteral(2),IntLiteral(3)])]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 206))

    def test_207(self):
        input = """const KhoaPineapple = poo(a.b.c);"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[FieldAccess(FieldAccess(Id("a"),"b"),"c")]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 207))

    def test_208(self):
        input = """const KhoaPineapple = poo(a(),b.a(2, 3));"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[FuncCall("a",[]),MethCall(Id("b"),"a",[IntLiteral(2),IntLiteral(3)])]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 208))

    def test_209(self):
        input = """const KhoaPineapple = poo(a * (1+2));"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[BinaryOp("*", Id("a"), BinaryOp("+", IntLiteral(1), IntLiteral(2)))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 209))

    def test_210(self):
        input = """const KhoaPineapple = poo(KhoaPineapple {}, KhoaPineapple {a: 1});"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[StructLiteral("KhoaPineapple",[]),StructLiteral("KhoaPineapple",[("a",IntLiteral(1))])]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 210))

    def test_211(self):
        input = """const KhoaPineapple = poo([1]int{1}, [1][1]int{2});"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[ArrayLiteral([IntLiteral(1)],IntType(),[IntLiteral(1)]),ArrayLiteral([IntLiteral(1),IntLiteral(1)],IntType(),[IntLiteral(2)])]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 211))

    def test_212(self):
        input = """
            var KhoaPineapple = 1;
            var KhoaPineapple int;
            var Votine int = 1;
        """
        expect = Program([VarDecl("KhoaPineapple", None,IntLiteral(1)),
            VarDecl("KhoaPineapple",IntType(), None),
            VarDecl("Votine",IntType(),IntLiteral(1))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 212))

    def test_213(self):
        input = """
            func poo() int {return;}
            func poo(a int, b int) {return;}
        """
        expect = Program([FuncDecl("poo",[],IntType(),Block([Return(None)])),
            FuncDecl("poo",[ParamDecl("a",IntType()),ParamDecl("b",IntType())],VoidType(),Block([Return(None)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 213))

    def test_214(self):
        input = """
            func (KhoaPineapple v) poo(KhoaPineapple int) {return;}
        """
        expect = Program([MethodDecl("KhoaPineapple",Id("v"),FuncDecl("poo",[ParamDecl("KhoaPineapple",IntType())],VoidType(),Block([Return(None)])))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 214))


    def test_215(self):
        input = """
            type KhoaPineapple struct {
                a int;
            }
        """
        expect = Program([StructType("KhoaPineapple",[("a",IntType())],[])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 215))


    def test_216(self):
        input = """
            type KhoaPineapple struct {
                a int;
                b float;
            }
        """
        expect = Program([StructType("KhoaPineapple",[("a",IntType()),("b",FloatType())],[])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 216))


    def test_217(self):
        input = """
            func KhoaPineapple() {
                var a int;
                const a = nil;
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([VarDecl("a",IntType(), None),ConstDecl("a",None,NilLiteral())]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 217))

    def test_218(self):
        input = """
            func KhoaPineapple() {
                a += 1;
                b -= 2;
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([Assign(Id("a"),BinaryOp("+", Id("a"), IntLiteral(1))),Assign(Id("b"),BinaryOp("-", Id("b"), IntLiteral(2)))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 218))

    def test_219(self):
        input = """
            func KhoaPineapple() {
                break;
                continue;
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([Break(),Continue()]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 219))

    def test_220(self):
        input = """
            func KhoaPineapple() {
                poo(1, 2);
                a[2].poo(1,3);
                a.b.poo(x, y);
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([
            FuncCall("poo",[IntLiteral(1),IntLiteral(2)]),
            MethCall(ArrayCell(Id("a"),[IntLiteral(2)]),"poo",[IntLiteral(1),IntLiteral(3)]),
            MethCall(FieldAccess(Id("a"),"b"),"poo",[Id("x"),Id("y")])
        ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 220))

    def test_221(self):
        input = """
            func KhoaPineapple() {
                if(1) {return;}
                if(x > y) {return 5;}
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([
            If(IntLiteral(1), Block([Return(None)]), None),
            If(BinaryOp(">", Id("x"), Id("y")), Block([Return(IntLiteral(5))]), None)
        ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 221))

    def test_222(self):
        input = """
            func KhoaPineapple() {
                if(1) {
                    a := 1;
                } else {
                    a := 2;
                }
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([If(IntLiteral(1), Block([Assign(Id("a"),IntLiteral(1))]), Block([Assign(Id("a"),IntLiteral(2))]))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 222))

    def test_223(self):
        input = """
            func KhoaPineapple() {
                if(1) { return;
                }else if(1) {
                    a := 1;
                }else if(2) {
                    a := 2;
                }
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([
            If(IntLiteral(1), Block([Return(None)]),
                If(IntLiteral(1), Block([Assign(Id("a"),IntLiteral(1))]),
                    If(IntLiteral(2), Block([Assign(Id("a"),IntLiteral(2))]), None)))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 223))


    def test_224(self):
        input = """
            func KhoaPineapple() {
                for i < 10 {return;}
                for var i = 0; i < 10; i += 1  {return;}
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([ForBasic(BinaryOp("<", Id("i"), IntLiteral(10)),Block([Return(None)])),ForStep(VarDecl("i", None,IntLiteral(0)),BinaryOp("<", Id("i"), IntLiteral(10)),Assign(Id("i"),BinaryOp("+", Id("i"), IntLiteral(1))),Block([Return(None)]))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 224))

    def test_225(self):
        input = """
            func KhoaPineapple() {
                for index, value := range array[2] {return;}
                for i, val := range myList {i += 1;}
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([
            ForEach(Id("index"),Id("value"),ArrayCell(Id("array"),[IntLiteral(2)]),Block([Return(None)])),
            ForEach(Id("i"),Id("val"),Id("myList"),Block([Assign(Id("i"),BinaryOp("+", Id("i"), IntLiteral(1)))]))
        ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 225))

    def test_226(self):
        input = """
            const a = true + false - true;
            const b = false && true || false;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("-", BinaryOp("+", BooleanLiteral(True), BooleanLiteral(False)), BooleanLiteral(True))),
            ConstDecl("b",None,BinaryOp("||", BinaryOp("&&", BooleanLiteral(False), BooleanLiteral(True)), BooleanLiteral(False)))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 226))

    def test_227(self):
        input = """
            const a = 1 && 2 || 3;
            const b = x || y && z;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("||", BinaryOp("&&", IntLiteral(1), IntLiteral(2)), IntLiteral(3))),
            ConstDecl("b",None,BinaryOp("||", Id("x"), BinaryOp("&&", Id("y"), Id("z"))))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 227))

    def test_228(self):
        input = """
            const a = 1 + 2 && 3;
            const b = 4 || 5 + 6;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("&&", BinaryOp("+", IntLiteral(1), IntLiteral(2)), IntLiteral(3))),
            ConstDecl("b",None,BinaryOp("||", IntLiteral(4), BinaryOp("+", IntLiteral(5), IntLiteral(6))))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 228))

    def test_229(self):
        input = """
            const a = 1 - 2 % 3;
            const b = 4 * 5 / 6 % 7;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("-", IntLiteral(1), BinaryOp("%", IntLiteral(2), IntLiteral(3)))),
            ConstDecl("b",None,BinaryOp("%", BinaryOp("/", BinaryOp("*", IntLiteral(4), IntLiteral(5)), IntLiteral(6)), IntLiteral(7)))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 229))

    def test_230(self):
        input = """
            const a = 1 + -2 - 1;
        """
        expect = Program([ConstDecl("a",None,BinaryOp("-", BinaryOp("+", IntLiteral(1), UnaryOp("-",IntLiteral(2))), IntLiteral(1)))
		])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 230))

    def test_231(self):
        input = """
            const a = [1]ID{KhoaPineapple{}};
            const b = [2]ID{Person{}, Student{}};
        """
        expect = Program([
            ConstDecl("a",None,ArrayLiteral([IntLiteral(1)],Id("ID"),[StructLiteral("KhoaPineapple",[])])),
            ConstDecl("b",None,ArrayLiteral([IntLiteral(2)],Id("ID"),[StructLiteral("Person",[]),StructLiteral("Student",[])]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 231))

    def test_232(self):
        input = """
            const a = [1][3]float{1.};
            const b = [2][2][2]int{1, 2, 3, 4, 5, 6, 7, 8};
        """
        expect = Program([
            ConstDecl("a",None,ArrayLiteral([IntLiteral(1),IntLiteral(3)],FloatType(),[FloatLiteral(1.0)])),
            ConstDecl("b",None,ArrayLiteral([IntLiteral(2),IntLiteral(2),IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3),IntLiteral(4),IntLiteral(5),IntLiteral(6),IntLiteral(7),IntLiteral(8)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 232))

    def test_233(self):
        input = """
            const a = ID{a: 1, b: true};
            const b = Person{name: "John", age: 25};
        """
        expect = Program([
            ConstDecl("a",None,StructLiteral("ID",[("a",IntLiteral(1)),("b",BooleanLiteral(True))])),
            ConstDecl("b",None,StructLiteral("Person",[("name",StringLiteral("\"John\"")),("age",IntLiteral(25))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 233))

    def test_234(self):
        input = """
            const a = ID{a: [1]int{1}};
            const b = Person{address: Address{city: "New York"}};
        """
        expect = Program([
            ConstDecl("a",None,StructLiteral("ID",[("a",ArrayLiteral([IntLiteral(1)],IntType(),[IntLiteral(1)]))])),
            ConstDecl("b",None,StructLiteral("Person",[("address",StructLiteral("Address",[("city",StringLiteral("\"New York\""))]))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 234))

    def test_235(self):
        input = """
            const a = ID{b: true, c: 42};
            const b = Employee{name: "Alice", salary: 50000.0};
        """
        expect = Program([
            ConstDecl("a",None,StructLiteral("ID",[("b",BooleanLiteral(True)),("c",IntLiteral(42))])),
            ConstDecl("b",None,StructLiteral("Employee",[("name",StringLiteral("\"Alice\"")),("salary",FloatLiteral(50000.0))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 235))

    def test_236(self):
        input = """
            const a = 0 && 1 && 2;
            const b = x && y && z;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("&&", BinaryOp("&&", IntLiteral(0), IntLiteral(1)), IntLiteral(2))),
            ConstDecl("b",None,BinaryOp("&&", BinaryOp("&&", Id("x"), Id("y")), Id("z")))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 236))

    def test_237(self):
        input = """
            const a = 0 || 1 || 2;
            const b = x || y || z;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("||", BinaryOp("||", IntLiteral(0), IntLiteral(1)), IntLiteral(2))),
            ConstDecl("b",None,BinaryOp("||", BinaryOp("||", Id("x"), Id("y")), Id("z")))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 237))

    def test_238(self):
        input = """
            const a = 0 >= 1 <= 2;
            const b = x > y <= z;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("<=", BinaryOp(">=", IntLiteral(0), IntLiteral(1)), IntLiteral(2))),
            ConstDecl("b",None,BinaryOp("<=", BinaryOp(">", Id("x"), Id("y")), Id("z")))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 238))

    def test_239(self):
        input = """
            const a = 0 + 1 - 2;
            const b = x + y - z;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("-", BinaryOp("+", IntLiteral(0), IntLiteral(1)), IntLiteral(2))),
            ConstDecl("b",None,BinaryOp("-", BinaryOp("+", Id("x"), Id("y")), Id("z")))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 239))

    def test_240(self):
        input = """
            const a = 0 * 1 / 2;
            const b = x * y / z;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("/", BinaryOp("*", IntLiteral(0), IntLiteral(1)), IntLiteral(2))),
            ConstDecl("b",None,BinaryOp("/", BinaryOp("*", Id("x"), Id("y")), Id("z")))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 240))

    def test_241(self):
        input = """
            const a = !-!2;
            const b = !-!x;
        """
        expect = Program([
            ConstDecl("a",None,UnaryOp("!",UnaryOp("-",UnaryOp("!",IntLiteral(2))))),
            ConstDecl("b",None,UnaryOp("!",UnaryOp("-",UnaryOp("!",Id("x")))))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 241))

    def test_242(self):
        input = """
            const a = 1 && 2 || 3 >= 4 + 5 * -6;
            const b = x && y || z >= w + v * -u;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("||", BinaryOp("&&", IntLiteral(1), IntLiteral(2)), BinaryOp(">=", IntLiteral(3), BinaryOp("+", IntLiteral(4), BinaryOp("*", IntLiteral(5), UnaryOp("-",IntLiteral(6))))))),
            ConstDecl("b",None,BinaryOp("||", BinaryOp("&&", Id("x"), Id("y")), BinaryOp(">=", Id("z"), BinaryOp("+", Id("w"), BinaryOp("*", Id("v"), UnaryOp("-",Id("u")))))))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 242))

    def test_243(self):
        input = """
            const a = 1 > 2 < 3 >= 4 <=5 == 6;
            const b = x > y < z >= w <= v == u;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("==", BinaryOp("<=", BinaryOp(">=", BinaryOp("<", BinaryOp(">", IntLiteral(1), IntLiteral(2)), IntLiteral(3)), IntLiteral(4)), IntLiteral(5)), IntLiteral(6))),
            ConstDecl("b",None,BinaryOp("==", BinaryOp("<=", BinaryOp(">=", BinaryOp("<", BinaryOp(">", Id("x"), Id("y")), Id("z")), Id("w")), Id("v")), Id("u")))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 243))

    def test_244(self):
        input = """
            const a = 1 >= 2 + 3;
            const b = x >= y + z;
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp(">=", IntLiteral(1), BinaryOp("+", IntLiteral(2), IntLiteral(3)))),
            ConstDecl("b",None,BinaryOp(">=", Id("x"), BinaryOp("+", Id("y"), Id("z"))))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 244))

    def test_245(self):
        input = """
            const a = a[1][2][3][4];
            const b = arr[i][j][k][l];
        """
        expect = Program([
            ConstDecl("a",None,ArrayCell(Id("a"),[IntLiteral(1),IntLiteral(2),IntLiteral(3),IntLiteral(4)])),
            ConstDecl("b",None,ArrayCell(Id("arr"),[Id("i"),Id("j"),Id("k"),Id("l")]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 245))

    def test_246(self):
        input = """
            const a = a[1 + 2];
            const b = arr[x + y];
        """
        expect = Program([
            ConstDecl("a",None,ArrayCell(Id("a"),[BinaryOp("+", IntLiteral(1), IntLiteral(2))])),
            ConstDecl("b",None,ArrayCell(Id("arr"),[BinaryOp("+", Id("x"), Id("y"))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 246))

    def test_247(self):
        input = """
            const a = a.b.c.d.e;
            const b = obj.field1.field2.field3.field4;
        """
        expect = Program([
            ConstDecl("a",None,FieldAccess(FieldAccess(FieldAccess(FieldAccess(Id("a"),"b"),"c"),"d"),"e")),
            ConstDecl("b",None,FieldAccess(FieldAccess(FieldAccess(FieldAccess(Id("obj"),"field1"),"field2"),"field3"),"field4"))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 247))

    def test_248(self):
        input = """
            const a = ID {}.a;
            const b = Person {}.name;
        """
        expect = Program([
            ConstDecl("a",None,FieldAccess(StructLiteral("ID",[]),"a")),
            ConstDecl("b",None,FieldAccess(StructLiteral("Person",[]),"name"))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 248))

    def test_249(self):
        input = """
            const a = ID {}.a[2];
            const b = Person {}.addresses[0];
        """
        expect = Program([
            ConstDecl("a",None,ArrayCell(FieldAccess(StructLiteral("ID",[]),"a"),[IntLiteral(2)])),
            ConstDecl("b",None,ArrayCell(FieldAccess(StructLiteral("Person",[]),"addresses"),[IntLiteral(0)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 249))

    def test_250(self):
        input = """
            const a = a.b().c().d();
            const b = obj.methamphetamine1().methamphetamine2().methamphetamine3();
        """
        expect = Program([
            ConstDecl("a",None,MethCall(MethCall(MethCall(Id("a"),"b",[]),"c",[]),"d",[])),
            ConstDecl("b",None,MethCall(MethCall(MethCall(Id("obj"),"methamphetamine1",[]),"methamphetamine2",[]),"methamphetamine3",[]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 250))

    def test_251(self):
        input = """
            const a = a().d();
            const b = poop1().poop2();
        """
        expect = Program([
            ConstDecl("a",None,MethCall(FuncCall("a",[]),"d",[])),
            ConstDecl("b",None,MethCall(FuncCall("poop1",[]),"poop2",[]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 251))


    def test_252(self):
        input = """const KhoaPineapple = poo(1+2-3&&5--1);"""
        expect = Program([ConstDecl("KhoaPineapple",None,FuncCall("poo",[BinaryOp("&&", BinaryOp("-", BinaryOp("+", IntLiteral(1), IntLiteral(2)), IntLiteral(3)), BinaryOp("-", IntLiteral(5), UnaryOp("-",IntLiteral(1))))]))
		])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 252))

    def test_253(self):
        input = """
            const a = a * (nil - "a");
            const b = x * (nil - "string");
        """
        expect = Program([
            ConstDecl("a",None,BinaryOp("*", Id("a"), BinaryOp("-", NilLiteral(), StringLiteral("\"a\"")))),
            ConstDecl("b",None,BinaryOp("*", Id("x"), BinaryOp("-", NilLiteral(), StringLiteral("\"string\""))))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 253))

    def test_254(self):
        input = """
            func poo () {
                if (1){return;} else if (2){return;} else if (3){return;} else {return;}
                if (1){return;} else if (2){return;} else if (3){return;}
            }
        """
        expect = Program([FuncDecl("poo",[],VoidType(),Block([
            If(IntLiteral(1), Block([Return(None)]),
               If(IntLiteral(2), Block([Return(None)]),
                  If(IntLiteral(3), Block([Return(None)]), Block([Return(None)])))),
            If(IntLiteral(1), Block([Return(None)]),
               If(IntLiteral(2), Block([Return(None)]),
                  If(IntLiteral(3), Block([Return(None)]), None)))]))
		])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 254))

    def test_255(self):
        input = """
            const a = poo()[2];
            const b = getData()[index];
        """
        expect = Program([
            ConstDecl("a",None,ArrayCell(FuncCall("poo",[]),[IntLiteral(2)])),
            ConstDecl("b",None,ArrayCell(FuncCall("getData",[]),[Id("index")]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 255))

    def test_256(self):
        input = """
            const a = a;
            const b = variable;
        """
        expect = Program([
            ConstDecl("a",None,Id("a")),
            ConstDecl("b",None,Id("variable"))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 256))

    def test_257(self):
        input = """
            var a KhoaPineapple = 1.;
            var b Person = 42.5;
        """
        expect = Program([
            VarDecl("a",Id("KhoaPineapple"),FloatLiteral(1.0)),
            VarDecl("b",Id("Person"),FloatLiteral(42.5))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 257))

    def test_258(self):
        input = """
            var a [2][3]int;
            var b [5][10]float;
        """
        expect = Program([
            VarDecl("a",ArrayType([IntLiteral(2),IntLiteral(3)],IntType()), None),
            VarDecl("b",ArrayType([IntLiteral(5),IntLiteral(10)],FloatType()), None)
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 258))

    def test_259(self):
        input = """
            var num = 1;
            var str = "hello";
        """
        expect = Program([
            VarDecl("num", None,IntLiteral(1)),
            VarDecl("str", None,StringLiteral("\"hello\""))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 259))

    def test_260(self):
        input = """
            type KhoaPineapple struct {
                x int; y string;
            }
        """
        expect = Program([
            StructType("KhoaPineapple",[("x",IntType()),("y",StringType())],[])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 260))

    def test_261(self):
        input = """
            type Person struct {
                name string;
                age int;
            }
        """
        expect = Program([
            StructType("Person",[("name",StringType()),("age",IntType())],[])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 261))

    def test_262(self):
        input = """
            type KhoaPineapple struct {
                a  int;
                b  boolean;
                c  float;
            }
        """
        expect = Program([
            StructType("KhoaPineapple",[("a",IntType()),("b",BoolType()),("c",FloatType())],[])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 262))

    def test_263(self):
        input = """
            type KhoaPineapple struct {
                a  int;
                b  boolean;
                c  [2]KhoaPineapple;
            }
        """
        expect = Program([
            StructType("KhoaPineapple",[("a",IntType()),("b",BoolType()),("c",ArrayType([IntLiteral(2)],Id("KhoaPineapple")))],[])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 263))

    def test_264(self):
        input = """
            type KhoaPineapple interface {
                Add();
            }
        """
        expect = Program([
            InterfaceType("KhoaPineapple",[Prototype("Add",[],VoidType())])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 264))

    def test_265(self):
        input = """
            type Calculator interface {
                Add(a int);
                Subtract(a int);
            }
        """
        expect = Program([
            InterfaceType("Calculator",[
                Prototype("Add",[IntType()],VoidType()),
                Prototype("Subtract",[IntType()],VoidType())
            ])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 265))

    def test_266(self):
        input = """
            type Mathematics interface {
                Add(a int, b int);
                Multiply(a int, b int);
            }
        """
        expect = Program([
            InterfaceType("Mathematics",[
                Prototype("Add",[IntType(),IntType()],VoidType()),
                Prototype("Multiply",[IntType(),IntType()],VoidType())
            ])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 266))

    def test_267(self):
        input = """
            type Arithmetic interface {
                Add(a, c int, b int);
                Subtract(a, c int, b int);
            }
        """
        expect = Program([
            InterfaceType("Arithmetic",[
                Prototype("Add",[IntType(),IntType(),IntType()],VoidType()),
                Prototype("Subtract",[IntType(),IntType(),IntType()],VoidType())
            ])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 267))

    def test_268(self):
        input = """
            type Parser interface {
                Parse(a, c int, b int) [2]string;
                Stringify(a, c int) [5]float;
            }
        """
        expect = Program([
            InterfaceType("Parser",[
                Prototype("Parse",[IntType(),IntType(),IntType()],ArrayType([IntLiteral(2)],StringType())),
                Prototype("Stringify",[IntType(),IntType()],ArrayType([IntLiteral(5)],FloatType()))
            ])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 268))

    def test_269(self):
        input = """
            type Backend interface {
                Process() [2]string;
                Store() Database;
            }
        """
        expect = Program([
            InterfaceType("Backend",[
                Prototype("Process",[],ArrayType([IntLiteral(2)],StringType())),
                Prototype("Store",[],Id("Database"))
            ])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 269))

    def test_270(self):
        input = """
            type Serializer interface {
                Encode();
                Decode();
            }
        """
        expect = Program([
            InterfaceType("Serializer",[
                Prototype("Encode",[],VoidType()),
                Prototype("Decode",[],VoidType())
            ])
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 270))

    def test_271(self):
        input = """
            func process() {return;}
        """
        expect = Program([
            FuncDecl("process",[],VoidType(),Block([Return(None)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 271))

    def test_272(self):
        input = """
            func transform(a [2]ID) {return;}
        """
        expect = Program([
            FuncDecl("transform",[ParamDecl("a",ArrayType([IntLiteral(2)],Id("ID")))],VoidType(),Block([Return(None)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 272))

    def test_273(self):
        input = """
            func calculate(a int, b [1]int) {return;}
        """
        expect = Program([
            FuncDecl("calculate",[ParamDecl("a",IntType()),ParamDecl("b",ArrayType([IntLiteral(1)],IntType()))],VoidType(),Block([Return(None)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 273))

    def test_274(self):
        input = """
            func getData() [2]int {return;}
        """
        expect = Program([
            FuncDecl("getData",[],ArrayType([IntLiteral(2)],IntType()),Block([Return(None)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 274))

    def test_275(self):
        input = """
            func (Dog d) bark() {return;}
        """
        expect = Program([
            MethodDecl("Dog",Id("d"),FuncDecl("bark",[],VoidType(),Block([Return(None)])))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 275))

    def test_276(self):
        input = """
            func (Vehicle v) move(a [2]ID) {return;}
        """
        expect = Program([
            MethodDecl("Vehicle",Id("v"),FuncDecl("move",[ParamDecl("a",ArrayType([IntLiteral(2)],Id("ID")))],VoidType(),Block([Return(None)])))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 276))

    def test_277(self):
        input = """
            func (Calculator c) add(a int, b [1]int) {return;}
        """
        expect = Program([
            MethodDecl("Calculator",Id("c"),FuncDecl("add",[ParamDecl("a",IntType()),ParamDecl("b",ArrayType([IntLiteral(1)],IntType()))],VoidType(),Block([Return(None)])))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 277))

    def test_278(self):
        input = """
            func (Math m) multiply() [2]int {return;}
        """
        expect = Program([
            MethodDecl("Math",Id("m"),FuncDecl("multiply",[],ArrayType([IntLiteral(2)],IntType()),Block([Return(None)])))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 278))

    def test_279(self):
        input = """
            var x = 1;
            const y = 2;
            type Point struct{x float;}
            type Shape interface {area();}
            func calculate(){return;}
            func (Vector v) normalize() [2]int {return;}
        """
        expect = Program([
            VarDecl("x", None,IntLiteral(1)),
            ConstDecl("y",None,IntLiteral(2)),
            StructType("Point",[("x",FloatType())],[]),
            InterfaceType("Shape",[Prototype("area",[],VoidType())]),
            FuncDecl("calculate",[],VoidType(),Block([Return(None)])),
            MethodDecl("Vector",Id("v"),FuncDecl("normalize",[],ArrayType([IntLiteral(2)],IntType()),Block([Return(None)])))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 279))

    def test_280(self):
        input = """
            func process(a,b,c,d [ID][2][length] Custom ){return;}
        """
        expect = Program([
            FuncDecl("process",[
                ParamDecl("a",ArrayType([Id("ID"),IntLiteral(2),Id("length")],Id("Custom"))),
                ParamDecl("b",ArrayType([Id("ID"),IntLiteral(2),Id("length")],Id("Custom"))),
                ParamDecl("c",ArrayType([Id("ID"),IntLiteral(2),Id("length")],Id("Custom"))),
                ParamDecl("d",ArrayType([Id("ID"),IntLiteral(2),Id("length")],Id("Custom")))
            ],VoidType(),Block([Return(None)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 280))

    def test_281(self):
        input = """
            func compute(){
                const result = 3.14;
            }
        """
        expect = Program([
            FuncDecl("compute",[],VoidType(),Block([ConstDecl("result",None,FloatLiteral(3.14))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 281))

    def test_282(self):
        input = """
            func process(){
                var data = 100;
            }
        """
        expect = Program([
            FuncDecl("process",[],VoidType(),Block([VarDecl("data", None,IntLiteral(100))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 282))

    def test_283(self):
        input = """
            func initialize(){
                var matrix [3]int = 42;
            }
        """
        expect = Program([
            FuncDecl("initialize",[],VoidType(),Block([VarDecl("matrix",ArrayType([IntLiteral(3)],IntType()),IntLiteral(42))]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 283))

    def test_284(self):
        input = """
            func setup(){
                var config string;
            }
        """
        expect = Program([
            FuncDecl("setup",[],VoidType(),Block([VarDecl("config",StringType(), None)]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 284))

    def test_285(self):
        input = """
            func update(){
                counter += 5;
                score -= 10;
                multiplier *= 2;
                quotient /= 4;
                remainder %= 3;
            }
        """
        expect = Program([
            FuncDecl("update",[],VoidType(),Block([
                Assign(Id("counter"),BinaryOp("+", Id("counter"), IntLiteral(5))),
                Assign(Id("score"),BinaryOp("-", Id("score"), IntLiteral(10))),
                Assign(Id("multiplier"),BinaryOp("*", Id("multiplier"), IntLiteral(2))),
                Assign(Id("quotient"),BinaryOp("/", Id("quotient"), IntLiteral(4))),
                Assign(Id("remainder"),BinaryOp("%", Id("remainder"), IntLiteral(3)))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 285))

    def test_286(self):
        input = """
            func transform(){
                matrix[2 * index] := value;
            }
        """
        expect = Program([
            FuncDecl("transform",[],VoidType(),Block([
                Assign(ArrayCell(Id("matrix"),[BinaryOp("*", IntLiteral(2), Id("index"))]),Id("value"))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 286))

    def test_287(self):
        input = """
            func modify(){
                obj[2].field.items[3] := new_value;
            }
        """
        expect = Program([
            FuncDecl("modify",[],VoidType(),Block([
                Assign(ArrayCell(FieldAccess(FieldAccess(ArrayCell(Id("obj"),[IntLiteral(2)]),"field"),"items"),[IntLiteral(3)]),Id("new_value"))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 287))

    def test_288(self):
        input = """
            func KhoaPineapple() {
                var a int;
                const a = nil;
            }
        """
        expect = Program([FuncDecl("KhoaPineapple",[],VoidType(),Block([VarDecl("a",IntType(), None),ConstDecl("a",None,NilLiteral())]))
		])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 288))

    def test_289(self):
        input = """
            func update(){
                object.field := 100;
            }
        """
        expect = Program([
            FuncDecl("update",[],VoidType(),Block([
                Assign(FieldAccess(Id("object"),"field"),IntLiteral(100))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 289))

    def test_290(self):
        input = """
            func transform(){
                document.user[5].profile.email := "new@example.com";
            }
        """
        expect = Program([
            FuncDecl("transform",[],VoidType(),Block([
                Assign(FieldAccess(FieldAccess(ArrayCell(FieldAccess(Id("document"),"user"),[IntLiteral(5)]),"profile"),"email"),StringLiteral("\"new@example.com\""))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 290))

    def test_291(self):
        input = """
            func control(){
                break;
                continue;
            }
        """
        expect = Program([
            FuncDecl("control",[],VoidType(),Block([Break(),Continue()]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 291))

    def test_292(self):
        input = """
            func compute(){
                return;
                return sqrt(25) + 5;
            }
        """
        expect = Program([
            FuncDecl("compute",[],VoidType(),Block([
                Return(None),
                Return(BinaryOp("+", FuncCall("sqrt",[IntLiteral(25)]), IntLiteral(5)))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 292))

    def test_293(self):
        input = """const KhoaPineapple = STRUCT {
            a : 1,
            b : false};"""
        expect = Program([ConstDecl("KhoaPineapple", None, StructLiteral("STRUCT",[("a",IntLiteral(1)),("b",BooleanLiteral(False))]))])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 293))

    def test_294(self):
        input = """
            func control(){
                if(error_code) {return;}
                if(x > threshold) {return error_message;}
            }
        """
        expect = Program([
            FuncDecl("control",[],VoidType(),Block([
                If(Id("error_code"), Block([Return(None)]), None),
                If(BinaryOp(">", Id("x"), Id("threshold")), Block([Return(Id("error_message"))]), None)
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 294))

    def test_295(self):
        input = """
            func decide(){
                if(condition) {
                    return "valid";
                } else {
                    return "invalid";
                }
            }
        """
        expect = Program([
            FuncDecl("decide",[],VoidType(),Block([
                If(Id("condition"), 
                Block([Return(StringLiteral("\"valid\""))]), 
                Block([Return(StringLiteral("\"invalid\""))]))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 295))

    def test_296(self):
        input = """
            func validate(){
                if(isValid) { 
                    return true;
                } else if(canFix) {
                    return fixAndValidate();
                } else if(shouldLog) {
                    logError();
                    return false;
                }
            }
        """
        expect = Program([
            FuncDecl("validate",[],VoidType(),Block([
                If(Id("isValid"), Block([Return(BooleanLiteral(True))]),
                    If(Id("canFix"), Block([Return(FuncCall("fixAndValidate",[]))]),
                        If(Id("shouldLog"), Block([
                            FuncCall("logError",[]),
                            Return(BooleanLiteral(False))
                        ]), None)))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 296))

    def test_297(self):
        input = """
            func iterate(){
                for i < max_items {return;}
                for var j = 0; j < 10; j += 1 {return;}
            }
        """
        expect = Program([
            FuncDecl("iterate",[],VoidType(),Block([
                ForBasic(BinaryOp("<", Id("i"), Id("max_items")),Block([Return(None)])),
                ForStep(VarDecl("j", None,IntLiteral(0)),
                    BinaryOp("<", Id("j"), IntLiteral(10)),
                    Assign(Id("j"),BinaryOp("+", Id("j"), IntLiteral(1))),
                    Block([Return(None)]))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 297))

    def test_298(self):
        input = """
            func enumerate(){
                for key, value := range collection {
                    updateRegistry(key, value);
                }
            }
        """
        expect = Program([
            FuncDecl("enumerate",[],VoidType(),Block([
                ForEach(Id("key"),Id("value"),Id("collection"),Block([
                    FuncCall("updateRegistry",[Id("key"),Id("value")])
                ]))
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 298))

    def test_299(self):
        input = """
            func process(){
                data.transform().filter().map().reduce();
            }
        """
        expect = Program([
            FuncDecl("process",[],VoidType(),Block([
                MethCall(MethCall(MethCall(MethCall(Id("data"),"transform",[]),"filter",[]),"map",[]),"reduce",[])
            ]))
        ])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 299))

    def test_300(self):
        input = """
            const a = a[1][2][3][4];
        """
        expect = Program([ConstDecl("a",None,ArrayCell(Id("a"),[IntLiteral(1),IntLiteral(2),IntLiteral(3),IntLiteral(4)]))
		])
        self.assertTrue(TestAST.checkASTGen(input, str(expect), 300))