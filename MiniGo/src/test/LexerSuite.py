import unittest
from TestUtils import TestLexer

class LexerSuite(unittest.TestCase):
    
    def test_001(self):
        self.assertTrue(TestLexer.checkLexeme("x", "x,<EOF>", 1))
    
    def test_002(self):
        self.assertTrue(TestLexer.checkLexeme("var _var123", "var,_var123,<EOF>", 2))
    
    def test_003(self):
        self.assertTrue(TestLexer.checkLexeme("func main(){}", "func,main,(,),{,},<EOF>", 3))

    def test_004(self):
        self.assertTrue(TestLexer.checkLexeme("1234", "1234,<EOF>", 4))

    def test_005(self):
        self.assertTrue(TestLexer.checkLexeme("0x1A", "0x1A,<EOF>", 5))

    def test_006(self):
        self.assertTrue(TestLexer.checkLexeme("0B101", "0B101,<EOF>", 6))

    def test_007(self):
        self.assertTrue(TestLexer.checkLexeme("0o123", "0o123,<EOF>", 7))

    def test_008(self):
        self.assertTrue(TestLexer.checkLexeme("true", "true,<EOF>", 8))

    def test_009(self):
        self.assertTrue(TestLexer.checkLexeme("false", "false,<EOF>", 9))

    def test_010(self):
        self.assertTrue(TestLexer.checkLexeme("nil", "nil,<EOF>", 10))

    def test_011(self):
        self.assertTrue(TestLexer.checkLexeme("return", "return,<EOF>", 11))

    def test_012(self):
        self.assertTrue(TestLexer.checkLexeme("if else for", "if,else,for,<EOF>", 12))

    def test_013(self):
        self.assertTrue(TestLexer.checkLexeme("x += 1", "x,+=,1,<EOF>", 13))

    def test_014(self):
        self.assertTrue(TestLexer.checkLexeme("y -= 2", "y,-=,2,<EOF>", 14))

    def test_015(self):
        self.assertTrue(TestLexer.checkLexeme("a * b", "a,*,b,<EOF>", 15))

    def test_016(self):
        self.assertTrue(TestLexer.checkLexeme("c / d", "c,/,d,<EOF>", 16))

    def test_017(self):
        self.assertTrue(TestLexer.checkLexeme("e % f", "e,%,f,<EOF>", 17))

    def test_018(self):
        self.assertTrue(TestLexer.checkLexeme("g == h", "g,==,h,<EOF>", 18))

    def test_019(self):
        self.assertTrue(TestLexer.checkLexeme("i != j", "i,!=,j,<EOF>", 19))

    def test_020(self):
        self.assertTrue(TestLexer.checkLexeme("k < l", "k,<,l,<EOF>", 20))

    def test_021(self):
        self.assertTrue(TestLexer.checkLexeme("m <= n", "m,<=,n,<EOF>", 21))

    def test_022(self):
        self.assertTrue(TestLexer.checkLexeme("o > p", "o,>,p,<EOF>", 22))

    def test_023(self):
        self.assertTrue(TestLexer.checkLexeme("q >= r", "q,>=,r,<EOF>", 23))

    def test_024(self):
        self.assertTrue(TestLexer.checkLexeme("str1 := \"hello\"", "str1,:=,\"hello\",<EOF>", 24))

    def test_025(self):
        self.assertTrue(TestLexer.checkLexeme("arr := [3]int{10, 20, 30}", "arr,:=,[,3,],int,{,10,,,20,,,30,},<EOF>", 25))

    def test_026(self):
        self.assertTrue(TestLexer.checkLexeme("type Person struct { name string ; age int ; }", "type,Person,struct,{,name,string,;,age,int,;,},<EOF>", 26))

    def test_027(self):
        self.assertTrue(TestLexer.checkLexeme("type Point struct { x, y int ; }", "type,Point,struct,{,x,,,y,int,;,},<EOF>", 27))

    def test_028(self):
        self.assertTrue(TestLexer.checkLexeme("interface Shape { area() float; }", "interface,Shape,{,area,(,),float,;,},<EOF>", 28))

    def test_029(self):
        self.assertTrue(TestLexer.checkLexeme("const Pi = 3.14", "const,Pi,=,3.14,<EOF>", 29))

    def test_030(self):
        self.assertTrue(TestLexer.checkLexeme("var x int = 10", "var,x,int,=,10,<EOF>", 30))

    def test_031(self):
        self.assertTrue(TestLexer.checkLexeme("func add(a, b int) int { return a + b; }", "func,add,(,a,,,b,int,),int,{,return,a,+,b,;,},<EOF>", 31))

    def test_032(self):
        self.assertTrue(TestLexer.checkLexeme("func main() { x := 5 ; }", "func,main,(,),{,x,:=,5,;,},<EOF>", 32))

    def test_033(self):
        self.assertTrue(TestLexer.checkLexeme("arr[1] = 10", "arr,[,1,],=,10,<EOF>", 33))

    def test_034(self):
        self.assertTrue(TestLexer.checkLexeme("person.name = \"John\"", "person,.,name,=,\"John\",<EOF>", 34))

    def test_035(self):
        self.assertTrue(TestLexer.checkLexeme("for i := 0; i < 10; i++ { }", "for,i,:=,0,;,i,<,10,;,i,+,+,{,},<EOF>", 35))

    def test_036(self):
        self.assertTrue(TestLexer.checkLexeme("for , value := range arr { }", "for,,,value,:=,range,arr,{,},<EOF>", 36))

    def test_037(self):
        self.assertTrue(TestLexer.checkLexeme("while x < 5 { x += 1 }", "while,x,<,5,{,x,+=,1,},<EOF>", 37))

    def test_038(self):
        self.assertTrue(TestLexer.checkLexeme("continue", "continue,<EOF>", 38))

    def test_039(self):
        self.assertTrue(TestLexer.checkLexeme("break", "break,<EOF>", 39))

    def test_040(self):
        self.assertTrue(TestLexer.checkLexeme("func main() { if x > 5 { break } }", "func,main,(,),{,if,x,>,5,{,break,},},<EOF>", 40))

    def test_041(self):
        self.assertTrue(TestLexer.checkLexeme("x = !y", "x,=,!,y,<EOF>", 41))

    def test_042(self):
        self.assertTrue(TestLexer.checkLexeme("arr[2] := 10", "arr,[,2,],:=,10,<EOF>", 42))

    def test_043(self):
        self.assertTrue(TestLexer.checkLexeme("str := \"this is a string\"", "str,:=,\"this is a string\",<EOF>", 43))

    def test_044(self):
        self.assertTrue(TestLexer.checkLexeme("const Max = 100 + 50", "const,Max,=,100,+,50,<EOF>", 44))

    def test_045(self):
        self.assertTrue(TestLexer.checkLexeme("for i := 0; i < 10; i++ { x = i * 2 }", "for,i,:=,0,;,i,<,10,;,i,+,+,{,x,=,i,*,2,},<EOF>", 45))

    def test_046(self):
        self.assertTrue(TestLexer.checkLexeme("x && y", "x,&&,y,<EOF>", 46))

    def test_047(self):
        self.assertTrue(TestLexer.checkLexeme("x || y", "x,||,y,<EOF>", 47))

    def test_048(self):
        self.assertTrue(TestLexer.checkLexeme("x == y", "x,==,y,<EOF>", 48))

    def test_049(self):
        self.assertTrue(TestLexer.checkLexeme("x != y", "x,!=,y,<EOF>", 49))

    def test_050(self):
        self.assertTrue(TestLexer.checkLexeme("x < y", "x,<,y,<EOF>", 50))

    def test_051(self):
        self.assertTrue(TestLexer.checkLexeme("a + b", "a,+,b,<EOF>", 51))

    def test_052(self):
        self.assertTrue(TestLexer.checkLexeme("a - b", "a,-,b,<EOF>", 52))

    def test_053(self):
        self.assertTrue(TestLexer.checkLexeme("a * b", "a,*,b,<EOF>", 53))

    def test_054(self):
        self.assertTrue(TestLexer.checkLexeme("a / b", "a,/,b,<EOF>", 54))

    def test_055(self):
        self.assertTrue(TestLexer.checkLexeme("a % b", "a,%,b,<EOF>", 55))

    def test_056(self):
        self.assertTrue(TestLexer.checkLexeme("x += 5", "x,+=,5,<EOF>", 56))

    def test_057(self):
        self.assertTrue(TestLexer.checkLexeme("y -= 3", "y,-=,3,<EOF>", 57))

    def test_058(self):
        self.assertTrue(TestLexer.checkLexeme("z *= 2", "z,*=,2,<EOF>", 58))

    def test_059(self):
        self.assertTrue(TestLexer.checkLexeme("w /= 4", "w,/=,4,<EOF>", 59))

    def test_060(self):
        self.assertTrue(TestLexer.checkLexeme("x %= 10", "x,%=,10,<EOF>", 60))

    def test_061(self):
        self.assertTrue(TestLexer.checkLexeme("struct Point { x int; y int; }", "struct,Point,{,x,int,;,y,int,;,},<EOF>", 61))

    def test_062(self):
        self.assertTrue(TestLexer.checkLexeme("type Circle struct { radius float; }", "type,Circle,struct,{,radius,float,;,},<EOF>", 62))

    def test_063(self):
        self.assertTrue(TestLexer.checkLexeme("interface Shape { area() float; perimeter() float; }", "interface,Shape,{,area,(,),float,;,perimeter,(,),float,;,},<EOF>", 63))

    def test_064(self):
        self.assertTrue(TestLexer.checkLexeme("const PI = 3.14159", "const,PI,=,3.14159,<EOF>", 64))

    def test_065(self):
        self.assertTrue(TestLexer.checkLexeme("var x float = 3.14", "var,x,float,=,3.14,<EOF>", 65))

    def test_066(self):
        self.assertTrue(TestLexer.checkLexeme("var arr [5]int", "var,arr,[,5,],int,<EOF>", 66))

    def test_067(self):
        self.assertTrue(TestLexer.checkLexeme("x := 5", "x,:=,5,<EOF>", 67))

    def test_068(self):
        self.assertTrue(TestLexer.checkLexeme("x = y", "x,=,y,<EOF>", 68))

    def test_069(self):
        self.assertTrue(TestLexer.checkLexeme("for i := 0; i < 10; i++ { }", "for,i,:=,0,;,i,<,10,;,i,+,+,{,},<EOF>", 69))

    def test_070(self):
        self.assertTrue(TestLexer.checkLexeme("for , value := range arr { }", "for,,,value,:=,range,arr,{,},<EOF>", 70))

    def test_071(self):
        self.assertTrue(TestLexer.checkLexeme("break", "break,<EOF>", 71))

    def test_072(self):
        self.assertTrue(TestLexer.checkLexeme("continue", "continue,<EOF>", 72))

    def test_073(self):
        self.assertTrue(TestLexer.checkLexeme("return x + y", "return,x,+,y,<EOF>", 73))

    def test_074(self):
        self.assertTrue(TestLexer.checkLexeme("var x = 10", "var,x,=,10,<EOF>", 74))

    def test_075(self):
        self.assertTrue(TestLexer.checkLexeme("type Circle struct { radius float ; }", "type,Circle,struct,{,radius,float,;,},<EOF>", 75))

    def test_076(self):
        self.assertTrue(TestLexer.checkLexeme("const MAX = 100", "const,MAX,=,100,<EOF>", 76))

    def test_077(self):
        self.assertTrue(TestLexer.checkLexeme("func foo() {}", "func,foo,(,),{,},<EOF>", 77))

    def test_078(self):
        self.assertTrue(TestLexer.checkLexeme("arr[1] = 5", "arr,[,1,],=,5,<EOF>", 78))

    def test_079(self):
        self.assertTrue(TestLexer.checkLexeme("var z string = \"hello\"", "var,z,string,=,\"hello\",<EOF>", 79))

    def test_080(self):
        self.assertTrue(TestLexer.checkLexeme("func main() { x := 10 }", "func,main,(,),{,x,:=,10,},<EOF>", 80))

    def test_081(self):
        self.assertTrue(TestLexer.checkLexeme("x := 2 * 3", "x,:=,2,*,3,<EOF>", 81))

    def test_082(self):
        self.assertTrue(TestLexer.checkLexeme("y /= 2", "y,/=,2,<EOF>", 82))

    def test_083(self):
        self.assertTrue(TestLexer.checkLexeme("for i := 0; i < 10; i++ { }", "for,i,:=,0,;,i,<,10,;,i,+,+,{,},<EOF>", 83))

    def test_084(self):
        self.assertTrue(TestLexer.checkLexeme("x > y", "x,>,y,<EOF>", 84))

    def test_085(self):
        self.assertTrue(TestLexer.checkLexeme("x <= y", "x,<=,y,<EOF>", 85))

    def test_086(self):
        self.assertTrue(TestLexer.checkLexeme("a && b", "a,&&,b,<EOF>", 86))

    def test_087(self):
        self.assertTrue(TestLexer.checkLexeme("a || b", "a,||,b,<EOF>", 87))

    def test_088(self):
        self.assertTrue(TestLexer.checkLexeme("!b", "!,b,<EOF>", 88))

    def test_089(self):
        self.assertTrue(TestLexer.checkLexeme("z := a + b", "z,:=,a,+,b,<EOF>", 89))

    def test_090(self):
        self.assertTrue(TestLexer.checkLexeme("str == \"hello\"", "str,==,\"hello\",<EOF>", 90))

    def test_091(self):
        self.assertTrue(TestLexer.checkLexeme("a == b", "a,==,b,<EOF>", 91))

    def test_092(self):
        self.assertTrue(TestLexer.checkLexeme("b != c", "b,!=,c,<EOF>", 92))

    def test_093(self):
        self.assertTrue(TestLexer.checkLexeme("a == 5", "a,==,5,<EOF>", 93))

    def test_094(self):
        self.assertTrue(TestLexer.checkLexeme("x + y", "x,+,y,<EOF>", 94))

    def test_095(self):
        self.assertTrue(TestLexer.checkLexeme("func main() { return 10; }", "func,main,(,),{,return,10,;,},<EOF>", 95))

    def test_096(self):
        self.assertTrue(TestLexer.checkLexeme("func sum(a int, b int) int { return a + b }", "func,sum,(,a,int,,,b,int,),int,{,return,a,+,b,},<EOF>", 96))

    def test_097(self):
        self.assertTrue(TestLexer.checkLexeme("x != y && z == w", "x,!=,y,&&,z,==,w,<EOF>", 97))

    def test_098(self):
        self.assertTrue(TestLexer.checkLexeme("z *= 10", "z,*=,10,<EOF>", 98))

    def test_099(self):
        self.assertTrue(TestLexer.checkLexeme("y -= 2", "y,-=,2,<EOF>", 99))

    def test_100(self):
        self.assertTrue(TestLexer.checkLexeme("if x == 5 { return true }", "if,x,==,5,{,return,true,},<EOF>", 100))