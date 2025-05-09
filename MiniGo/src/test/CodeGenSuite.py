import unittest
from TestUtils import TestCodeGen
from AST import *


class CheckCodeGenSuite(unittest.TestCase):
    
    def test_401(self):
        input = """func main() {putInt(5);};"""
        expect = "5"
        self.assertTrue(TestCodeGen.test(input, expect, 401))
    
    def test_402(self):
        input = """func main() {var a int = 20;  putInt(a);};"""
        expect = "20"
        self.assertTrue(TestCodeGen.test(input, expect, 402))
    
    def test_403(self):
        input = """var a int = 10; func main() { putInt(a);};"""
        expect = "10"
        self.assertTrue(TestCodeGen.test(input, expect, 403))
    
    def test_404(self):
        input = Program([FuncDecl("main",[],VoidType(),Block([FuncCall("putInt", [IntLiteral(25)])]))])
        expect = "25"
        self.assertTrue(TestCodeGen.test(input, expect, 404))
    
    def test_405(self):
        input = Program([FuncDecl("main",[],VoidType(),Block([VarDecl("a",IntType(),IntLiteral(500)),FuncCall("putInt", [Id("a")])]))])
        expect = "500"
        self.assertTrue(TestCodeGen.test(input, expect, 405))
    
    def test_406(self):  
        input = Program([VarDecl("a",IntType(),IntLiteral(5000)),FuncDecl("main",[],VoidType(),Block([FuncCall("putInt", [Id("a")])]))])
        expect = "5000"
        self.assertTrue(TestCodeGen.test(input, expect, 406))
    
    def test_407(self):
        input = """
        func fvoid() {putStringLn("Corgi");}

        var global = fint()
        func main() {
            fvoid();
            putFloatLn(global + 2.0)

            var local = "a";
            putBoolLn(local <= "b")
            local += "c"
            putStringLn(local)

        };

        func fint() int {return 1;}
        """
        self.assertTrue(TestCodeGen.test(input, "Corgi\n3.0\ntrue\nac\n", 407)) 
    
    def test_408(self):
        input = """
        func main() {
            putBoolLn(5.0 > 2.0)
            putBoolLn(5.0 < 2.0)
            putBoolLn(5.0 <= 5.0)
            putBoolLn(5.0 >= 5.0)
            putBoolLn(5.0 == 5.0)
            putBoolLn(5.0 != 5.0)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "true\nfalse\ntrue\ntrue\ntrue\nfalse\n", 408)) 

    
    def test_409(self):
        input = """
        func main() {
            var a [1] int ;
            a[0] := 1
            putInt(a[0]);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "1", 409))

    
    def test_410(self):
        input = """
        func main() {
            var a [1][1][1] int  = [1][1][1] int {{{0}}};
            a[0][0][0] := 1
            putInt(a[0][0][0]);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "1", 410))

    
    def test_411(self):
        input = """
        func main() {
            var a [2] int = [2] int {10, 20};
            putInt(a[0])
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 411))

    
    def test_412(self):
        input = """
        func main() {
            var a [2] int;
            a[0] := 100
            a[1] += a[0] + a[0]
            putInt(a[1])
        }
        """
        self.assertTrue(TestCodeGen.test(input, "200", 412))
    
    
    def test_413(self):
        input = """
        var a [2] int;
        func main() {
            a[0] := 100
            a[1] += a[0] + a[0]
            putInt(a[1])
        }
        """
        self.assertTrue(TestCodeGen.test(input, "200", 413))

    
    def test_414(self):
        input = """
        func main() {
            if (true) {
                putBool(true)
            } 
        }
        """
        self.assertTrue(TestCodeGen.test(input, "true", 414))

    
    def test_415(self):
        input = """
        func main() {
            if (true) {
                putBool(true)
            } else {
                putBool(false)     
            }
        }
        """
        self.assertTrue(TestCodeGen.test(input, "true", 415))

    def test_416(self):
        input = """
        func main() {
            if (false) {
                putBool(true)
            } else {
                putBool(false)     
            }
        }
        """
        self.assertTrue(TestCodeGen.test(input, "false", 416))

    def test_417(self):
        input = """
        func main() {
            var i = 0;
            for i < 3 {
                putInt(i);
                i += 1;
            }
            putInt(i);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "0123", 417))

    def test_418(self):
        input = """
        func main() {
            var i = 0;
            for i < 5 {
                if (i == 3) {
                    break;
                }
                putInt(i);
                i += 1;
            }
            putInt(i);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "0123", 418))

    
    def test_419(self):
        input = """
        func main() {
            var i = 0;
            for i < 5 {
                i += 1;
                if (i % 2 == 0) {
                    continue;
                }
                putInt(i);
            }
            putInt(i);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "1355", 419))

    
    def test_420(self):
        input = """
        func main() {
            var i int = 10;
            for var i int = 0; i < 2; i += 1 {
                putIntLn(i)
                break;
            }
            putInt(i)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "0\n10", 420))

    
    def test_421(self):
        input = """
        const a = 1 + 1
        const c = 5 - a
        func main() {
            var b [a][c] int;
            putInt(b[0][0]);
            b[0][0] := 20;
            putInt(b[0][0]);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "020", 421))

    
    def test_422(self):
        input = """
        type Course interface {study();}
        type PPL3 struct {number int;}
        func (p PPL3) study() {putInt(p.number);}

        func main(){
            var a PPL3 = PPL3 {number: 10}
            putIntLn(a.number)
            a.study()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10\n10", 422))

    
    def test_423(self):
        input = """
        type Course interface {study();}
        type PPL3 struct {number int;}
        func (p PPL3) study() {putInt(p.number);}

        func main(){
            var a Course = nil
            a := PPL3 {number: 10}
            a.study()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 423))
    
    
    def test_424(self):
        input = """
        type Course interface {study();}
        type PPL3 struct {number int;}
        func (p PPL3) study() {putInt(p.number);}

        func main(){
            var a PPL3 = PPL3 {number: 10}
            putIntLn(a.number)
            a.study()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10\n10", 424))

    
    def test_425(self):
        input = """
        type Course interface {study();}
        type PPL3 struct {number int;}
        func (p PPL3) study() {putInt(p.number);}

        func main(){
            var a PPL3 = PPL3 {number: 10}
            putIntLn(a.number)
            a.study()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10\n10", 425))

    
    def test_426(self):
        input = """
        type Course interface {study();}
        type PPL3 struct {number int;}
        func (p PPL3) study() {putInt(p.number);}

        func main(){
            var a Course = nil
            a := PPL3 {number: 10}
            a.study()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 426))

    
    def test_427(self):
        input = """
        type PPL3 struct {number int;}

        func main(){
            var a PPL3 = PPL3 {number: 10}
            putInt(a.number)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 427))

    
    def test_428(self):
        input = """
        type PPL3 struct {number int;}

        func main(){
            var a PPL3
            a.number := 10
            putInt(a.number)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 428))

    
    def test_429(self):
        input = """
        type PPL2 struct {number int;}
        type PPL3 struct {number int; ppl PPL2;}

        func main(){
            var a PPL3
            a.ppl := PPL2 {number: 10}
        putInt(a.ppl.number)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 429))

    
    def test_430(self):
        input = """
        type PPL2 struct {number int;}
        type PPL3 struct {number int; ppl PPL2;}

        func main(){
            var a PPL3
            a.ppl := PPL2 {number: 10}
            a.ppl.number := 100
        putInt(a.ppl.number)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "100", 430))        

    
    def test_431(self):
        input = """
        type Study interface { study(); }
        type Play interface { play(); }

        type PPL3 struct {number int;}

        func (p PPL3) study() { putInt(p.number); }
        func (p PPL3) play()  { putInt(p.number + 5); }

        func main() {
            var a PPL3 = PPL3 {number: 1}
            a.study()
            a.play()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "16", 431))


    
    def test_432(self):
        input = """
        type Study interface { study(); }
        type Play interface { play(); }

        type PPL3 struct {number int;}

        func (p PPL3) study() { putInt(p.number); }
        func (p PPL3) play()  { putInt(p.number + 5); }

        func main() {
            var a PPL3 = PPL3 {number: 1}
            var b Study = a
            var c Play = a
            b.study()
            c.play()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "16", 432))

    
    def test_433(self):
        input = """
        type Study interface { study(); }
        type Play interface { play(); }

        type PPL3 struct {number int;}

        func (p PPL3) study() { putInt(p.number); }
        func (p PPL3) play()  { putInt(p.number + 5); }

        func main() {
            var a PPL3 = PPL3 {number: 1}
            var b Study = a
            var c Play = a
            b.study()
            c.play()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "16", 433))

    
    def test_434(self):
        input = """
        type Worker interface { 
            study(); 
            play(); 
        }

        type PPL4 struct {number int;}
        type PPL5 struct {number int;}

        // Implement Worker cho PPL4
        func (p PPL4) study() { putInt(p.number); }
        func (p PPL4) play()  { putInt(p.number + 5); }

        // Implement Worker cho PPL5
        func (p PPL5) study() { putInt(p.number * 2); }
        func (p PPL5) play()  { putInt(p.number * 3); }

        func main() {
            var w1 Worker = PPL4 {number: 3}
            var w2 Worker = PPL5 {number: 4}

            w1.study(); // in: 3
            w1.play();  // in: 8

            w2.study(); // in: 8
            w2.play();  // in: 12
        }
        """
        self.assertTrue(TestCodeGen.test(input, "38" "812", 434))

    
    def test_435(self):
        input = """
        type Worker interface { 
            study(); 
            play(); 
        }

        type PPL4 struct {number int;}
        type PPL5 struct {number int;}

        // Implement Worker cho PPL4
        func (p PPL4) study() { putInt(p.number); }
        func (p PPL4) play()  { putInt(p.number + 5); }

        // Implement Worker cho PPL5
        func (p PPL5) study() { putInt(p.number * 2); }

        func main() {
            var w1 Worker = PPL4 {number: 3}
            var w2 PPL5 = PPL5 {number: 4}

            w1.study(); // in: 3
            w1.play();  // in: 8

            w2.study(); // in: 8
        }
        """
        self.assertTrue(TestCodeGen.test(input, "38" "8", 435))


    
    def test_436(self):
        input = """
        type Speaker interface { speak(); }

        type Human struct {name int; }

        func (h Human) speak() { putIntLn(h.name); }

        func saySomething(s Speaker) {
            s.speak();
        }

        func main() {
            var h Speaker = Human {name: 2025};
            saySomething(h);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "2025\n", 436))


    
    def test_437(self):
        input = """
        type Speaker interface { speak(); }

        type Human struct { name int; }

        func (h Human) speak() { putIntLn(h.name); }

        func main() {
            var people [3]Speaker;

            people[0] := Human {name: 1};
            people[1] := Human {name: 2};
            people[2] := Human {name: 3};

            people[0].speak(); // Output: 1
            people[1].speak(); // Output: 2
            people[2].speak(); // Output: 3
        }
        """
        self.assertTrue(TestCodeGen.test(input, "1\n2\n3\n", 437))

    
    def test_438(self):
        input = """
        type Speaker interface { speak(); }

        type Human struct { name int; }

        func (h Human) speak() { putIntLn(h.name); }

        func main() {
            var people [3]Human;

            people[0] := Human {name: 1};
            people[1] := Human {name: 2};
            people[2] := Human {name: 3};

            people[0].speak(); // Output: 1
            people[1].speak(); // Output: 2
            people[2].speak(); // Output: 3
        }
        """
        self.assertTrue(TestCodeGen.test(input, "1\n2\n3\n", 438))

    
    def test_439(self):
        input = """
        type Calculator struct { x int; y int; }

        func (c Calculator) sum() int {
            return c.x + c.y;
        }

        func main() {
            var cal Calculator = Calculator {x: 7, y: 8};
            var result int = cal.sum();
            putIntLn(result);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "15\n", 439))

    
    def test_440(self):
        input = """
        type Calculator interface { sum() int; }

        type BasicCalc struct { x int; y int; }

        func (b BasicCalc) sum() int {
            return b.x + b.y;
        }

        func main() {
            var c Calculator = BasicCalc {x: 5, y: 15};
            var result int = c.sum();
            putIntLn(result);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "20\n", 440))

    
    def test_441(self):
        input = """
        type Speaker interface { speak(); }

        type Human struct { name int; }

        func (h Human) speak() { putIntLn(h.name); }

        func sayHello(s Speaker) {
            s.speak();
        }

        func main() {
            var h Human = Human {name: 100};
            sayHello(h);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "100\n", 441))

    
    def test_442(self):
        input = """
        type Calculator interface { sum() int; }

        type BasicCalc struct { x int; y int; }

        func (b BasicCalc) sum() int {
            return b.x + b.y;
        }

        func calculate(c Calculator) int {
            return c.sum();
        }

        func main() {
            var b BasicCalc = BasicCalc {x: 20, y: 30};
            var result int = calculate(b);
            putIntLn(result);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "50\n", 442))

    
    def test_443(self):
        input = """
        type Multiplier struct { factor int; }

        func (m Multiplier) multiply(value int) int {
            return m.factor * value;
        }

        func main() {
            var mul Multiplier = Multiplier {factor: 5};
            var result int = mul.multiply(4);
            putIntLn(result);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "20\n", 443))

    
    def test_444(self):
        input = """
        type Calculator interface { calculate(a int, b int) int; }

        type BasicCalc struct {number int;}

        func (b BasicCalc) calculate(a int, b int) int {
            return a + b;
        }

        func main() {
            var c Calculator = BasicCalc {};
            var result int = c.calculate(15, 25);
            putIntLn(result);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "40\n", 444))


    
    def test_445(self):
        input = """
        type Calculator interface { calculate(a int, b int); }

        type BasicCalc struct {number int;}

        func (b BasicCalc) calculate(a int, b int) {
            putIntLn(a+b);
        }

        func main() {
            var c Calculator = BasicCalc {};
            c.calculate(15, 25);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "40\n", 445))

    
    def test_446(self):
        input = """
        type Calculator interface { calculate(a int, b int); }

        type BasicCalc struct {number int;}

        func (b BasicCalc) calculate(a int, b int) {
            putIntLn(a+b);
        }

        func main() {
            var c BasicCalc
            c.calculate(15, 25);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "40\n", 446))

    
    def test_447(self):
        input = """
        type Speaker interface { speak(); }

        type Human struct { name int; }

        func (h Human) speak() {
            putIntLn(h.name);
        }

        type Classroom struct {
            student Human;
            guest Speaker;
        }

        func main() {
            var h Human = Human {name: 777};
            var k Speaker = Human {name: 999};
            var room Classroom = Classroom {student: h, guest: k};

            putIntLn(room.student.name);
            room.guest.speak();
        }
        """
        self.assertTrue(TestCodeGen.test(input, "777\n999\n", 447))

    
    def test_448(self):
        input = """
        type Person struct {
            name string;
            age int;
        }
        func main() {
            var p Person = Person{name: "Alice", age: 22};
            putStringLn(p.name);
            putIntLn(p.age);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Alice\n22\n", 448))

    
    def test_449(self):
        input = """
        type Greeter interface { greet(); }

        type Person struct {
            name string;
            age int;
        }
        func (p Person) greet() {
            putStringLn(p.name);
        }

        func main() {
            var g Greeter = Person{name: "Bob", age: 30};
            g.greet();
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Bob\n", 449))

    
    def test_450(self):
        input = """
        type Person struct {
            name string;
            age int;
        }
        func (p Person) agePlus(n int) int {
            return p.age + n;
        }
        func main() {
            var p Person = Person{name: "Charlie", age: 18};
            var result int = p.agePlus(5);
            putIntLn(result);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "23\n", 450))

    
    def test_451(self):
        input = """
        type Person struct {
            name string;
            age int;
        }
        func sumAges(p1 Person, p2 Person) int {
            return p1.age + p2.age;
        }
        func main() {
            var p1 Person = Person{name: "Dan", age: 20};
            var p2 Person = Person{name: "Eve", age: 25};
            var total int = sumAges(p1, p2);
            putIntLn(total);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "45\n", 451))

    
    def test_452(self):
        input = """
        type Person struct {
            name string;
            age int;
        }
        func (p Person) printInfo() {
            putStringLn(p.name);
            putIntLn(p.age);
        }
        func main() {
            var people [1]Person
            people[0] := Person{name: "Anna", age: 19};
            people[0].printInfo() 
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Anna\n19\n", 452))

    
    def test_453(self):
        input = """
        type Speaker interface { speak(); }
        type Person struct {
            name string;
            age int;
        }
        func (p Person) speak() {
            putStringLn(p.name);
        }
        func announce(s Speaker) {
            s.speak();
        }
        func main() {
            var p Person = Person{name: "Grace", age: 27};
            announce(p);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Grace\n", 453))

    
    def test_454(self):
        input = """
        type Person struct {
            name string;
            age int;
        }
        func createPerson(n string, a int) Person {
            return Person{name: n, age: a};
        }
        func main() {
            var p Person = createPerson("Helen", 24);
            putStringLn(p.name);
            putIntLn(p.age);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Helen\n24\n", 454))

    
    def test_455(self):
        input = """
        type Person struct {
            name string;
            age int;
        }
        func (p Person) isAdult() boolean {
            return p.age >= 18;
        }
        func main() {
            var p Person = Person{name: "Ivy", age: 17};
            if (p.isAdult()) {
                putStringLn("Adult");
            } else {
                putStringLn("Minor");
            }
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Minor\n", 455))

    
    def test_456(self):
        input = """
        type Person struct {
            name string;
            age int;
        }
        func (p Person) duplicate() Person {
            return Person{name: p.name, age: p.age};
        }
        func main() {
            var p1 Person = Person{name: "Jack", age: 31};
            var p2 Person = p1.duplicate();
            putStringLn(p2.name);
            putIntLn(p2.age);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Jack\n31\n", 456))

    
    def test_457(self):
        input = """
        type Person struct {
            name string;
            age int;
        }
        func (p Person) printInfo() {
            putStringLn(p.name);
            putIntLn(p.age);
        }
        func main() {
            var people [2]Person = [2]Person{Person{name: "Anna", age: 19},Person{name: "Bill", age: 21}};
            people[0].printInfo();
            people[1].printInfo();
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Anna\n19\nBill\n21\n", 457))

    
    def test_458(self):
        input = """
        var prefix string;

        type Person struct {
            name string;
            age int;
        }

        func getGreeting(name string) string {
            return prefix + name;
        }

        func (p Person) greet() string {
            return getGreeting(p.name);
        }

        func main() {
            var Corgi Person = Person{name: "Corgi", age: 19};
            prefix := "Hello, my name is ";
            var msg string = Corgi.greet();
            putStringLn(msg);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Hello, my name is Corgi\n", 458))
        
    def test_459(self):
        input = """
        func foo() boolean {
            putStringLn("foo");
            return true;
        }

        func main() {
            var a = true && foo()
            putBoolLn(a)
            var b = false
            putBoolLn(b)

        }
        """
        self.assertTrue(TestCodeGen.test(input, "foo\ntrue\nfalse\n", 459))
        
        
    def test_460(self):
        input = """
        func foo() boolean {
            putStringLn("foo");
            return false;
        }

        func main() {
            foo()
            var a = true
            putBoolLn(a)
            var b = false || foo()
            putBoolLn(b)

        }
        """
        self.assertTrue(TestCodeGen.test(input, "foo\ntrue\nfoo\nfalse\n", 460))

    
    def test_461(self):
        input = """
        type Course interface {print(a [2] int);}
        type PPL3 struct {number int;}
        func (p PPL3) print(a [2] int) {putInt(a[0]);}

        func main(){
            var a PPL3 = PPL3 {number: 10}
            a.print([2] int {10, 2})
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 461))
    
    def test_462(self):
        input = """
        type PPL2 struct {number [1][1][1]int;}
        type PPL3 struct {ppl2 PPL2;}


        func main(){
            var a [2][2]PPL3 
            a[0][1] := PPL3 {ppl2: PPL2 {number: [1][1][1]int{{{10}}} }}
            putInt(a[0][1].ppl2.number[0][0][0])
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 462))
    
    def test_463(self):
        input = """
        type Student struct {
            name string;
            score int;
        }
        
        func sortStudents(students [3]Student, n int) {
            for i := 0; i < n - 1; i += 1 {
                for j := 0; j < n - i - 1; j += 1 {
                    if (students[j].score > students[j + 1].score) {
                        var temp Student = students[j];
                        students[j] := students[j + 1];
                        students[j + 1] := temp;
                    }
                }
            }
        }
        
        func main(){
            var students = [3] Student {Student{name: "John", score: 85}, Student{name: "Alice", score: 92}, Student{name: "Bob", score: 78}};
            sortStudents(students, 3);
            for i := 0; i < 3; i += 1 {
                putString(students[i].name + " ");
                putInt(students[i].score);
                putLn();
            }
        }
        """
        self.assertTrue(TestCodeGen.test(input, "Bob 78\nJohn 85\nAlice 92\n", 463))

    
    def test_464(self):
        input = """
        const MAX = 5;
        
        func bfs(graph [MAX][MAX]int, start int){
            var visited [MAX] boolean;
            var queue [MAX] int;
            var front = 0;
            var rear = 0;
            visited[start] := true;
            queue[rear] := start;
            rear += 1;
            
            for front < rear {
                var u = queue[front]
                front += 1;
                putInt(u)
                putString(" ")
                for v := 0; v < MAX; v += 1{
                    if (graph[u][v] == 1 && !visited[v]){
                        visited[v] := true;
                        queue[rear] := v;
                        rear += 1;
                    }
                }   
            }
        }
        
        func main(){
            var graph = [MAX][MAX] int {{0, 1, 0, 0, 0}, {1, 0, 1, 0, 0}, {0, 1, 0, 1, 0}, {0, 0, 1, 0, 1}, {0, 0, 0, 1, 0}};
            bfs(graph, 0);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "0 1 2 3 4 ", 464))

    
    def test_465(self):
        input = """
        const MAX = 10;
        
        func generateBinary(arr [MAX]int, n int, index int){
            if (index == n) {
                for i := 0; i < n; i += 1 {
                    putInt(arr[i]);
                }
                putLn();
            } else {
                arr[index] := 0;
                generateBinary(arr, n, index + 1);
                arr[index] := 1;
                generateBinary(arr, n, index + 1);
            }
        }
        
        func main() {
            var n = 3;
            var arr [MAX] int;
            putString("All binary strings of length = ")
            putInt(n)
            putLn()
            generateBinary(arr, n, 0);
        }
        """
        self.assertTrue(TestCodeGen.test(input, 
            """All binary strings of length = 3\n000\n001\n010\n011\n100\n101\n110\n111\n""", 465))
    
    def test_466(self):
        input = """
        func fvoid() {putStringLn("Corgi");}

        var global = fint()
        func main() {
            fvoid();
            putFloatLn(global + 2.0)

            var local = "a";
            putBoolLn(local <= "b")
            local += "c"
            putStringLn(local)

        };

        func fint() int {return 1;}
        """
        self.assertTrue(TestCodeGen.test(input, "Corgi\n3.0\ntrue\nac\n", 466))

    
    def test_467(self):
        input = """
        func main() {putInt(5);};
        """
        self.assertTrue(TestCodeGen.test(input, "5", 467))

    
    def test_468(self):
        input = """
        var a int = 10; func main() { putInt(a);};
        """
        self.assertTrue(TestCodeGen.test(input, "10", 468))

    
    def test_469(self):
        input = """
        func main() {
            putIntLn(5 / 2)
            putFloatLn(5 / 2.0)
            putFloatLn(5.0 / 2)
            putFloatLn(5.0 / 2.0)
        }

        """
        self.assertTrue(TestCodeGen.test(input, "2\n2.5\n2.5\n2.5\n", 469))

    
    def test_470(self):
        input = """
        func main() {
            putIntLn(5 % 2)
            putIntLn(2 % 5)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "1\n2\n", 470))

    
    def test_471(self):
        input = """
        func main() {
            putBoolLn(5.0 > 2.0)
            putBoolLn(5.0 < 2.0)
            putBoolLn(5.0 <= 5.0)
            putBoolLn(5.0 >= 5.0)
            putBoolLn(5.0 == 5.0)
            putBoolLn(5.0 != 5.0)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "true\nfalse\ntrue\ntrue\ntrue\nfalse\n", 471))
    
    def test_472(self):
        input = """
        func main() {
            putBoolLn(! true)
            putBoolLn(! false)
            putIntLn(-1)
            putFloatLn(-1.0)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "false\ntrue\n-1\n-1.0\n", 472))

    
    def test_473(self):
        input = """
        func foo() int {return 1;}

        func main() {
            putInt(foo())
        }
        """
        self.assertTrue(TestCodeGen.test(input, "1", 473))

    
    def test_474(self):
        input = """
        var a = 1;
        func main() {
            b := a + 1;
            putInt(a)
            putInt(b)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "12", 474))

    
    def test_475(self):
        input = """
        func main() {
            var a [1] int ;
            a[0] := 1
            putInt(a[0]);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "1", 475))

    
    def test_476(self):
        input = """
        func main() {
            var a [1][1][1] int  = [1][1][1] int {{{0}}};
            a[0][0][0] := 1
            putInt(a[0][0][0]);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "1", 476))

    
    def test_477(self):
        input = """
        func main() {
            var a [2] int;
            a[0] := 100
            a[1] += a[0] + a[0]
            putInt(a[1])
        }
        """
        self.assertTrue(TestCodeGen.test(input, "200", 477))


    def test_478(self):
        input = """
        func main() {
            var a [2] int = [2] int {10, 20};
            putInt(a[0])
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 478))

    
    def test_479(self):
        input = """
        func main() {
            var a = [2][2] int {{1,2}, {3,4}};
            var b = a[0]
            putInt(b[1]);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "2", 479))


    
    def test_480(self):
        input = """
        func main() {
            if (true) {
                putBool(true)
            }
        }
        """
        self.assertTrue(TestCodeGen.test(input, "true", 480))

    
    def test_481(self):
        input = """
        func main() {
            if (true) {
                putBool(true)
            } else {
                putBool(false)
            }
        }
        """
        self.assertTrue(TestCodeGen.test(input, "true", 481))

    
    def test_482(self):
        input = """
        func main() {
            if (false) {
                putBool(true)
            } else {
                putBool(false)
            }
        }
        """
        self.assertTrue(TestCodeGen.test(input, "false", 482))

    
    def test_483(self):
        input = """
        func main() {
            var i = 2;
            for i > 0 {
                putInt(i);
                i -= 1;
            }
            putInt(i);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "210", 483))

    
    def test_484(self):
        input = """
        func main() {
            var i int;
            for i := 0; i < 2; i += 1 {
                putInt(i)
            }
            putInt(i)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "012", 484))


    
    def test_485(self):
        input = """
        func main() {
            var i int;
            for i := 0; i < 5; i += 1 {
                if (i % 2 == 0) {
                    continue;
                }
                putInt(i);
            }
            putInt(i);
        }
        """
        self.assertTrue(TestCodeGen.test(input, "135", 485))


    
    def test_486(self):
        input = """
        func main() {
            var i int = 10;
            for var i int = 0; i < 2; i += 1 {
                putIntLn(i)
            }
            putInt(i)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "0\n1\n10", 486))



    
    def test_487(self):
        input = """
        const a = "Corgi"
        func main() {
            putString(a)
        }
        """
        self.assertTrue(TestCodeGen.test(input, """Corgi""", 487))


    
    def test_488(self):
        input = """
        func main() {
            const i = 10;
            for var i int = 0; i < 2; i += 1 {
                putIntLn(i)
            }
            putInt(i)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "0\n1\n10", 488))


    
    def test_489(self):
        input = """
        type Course interface {study();}
        type PPL3 struct {number int;}
        func (p PPL3) study() {putInt(p.number);}

        func main(){
            var a PPL3 = PPL3 {number: 10}
            putIntLn(a.number)
            a.study()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10\n10", 489))

    
    def test_490(self):
        input = """
        type Course interface {study();}
        type PPL3 struct {number int;}
        func (p PPL3) study() {putInt(p.number);}

        func main(){
            var a Course = nil
            a := PPL3 {number: 10}
            a.study()
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 490))


    def test_491(self):
        input = """
        type PPL3 struct {number int;}

        func main(){
            var a PPL3
            a.number := 10
            putInt(a.number)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "10", 491))

    
    def test_492(self):
        input = """
        type Person struct {
                name string;
                age int;
            }
            func (p Person) printInfo() {
                putStringLn(p.name);
                putIntLn(p.age);
            }
            func main() {
                var people [2]Person = [2]Person{Person{name: "Anna", age: 19},Person{name: "Bill", age: 21}};
                people[0].printInfo();
                people[1].printInfo();
            }
        """
        self.assertTrue(TestCodeGen.test(input, "Anna\n19\nBill\n21\n", 492))

    
    def test_493(self):
        input = """func main() {putInt(69420);};"""
        expect = "69420"
        self.assertTrue(TestCodeGen.test(input, expect, 493))
    
    def test_494(self):
        input = """func main() {var trallalero int = 20;  putInt(trallalero);};"""
        expect = "20"
        self.assertTrue(TestCodeGen.test(input, expect, 494))
    
    def test_495(self):
        input = """var tralala int = 10; func main() { putInt(tralala);};"""
        expect = "10"
        self.assertTrue(TestCodeGen.test(input, expect, 495))
    
    def test_496(self):
        input = Program([FuncDecl("main",[],VoidType(),Block([FuncCall("putInt", [IntLiteral(13092004)])]))])
        expect = "13092004"
        self.assertTrue(TestCodeGen.test(input, expect, 496))
    
    def test_497(self):
        input = Program([FuncDecl("main",[],VoidType(),Block([VarDecl("tung_tung_tung_sahur",IntType(),IntLiteral(500)),FuncCall("putInt", [Id("tung_tung_tung_sahur")])]))])
        expect = "500"
        self.assertTrue(TestCodeGen.test(input, expect, 497))
    
    def test_498(self):  
        input = Program([VarDecl("bombardino",IntType(),IntLiteral(5000)),FuncDecl("main",[],VoidType(),Block([FuncCall("putInt", [Id("bombardino")])]))])
        expect = "5000"
        self.assertTrue(TestCodeGen.test(input, expect, 498))
    
    def test_499(self):
        input = """
        func fvoid() {putStringLn("Khoa Tran");}

        var global = fint()
        func main() {
            fvoid();
            putFloatLn(global + 2.0)

            var local = "a";
            putBoolLn(local <= "b")
            local += "c"
            putStringLn(local)

        };

        func fint() int {return 1;}
        """
        self.assertTrue(TestCodeGen.test(input, "Khoa Tran\n3.0\ntrue\nac\n", 499)) 
    
    def test_500(self):
        input = """
        func main() {
            putBoolLn(5.0 > 2.0)
            putBoolLn(5.0 < 2.0)
            putBoolLn(5.0 <= 5.0)
            putBoolLn(5.0 >= 5.0)
            putBoolLn(5.0 == 5.0)
            putBoolLn(5.0 != 5.0)
        }
        """
        self.assertTrue(TestCodeGen.test(input, "true\nfalse\ntrue\ntrue\ntrue\nfalse\n", 500)) 