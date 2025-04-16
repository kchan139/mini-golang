import unittest
from TestUtils import TestParser


class ParserSuite(unittest.TestCase):

    def test_101(self):
        """Literal: constant int declaration"""
        self.assertTrue(
            TestParser.test("const Toilet = 1;", "successful", 101)
        )

    def test_102(self):
        """Literal: constant boolean declaration"""
        self.assertTrue(
            TestParser.test("const Toilet = true;", "successful", 102)
        )

    def test_103(self):
        """Literal: array literal in constant declaration"""
        self.assertTrue(
            TestParser.test('const Toilet = [5][0]string{1, "string"};', "successful", 103)
        )

    def test_104(self):
        """Error: illegal float literal in array type"""
        self.assertTrue(
            TestParser.test("const Toilet = [1.]ID{1, 3};", "Error on line 1 col 16: 1.", 104)
        )

    def test_105(self):
        """Literal: struct literal constant declaration"""
        self.assertTrue(
            TestParser.test('const Toilet = Person{name: "Alice", age: 30};', "successful", 105)
        )

    def test_106(self):
        """Expression: mix of logical, arithmetic and unary operators"""
        self.assertTrue(
            TestParser.test("const Toilet = 1 || 2 && c + 3 / 2 - -1;", "successful", 106)
        )

    def test_107(self):
        """Expression: array accesses and field accesses"""
        self.assertTrue(
            TestParser.test("const Toilet = 1[2] + foo()[2] + ID[2].b.b;", "successful", 107)
        )

    def test_108(self):
        """Expression: function call with field access in expression"""
        self.assertTrue(
            TestParser.test("const Toilet = ca.foo(132) + b.c[2];", "successful", 108)
        )

    def test_109(self):
        """Expression: chained field access with function call"""
        self.assertTrue(
            TestParser.test("const Toilet = a.a.foo();", "successful", 109)
        )

    def test_110(self):
        """Declaration: multiple variable declarations"""
        input_str = """
            var x int = foo() + 3 / 4;
            var y = "Hello" / 4;   
            var z str;
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 110)
        )

    def test_111(self):
        """Declaration: constant expression with function call"""
        self.assertTrue(
            TestParser.test("const Toilet = a.b() + 2;", "successful", 111)
        )

    def test_112(self):
        """Declaration: multiple function declarations with different return types"""
        input_str = """
            func Toilet(x int, y int) int {return;}
            func Toilet1() [2][3] ID {return;};
            func Toilet2() {return;}
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 112)
        )

    def test_113(self):
        """Declaration: multiple method declarations"""
        input_str = """
            func (c Calculator) Toilet(x int) int {return;};
            func (c Calculator) Toilet() ID {return;};
            func (c Calculator) Toilet(x int, y [2]Toilet) {return;};
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 113)
        )

    def test_114(self):
        """Declaration: struct type declaration"""
        input_str = """
            type Toilet struct {
                Toilet string;
                Toilet [1][3]Toilet;
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 114)
        )

    def test_115(self):
        """Error: struct declaration with empty body"""
        input_str = """
            type Toilet struct {}
        """
        self.assertTrue(
            TestParser.test(input_str, "Error on line 2 col 32: }", 115)
        )

    def test_116(self):
        """Error: interface declaration with extra closing brace"""
        input_str = """
            type Calculator interface {
                Add(x, y int) int;
                Subtract(a, b float, c int) [3]ID;
                Reset()
                SayHello(name string);
            }
            type Toilet interface {}
        """
        self.assertTrue(
            TestParser.test(input_str, "Error on line 8 col 35: }", 116)
        )

    def test_117(self):
        """Declaration: function with inner declarations"""
        input_str = """
            func Toilet() {
                var x int = foo() + 3 / 4;
                var y = "Hello" / 4;
                var z str;
                const Toilet = a.b() + 2;
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 117)
        )

    def test_118(self):
        """Statement: assignment using short declaration and field indexing"""
        input_str = """
            func Toilet() {
                x := foo() + 3 / 4;
                x.c[2][4] := 1 + 2;
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 118)
        )

    def test_119(self):
        """Statement: if-else-if statement with nested declarations"""
        input_str = """
            func Toilet() {
                if (x > 10) {return;}
                if (x > 10) {
                  return;
                } else if (x == 10) {
                    var z str;
                } else {
                    var z ID;
                }
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 119)
        )

    def test_120(self):
        """Statement: various forms of for loops"""
        input_str = """
            func Toilet() {
                for i < 10 {return;}
                for i := 0; i < 10; i += 1 {return;}
                for index, value := range array {return;}
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 120)
        )

    def test_121(self):
        """Statement: break, continue, return and call statements"""
        input_str = """
            func Toilet() {
                for i < 10 {break;}
                break;
                continue;
                return 1;
                return;
                foo(2 + x, 14 / y); m.goo();
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 121)
        )

    def test_122(self):
        """Literal: binary integer literal"""
        self.assertTrue(
            TestParser.test("const a = 0b11;", "successful", 122)
        )

    def test_123(self):
        """Error: invalid array literal element type"""
        self.assertTrue(
            TestParser.test("var z Toilet = [true]int{1};", "Error on line 1 col 16: true", 123)
        )

    def test_124(self):
        """Expression: identifier followed by empty block (interpreted as a struct literal)"""
        self.assertTrue(
            TestParser.test("var z Toilet = ID {};", "successful", 124)
        )

    def test_125(self):
        """Expression: nested struct literal in variable initialization"""
        self.assertTrue(
            TestParser.test("var z Toilet = ID {a: 2, b: 2 + 2 + ID {a: 1}};", "successful", 125)
        )

    def test_126(self):
        """Expression: multiple logical operators"""
        self.assertTrue(
            TestParser.test("var z Toilet = 1 && 2 && 3 || 1 || 1;", "successful", 126)
        )

    def test_127(self):
        """Expression: mixed relational operators with array and struct literals"""
        self.assertTrue(
            TestParser.test("var z Toilet = a >= 2 <= \"string\" > a[2][3] < ID{A: 2} >= [2]S{2};", "successful", 127)
        )

    def test_128(self):
        """Expression: chained field accesses"""
        self.assertTrue(
            TestParser.test("var z Toilet = a.b.a.c.e.g;", "successful", 128)
        )

    def test_129(self):
        """Expression: nested array indexing with expression"""
        self.assertTrue(
            TestParser.test("var z Toilet = a[2][3][a + 2];", "successful", 129)
        )

    def test_130(self):
        """Expression: function call on an array element in a chained expression"""
        self.assertTrue(
            TestParser.test("var z Toilet = a.a.a[2].foo(1);", "successful", 130)
        )

    def test_131(self):
        """Expression: chained function and array call"""
        self.assertTrue(
            TestParser.test("var z Toilet = foo().a[2].goo();", "successful", 131)
        )

    def test_132(self):
        """Expression: use of multiple unary operators"""
        self.assertTrue(
            TestParser.test("const k = -a + -!-!c - ---[2]int{2};", "successful", 132)
        )

    def test_133(self):
        """Declaration: array variable without initializer"""
        self.assertTrue(
            TestParser.test("var c [2][3]ID;", "successful", 133)
        )

    def test_134(self):
        """Error: constant declaration with missing initializer"""
        self.assertTrue(
            TestParser.test("const a =;", "Error on line 1 col 9: ;", 134)
        )

    def test_135(self):
        """Declaration: function with array parameter and array return type"""
        self.assertTrue(
            TestParser.test("func Add(x int, y [2]int) [2]id {return ;};", "successful", 135)
        )

    def test_136(self):
        """Declaration: function with no parameter and no return type"""
        self.assertTrue(
            TestParser.test("func Add() {return ;};", "successful", 136)
        )

    def test_137(self):
        """Declaration: struct type with multiple fields"""
        input_str = """
            type Calculator struct {
                value int;
                a [2]int; a [2]ID;
                c Calculator
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 137)
        )

    def test_138(self):
        """Error: struct field declared with assignment (not allowed)"""
        input_str = """
            type Calculator struct {
                a int = 2;
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "Error on line 3 col 22: =", 138)
        )

    def test_139(self):
        """Declaration: interface type with multiple methods"""
        input_str = """
            type Calculator interface {
                Add(x, y [2]ID) [2]int;
                Subtract(a, b float, c, e int);
                Reset();
                SayHello(name string)
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 139)
        )

    def test_140(self):
        """Error: interface type declaration with missing semicolon or newline token"""
        self.assertTrue(
            TestParser.test("type Calculator interface {Reset()}", "Error on line 1 col 34: }", 140)
        )

    def test_141(self):
        """Declaration: interface type with two method declarations on one line"""
        input_str = """
            type Calculator interface { 
                Add(x int,c,d ID); Add() 
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 141)
        )

    def test_142(self):
        """Declaration: function with parameters and return type"""
        self.assertTrue(
            TestParser.test("func Add(x int, y int) int {return ;};", "successful", 142)
        )

    def test_143(self):
        """Error: method declaration with invalid receiver type"""
        self.assertTrue(
            TestParser.test("""
                func (c Calculator) Add(x int) int {
                    return ;
                }
                """, "successful", 143)
        )

    def test_144(self):
        """Error: empty program (or missing content)"""
        self.assertTrue(
            TestParser.test("", "Error on line 1 col 0: <EOF>", 144)
        )

    def test_145(self):
        """Statement: function with a simple variable declaration inside a block"""
        input_str = """
            func Add() {
                var a int;
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 145)
        )

    def test_146(self):
        """Statement: function with variable initialized using array access"""
        input_str = """
            func Add() {
                var a = a[2].b;
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 146)
        )

    def test_147(self):
        """Statement: function with several compound assignment statements"""
        input_str = """
            func Add() {
                a += 2;
                a -= a[2].b();
                a /= 2;
                a *= 2;
                a %= 2;
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 147)
        )

    def test_148(self):
        """Statement: function with complex chained field and array accesses in assignment"""
        input_str = """
            func Add() {
                a.c[2].e[3].k += 2;
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 148)
        )

    def test_149(self):
        """Error: function attempting to assign to a function call result"""
        input_str = """
            func Add() {
                a.foo() += 2;
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "Error on line 3 col 24: +=", 149)
        )

    def test_150(self):
        """Statement: function with complex expression inside an array index and assignment"""
        input_str = """
            func Add() {
                a[2+3&&2] += foo().b[2];
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 150)
        )

    def test_151(self):
        """Statement: function with if-else statement including declarations and returns"""
        input_str = """
            func Add() {
                if (x.foo().b[2]) {
                    a := 2;
                } else if (a && b) {
                    return;
                } else {
                    a := 2;
                }
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 151)
        )

    def test_152(self):
        """Statement: function with for loop using an expression as header"""
        input_str = """
            func Add() {
                for true + 2 + foo().b {return; }
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 152)
        )

    def test_153(self):
        """Statement: function with standard for loop header"""
        input_str = """
            func Add() {
                for i := 0; i < 10; i += 1 { return; }
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 153)
        )

    def test_154(self):
        """Statement: function with for loop using range clause"""
        input_str = """
            func Add() {
                for index, value := range 23 { return; }
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 154)
        )

    def test_155(self):
        """Statement: function with multiple break and continue statements"""
        input_str = """
            func Add() {
                break;
                continue;
                break; continue; break;
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 155)
        )

    def test_156(self):
        """Statement: function with several return statements"""
        input_str = """
            func Add() {
                return;
                return 2 + a[2].b();
                return; return a;
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 156)
        )

    def test_157(self):
        """Statement: function with two function calls having struct literals as arguments"""
        input_str = """
            func Add() {
                a.foo(2 + 3, a {a:2});
                foo(2 + 3, a {a:2});
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 157)
        )

    def test_158(self):
        """Statement: for loop with variable declaration in initializer"""
        input_str = """
            func Add() {
                for var b [2]ID = 1 + 2 / 4; foo().a.b(); i := 1 {
                    return;
                }
            };
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 158)
        )

    def test_159(self):
        """Literal: complex array literal with multidimensional type"""
        self.assertTrue(
            TestParser.test("const a = [ID][2][VT]int{{{1}}};", "successful", 159)
        )

    def test_160(self):
        """Error: variable declaration missing initializer"""
        self.assertTrue(
            TestParser.test("var a;", "Error on line 1 col 5: ;", 160)
        )

    def test_161(self):
        """Error: variable declaration with illegal literal form"""
        self.assertTrue(
            TestParser.test("var a = {1, 2};", "Error on line 1 col 8: {", 161)
        )

    def test_162(self):
        """Literal: constant float literal"""
        self.assertTrue(
            TestParser.test("const pi = 3.1415;", "successful", 162)
        )

    def test_163(self):
        """Literal: constant wtf"""
        self.assertTrue(
            TestParser.test("const a = [1]ID{Toilet{}};", "successful", 163)
        )

    def test_164(self):
        """Error: illegal escape sequence in string literal"""
        self.assertTrue(
            TestParser.test("const s = \"Hello\\q\";", "\"Hello\\q", 164)
        )

    def test_165(self):
        """Error: unclosed string literal"""
        self.assertTrue(
            TestParser.test("const s = \"Hello", "\"Hello", 165)
        )

    def test_166(self):
        """Literal: valid string literal with escape sequence"""
        self.assertTrue(
            TestParser.test("const s = \"Hello\\nWorld\";", "successful", 166)
        )

    def test_167(self):
        """Declaration: array literal declaration"""
        self.assertTrue(
            TestParser.test("var arr = [3]int{1,2,3};", "successful", 167)
        )

    def test_168(self):
        """Declaration: array variable declaration with initializer"""
        self.assertTrue(
            TestParser.test("var arr [2]int = [2]int{1, 2};", "successful", 168)
        )

    def test_169(self):
        """Literal: struct literal variable declaration"""
        self.assertTrue(
            TestParser.test("var person = Person{name: \"John\", age: 25};", "successful", 169)
        )

    def test_170(self):
        """Literal: nested struct literal variable declaration"""
        self.assertTrue(
            TestParser.test("var rec = Rectangle{topLeft: Point{x:0, y:0}, bottomRight: Point{x:10, y:10}};", "successful", 170)
        )

    def test_171(self):
        """Declaration: function that multiplies two integers"""
        self.assertTrue(
            TestParser.test("func Multiply(a int, b int) int { return a * b; };", "successful", 171)
        )

    def test_172(self):
        """Declaration: function with string parameter and no return type"""
        self.assertTrue(
            TestParser.test("func Print(a string) { return; };", "successful", 172)
        )

    def test_173(self):
        """Expression: function call inside an arithmetic expression"""
        self.assertTrue(
            TestParser.test("var result = Multiply(3, 14) + 2;", "successful", 173)
        )

    def test_174(self):
        """Expression: array access on a previously declared array"""
        self.assertTrue(
            TestParser.test("var element = arr[1];", "successful", 174)
        )

    def test_175(self):
        """Expression: field access on a struct variable"""
        self.assertTrue(
            TestParser.test("var name = person.name;", "successful", 175)
        )

    def test_176(self):
        """Expression: complex arithmetic expression with parentheses"""
        self.assertTrue(
            TestParser.test("var comp = (a + b) * (c - d) / e;", "successful", 176)
        )

    def test_177(self):
        """Expression: method call on an object"""
        self.assertTrue(
            TestParser.test("var ret = obj.method(1,2);", "successful", 177)
        )

    def test_178(self):
        """Expression: chained method calls"""
        self.assertTrue(
            TestParser.test("var ret = obj.getA().getB().do();", "successful", 178)
        )

    def test_179(self):
        """Statement: compound assignment with arithmetic operators"""
        self.assertTrue(
            TestParser.test("a += b * c - d / e;", "successful", 179)
        )

    def test_180(self):
        """Literal: constant boolean expression with logical operators"""
        self.assertTrue(
            TestParser.test("const flag = false && true || false;", "successful", 180)
        )

    def test_181(self):
        """Expression: chained relational operators"""
        self.assertTrue(
            TestParser.test("var rel = a == b != c < d <= e > f >= g;", "successful", 181)
        )

    def test_182(self):
        """Expression: logical operators with grouping"""
        self.assertTrue(
            TestParser.test("var logic = (a && b) || (!c);", "successful", 182)
        )

    def test_183(self):
        """Expression: use of unary minus operator"""
        self.assertTrue(
            TestParser.test("var neg = -a + (-b);", "successful", 183)
        )

    def test_184(self):
        """Expression: multiple nested parentheses"""
        self.assertTrue(
            TestParser.test("var paren = (((a)));", "successful", 184)
        )

    def test_185(self):
        """Statement: if statement without else clause"""
        self.assertTrue(
            TestParser.test("func Check() { if (a > 0) { return; } };", "successful", 185)
        )

    def test_186(self):
        """Statement: for loop with minimal header"""
        self.assertTrue(
            TestParser.test("func Loop() { for i < 10 { return; } };", "successful", 186)
        )

    def test_187(self):
        """Statement: for loop with complete header"""
        self.assertTrue(
            TestParser.test("func Loop() { for i := 0; i < 5; i += 1 { return; } };", "successful", 187)
        )

    def test_188(self):
        """Statement: for loop using range clause with two identifiers"""
        self.assertTrue(
            TestParser.test("""
                func Iterate() { 
                    for key, value := range array {
                        return;
                    } 
                }
                """, "successful", 188)
        )

    def test_189(self):
        """Declaration: function with return statement returning an integer literal"""
        self.assertTrue(
            TestParser.test("func GetValue() int { return 42; };", "successful", 189)
        )

    def test_190(self):
        """Statement: for loop with if-else inside, using break and continue"""
        self.assertTrue(
            TestParser.test("""
                func Process() { 
                    for i := 0; i < 10; i += 1 { 
                        if (i == 5) { 
                            break; 
                        } else { 
                            continue; 
                        } 
                    } 
                };""", "successful", 190)
        )

    def test_191(self):
        """Expression: nested function calls as part of an expression"""
        self.assertTrue(
            TestParser.test("var nested = foo(bar(1, 2), baz(3));", "successful", 191)
        )

    def test_192(self):
        """Statement: assignment to an array element"""
        self.assertTrue(
            TestParser.test("arr[0] := 100;", "successful", 192)
        )

    def test_193(self):
        """Statement: assignment to a struct field"""
        self.assertTrue(
            TestParser.test("person.age := person.age + 1;", "successful", 193)
        )

    def test_194(self):
        """Declaration: multiple sequential variable declarations"""
        input_str = """
            var a int = 1;
            var b int = 2;
            var c int = a + b;
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 194)
        )

    def test_195(self):
        """Literal: constant string declaration"""
        self.assertTrue(
            TestParser.test("const greeting = \"Hello, World!\";", "successful", 195)
        )

    def test_196(self):
        """Declaration: struct type with two fields"""
        input_str = """
            type Point struct {
                x int;
                y int;
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 196)
        )

    def test_197(self):
        """Declaration: interface type with one method"""
        input_str = """
            type Drawable interface {
                Draw();
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 197)
        )

    def test_198(self):
        """Declaration: interface type with method returning a float"""
        input_str = """
            type Shape interface {
                Area() float;
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 198)
        )

    def test_199(self):
        """Declaration: method declaration with a receiver on a struct type"""
        input_str = """
            func (p Point) Distance(q Point) float { return 0.0; }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 199)
        )

    def test_200(self):
        """Declaration: function calling a function and a method"""
        input_str = """
            func Toilet() {
                foo(1, 2);
                a[2].foo(1,3);
            }
        """
        self.assertTrue(
            TestParser.test(input_str, "successful", 200)
        )