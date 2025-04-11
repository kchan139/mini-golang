# MiniGo Language Cheatsheet

MiniGo is a simplified version of Go designed for educational purposes.

## Program Structure
- Single file with declarations in any order
- May contain a `main` function as entry point

## Lexical Structure
- **Comments:** `//` for single-line, `/* */` for multi-line (nestable)
- **Keywords:** `if`, `else`, `for`, `return`, `func`, `type`, `struct`, `interface`, `string`, `int`, `float`, `boolean`, `const`, `var`, `continue`, `break`, `range`, `nil`, `true`, `false`

## Types
- **Basic:** `int`, `float`, `boolean`, `string`
- **Composite:** arrays, structs, interfaces
- **Arrays:** Fixed size, zero-indexed
- **Structs:** Group of fields
- **Interfaces:** Set of method signatures

## Variables and Constants
- **Declaration:** `var name [type] [= value];` or `const name = value;`
- **Assignment:** `:=`, `=`, `+=`, `-=`, `*=`, `/=`, `%=`
- **Scope:** global, function/method, local
- `string`, `struct`, `array`, and `interface` types are passed by reference

## Functions and Methods
- **Functions:** `func name(params) [return-type] { body }`
- **Methods:** `func (receiver type) name(params) [return-type] { body }`

## Expressions
- **Arithmetic:** `+`, `-`, `*`, `/`, `%`
- **Relational:** `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical:** `!`, `&&`, `||`
- **Access:** `array[index]`, `struct.field`
- **Literals:** numeric, string, boolean, array, struct

## Statements
- **Control Flow:**
  - `if (condition) { } else { }`
  - `for condition { }`
  - `for init; condition; update { }`
  - `for index, value := range array { }`
  - `break;`
  - `continue;`
  - `return [expression];`

## Built-in Functions
- I/O: `getInt()`, `putInt()`, `putIntLn()`, `getFloat()`, `putFloat()`, `putFloatLn()`, `getBool()`, `putBool()`, `putBoolLn()`, `getString()`, `putString()`, `putStringLn()`, `putLn()`