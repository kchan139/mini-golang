import unittest
from TestUtils import TestChecker
from AST import *

class CheckSuite(unittest.TestCase):
    def test_301(self):
        input = """
            const CHEESE = 1; 
            const CHEESE = 2;        
        """
        expect = "Redeclared Constant: CHEESE"
        self.assertTrue(TestChecker.test(input, expect, 301))

    def test_302(self):
        input = """
            var Cheese = 1; 
            const Cheese = 2;
        """
        expect = "Redeclared Constant: Cheese"
        self.assertTrue(TestChecker.test(input, expect, 302))
    
    def test_303(self):
        input = """
            const CHEESE = 1; 
            var CHEESE = 2;
        """
        expect = "Redeclared Variable: CHEESE"
        self.assertTrue(TestChecker.test(input, expect, 303))

    def test_304(self):
        input = """
            const CHEESE = 1; 
            func CHEESE () {return;}
        """
        expect = "Redeclared Function: CHEESE"
        self.assertTrue(TestChecker.test(input, expect, 304))

    def test_305(self):
        input = """
            func Cheese () {return;}
            var Cheese = 1;
        """
        expect = "Redeclared Variable: Cheese"
        self.assertTrue(TestChecker.test(input, expect, 305))

    def test_306(self):
        input = """
            var getInt = 1;
        """
        expect = "Redeclared Variable: getInt"
        self.assertTrue(TestChecker.test(input, expect, 306))

    def test_307(self):
        input = """
            type Cheese struct {
                Cheese int;
            }
            type CHEESE struct {
                Cheese string;
                CHEESE int;
                CHEESE float;
            }
        """
        expect = "Redeclared Field: CHEESE"
        self.assertTrue(TestChecker.test(input, expect, 307))

    def test_308(self):
        input = """
            func (veiny_ahh DIH) putIntLn () {return;}
            func (veiny_ahh DIH) getInt () {return;}
            func (veiny_ahh DIH) getInt () {return;}
            type DIH struct {
                Dih int;
            }
        """
        expect = "Redeclared Method: getInt"
        self.assertTrue(TestChecker.test(input, expect, 308))

    def test_309(self):
        input = """
            type Cheese interface {
                Cheese ();
                Cheese (aura int);
            }
        """
        expect = "Redeclared Prototype: Cheese"
        self.assertTrue(TestChecker.test(input, expect, 309))

    def test_310(self):
        input = """
            func Cheese (aura, aura int) {return;}
        """
        expect = "Redeclared Parameter: aura"
        self.assertTrue(TestChecker.test(input, expect, 310))

    def test_311(self):
        input = """
            func Cheese (aura int) {
                var aura = 1;
                var farming = 1;
                const farming = 1;
            }
        """
        expect = "Redeclared Constant: farming"
        self.assertTrue(TestChecker.test(input, expect, 311))

    def test_312(self):
        input = """
            func Cheese (bruh int) {
                for var aura = 1; aura < 1; aura += 1 {
                    const aura = 2;
                }
            }  
        """
        expect = "Redeclared Constant: aura"
        self.assertTrue(TestChecker.test(input, expect, 312))

    def test_313(self):
        input = """
            var rizz = 1;
            var flex = rizz;
            var chad = dih;
        """
        expect = "Undeclared Identifier: dih"
        self.assertTrue(TestChecker.test(input, expect, 313))

    def test_314(self):
        input = """
            func Cheese () int {return 1;}

            func poop () {
                var bruh = Cheese();
                poop_cheese();
                return;
            }
        """
        expect = "Undeclared Function: poop_cheese"
        self.assertTrue(TestChecker.test(input, expect, 314))

    def test_315(self):
        input = """
            type CHEESE struct {
                Cheese int;
            }

            func (yap CHEESE) getInt () {
                const chad = yap.Cheese;
                var dih = yap.Chi;
            }
        """
        expect = "Undeclared Field: Chi"
        self.assertTrue(TestChecker.test(input, expect, 315))

    def test_316(self):
        input = """
            type CHEESE struct {
                Cheese int;
            }

            func (yap CHEESE) getInt () {
                yap.getInt ();
                yap.putInt ();
            }
        """
        expect = "Undeclared Method: putInt"
        self.assertTrue(TestChecker.test(input, expect, 316))

    def test_317(self):
        input = """
            type CHEESE struct {Cheese int;}
            type CHEESE struct {v int;}
        """
        expect = "Redeclared Type: CHEESE"
        self.assertTrue(TestChecker.test(input, expect, 317))

    def test_318(self):
        input = """
            var aura = 1;
            type aura struct {
                bruh int;
            }
        """
        expect = "Redeclared Type: aura"
        self.assertTrue(TestChecker.test(input, expect, 318))

    def test_319(self):
        input = """var aura int; var bruh int; var aura int; """
        expect = "Redeclared Variable: aura"
        self.assertTrue(TestChecker.test(input, expect, 319))

    def test_320(self):
        input = """var aura int = 1.2;"""
        expect = "Type Mismatch: VarDecl(aura,IntType,FloatLiteral(1.2))"
        self.assertTrue(TestChecker.test(input, expect, 320))

    def test_321(self):
        input = Program([VarDecl("aura",IntType(),Id("bruh"))])
        expect = "Undeclared Identifier: bruh"
        self.assertTrue(TestChecker.test(input, expect, 321))

    def test_322(self):
        input =  """
            const yap = 3;
            const aura = yap + yap;
            var bruh [aura * 2 + aura] int;
            var chad [18] int = bruh;
        """
        input = Program([ConstDecl("yap",None,IntLiteral(3)),ConstDecl("aura",None,BinaryOp("+", Id("yap"), Id("yap"))),VarDecl("bruh",ArrayType([BinaryOp("+", BinaryOp("*", Id("aura"), IntLiteral(2)), Id("aura"))],IntType()), None),VarDecl("chad",ArrayType([IntLiteral(18)],IntType()),Id("bruh"))])
        self.assertTrue(TestChecker.test(input, "", 322))
    def test_323(self):
        input =  """
            func Cheese (b int) {
                for var a = 1; a < 1; a += 1 {
                    const a = 2;
                }
            }
        """
        input = Program([FuncDecl("Cheese",[ParamDecl("b",IntType())],VoidType(),Block([ForStep(VarDecl("a", None,IntLiteral(1)),BinaryOp("<", Id("a"), IntLiteral(1)),Assign(Id("a"),BinaryOp("+", Id("a"), IntLiteral(1))),Block([ConstDecl("a",None,IntLiteral(2))]))]))])

        self.assertTrue(TestChecker.test(input, "Redeclared Constant: a", 323))

    def test_324(self):
        input =  """
            const a = 2;
            func poop () {
                const a = 1;
                for a < 1 {
                    const a = 1;
        """
        input = Program([ConstDecl("a",None,IntLiteral(2)),FuncDecl("poop",[],VoidType(),Block([ConstDecl("a",None,IntLiteral(1)),ForBasic(BinaryOp("<", Id("a"), IntLiteral(1)),Block([ConstDecl("a",None,IntLiteral(1)),ForBasic(BinaryOp("<", Id("a"), IntLiteral(1)),Block([ConstDecl("a",None,IntLiteral(1)),ConstDecl("b",None,IntLiteral(1))])),ConstDecl("b",None,IntLiteral(1)),VarDecl("a", None,IntLiteral(1))]))]))])


        self.assertTrue(TestChecker.test(input, "Redeclared Variable: a", 324))

    def test_325(self):
        input =  """
            type Skibidi struct {Cheese int;}
            type Smol struct {Cheese int;}
            type Toilet interface {Cheese();}
            type Amongus interface {Cheese();}

            func (s Skibidi) cheese() {return;}

            var a Skibidi;
            var b Smol;
            var c Toilet = a;
            var d Amongus = b;
        """
        input = Program([StructType("Skibidi",[("Cheese",IntType())],[]),StructType("Smol",[("Cheese",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],VoidType())]),InterfaceType("Amongus",[Prototype("Cheese",[],VoidType())]),MethodDecl("s",Id("Skibidi"),FuncDecl("cheese",[],VoidType(),Block([Return(None)]))),VarDecl("a",Id("Skibidi"), None),VarDecl("b",Id("Smol"), None),VarDecl("c",Id("Toilet"),Id("a")),VarDecl("d",Id("Amongus"),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(c,Id(Toilet),Id(a))", 325))

    def test_326(self):
        input =  """
            type Skibidi struct {Cheese int;}
            type Smol struct {Cheese int;}
            type Toilet interface {Cheese();}
            type Amongus interface {Cheese() int;}

            func (s Skibidi) cheese() {return;}

            var a Skibidi;
            var b Smol;
            var c Amongus = a;
        """
        input = Program([StructType("Skibidi",[("Cheese",IntType())],[]),StructType("Smol",[("Cheese",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],VoidType())]),InterfaceType("Amongus",[Prototype("Cheese",[],IntType())]),MethodDecl("s",Id("Skibidi"),FuncDecl("cheese",[],VoidType(),Block([Return(None)]))),VarDecl("a",Id("Skibidi"), None),VarDecl("b",Id("Smol"), None),VarDecl("c",Id("Amongus"),Id("a"))])

        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(c,Id(Amongus),Id(a))", 326))

    def test_327(self):
        input =  """
            type Skibidi struct {Cheese int;}
            type Smol struct {Cheese int;}
            type Toilet interface {Cheese() Skibidi;}
            type Amongus interface {Cheese() Smol;}

            func (s Skibidi) cheese() Skibidi {return s;}

            var a Skibidi;
            var c Toilet = a;
            var d Amongus = a;
        """
        input = Program([StructType("Skibidi",[("Cheese",IntType())],[]),StructType("Smol",[("Cheese",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],Id("Skibidi"))]),InterfaceType("Amongus",[Prototype("Cheese",[],Id("Smol"))]),MethodDecl("s",Id("Skibidi"),FuncDecl("cheese",[],Id("Skibidi"),Block([Return(Id("s"))]))),VarDecl("a",Id("Skibidi"), None),VarDecl("c",Id("Toilet"),Id("a")),VarDecl("d",Id("Amongus"),Id("a"))])

        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(c,Id(Toilet),Id(a))", 327))

    def test_328(self):
        input =  """
            type Skibidi struct {Cheese int;}
            type Smol struct {Cheese int;}
            type Toilet interface {Cheese(e, e int) Skibidi;}
            type Amongus interface {Cheese(a int, b float) Skibidi;}

            func (s Skibidi) cheese(a, b int) Skibidi {return s;}

            var a Skibidi;
            var c Toilet = a;
            var d Amongus = a;
        """
        input = Program([StructType("Skibidi",[("Cheese",IntType())],[]),StructType("Smol",[("Cheese",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[IntType(),IntType()],Id("Skibidi"))]),InterfaceType("Amongus",[Prototype("Cheese",[IntType(),FloatType()],Id("Skibidi"))]),MethodDecl("s",Id("Skibidi"),FuncDecl("cheese",[ParamDecl("a",IntType()),ParamDecl("b",IntType())],Id("Skibidi"),Block([Return(Id("s"))]))),VarDecl("a",Id("Skibidi"), None),VarDecl("c",Id("Toilet"),Id("a")),VarDecl("d",Id("Amongus"),Id("a"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(c,Id(Toilet),Id(a))", 328))

    def test_329(self):
        input =  """
            type Skibidi struct {v int; t int;}

            var a = Skibidi {v : 1, t: 2}
            var b Skibidi = a;
            var c int = b;
        """
        input = Program([StructType("Skibidi",[("v",IntType()),("t",IntType())],[]),VarDecl("a", None,StructLiteral("Skibidi",[("v",IntLiteral(1)),("t",IntLiteral(2))])),VarDecl("b",Id("Skibidi"),Id("a")),VarDecl("c",IntType(),Id("b"))])

        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(c,IntType,Id(b))", 329))

    def test_330(self):
        input =  """
            var a = [2] int {1, 2}
            var c [2] float = a
        """
        input = Program([VarDecl("a", None,ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)])),VarDecl("c",ArrayType([IntLiteral(2)],FloatType()),Id("a"))])
        self.assertTrue(TestChecker.test(input, "", 330))

    def test_331(self):
        input =  """
            var a [2][3] int;
            var b = a[1][2];
            var c int = b;
            var d [1] string = b;
        """
        input = Program([VarDecl("a",ArrayType([IntLiteral(2),IntLiteral(3)],IntType()), None),VarDecl("b", None,ArrayCell(Id("a"),[IntLiteral(1),IntLiteral(2)])),VarDecl("c",IntType(),Id("b")),VarDecl("d",ArrayType([IntLiteral(1)],StringType()),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,ArrayType(StringType,[IntLiteral(1)]),Id(b))", 331))

    def test_332(self):
        input =  """
            type Skibidi struct {Cheese int;}
            type Toilet interface {Cheese();}
            var a Toilet;
            var c Toilet = nil;
            var d Skibidi = nil;
            func poop(){
                c := a;
                a := nil;
            }

            var e int = nil;
        """
        input = Program([StructType("Skibidi",[("Cheese",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],VoidType())]),VarDecl("a",Id("Toilet"), None),VarDecl("c",Id("Toilet"),NilLiteral()),VarDecl("d",Id("Skibidi"),NilLiteral()),FuncDecl("poop",[],VoidType(),Block([Assign(Id("c"),Id("a")),Assign(Id("a"),NilLiteral())])),VarDecl("e",IntType(),NilLiteral())])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(e,IntType,Nil)", 332))
    
    def test_333(self):
        input =  """
            var a = -1;
            var b = -1.02;
            var c = - true;
        """
        input = Program([VarDecl("a", None,UnaryOp("-",IntLiteral(1))),VarDecl("b", None,UnaryOp("-",FloatLiteral(1.02))),VarDecl("c", None,UnaryOp("-",BooleanLiteral(True)))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: UnaryOp(-,BooleanLiteral(true))", 333))

    def test_334(self):
        input =  """
            type Person struct {
                name string ;
                age int ;
            }

            func Cheese()  {
                var person = Person{name: "Chi", age: 30}
                person.name := "Xuan";
                person.age := 30;
                putStringLn(person.name)
                putStringLn(person.Greeting())
            }

            func (p Person) Greeting() string {
                return "Wassup, " + p.name
            }
        """
        input = Program([StructType("Person",[("name",StringType()),("age",IntType())],[]),FuncDecl("Cheese",[],VoidType(),Block([VarDecl("person", None,StructLiteral("Person",[("name",StringLiteral("\"Chi\"")),("age",IntLiteral(30))])),Assign(FieldAccess(Id("person"),"name"),StringLiteral("\"Xuan\"")),Assign(FieldAccess(Id("person"),"age"),IntLiteral(30)),FuncCall("putStringLn",[FieldAccess(Id("person"),"name")]),FuncCall("putStringLn",[MethCall(Id("person"),"Greeting",[])])])),MethodDecl("p",Id("Person"),FuncDecl("Greeting",[],StringType(),Block([Return(BinaryOp("+", StringLiteral("\"Wassup, \""), FieldAccess(Id("p"),"name")))])))])

        self.assertTrue(TestChecker.test(input, "", 334))

    def test_335(self):
        input =  """
            type CHEESE struct {a [2]int;}
            type VO interface {poop() int;}

            func (v CHEESE) poop() int {return 1;}

            func poop() {
                var b VO = CHEESE{a: [2]int{1, 2}};
                var a CHEESE = b;
            }
        """
        input = Program([StructType("CHEESE",[("a",ArrayType([IntLiteral(2)],IntType()))],[]),InterfaceType("VO",[Prototype("poop",[],IntType())]),MethodDecl("v",Id("CHEESE"),FuncDecl("poop",[],IntType(),Block([Return(IntLiteral(1))]))),FuncDecl("poop",[],VoidType(),Block([VarDecl("b",Id("VO"),StructLiteral("CHEESE",[("a",ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)]))])),VarDecl("a",Id("CHEESE"),Id("b"))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(a,Id(CHEESE),Id(b))", 335))

    def test_336(self):
        input =  """
            type CHEESE struct {a [2]int;}
            type VO interface {poop() int;}

            func (v CHEESE) poop() int {return 1;}

            func poop(a VO) {
                var b VO = CHEESE{a: [2]int{1, 2}};
                poop(b)
            }
        """
        input = Program([StructType("CHEESE",[("a",ArrayType([IntLiteral(2)],IntType()))],[]),InterfaceType("VO",[Prototype("poop",[],IntType())]),MethodDecl("v",Id("CHEESE"),FuncDecl("poop",[],IntType(),Block([Return(IntLiteral(1))]))),FuncDecl("poop",[ParamDecl("a",Id("VO"))],VoidType(),Block([VarDecl("b",Id("VO"),StructLiteral("CHEESE",[("a",ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)]))])),FuncCall("poop",[Id("b")])]))])
        self.assertTrue(TestChecker.test(input, "", 336))

    def test_337(self):
        input =  """
            var a CHEESE;
            func poop() CHEESE {
                return a;
                return CHEESE;
            }

            type CHEESE struct {CHEESE int;}
            }
        """
        input = Program([VarDecl("a",Id("CHEESE"), None),FuncDecl("poop",[],Id("CHEESE"),Block([Return(Id("a")),Return(Id("CHEESE"))])),StructType("CHEESE",[("CHEESE",IntType())],[])])
        self.assertTrue(TestChecker.test(input, "Undeclared Identifier: CHEESE", 337))

    def test_338(self):
        input =  """
            type CHEESE struct {a [2]int;}

            func poop() CHEESE {
                return nil
            }
        """
        input = Program([StructType("CHEESE",[("a",ArrayType([IntLiteral(2)],IntType()))],[]),FuncDecl("poop",[],Id("CHEESE"),Block([Return(NilLiteral())]))])
        self.assertTrue(TestChecker.test(input, "", 338))

    def test_339(self):
        input =  """
            func poop() int {
                var a = 1;
                if (a < 3) {
                    var a = 1;
                } else if(a > 2) {
                    var a = 2;
                }
                return a;
            }
        """
        input = Program([FuncDecl("poop",[],IntType(),Block([VarDecl("a", None,IntLiteral(1)),If(BinaryOp("<", Id("a"), IntLiteral(3)), Block([VarDecl("a", None,IntLiteral(1))]), If(BinaryOp(">", Id("a"), IntLiteral(2)), Block([VarDecl("a", None,IntLiteral(2))]), None)),Return(Id("a"))]))])
        self.assertTrue(TestChecker.test(input, "", 339))
    
    def test_340(self):
        input =  """
            const v = 3;
            const k = v + 1;
            func poop(a [1 + 2] int) {
                poop([k - 1] int {1,2,3})
            }
        """
        input = Program([ConstDecl("v",None,IntLiteral(3)),ConstDecl("k",None,BinaryOp("+", Id("v"), IntLiteral(1))),FuncDecl("poop",[ParamDecl("a",ArrayType([BinaryOp("+", IntLiteral(1), IntLiteral(2))],IntType()))],VoidType(),Block([FuncCall("poop",[ArrayLiteral([BinaryOp("-", Id("k"), IntLiteral(1))],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3)])])]))])
        self.assertTrue(TestChecker.test(input, "", 340))

    def test_341(self):
        input =  """
            var aura = [2] int {1, 2}
            var cringe [2] float = aura
        """
        input = Program([VarDecl("aura", None,ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)])),VarDecl("cringe",ArrayType([IntLiteral(2)],FloatType()),Id("aura"))])
        self.assertTrue(TestChecker.test(input, "", 341))

    def test_342(self):
        input =  """
            type K struct {a int;}
            func (k K) koo(a [1 + 2] int) [1 + 2] int {return [3*1] int {1,2,3};}
            type H interface {koo(a [1 + 2] int) [1 + 2] int;}

            const c = 4;
            func poop() [1 + 2] int{
                return poop()
                var k K;
                return k.koo([c - 1] int {1,2,3})
                var h H;
                return h.koo([c - 1] int {1,2,3})
            }
        """
        input = Program([StructType("K",[("a",IntType())],[]),MethodDecl("k",Id("K"),FuncDecl("koo",[ParamDecl("a",ArrayType([BinaryOp("+", IntLiteral(1), IntLiteral(2))],IntType()))],ArrayType([BinaryOp("+", IntLiteral(1), IntLiteral(2))],IntType()),Block([Return(ArrayLiteral([BinaryOp("*", IntLiteral(3), IntLiteral(1))],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3)]))]))),InterfaceType("H",[Prototype("koo",[ArrayType([BinaryOp("+", IntLiteral(1), IntLiteral(2))],IntType())],ArrayType([BinaryOp("+", IntLiteral(1), IntLiteral(2))],IntType()))]),ConstDecl("c",None,IntLiteral(4)),FuncDecl("poop",[],ArrayType([BinaryOp("+", IntLiteral(1), IntLiteral(2))],IntType()),Block([Return(FuncCall("poop",[])),VarDecl("k",Id("K"), None),Return(MethCall(Id("k"),"koo",[ArrayLiteral([BinaryOp("-", Id("c"), IntLiteral(1))],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3)])])),VarDecl("h",Id("H"), None),Return(MethCall(Id("h"),"koo",[ArrayLiteral([BinaryOp("-", Id("c"), IntLiteral(1))],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3)])]))]))])
        self.assertTrue(TestChecker.test(input, "", 342))

    def test_343(self):
        input =  """
            var v = 2 * 3;
            const a = v + 1;
            const b = a * 5;
            const c = ! (b > 3);
        """
        input = Program([VarDecl("v", None,BinaryOp("*", IntLiteral(2), IntLiteral(3))),ConstDecl("a",None,BinaryOp("+", Id("v"), IntLiteral(1))),ConstDecl("b",None,BinaryOp("*", Id("a"), IntLiteral(5))),ConstDecl("c",None,UnaryOp("!",BinaryOp(">", Id("b"), IntLiteral(3))))])
        self.assertTrue(TestChecker.test(input, "", 343))

    def test_344(self):
        input =  """
            func poop () {
                const a = 1;
                for a, b := range [3]int {1, 2, 3} {
                    var b = 1;
                }
        """
        input = Program([FuncDecl("poop",[],VoidType(),Block([ConstDecl("a",None,IntLiteral(1)),ForEach(Id("a"),Id("b"),ArrayLiteral([IntLiteral(3)],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3)]),Block([VarDecl("b", None,IntLiteral(1))]))]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: b", 344))

    def test_345(self):
        input =  """
            var a = -1;
            var b = -1.02;
            var c = - true;
        """
        input = Program([VarDecl("a", None,UnaryOp("-",IntLiteral(1))),VarDecl("b", None,UnaryOp("-",FloatLiteral(1.02))),VarDecl("c", None,UnaryOp("-",BooleanLiteral(True)))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: UnaryOp(-,BooleanLiteral(true))", 345))

    def test_346(self):
        input =  """
            var a [2][3][4] int;
            var b [3][4] int = a[1];
            var c [4] int = a[1][1];
            var d int = a[1][1][1];
        """
        input = Program([VarDecl("a",ArrayType([IntLiteral(2),IntLiteral(3),IntLiteral(4)],IntType()), None),VarDecl("b",ArrayType([IntLiteral(3),IntLiteral(4)],IntType()),ArrayCell(Id("a"),[IntLiteral(1)])),VarDecl("c",ArrayType([IntLiteral(4)],IntType()),ArrayCell(Id("a"),[IntLiteral(1),IntLiteral(1)])),VarDecl("d",IntType(),ArrayCell(Id("a"),[IntLiteral(1),IntLiteral(1),IntLiteral(1)]))])
        self.assertTrue(TestChecker.test(input, "", 346))

    def test_347(self):
        input =  """
            func poop() {
                a := 1;
                var a = 1;
            }
        """
        input = Program([FuncDecl("poop",[],VoidType(),Block([Assign(Id("a"),IntLiteral(1)),VarDecl("a", None,IntLiteral(1))]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: a", 347))

    def test_348(self):
        input =  """
            const a = 2;
            type STRUCT struct {x [a] int;}
            func (s STRUCT) poop(x [a] int) [a] int {return s.x;}
        """
        input = Program([ConstDecl("a",None,IntLiteral(2)),StructType("STRUCT",[("x",ArrayType([Id("a")],IntType()))],[]),MethodDecl("s",Id("STRUCT"),FuncDecl("poop",[ParamDecl("x",ArrayType([Id("a")],IntType()))],ArrayType([Id("a")],IntType()),Block([Return(FieldAccess(Id("s"),"x"))]))),FuncDecl("poop",[ParamDecl("x",ArrayType([Id("a")],IntType()))],ArrayType([Id("a")],IntType()),Block([ConstDecl("a",None,IntLiteral(3)),Return(ArrayLiteral([Id("a")],IntType(),[IntLiteral(1),IntLiteral(2)]))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: Return(ArrayLiteral([Id(a)],IntType,[IntLiteral(1),IntLiteral(2)]))", 348))

    def test_349(self):
        input =  """
            type CHEESE struct {
                Cheese int;
            }

            var a = 1;

            func (v CHEESE) poop (a, b int) {
                var a = 1;
            }

            func poop (a, b int) {
                var a = 1;
            }
        """
        input = Program([StructType("CHEESE",[("Cheese",IntType())],[]),VarDecl("a", None,IntLiteral(1)),MethodDecl("v",Id("CHEESE"),FuncDecl("poop",[ParamDecl("a",IntType()),ParamDecl("b",IntType())],VoidType(),Block([VarDecl("a", None,IntLiteral(1))]))),FuncDecl("poop",[ParamDecl("a",IntType()),ParamDecl("b",IntType())],VoidType(),Block([VarDecl("a", None,IntLiteral(1))]))])
        self.assertTrue(TestChecker.test(input, "", 349))


    def test_350(self):
        """
            func poop(){
                for var i int = 1; a < 10; i := 1.0 {
                    var a = 1;
                }
            }
        """
        input = Program([FuncDecl("poop",[],VoidType(),Block([ForStep(VarDecl("i",IntType(),IntLiteral(1)),BinaryOp("<", Id("a"), IntLiteral(10)),Assign(Id("i"),FloatLiteral(1.0)),Block([VarDecl("a", None,IntLiteral(1))]))]))])
        self.assertTrue(TestChecker.test(input, "Undeclared Identifier: a", 350))


    def test_351(self):
        """
            var sigma int;
            var gyatt float;
            var sigma int;
        """
        input = Program([VarDecl("sigma",IntType(),None),VarDecl("gyatt",FloatType(),None),VarDecl("sigma",IntType(),None)])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: sigma", 351))


    def test_352(self):
        """
            func Cheese (b int) {
                for var a = 1; cok < 1; a += cok {
                    const cok = 2;
                }
            }
        """
        input = Program([FuncDecl("Cheese",[ParamDecl("b",IntType())],VoidType(),Block([ForStep(VarDecl("a", None,IntLiteral(1)),BinaryOp("<", Id("cok"), IntLiteral(1)),Assign(Id("a"),BinaryOp("+", Id("a"), Id("cok"))),Block([ConstDecl("cok",None,IntLiteral(2))]))]))])
        self.assertTrue(TestChecker.test(input, """Undeclared Identifier: cok""", 352))

    def test_353(self):
        input="""
            var v CHEESE;
            func (v CHEESE) poop (v int) int {
                return v;
            }

            type CHEESE struct {
                Cheese int;
            }
        """
        input = Program([VarDecl("v",Id("CHEESE"), None),MethodDecl("v",Id("CHEESE"),FuncDecl("poop",[ParamDecl("v",IntType())],IntType(),Block([Return(Id("v"))]))),StructType("CHEESE",[("Cheese",IntType())],[])])
        self.assertTrue(TestChecker.test(input, "", 353))

    def test_354(self):
        input="""
            const a = 2;
            type STRUCT struct {x [a] int;}
            func (s STRUCT) poop(x [a] int) [a] int {return s.x;}
            func poop(x [a] int) [a] int  {
                const a = 3;
                return [a] int {1,2};
            }
        """
        input = Program([ConstDecl("a",None,IntLiteral(2)),StructType("STRUCT",[("x",ArrayType([Id("a")],IntType()))],[]),MethodDecl("s",Id("STRUCT"),FuncDecl("poop",[ParamDecl("x",ArrayType([Id("a")],IntType()))],ArrayType([Id("a")],IntType()),Block([Return(FieldAccess(Id("s"),"x"))]))),FuncDecl("poop",[ParamDecl("x",ArrayType([Id("a")],IntType()))],ArrayType([Id("a")],IntType()),Block([ConstDecl("a",None,IntLiteral(3)),Return(ArrayLiteral([Id("a")],IntType(),[IntLiteral(1),IntLiteral(2)]))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: Return(ArrayLiteral([Id(a)],IntType,[IntLiteral(1),IntLiteral(2)]))", 354))

    def test_355(self):
        """
            var Cheese = 1; 
            var Cheese = 2;
        """
        input = Program([VarDecl("Cheese", None,IntLiteral(1)),VarDecl("Cheese", None,IntLiteral(2))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: Cheese", 355))

    def test_356(self):
        """
            var Cheese = 1; 
            const Cheese = 2;
        """
        input = Program([VarDecl("Cheese", None,IntLiteral(1)),ConstDecl("Cheese",None,IntLiteral(2))])
        self.assertTrue(TestChecker.test(input, "Redeclared Constant: Cheese", 356))
        
    def test_357(self):
        """
            const Cheese = 1; 
            var Cheese = 2;
        """
        input = Program([ConstDecl("Cheese",None,IntLiteral(1)),VarDecl("Cheese", None,IntLiteral(2))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: Cheese", 357))

    def test_358(self):
        """
            func Cheese () {return;}
            var Cheese = 1;
        """
        input = Program([FuncDecl("Cheese",[],VoidType(),Block([Return(None)])),VarDecl("Cheese", None,IntLiteral(1))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: Cheese", 358))
        
    def test_359(self):
        """
            func (v CHEESE) putIntLn () {return;}
            func (v CHEESE) getInt () {return;}
            func (v CHEESE) getInt () {return;}
            type CHEESE struct {
                Cheese int;
            }
        """
        input = Program([MethodDecl("v",Id("CHEESE"),FuncDecl("putIntLn",[],VoidType(),Block([Return(None)]))),MethodDecl("v",Id("CHEESE"),FuncDecl("getInt",[],VoidType(),Block([Return(None)]))),MethodDecl("v",Id("CHEESE"),FuncDecl("getInt",[],VoidType(),Block([Return(None)]))),StructType("CHEESE",[("Cheese",IntType())],[])])
        self.assertTrue(TestChecker.test(input, "Redeclared Method: getInt", 359))
    
    def test_360(self):
        """
            func Cheese (b int) {
                for var a = 1; a < 1; a += 1 {
                    const a = 2;
                }
            }
        """
        input = Program([FuncDecl("Cheese",[ParamDecl("b",IntType())],VoidType(),Block([ForStep(VarDecl("a", None,IntLiteral(1)),BinaryOp("<", Id("a"), IntLiteral(1)),Assign(Id("a"),BinaryOp("+", Id("a"), IntLiteral(1))),Block([ConstDecl("a",None,IntLiteral(2))]))]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Constant: a", 360))
        
    def test_361(self):
        """
            type CHEESE struct {
                Cheese int;
            }

            func (v CHEESE) getInt () {
                v.getInt ();
                v.putInt ();
        """
        input = Program([StructType("CHEESE",[("Cheese",IntType())],[]),MethodDecl("v",Id("CHEESE"),FuncDecl("getInt",[],VoidType(),Block([MethCall(Id("v"),"getInt",[]),MethCall(Id("v"),"putInt",[])])))])
        self.assertTrue(TestChecker.test(input, "Undeclared Method: putInt", 361))
    
    def test_362(self):
        """
            var poop = 1;
            func poop() {return;}
        """
        input = Program([VarDecl("poop", None,IntLiteral(1)),FuncDecl("poop",[],VoidType(),Block([Return(None)]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Function: poop", 362))

    def test_363(self):
        """
            type CHEESE struct {
                Cheese int;
            }
            func (v CHEESE) poop (v int) {return;}
            func poop () {return;}
        """
        input = Program([StructType("CHEESE",[("Cheese",IntType())],[]),MethodDecl("v",Id("CHEESE"),FuncDecl("poop",[ParamDecl("v",IntType())],VoidType(),Block([Return(None)]))),FuncDecl("poop",[],VoidType(),Block([Return(None)]))])
        self.assertTrue(TestChecker.test(input, "", 363))
        
    def test_364(self):
        """
            const a = 2;
            func poop () {
                const a = 1;
                // b := 2 <=> var b = 2
                for var a = 1; a < 1; b := 2 {
                    const b = 1;
                }
            }
        """
        input = Program([ConstDecl("a",None,IntLiteral(2)),FuncDecl("poop",[],VoidType(),Block([ConstDecl("a",None,IntLiteral(1)),ForStep(VarDecl("a", None,IntLiteral(1)),BinaryOp("<", Id("a"), IntLiteral(1)),Assign(Id("b"),IntLiteral(2)),Block([ConstDecl("b",None,IntLiteral(1))]))]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Constant: b", 364))
        
    def test_365(self):
        """
            var v CHEESE;
            const b = v.poop();        
            type CHEESE struct {
                a int;
            }
            func (v CHEESE) poop() int {return 1;}
            func (v CHEESE) koo() int {return 1;}
            const c = v.koo();  
            const d = v.zoo();
        """
        input = Program([VarDecl("v",Id("CHEESE"), None),ConstDecl("b",None,MethCall(Id("v"),"poop",[])),StructType("CHEESE",[("a",IntType())],[]),MethodDecl("v",Id("CHEESE"),FuncDecl("poop",[],IntType(),Block([Return(IntLiteral(1))]))),MethodDecl("v",Id("CHEESE"),FuncDecl("koo",[],IntType(),Block([Return(IntLiteral(1))]))),ConstDecl("c",None,MethCall(Id("v"),"koo",[])),ConstDecl("d",None,MethCall(Id("v"),"zoo",[]))])
        self.assertTrue(TestChecker.test(input, "Undeclared Method: zoo", 365))
        
    def test_366(self):
        """
            var v float = 1;
        """    
        input = Program([VarDecl("v",FloatType(),IntLiteral(1))])
        self.assertTrue(TestChecker.test(input, "", 366))
    
    def test_367(self):
        """
            type Skibidi struct {Cheese int;}
            type Smol struct {Cheese int;}

            var v Skibidi;
            const x = v;
            var z Skibidi = x;
            var k Smol = x;
        """
        input = Program([StructType("Skibidi",[("Cheese",IntType())],[]),StructType("Smol",[("Cheese",IntType())],[]),VarDecl("v",Id("Skibidi"), None),ConstDecl("x",None,Id("v")),VarDecl("z",Id("Skibidi"),Id("x")),VarDecl("k",Id("Smol"),Id("x"))])
        output = """Type Mismatch: VarDecl(k,Id(Smol),Id(x))"""
        self.assertTrue(TestChecker.test(input, output, 367))
        
    def test_368(self):
        """
            type Skibidi struct {Cheese int;}
            type Smol struct {Cheese int;}
            type Toilet interface {Cheese1();}
            type Amongus interface {Cheese1();}

            func (s Skibidi) Cheese1() {return;}

            var a Skibidi;
            var b Smol;
            var c Toilet = a;
            var d Amongus = b;
        """
        input = Program([StructType("Skibidi",[("Cheese",IntType())],[]),StructType("Smol",[("Cheese",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese1",[],VoidType())]),InterfaceType("Amongus",[Prototype("Cheese1",[],VoidType())]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese1",[],VoidType(),Block([Return(None)]))),VarDecl("a",Id("Skibidi"), None),VarDecl("b",Id("Smol"), None),VarDecl("c",Id("Toilet"),Id("a")),VarDecl("d",Id("Amongus"),Id("b"))])
        output = """Type Mismatch: VarDecl(d,Id(Amongus),Id(b))"""
        self.assertTrue(TestChecker.test(input, output, 368))
        
    def test_369(self):
        """
            type Skibidi struct {Cheese int;}
            type Smol struct {Cheese int;}
            type Toilet interface {Cheese1() Skibidi;}
            type Amongus interface {Cheese1() Smol;}

            func (s Skibidi) Cheese1() Skibidi {return s;}

            var a Skibidi;
            var c Toilet = a;
            var d Amongus = a;
        """
        input = Program([StructType("Skibidi",[("Cheese",IntType())],[]),StructType("Smol",[("Cheese",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese1",[],Id("Skibidi"))]),InterfaceType("Amongus",[Prototype("Cheese1",[],Id("Smol"))]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese1",[],Id("Skibidi"),Block([Return(Id("s"))]))),VarDecl("a",Id("Skibidi"), None),VarDecl("c",Id("Toilet"),Id("a")),VarDecl("d",Id("Amongus"),Id("a"))])
        output = """Type Mismatch: VarDecl(d,Id(Amongus),Id(a))"""
        self.assertTrue(TestChecker.test(input, output, 369))
        
    def test_370(self):
        """
            func poop(){
                if (true) {
                    var a float = 1.02;
                } else {
                    var a int = 1.02;
                }
            }
        """
        input = Program([FuncDecl("poop",[],VoidType(),Block([If(BooleanLiteral(True), Block([VarDecl("a",FloatType(),FloatLiteral(1.02))]), Block([VarDecl("a",IntType(),FloatLiteral(1.02))]))]))])
        output = """Type Mismatch: VarDecl(a,IntType,FloatLiteral(1.02))"""
        self.assertTrue(TestChecker.test(input, output, 370))
        
    def test_371(self):
        """
            func poop(){
                return
            }
            func poop1() int{
                return 1
            }
            func poop2() float{
                return 2
            }
        """
        input = Program([FuncDecl("poop",[],VoidType(),Block([Return(None)])),FuncDecl("poop1",[],IntType(),Block([Return(IntLiteral(1))])),FuncDecl("poop2",[],FloatType(),Block([Return(IntLiteral(2))]))])
        output = """Type Mismatch: Return(IntLiteral(2))"""
        self.assertTrue(TestChecker.test(input, output, 371))
        
    def test_372(self):
        """
            type Skibidi struct {Cheese1 int;}
            type Toilet interface {Cheese();}

            func (s Skibidi) Cheese() {return;}

            func poop() Skibidi {
                var a Skibidi;
                return a
            }

            func poop1() Toilet {
                var a Toilet;
                return a
            }

            func poop2() Skibidi {
                var b Toilet;
                return b
            }
        """
        input = Program([StructType("Skibidi",[("Cheese1",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],VoidType())]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese",[],VoidType(),Block([Return(None)]))),FuncDecl("poop",[],Id("Skibidi"),Block([VarDecl("a",Id("Skibidi"), None),Return(Id("a"))])),FuncDecl("poop1",[],Id("Toilet"),Block([VarDecl("a",Id("Toilet"), None),Return(Id("a"))])),FuncDecl("poop2",[],Id("Skibidi"),Block([VarDecl("b",Id("Toilet"), None),Return(Id("b"))]))])
        output = """Type Mismatch: Return(Id(b))"""
        self.assertTrue(TestChecker.test(input, output, 372))

    def test_373(self):
        """ 
            const a = 2;
            func poop () {
                const a = 1;
                for a < 1 {
                    const a = 1;
                    for a < 1 {
                        const a = 1;
                        const b = 1;
                    }
                    const b = 1;
                    var a = 1;
                }
            }
        """
        input = Program([ConstDecl("a",None,IntLiteral(2)),FuncDecl("poop",[],VoidType(),Block([ConstDecl("a",None,IntLiteral(1)),ForBasic(BinaryOp("<", Id("a"), IntLiteral(1)),Block([ConstDecl("a",None,IntLiteral(1)),ForBasic(BinaryOp("<", Id("a"), IntLiteral(1)),Block([ConstDecl("a",None,IntLiteral(1)),ConstDecl("b",None,IntLiteral(1))])),ConstDecl("b",None,IntLiteral(1)),VarDecl("a", None,IntLiteral(1))]))]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: a", 373))
    
    def test_374(self):
        """ 
            func poop () {
                const a = 1;
                for a, b := range [3]int {1, 2, 3} {
                    var b = 1;
                }
            }
        """
        input = Program([FuncDecl("poop",[],VoidType(),Block([ConstDecl("a",None,IntLiteral(1)),ForEach(Id("a"),Id("b"),ArrayLiteral([IntLiteral(3)],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3)]),Block([VarDecl("b", None,IntLiteral(1))]))]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: b", 374))
    
    def test_375(self):
        """ 
            const a = 2;
            func poop () {
                const a = 1;
                for var a = 1; a < 1; b := 2 {
                    const b = 1;
                }
            }
        """
        input = Program([ConstDecl("a",None,IntLiteral(2)),FuncDecl("poop",[],VoidType(),Block([ConstDecl("a",None,IntLiteral(1)),ForStep(VarDecl("a", None,IntLiteral(1)),BinaryOp("<", Id("a"), IntLiteral(1)),Assign(Id("b"),IntLiteral(2)),Block([ConstDecl("b",None,IntLiteral(1))]))]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Constant: b", 375))
        
    def test_376(self):
        """ 
            var v CHEESE;
            const b = v.b;        
            type CHEESE struct {
                a int;
                b int;
                c int;
            }
            const a = v.a;
            const e = v.e;
        """
        input = Program([VarDecl("v",Id("CHEESE"), None),ConstDecl("b",None,FieldAccess(Id("v"),"b")),StructType("CHEESE",[("a",IntType()),("b",IntType()),("c",IntType())],[]),ConstDecl("a",None,FieldAccess(Id("v"),"a")),ConstDecl("e",None,FieldAccess(Id("v"),"e"))])
        self.assertTrue(TestChecker.test(input, "Undeclared Field: e", 376))
        
    def test_377(self):
        """ 
            type CHEESE struct {
                Cheese int;
            }
            func (v CHEESE) poop (a, b int) {return;}
            func poop (a, a int) {return;}
        """
        input = Program([StructType("CHEESE",[("Cheese",IntType())],[]),MethodDecl("v",Id("CHEESE"),FuncDecl("poop",[ParamDecl("a",IntType()),ParamDecl("b",IntType())],VoidType(),Block([Return(None)]))),FuncDecl("poop",[ParamDecl("a",IntType()),ParamDecl("a",IntType())],VoidType(),Block([Return(None)]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Parameter: a", 377))
    
    def test_378(self):
        """ 
            var v CHEESE;
            type CHEESE struct {
                a int;
            } 
            type VO interface {
                poop() int;
            }

            func (v CHEESE) poop() int {return 1;}
            func (b CHEESE) koo() {b.koo();}
            func poop() {
                var x VO;  
                const b = x.poop(); 
                x.koo(); 
            }
        """
        input = Program([VarDecl("v",Id("CHEESE"), None),StructType("CHEESE",[("a",IntType())],[]),InterfaceType("VO",[Prototype("poop",[],IntType())]),MethodDecl("v",Id("CHEESE"),FuncDecl("poop",[],IntType(),Block([Return(IntLiteral(1))]))),MethodDecl("b",Id("CHEESE"),FuncDecl("koo",[],VoidType(),Block([MethCall(Id("b"),"koo",[])]))),FuncDecl("poop",[],VoidType(),Block([VarDecl("x",Id("VO"), None),ConstDecl("b",None,MethCall(Id("x"),"poop",[])),MethCall(Id("x"),"koo",[])]))])
        self.assertTrue(TestChecker.test(input, "Undeclared Method: koo", 378))
    
    def test_379(self):
        """ 
            var a = poop();
            func poop () int {
                var a =  koo();
                var c = getInt();
                putInt(c);
                putIntLn(c);
                return 1;
            }
            var d = poop();
            func koo () int {
                var a =  poop ();
                return 1;
            }
        """
        input = Program([VarDecl("a", None,FuncCall("poop",[])),FuncDecl("poop",[],IntType(),Block([VarDecl("a", None,FuncCall("koo",[])),VarDecl("c", None,FuncCall("getInt",[])),FuncCall("putInt",[Id("c")]),FuncCall("putIntLn",[Id("c")]),Return(IntLiteral(1))])),VarDecl("d", None,FuncCall("poop",[])),FuncDecl("koo",[],IntType(),Block([VarDecl("a", None,FuncCall("poop",[])),Return(IntLiteral(1))]))])

        self.assertTrue(TestChecker.test(input, "", 379))
    
    def test_380(self):
        """ 
            type Skibidi struct {LockIn int;}
            type Smol struct {LockIn int;}
            type Toilet interface {Cheese();}
            type Amongus interface {Cheese();}

            func (s Skibidi) Cheese() {return;}

            var a Skibidi;
            var b Smol;
            var c Toilet = a;
            var d Amongus = b;
        """
        input = Program([StructType("Skibidi",[("LockIn",IntType())],[]),StructType("Smol",[("LockIn",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],VoidType())]),InterfaceType("Amongus",[Prototype("Cheese",[],VoidType())]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese",[],VoidType(),Block([Return(None)]))),VarDecl("a",Id("Skibidi"), None),VarDecl("b",Id("Smol"), None),VarDecl("c",Id("Toilet"),Id("a")),VarDecl("d",Id("Amongus"),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,Id(Amongus),Id(b))", 380))
    
    def test_381(self):
        """ 
            type Skibidi struct {LockIn int;}
            type Smol struct {LockIn int;}
            type Toilet interface {Cheese();}
            type Amongus interface {Cheese() int;}

            func (s Skibidi) Cheese() {return;}

            var a Skibidi;
            var b Smol;
            var c Amongus = a;
        """
        input = Program([StructType("Skibidi",[("LockIn",IntType())],[]),StructType("Smol",[("LockIn",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],VoidType())]),InterfaceType("Amongus",[Prototype("Cheese",[],IntType())]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese",[],VoidType(),Block([Return(None)]))),VarDecl("a",Id("Skibidi"), None),VarDecl("b",Id("Smol"), None),VarDecl("c",Id("Amongus"),Id("a"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(c,Id(Amongus),Id(a))", 381))
    
    def test_382(self):
        """ 
            type Skibidi struct {LockIn int;}
            type Smol struct {LockIn int;}
            type Toilet interface {Cheese() Skibidi;}
            type Amongus interface {Cheese() Smol;}

            func (s Skibidi) Cheese() Skibidi {return s;}

            var a Skibidi;
            var c Toilet = a;
            var d Amongus = a;
        """
        input = Program([StructType("Skibidi",[("LockIn",IntType())],[]),StructType("Smol",[("LockIn",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],Id("Skibidi"))]),InterfaceType("Amongus",[Prototype("Cheese",[],Id("Smol"))]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese",[],Id("Skibidi"),Block([Return(Id("s"))]))),VarDecl("a",Id("Skibidi"), None),VarDecl("c",Id("Toilet"),Id("a")),VarDecl("d",Id("Amongus"),Id("a"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,Id(Amongus),Id(a))", 382))
    
    def test_383(self):
        """ 
            type Skibidi struct {LockIn int;}
            type Smol struct {LockIn int;}
            type Toilet interface {Cheese(e, e int) Skibidi;}
            type Amongus interface {Cheese(a int) Skibidi;}

            func (s Skibidi) Cheese(a, b int) Skibidi {return s;}

            var a Skibidi;
            var c Toilet = a;
            var d Amongus = a;
        """
        input = Program([StructType("Skibidi",[("LockIn",IntType())],[]),StructType("Smol",[("LockIn",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[IntType(),IntType()],Id("Skibidi"))]),InterfaceType("Amongus",[Prototype("Cheese",[IntType()],Id("Skibidi"))]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese",[ParamDecl("a",IntType()),ParamDecl("b",IntType())],Id("Skibidi"),Block([Return(Id("s"))]))),VarDecl("a",Id("Skibidi"), None),VarDecl("c",Id("Toilet"),Id("a")),VarDecl("d",Id("Amongus"),Id("a"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,Id(Amongus),Id(a))", 383))
    
    def test_384(self):
        """ 
            type Skibidi struct {LockIn int;}
            type Smol struct {LockIn int;}
            type Toilet interface {Cheese(e, e int) Skibidi;}
            type Amongus interface {Cheese(a int, b float) Skibidi;}

            func (s Skibidi) Cheese(a, b int) Skibidi {return s;}

            var a Skibidi;
            var c Toilet = a;
            var d Amongus = a;
        """
        input = Program([StructType("Skibidi",[("LockIn",IntType())],[]),StructType("Smol",[("LockIn",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[IntType(),IntType()],Id("Skibidi"))]),InterfaceType("Amongus",[Prototype("Cheese",[IntType(),FloatType()],Id("Skibidi"))]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese",[ParamDecl("a",IntType()),ParamDecl("b",IntType())],Id("Skibidi"),Block([Return(Id("s"))]))),VarDecl("a",Id("Skibidi"), None),VarDecl("c",Id("Toilet"),Id("a")),VarDecl("d",Id("Amongus"),Id("a"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,Id(Amongus),Id(a))", 384))
    
    def test_385(self):
        """ 
            func poop(){
                if (true) {
                    var a float = 1.02;
                } else {
                    var a int = 1.02;
                }
            }
        """
        input = Program([FuncDecl("poop",[],VoidType(),Block([If(BooleanLiteral(True), Block([VarDecl("a",FloatType(),FloatLiteral(1.02))]), Block([VarDecl("a",IntType(),FloatLiteral(1.02))]))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(a,IntType,FloatLiteral(1.02))", 385))
   
    def test_386(self):
        """ 
            type Skibidi struct {v int; t int;}

            var a = Skibidi {v : 1, t: 2}
            var b Skibidi = a;
            var c int = b;
        """
        input = Program([StructType("Skibidi",[("v",IntType()),("t",IntType())],[]),VarDecl("a", None,StructLiteral("Skibidi",[("v",IntLiteral(1)),("t",IntLiteral(2))])),VarDecl("b",Id("Skibidi"),Id("a")),VarDecl("c",IntType(),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(c,IntType,Id(b))", 386))
    
    def test_387(self):
        """ 
            var a = [2] int {1, 2}
            var c [2] float = a
        """
        input = Program([VarDecl("a", None,ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)])),VarDecl("c",ArrayType([IntLiteral(2)],FloatType()),Id("a"))])
        self.assertTrue(TestChecker.test(input, "", 387))
    
    def test_388(self):
        """ 
            var a [2][3] int;
            var b = a[1][2];
            var c int = b;
            var d [1] string = b;
        """
        input = Program([VarDecl("a",ArrayType([IntLiteral(2),IntLiteral(3)],IntType()), None),VarDecl("b", None,ArrayCell(Id("a"),[IntLiteral(1),IntLiteral(2)])),VarDecl("c",IntType(),Id("b")),VarDecl("d",ArrayType([IntLiteral(1)],StringType()),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,ArrayType(StringType,[IntLiteral(1)]),Id(b))", 388))
    
    def test_389(self):
        """ 
            var a [2][3] int;
            var b = a[1];
            var c [3] int = b;
            var d [3] string = b;
        """
        input = Program([VarDecl("a",ArrayType([IntLiteral(2),IntLiteral(3)],IntType()), None),VarDecl("b", None,ArrayCell(Id("a"),[IntLiteral(1)])),VarDecl("c",ArrayType([IntLiteral(3)],IntType()),Id("b")),VarDecl("d",ArrayType([IntLiteral(3)],StringType()),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,ArrayType(StringType,[IntLiteral(3)]),Id(b))", 389))
    
    def test_390(self):
        """ 
            var a [2][3] int;
            var b = a[1.0];
        """
        input = Program([VarDecl("a",ArrayType([IntLiteral(2),IntLiteral(3)],IntType()), None),VarDecl("b", None,ArrayCell(Id("a"),[FloatLiteral(1.0)]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: ArrayCell(Id(a),[FloatLiteral(1.0)])", 390))
    
    def test_391(self):
        """ 
            type Skibidi struct {v int; x Skibidi;}
            var b Skibidi;
            var c = b.x.v;
            var d = c.x;
        """
        input = Program([StructType("Skibidi",[("v",IntType()),("x",Id("Skibidi"))],[]),VarDecl("b",Id("Skibidi"), None),VarDecl("c", None,FieldAccess(FieldAccess(Id("b"),"x"),"v")),VarDecl("d", None,FieldAccess(Id("c"),"x"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: FieldAccess(Id(c),x)", 391))
    
    def test_392(self):
        """ 
            type Skibidi struct {Cheese int;}
            type Toilet interface {Cheese();}
            var a Toilet;
            var c Toilet = nil;
            var d Skibidi = nil;
            func poop(){
                c := a;
                a := nil;
            }

            var e int = nil;
        """
        input = Program([StructType("Skibidi",[("Cheese",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],VoidType())]),VarDecl("a",Id("Toilet"), None),VarDecl("c",Id("Toilet"),NilLiteral()),VarDecl("d",Id("Skibidi"),NilLiteral()),FuncDecl("poop",[],VoidType(),Block([Assign(Id("c"),Id("a")),Assign(Id("a"),NilLiteral())])),VarDecl("e",IntType(),NilLiteral())])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(e,IntType,Nil)", 392))
    
    def test_393(self):
        """ 
            var a = ! true;
            var b = ! 1;
        """
        input = Program([VarDecl("a", None,UnaryOp("!",BooleanLiteral(True))),VarDecl("b", None,UnaryOp("!",IntLiteral(1)))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: UnaryOp(!,IntLiteral(1))", 393))
    
    def test_394(self):
        """ 
            func poop(){
                var arr [2] int;
                for a, b := range arr {
                    var c int = a;
                    var d int = b;
                    var e string = a;
                }
            }
        """
        input = Program([FuncDecl("poop",[],VoidType(),Block([VarDecl("arr",ArrayType([IntLiteral(2)],IntType()), None),ForEach(Id("a"),Id("b"),Id("arr"),Block([VarDecl("c",IntType(),Id("a")),VarDecl("d",IntType(),Id("b")),VarDecl("e",StringType(),Id("a"))]))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(e,StringType,Id(a))", 394))
    
    def test_395(self):
        """ 
            func poop(){
                var arr [2][3] int;
                for a, b := range arr {
                    var c int = a;
                    var d [3]int = b;
                    var e [2]string = a;
                }
            }
        """
        input = Program([FuncDecl("poop",[],VoidType(),Block([VarDecl("arr",ArrayType([IntLiteral(2),IntLiteral(3)],IntType()), None),ForEach(Id("a"),Id("b"),Id("arr"),Block([VarDecl("c",IntType(),Id("a")),VarDecl("d",ArrayType([IntLiteral(3)],IntType()),Id("b")),VarDecl("e",ArrayType([IntLiteral(2)],StringType()),Id("a"))]))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(e,ArrayType(StringType,[IntLiteral(2)]),Id(a))", 395))
    
    def test_396(self):
        """ 
            type Skibidi struct {LockIn int;}
            type Toilet interface {Cheese() int;}
            func (s Skibidi) Cheese() int {return 1;}

            var i Toilet;
            var s Skibidi;
            var a int = i.Cheese();
            var b int = s.Cheese();
            var c int = a.Cheese();
        """
        input = Program([StructType("Skibidi",[("LockIn",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],IntType())]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese",[],IntType(),Block([Return(IntLiteral(1))]))),VarDecl("i",Id("Toilet"), None),VarDecl("s",Id("Skibidi"), None),VarDecl("a",IntType(),MethCall(Id("i"),"Cheese",[])),VarDecl("b",IntType(),MethCall(Id("s"),"Cheese",[])),VarDecl("c",IntType(),MethCall(Id("a"),"Cheese",[]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: MethodCall(Id(a),Cheese,[])", 396))
    
    def test_397(self):
        """ 
            type Skibidi struct {LockIn int;}
            func (s Skibidi) Cheese() int {
                s.Cheese();
                return 1;
            }
        """
        input = Program([StructType("Skibidi",[("LockIn",IntType())],[]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese",[],IntType(),Block([MethCall(Id("s"),"Cheese",[]),Return(IntLiteral(1))])))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: MethodCall(Id(s),Cheese,[])", 397))
    
    def test_398(self):
        """ 
            func poop() [2] float {
                return [2] float {1.0, 2.0};
                return [2] int {1, 2};
            }
        """
        input = Program([FuncDecl("poop",[],ArrayType([IntLiteral(2)],FloatType()),Block([Return(ArrayLiteral([IntLiteral(2)],FloatType(),[FloatLiteral(1.0),FloatLiteral(2.0)])),Return(ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)]))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: Return(ArrayLiteral([IntLiteral(2)],IntType,[IntLiteral(1),IntLiteral(2)]))", 398))
    
    def test_399(self):
        """ 
            type CHEESE struct {a [2]int;} 
            type VO interface {poop() int;}

            func (v CHEESE) poop() int {return 1;}

            func poop(a VO) {
                var b VO = CHEESE{a: [2]int{1, 2}};
                poop(b)
            }
        """
        input = Program([StructType("CHEESE",[("a",ArrayType([IntLiteral(2)],IntType()))],[]),InterfaceType("VO",[Prototype("poop",[],IntType())]),MethodDecl("v",Id("CHEESE"),FuncDecl("poop",[],IntType(),Block([Return(IntLiteral(1))]))),FuncDecl("poop",[ParamDecl("a",Id("VO"))],VoidType(),Block([VarDecl("b",Id("VO"),StructLiteral("CHEESE",[("a",ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)]))])),FuncCall("poop",[Id("b")])]))])
        self.assertTrue(TestChecker.test(input, "", 399))

    def test_400(self):
        """ 
            type Skibidi struct {LockIn int;}
            type Toilet interface {Cheese();}

            func (s Skibidi) Cheese() {return;}

            var b [2] Skibidi;
            var a [2] Toilet = b;
        """
        input = Program([StructType("Skibidi",[("LockIn",IntType())],[]),InterfaceType("Toilet",[Prototype("Cheese",[],VoidType())]),MethodDecl("s",Id("Skibidi"),FuncDecl("Cheese",[],VoidType(),Block([Return(None)]))),VarDecl("b",ArrayType([IntLiteral(2)],Id("Skibidi")), None),VarDecl("a",ArrayType([IntLiteral(2)],Id("Toilet")),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(a,ArrayType(Id(Toilet),[IntLiteral(2)]),Id(b))", 401))