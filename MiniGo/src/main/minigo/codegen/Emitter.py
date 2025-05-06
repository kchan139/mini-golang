from AST import *
from Utils import *
from StaticCheck import *
from StaticError import *
import CodeGenerator as cgen
from MachineCode import JasminCode


class MType:
    def __init__(self,partype,rettype):
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
    def __init__(self, name):
        #value: Id
        self.name = name

class Symbol:
    def __init__(self, name, mtype, value=None):
        self.name = name
        self.mtype = mtype
        self.value = value

    def __str__(self):
        return "Symbol(" + str(self.name) + "," + str(self.mtype) + ("" if self.value is None else "," + str(self.value)) + ")"
    

class Emitter:
    def __init__(self, filename):
        self.filename = filename
        self.buff = list()
        self.jvm = JasminCode()

    def getJVMType(self, inType):
        typeIn = type(inType)
        if typeIn is IntType:
            return "I"
        elif typeIn is FloatType:
            return "F"
        elif typeIn is BoolType:
            return "Z"
        elif typeIn is cgen.StringType:
            return "Ljava/lang/String;"
        elif typeIn is VoidType:
            return "V"
        elif typeIn is ArrayType:
            return "[" + self.getJVMType(inType.eleType)
        elif typeIn is MType:
            return "(" + "".join(list(map(lambda x: self.getJVMType(x), inType.partype))) + ")" + self.getJVMType(inType.rettype)
        elif typeIn is cgen.ClassType:
            return "L" + inType.classname.name + ";"

    def emitPUSHICONST(self, value, frame):
        frame.push()

        ICONST_MIN = -1
        ICONST_MAX = 5
        BIPUSH_MIN = -128
        BIPUSH_MAX = 127
        SIPUSH_MIN = -32768
        SIPUSH_MAX = 32767

        if ICONST_MIN <= value <= ICONST_MAX:
            return self.jvm.emitICONST(value)
        elif BIPUSH_MIN <= value <= BIPUSH_MAX:
            return self.jvm.emitBIPUSH(value)
        elif SIPUSH_MIN <= value <= SIPUSH_MAX:
            return self.jvm.emitSIPUSH(value)
        else:
            return self.jvm.emitLDC(str(value))

    def emitFCONST(self, in_, frame):
        frame.push()
        if in_ == 0.0:
            return self.jvm.emitFCONST_0()
        elif in_ == 1.0:
            return self.jvm.emitFCONST_1()
        elif in_ == 2.0:
            return self.jvm.emitFCONST_2()
        else:
            return self.jvm.emitLDC(str(in_))

    def emitBIPUSH(self, val, frame):
        frame.push()
        return self.jvm.emitBIPUSH(val)

    def emitSIPUSH(self, val, frame):
        frame.push()
        return self.jvm.emitSIPUSH(val)

    def emitLDC(self, in_, frame):
        frame.push()
        return self.jvm.emitLDC(in_)

    def emitVAR(self, in_, varName, inType, fromLabel, toLabel, frame):
        return self.jvm.emitVAR(in_, varName, self.getJVMType(inType), fromLabel, toLabel)

    def emitREADVAR(self, name, inType, index, frame):
        frame.push()
        emitType = self.getJVMType(inType)
        if emitType in ("I", "Z"):
            return self.jvm.emitILOAD(index)
        elif emitType is "F":
            return self.jvm.emitFLOAD(index)
        else:
            return self.jvm.emitALOAD(index)

    def emitWRITEVAR(self, name, inType, index, frame):
        frame.pop()
        emitType = self.getJVMType(inType)
        if emitType in ("I", "Z"):
            return self.jvm.emitISTORE(index)
        elif emitType is "F":
            return self.jvm.emitFSTORE(index)
        else:
            return self.jvm.emitASTORE(index)

    def emitGETSTATIC(self, lexeme, inType, frame):
        frame.push()
        return self.jvm.emitGETSTATIC(lexeme, self.getJVMType(inType))

    def emitPUTSTATIC(self, lexeme, inType, frame):
        frame.pop()
        return self.jvm.emitPUTSTATIC(lexeme, self.getJVMType(inType))

    def emitGETFIELD(self, lexeme, inType, frame):
        return self.jvm.emitGETFIELD(lexeme, self.getJVMType(inType))

    def emitPUTFIELD(self, lexeme, inType, frame):
        frame.pop()
        frame.pop()
        return self.jvm.emitPUTFIELD(lexeme, self.getJVMType(inType))

    def emitINVOKESTATIC(self, lexeme, in_, frame):
        typ = in_
        list(map(lambda x: frame.pop(), typ.partype))
        if type(typ.rettype) is not VoidType:
            frame.push()
        return self.jvm.emitINVOKESTATIC(lexeme, self.getJVMType(in_))

    def emitINVOKESPECIAL(self, frame, lexeme=None):
        if not lexeme:
            frame.pop()
        return self.jvm.emitINVOKESPECIAL(lexeme)

    def emitINVOKEVIRTUAL(self, lexeme, in_, frame):
        typ = in_
        list(map(lambda x: frame.pop(), typ.partype))
        frame.pop()
        if type(typ.rettype) is not VoidType:
            frame.push()
        return self.jvm.emitINVOKEVIRTUAL(lexeme, self.getJVMType(in_))

    def emitNEW(self, lexeme, frame):
        frame.push()
        return self.jvm.emitNEW(lexeme)

    def emitNEWARRAY(self, in_, frame):
        frame.pop()
        frame.push()
        return self.jvm.emitNEWARRAY(self.getJVMType(in_))

    def emitANEWARRAY(self, in_, frame):
        frame.pop()
        frame.push()
        return self.jvm.emitANEWARRAY(in_)

    def emitMULTIANEWARRAY(self, in_, frame):
        dimensions = in_[0]
        for i in range(dimensions):
            frame.pop()
        frame.push()
        return self.jvm.emitMULTIANEWARRAY(in_[1], in_[0])

    def emitDUP(self, frame):
        frame.push()
        return self.jvm.emitDUP()

    def emitPOP(self, frame):
        frame.pop()
        return self.jvm.emitPOP()

    def emitI2F(self, frame):
        return self.jvm.emitI2F()

    def emitNEGOP(self, in_, frame):
        if type(in_) is IntType:
            return self.jvm.emitINEG()
        else:
            return self.jvm.emitFNEG()

    def emitNOT(self, frame):
        result = list()
        labelTrue = frame.getNewLabel()
        labelEnd = frame.getNewLabel()
        
        result.append(self.emitIFEQ(labelTrue, frame))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelEnd, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelEnd, frame))
        return ''.join(result)

    def emitIADD(self, frame):
        frame.pop()
        return self.jvm.emitIADD()

    def emitFADD(self, frame):
        frame.pop()
        return self.jvm.emitFADD()

    def emitISUB(self, frame):
        frame.pop()
        return self.jvm.emitISUB()

    def emitFSUB(self, frame):
        frame.pop()
        return self.jvm.emitFSUB()

    def emitIMUL(self, frame):
        frame.pop()
        return self.jvm.emitIMUL()

    def emitFMUL(self, frame):
        frame.pop()
        return self.jvm.emitFMUL()

    def emitIDIV(self, frame):
        frame.pop()
        return self.jvm.emitIDIV()

    def emitFDIV(self, frame):
        frame.pop()
        return self.jvm.emitFDIV()

    def emitIREM(self, frame):
        frame.pop()
        return self.jvm.emitIREM()

    def emitIAND(self, frame):
        frame.pop()
        return self.jvm.emitIAND()

    def emitIOR(self, frame):
        frame.pop()
        return self.jvm.emitIOR()

    def emitIEQ(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        labelEnd = frame.getNewLabel()
        
        result.append(self.jvm.emitIF_ICMPEQ(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelEnd, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelEnd, frame))
        return ''.join(result)

    def emitFEQ(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitFCMPL())
        result.append(self.jvm.emitIFEQ(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitINE(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitIF_ICMPNE(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitFNE(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitFCMPL())
        result.append(self.jvm.emitIFNE(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitILT(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitIF_ICMPLT(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitFLT(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitFCMPL())
        result.append(self.jvm.emitIFLT(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitILE(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitIF_ICMPLE(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitFLE(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitFCMPL())
        result.append(self.jvm.emitIFLE(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitIGT(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitIF_ICMPGT(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitFGT(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitFCMPL())
        result.append(self.jvm.emitIFGT(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitIGE(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitIF_ICMPGE(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitFGE(self, frame):
        frame.pop()
        frame.pop()
        result = list()
        labelTrue = frame.getNewLabel()
        labelFalse = frame.getNewLabel()
        
        result.append(self.jvm.emitFCMPL())
        result.append(self.jvm.emitIFGE(labelTrue))
        result.append(self.emitPUSHICONST(0, frame))
        result.append(self.emitGOTO(labelFalse, frame))
        result.append(self.emitLABEL(labelTrue, frame))
        result.append(self.emitPUSHICONST(1, frame))
        result.append(self.emitLABEL(labelFalse, frame))
        return ''.join(result)

    def emitLABEL(self, label, frame):
        return self.jvm.emitLABEL(label)

    def emitGOTO(self, label, frame):
        return self.jvm.emitGOTO(label)

    def emitIFTRUE(self, label, frame):
        frame.pop()
        return self.jvm.emitIFGT(label)

    def emitIFFALSE(self, label, frame):
        frame.pop()
        return self.jvm.emitIFLE(label)

    def emitIFICMPGT(self, label, frame):
        frame.pop()
        frame.pop()
        return self.jvm.emitIF_ICMPGT(label)

    def emitIFICMPLT(self, label, frame):
        frame.pop()
        frame.pop()
        return self.jvm.emitIF_ICMPLT(label)

    def emitIFICMPGE(self, label, frame):
        frame.pop()
        frame.pop()
        return self.jvm.emitIF_ICMPGE(label)

    def emitIFICMPLE(self, label, frame):
        frame.pop()
        frame.pop()
        return self.jvm.emitIF_ICMPLE(label)

    def emitIFICMPEQ(self, label, frame):
        frame.pop()
        frame.pop()
        return self.jvm.emitIF_ICMPEQ(label)

    def emitIFICMPNE(self, label, frame):
        frame.pop()
        frame.pop()
        return self.jvm.emitIF_ICMPNE(label)

    def emitIFEQ(self, label, frame):
        frame.pop()
        return self.jvm.emitIFEQ(label)

    def emitIFNE(self, label, frame):
        frame.pop()
        return self.jvm.emitIFNE(label)

    def emitIFLT(self, label, frame):
        frame.pop()
        return self.jvm.emitIFLT(label)

    def emitIFGT(self, label, frame):
        frame.pop()
        return self.jvm.emitIFGT(label)

    def emitIFLE(self, label, frame):
        frame.pop()
        return self.jvm.emitIFLE(label)

    def emitIFGE(self, label, frame):
        frame.pop()
        return self.jvm.emitIFGE(label)

    def emitInitNewArray(self, arrayType, frame, defaultInit=None):
        result = []
        result.append(self.emitDUP(frame)) # duplicate the array reference
        
        if isinstance(arrayType, ArrayType):
            elemType = arrayType.eleType
            # For each element, duplicate array ref, push index, init value, and store
            for i in range(arrayType.size):
                result.append(self.emitDUP(frame))  # duplicate array ref
                result.append(self.emitPUSHICONST(i, frame))  # push index
                
                # Push default value based on element type
                if isinstance(elemType, IntType):
                    result.append(self.emitPUSHICONST(0, frame))
                elif isinstance(elemType, FloatType):
                    result.append(self.emitFCONST(0.0, frame))
                elif isinstance(elemType, BoolType):
                    result.append(self.emitPUSHICONST(0, frame))
                elif isinstance(elemType, StringType):
                    result.append(self.emitPUSHCONST("", StringType(), frame))
                else:
                    result.append(self.jvm.emitACONST_NULL())
                    frame.push()
                
                # Store the value in the array
                result.append(self.jvm.emitIASTORE() if isinstance(elemType, (IntType, BoolType)) 
                             else self.jvm.emitFASTORE() if isinstance(elemType, FloatType) 
                             else self.jvm.emitAASTORE())
                frame.pop()
                frame.pop()
                frame.pop()
        
        return ''.join(result)

    def emitARRAYACCESS(self, frame, arrayType):
        frame.pop()  # pop index
        frame.pop()  # pop array reference
        frame.push() # push accessed value
        
        elemType = arrayType.eleType
        if isinstance(elemType, IntType) or isinstance(elemType, BoolType):
            return self.jvm.emitIALOAD()
        elif isinstance(elemType, FloatType):
            return self.jvm.emitFALOAD()
        else:  # Array, String, or other object types
            return self.jvm.emitAALOAD()

    def emitARRAYSTORE(self, frame, arrayType):
        frame.pop()  # pop value
        frame.pop()  # pop index
        frame.pop()  # pop array reference
        
        elemType = arrayType.eleType
        if isinstance(elemType, IntType) or isinstance(elemType, BoolType):
            return self.jvm.emitIASTORE()
        elif isinstance(elemType, FloatType):
            return self.jvm.emitFASTORE()
        else:  # Array, String, or other object types
            return self.jvm.emitAASTORE()

    def emitPUSHCONST(self, value, typ, frame):
        frame.push()
        if isinstance(typ, IntType):
            return self.emitPUSHICONST(value, frame)
        elif isinstance(typ, FloatType):
            return self.emitFCONST(value, frame)
        elif isinstance(typ, StringType):
            return self.emitLDC(f'"{value}"', frame)
        elif isinstance(typ, BoolType):
            return self.emitPUSHICONST(1 if value else 0, frame)
        else:
            return self.emitLDC('""', frame)  # Empty string as default

    def emitARRAYLEN(self, frame):
        frame.pop()  # pop array reference
        frame.push() # push length value (int)
        return self.jvm.emitARRAYLENGTH()

    def emitMETHOD(self, name, mtype, isStatic=False, isMain=False):
        returnType = mtype.rettype
        is_static = isStatic or isMain
        param_types = "".join(self.getJVMType(p) for p in mtype.partype)
        return_type = self.getJVMType(returnType)
        descriptor = "(" + param_types + ")" + return_type
        return self.jvm.emitMETHOD(name, descriptor, is_static)

    def emitENDMETHOD(self, frame):
        buffer = []
        buffer.append(self.jvm.emitLIMITSTACK(frame.getMaxOpStackSize()))
        buffer.append(self.jvm.emitLIMITLOCAL(frame.getMaxIndex()))
        buffer.append(self.jvm.emitENDMETHOD())
        return ''.join(buffer)

    def emitPROLOG(self, name, parent):
        result = []
        result.append(self.jvm.emitSOURCE(self.filename))
        result.append(self.jvm.emitCLASS("public " + name))
        result.append(self.jvm.emitSUPER(parent))
        return ''.join(result)

    def emitEPILOG(self):
        return self.jvm.emitEND()

    def printout(self):
        return ''.join(self.buff)

    def clearBuff(self):
        self.buff.clear()

    def emit(self, code):
        self.buff.append(code)