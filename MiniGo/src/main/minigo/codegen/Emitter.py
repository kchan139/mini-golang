from AST import *
from Utils import *
from StaticCheck import *
from StaticError import *
from CodeGenError import *
from MachineCode import JasminCode
from Frame import Frame
from typing import Union
import CodeGenerator as codegen


class MType:
    def __init__(self, partype, rettype):
        self.partype = partype
        self.rettype = rettype

    def __str__(self):
        return "MType([" + ",".join(str(x) for x in self.partype) + "]," + str(self.rettype) + ")"

class Val(ABC):
    pass

class Index(Val):
    def __init__(self, value: int):
        self.value = value

class CName(Val):
    def __init__(self, value: str, isStatic=True):
        self.isStatic = isStatic
        self.value = value

class ClassType:
    def __init__(self, name: Id):
        self.name = name

class Symbol:
    def __init__(self, name, mtype, value=None):
        self.name = name
        self.mtype = mtype
        self.value = value

    def __str__(self):
        return "Symbol(" + str(self.name) + "," + str(self.mtype) + ("" if self.value is None else "," + str(self.value)) + ")"
    

class Emitter():
    def __init__(self, filename):
        self.filename = filename
        self.buff = []
        self.jvm = JasminCode()

    def getJVMType(self, inType):
        type_mapping = {
            IntType: "I",
            FloatType: "F",
            BoolType: "Z",
            StringType: "Ljava/lang/String;",
            VoidType: "V"
        }
        
        typeIn = type(inType)
        if typeIn in type_mapping:
            return type_mapping[typeIn]
        if typeIn is Id:
            return "L" + inType.name + ";"
        if typeIn is MType:
            return "(" + "".join(map(self.getJVMType, inType.partype)) + ")" + self.getJVMType(inType.rettype)
        if typeIn is ArrayType:
            if inType.dimens and len(inType.dimens) > 0:
                dim = len(inType.dimens)
                return "[" * dim + self.getJVMType(inType.eleType)
            return "[" + self.getJVMType(inType.eleType)
        return str(typeIn)

    @staticmethod
    def getFullType(inType):
        typeIn = type(inType)
        if typeIn is IntType:
            return "int"
        if typeIn is codegen.StringType:
            return "java/lang/String"
        if typeIn is VoidType:
            return "void"

    def emitPUSHICONST(self, in_: Union[int, str], frame: Frame):
        frame.push()
        ICONST_MIN = -1
        ICONST_MAX = 5
        BIPUSH_MIN = -128
        BIPUSH_MAX = 127
        SIPUSH_MIN = -32768
        SIPUSH_MAX = 32767

        if isinstance(in_, bool):
            actual_val = 1 if in_ else 0
            return self.jvm.emitICONST(actual_val)

        if isinstance(in_, int):
            if ICONST_MIN <= in_ <= ICONST_MAX:
                return self.jvm.emitICONST(in_)
            if BIPUSH_MIN <= in_ <= BIPUSH_MAX:
                return self.jvm.emitBIPUSH(in_)
            if SIPUSH_MIN <= in_ <= SIPUSH_MAX:
                return self.jvm.emitSIPUSH(in_)
            
        if type(in_) is str:
            str_val_lower = in_.lower()
            if str_val_lower == "true":
                return self.emitPUSHICONST(1, frame)
            if str_val_lower == "false":
                return self.emitPUSHICONST(0, frame)
            
            try:
                numeric_val = int(in_)
                return self.emitPUSHICONST(numeric_val, frame)
            except ValueError:
                raise IllegalOperandException(f"String operand '{in_}' cannot be pushed as an iconst.")

        raise IllegalOperandException(f"Unsupported type '{type(in_)}' for PUSHICONST with value '{in_}'.")


    def emitPUSHFCONST(self, in_: str, frame: Frame):
        value = float(in_)
        frame.push()
        if value in [0.0, 1.0, 2.0]:
            return self.jvm.emitFCONST("{0:.1f}".format(value))
        return self.jvm.emitLDC(str(value))     

    def emitPUSHCONST(self, in_: str, typ: Type, frame: Frame):
        if type(typ) is IntType or type(typ) is BoolType:
            return self.emitPUSHICONST(in_, frame)
        if type(typ) is StringType:
            frame.push()
            return self.jvm.emitLDC(in_)
        raise IllegalOperandException(in_)

    def emitALOAD(self, in_: Type, frame: Frame):
        frame.pop()
        frame.pop()
        frame.push()
        if type(in_) is IntType:
            return self.jvm.emitIALOAD()
        if type(in_) is FloatType:
            return self.jvm.emitFALOAD()
        if type(in_) is BoolType:
            return self.jvm.emitBALOAD()
        if type(in_) is codegen.ArrayType or type(in_) is Id or type(in_) is StringType:
            return self.jvm.emitAALOAD()
        raise IllegalOperandException(str(in_))

    def emitASTORE(self, in_: Type, frame: Frame):
        frame.pop() # val
        frame.pop() # idx
        frame.pop() # arr ref
        
        if type(in_) is IntType:
            return self.jvm.emitIASTORE()
        if type(in_) is FloatType:
            return self.jvm.emitFASTORE()
        if type(in_) is BoolType:
            return self.jvm.emitBASTORE()
        if type(in_) is codegen.ArrayType or type(in_) is Id or type(in_) is StringType:
            return self.jvm.emitAASTORE()
        raise IllegalOperandException(str(in_))

    def emitVAR(self, in_: int, varName: str, inType: Type, fromLabel: int, toLabel: int, _: Frame):
        if isinstance(inType, str):
            typeStr = inType
        elif isinstance(inType, ClassType):
            typeStr = "L" + inType.cname + ";"
        else:
            typeStr = self.getJVMType(inType)
        
        return f".var {in_} is {varName} {typeStr} from {fromLabel} to {toLabel}\n"

    def emitREADVAR(self, name: str, inType: Type, index: int, frame: Frame):
        frame.push()
        if type(inType) is IntType or type(inType) is BoolType:
            return self.jvm.emitILOAD(index)
        if type(inType) is FloatType:
            return self.jvm.emitFLOAD(index)
        if type(inType) is codegen.ArrayType or type(inType) is Id or \
            type(inType) is codegen.ClassType or type(inType) is StringType:
            return self.jvm.emitALOAD(index)
        raise IllegalOperandException(name)

    def emitREADVAR2(self, name: str, *_):
        raise IllegalOperandException(name)

    def emitWRITEVAR(self, name: str, inType: Type, index: int, frame: Frame):
        frame.pop()
        if type(inType) is IntType or type(inType) is BoolType:
            return self.jvm.emitISTORE(index)
        if type(inType) is FloatType:
            return self.jvm.emitFSTORE(index)
        if type(inType) is codegen.ArrayType or type(inType) is Id or type(inType) is StringType:
            return self.jvm.emitASTORE(index)
        raise IllegalOperandException(name)

    def emitWRITEVAR2(self, name: str, *_):
        raise IllegalOperandException(name)

    def emitATTRIBUTE(self, lexeme: str, in_: Type, isStatic: bool, isFinal: bool, value: str):
        if isStatic:
            return self.jvm.emitSTATICFIELD(lexeme, self.getJVMType(in_), isFinal, value)
        
        field_code = self.jvm.emitINSTANCEFIELD(lexeme, self.getJVMType(in_), isFinal, value)
        if "public" not in field_code:
            field_code = field_code.replace(".field ", ".field public ")
        return field_code

    def emitGETSTATIC(self, lexeme: str, in_: Type, frame: Frame):
        frame.push()
        return self.jvm.emitGETSTATIC(lexeme, self.getJVMType(in_))

    def emitPUTSTATIC(self, lexeme: str, in_: Type, frame: Frame):
        frame.pop()
        return self.jvm.emitPUTSTATIC(lexeme, self.getJVMType(in_))

    def emitGETFIELD(self, lexeme: str, in_: Type, frame: Frame):
        return self.jvm.emitGETFIELD(lexeme, self.getJVMType(in_))

    def emitPUTFIELD(self, lexeme: str, in_: Type, frame: Frame):
        frame.pop()
        frame.pop()
        return self.jvm.emitPUTFIELD(lexeme, self.getJVMType(in_))

    def emitINVOKESTATIC(self, lexeme: str, in_: Type, frame: Frame):
        typ = in_
        [frame.pop() for _ in range(len(typ.partype))]
        if type(typ.rettype) is not VoidType:
            frame.push()
        return self.jvm.emitINVOKESTATIC(lexeme, self.getJVMType(in_))

    def emitINVOKESPECIAL(self, frame: Frame, lexeme: str=None, in_: Type=None):
        if lexeme and in_:
            typ = in_
            [frame.pop() for _ in range(len(typ.partype))]
            frame.pop()
            if type(typ.rettype) is not VoidType:
                frame.push()
            return self.jvm.emitINVOKESPECIAL(lexeme, self.getJVMType(in_))
        
        if not lexeme and not in_:
            frame.pop()
            return self.jvm.emitINVOKESPECIAL()

    def emitINVOKEVIRTUAL(self, lexeme: str, in_: Type, frame: Frame):
        typ = in_    
        [frame.pop() for _ in range(len(typ.partype))]
        frame.pop()
        if type(typ.rettype) is not VoidType:
            frame.push()
        return self.jvm.emitINVOKEVIRTUAL(lexeme, self.getJVMType(in_))

    def emitNEGOP(self, in_: Type, frame: Frame):
        if type(in_) is IntType:
            return self.jvm.emitINEG()
        return self.jvm.emitFNEG()

    def emitNOT(self, in_: Type, frame: Frame):
        label_1 = frame.getNewLabel()
        label_2 = frame.getNewLabel()
        result = []
        result.append(self.emitIFTRUE(label_1, frame))
        result.append(self.emitPUSHCONST("true", in_, frame))
        result.append(self.emitGOTO(label_2, frame))
        result.append(self.emitLABEL(label_1, frame))
        result.append(self.emitPUSHCONST("false", in_, frame))
        result.append(self.emitLABEL(label_2, frame))
        return ''.join(result)

    def emitADDOP(self, lexeme: str, in_: Type, frame: Frame):
        frame.pop()
        if lexeme == "+":
            if type(in_) is IntType:
                return self.jvm.emitIADD()
            return self.jvm.emitFADD()
        if type(in_) is IntType:
            return self.jvm.emitISUB()
        return self.jvm.emitFSUB()

    def emitMULOP(self, lexeme: str, in_: Type, frame: Frame):
        frame.pop()
        if lexeme == "*":
            if type(in_) is IntType:
                return self.jvm.emitIMUL()
            return self.jvm.emitFMUL()
        if type(in_) is IntType:
            return self.jvm.emitIDIV()
        return self.jvm.emitFDIV()

    def emitDIV(self, frame: Frame):
        frame.pop()
        return self.jvm.emitIDIV()

    def emitMOD(self, frame: Frame):
        frame.pop()
        return "\tirem\n"

    def emitANDOP(self, frame: Frame):
        frame.pop()
        return self.jvm.emitIAND()
    
    def emitOROP(self, frame: Frame):
        frame.pop()
        return self.jvm.emitIOR()

    def emitREOP(self, op: str, in_: Type, frame: Frame):
        result = []
        false_label = frame.getNewLabel()
        end_label = frame.getNewLabel()

        frame.pop()
        frame.pop()

        if type(in_) is IntType:
            if op == ">":
                result.append(self.jvm.emitIFICMPLE(false_label))
            elif op == ">=":
                result.append(self.jvm.emitIFICMPLT(false_label))
            elif op == "<":
                result.append(self.jvm.emitIFICMPGE(false_label))
            elif op == "<=":
                result.append(self.jvm.emitIFICMPGT(false_label))
            elif op == "!=":
                result.append(self.jvm.emitIFICMPEQ(false_label))
            elif op == "==":
                result.append(self.jvm.emitIFICMPNE(false_label))

        elif type(in_) is FloatType:
            if op == ">":
                result.append(self.jvm.emitFCMPL())
                result.append(self.jvm.emitIFLE(false_label))
            elif op == ">=":
                result.append(self.jvm.emitFCMPL())
                result.append(self.jvm.emitIFLT(false_label))
            elif op == "<":
                result.append(self.jvm.emitFCMPL())
                result.append(self.jvm.emitIFGE(false_label))
            elif op == "<=":
                result.append(self.jvm.emitFCMPL())
                result.append(self.jvm.emitIFGT(false_label))
            elif op == "!=":
                result.append(self.jvm.emitFCMPL())
                result.append(self.jvm.emitIFEQ(false_label))
            elif op == "==":
                result.append(self.jvm.emitFCMPL())
                result.append(self.jvm.emitIFNE(false_label))

        elif type(in_) is StringType:
            if op == "==":
                result.append(self.jvm.emitIFICMPNE(false_label))
            elif op == "!=":
                result.append(self.jvm.emitIFICMPEQ(false_label))
            elif op == "<":
                result.append(self.jvm.emitIFICMPGE(false_label))
            elif op == "<=":
                result.append(self.jvm.emitIFICMPGT(false_label))
            elif op == ">":
                result.append(self.jvm.emitIFICMPLE(false_label))
            elif op == ">=":
                result.append(self.jvm.emitIFICMPLT(false_label))

        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitGOTO(end_label, frame))
        result.append(self.emitLABEL(false_label, frame))

        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitLABEL(end_label, frame))
        return ''.join(result)

    def emitRELOP(self, op: str, in_: Type, trueLabel: int, falseLabel: int, frame: Frame):
        result = []
        frame.pop()
        frame.pop()

        if op == ">":
            result.append(self.jvm.emitIFICMPLE(falseLabel))
            result.append(self.emitGOTO(trueLabel))
        elif op == ">=":
            result.append(self.jvm.emitIFICMPLT(falseLabel))
        elif op == "<":
            result.append(self.jvm.emitIFICMPGE(falseLabel))
        elif op == "<=":
            result.append(self.jvm.emitIFICMPGT(falseLabel))
        elif op == "!=":
            result.append(self.jvm.emitIFICMPEQ(falseLabel))
        elif op == "==":
            result.append(self.jvm.emitIFICMPNE(falseLabel))
        
        result.append(self.jvm.emitGOTO(trueLabel))
        return ''.join(result)

    def emitMETHOD(self, lexeme, in_, isStatic,abstract = False):
        if abstract:
            return JasminCode.END + ".method public abstract " + lexeme + self.getJVMType(in_) + JasminCode.END
        return self.jvm.emitMETHOD(lexeme, self.getJVMType(in_), isStatic)

    def emitENDMETHOD(self, frame: Frame):
        buff = []
        if frame:
            buff.append(self.jvm.emitLIMITSTACK(frame.getMaxOpStackSize() + 2))
            buff.append(self.jvm.emitLIMITLOCAL(frame.getMaxIndex()))
        buff.append(self.jvm.emitENDMETHOD())
        return ''.join(buff)

    def getConst(self, ast: Literal):
        if type(ast) is IntLiteral:
            return (str(ast.value), IntType())

    def emitIFTRUE(self, label: int, frame: Frame):
        frame.pop()
        return self.jvm.emitIFGT(label)

    def emitIFFALSE(self, label: int, frame: Frame):
        frame.pop()
        return self.jvm.emitIFLE(label)

    def emitIFICMPGT(self, label: int, frame: Frame):
        frame.pop()
        return self.jvm.emitIFICMPGT(label)

    def emitIFICMPLT(self, label: int, frame: Frame):
        frame.pop()
        return self.jvm.emitIFICMPLT(label)    
    
    def emitDUP(self, frame: Frame):
        frame.push()
        return self.jvm.emitDUP()

    def emitPOP(self, frame: Frame):
        frame.pop()
        return self.jvm.emitPOP()

    def emitI2F(self, _: Frame):
        return self.jvm.emitI2F()

    def emitRETURN(self, in_: Type, frame: Frame):
        if type(in_) is IntType or type(in_) is BoolType:
            frame.pop()
            return self.jvm.emitIRETURN()
        if type(in_) is FloatType:
            frame.pop()
            return self.jvm.emitFRETURN()  
        if type(in_) is StringType or type(in_) is ArrayType or type(in_) is Id:
            frame.pop()
            return self.jvm.emitARETURN()                 
        if type(in_) is VoidType:
            return self.jvm.emitRETURN()

    def emitLABEL(self, label: int, _: Frame):
        return self.jvm.emitLABEL(label)

    def emitGOTO(self, label: int, _: Frame):
        return self.jvm.emitGOTO(str(label))

    def emitPROLOG(self, name: str, parent: str, interface = False):
        result = []
        result.append(self.jvm.emitSOURCE(name + ".java"))
        result.append(self.jvm.emitCLASS(f"public {'interface' if interface else ''} {name}"))
        result.append(self.jvm.emitSUPER("java/land/Object" if parent == "" else parent))
        return ''.join(result)
    
    def emitIMPLEMENT(self, name):
        return '\t' + '.implements ' + name + '\n'

    def emitLIMITSTACK(self, num: int):
        return self.jvm.emitLIMITSTACK(num)

    def emitLIMITLOCAL(self, num: int):
        return self.jvm.emitLIMITLOCAL(num)

    def emitEPILOG(self):
        file = open(self.filename, "w")
        file.write(''.join(self.buff))
        file.close()
        return ""
    

    def printout(self, in_: str):
        self.buff.append(in_)

    def clearBuff(self):
        self.buff.clear()

    def emitNEWARRAY(self, in_: Type, _: Frame):
        if type(in_) is IntType:
            return self.jvm.emitNEWARRAY("int")
        if type(in_) is BoolType:
            return self.jvm.emitNEWARRAY("boolean")
        if type(in_) is FloatType:
            return self.jvm.emitNEWARRAY("float")
        raise IllegalOperandException(str(in_))

    def emitANEWARRAY(self, in_: Type, _: Frame):        
        if type(in_) is StringType:
            return self.jvm.emitANEWARRAY("java/lang/String")
        if type(in_) is ArrayType:
            return self.jvm.emitANEWARRAY(self.getJVMType(in_))
        if type(in_) is Id:
            return self.jvm.emitANEWARRAY(in_.name)
        raise IllegalOperandException(str(in_))

    def emitMULTIANEWARRAY(self, in_: Type, frame: Frame):
        type_descriptor = self.getJVMType(in_)
        dim = len(in_.dimens)
        
        [frame.pop() for _ in range(dim)]
        frame.push()
        
        return self.jvm.emitMULTIANEWARRAY(type_descriptor, str(dim))
    
    def emitNEW(self, lexeme: str, frame: Frame):
        frame.push()
        return self.jvm.emitNEW(lexeme)

    def emitPUSHNULL(self, frame: Frame):
        frame.push()
        return self.jvm.emitPUSHNULL()
    
    def emitINVOKEINTERFACE(self, lexeme: str, in_: Type, frame: Frame):
        typ = in_
        [frame.pop() for _ in range(len(typ.partype))]
        frame.pop()
        
        if not type(typ.rettype) is VoidType:
            frame.push()
        
        numArgs = len(typ.partype) + 1
        return self.jvm.emitINVOKEINTERFACE(lexeme, self.getJVMType(in_), numArgs)

    def emitIFGT(self, label: int, frame: Frame):
        frame.pop()
        return self.jvm.emitIFGT(label)
    
    def emitIMPLEMENTS(self, lexeme: str):
        return self.jvm.emitIMPLEMENTS(lexeme)