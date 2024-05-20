import copy


# 目标代码生成器
class ObjectCode:
    def __init__(self, middleCode, symbolTable, funcTable):
        self.mipsCode = list()  # 目标代码
        self.regTable = {'$' + str(i): '' for i in range(7, 26)}  # 寄存器状态表 如'$7': ''
        self.varStatus = {}  # 记录变量是在寄存器当中还是内存当中 变量状态表
        self.mid_Code = copy.deepcopy(middleCode)  # 中间代码
        self.symbolTable = copy.deepcopy(symbolTable)  # 符号表
        self.funcNameTable = list()  # 函数名表
        for f in funcTable:
            self.funcNameTable.append(f.name)
        self.DATA_SEGMENT = 10010000  # 数据段偏移量
        self.STACK_OFFSET = 8000  # 堆栈偏移量
        return

    # 申请一个寄存器
    def reg(self, identifier, codes):
        if identifier[0] != 't': 
            return identifier
        mark = (identifier in self.varStatus and self.varStatus[identifier] == 'reg')
        if mark:
            for key in self.regTable:  
                if self.regTable[key] == identifier: 
                    return key
        while True:
            for key in self.regTable:
                if self.regTable[key] == '':  
                    self.regTable[key] = identifier  
                    self.varStatus[identifier] = 'reg'
                    return key
            varRegUsed = list(filter(lambda x: x != '', self.regTable.values()))
            varUsageCnts = dict()
            for code in codes:
                for term in code: 
                    tmp = str(term)
                    if tmp[0] == 't':
                        if tmp in varRegUsed:
                            if tmp in varUsageCnts:
                                varUsageCnts[tmp] += 1
                            else:
                                varUsageCnts[tmp] = 1
            mark = False
            for var in varRegUsed:
                if var not in varUsageCnts:
                    for reg in self.regTable:
                        if self.regTable[reg] == var:
                            mark = True
                            self.regTable[reg] = '' 
                            self.varStatus[var] = 'memory' 
            if mark: 
                return
            sorted(varUsageCnts.items(), key=lambda x: x[1])
            varFreed = list(varUsageCnts.keys())[0]
            for reg in self.regTable:
                if self.regTable[reg] == varFreed:
                    for item in self.symbolTable:
                        if item.midval == varFreed: 
                            self.mipsCode.append('addi $at, $zero, 0x{}'.format(self.DATA_SEGMENT)) 
                            self.mipsCode.append('sw {}, {}($at)'.format(reg, item.offset)) 
                            self.regTable[reg] = ''
                            self.varStatus[varFreed] = 'memory'
                            return
            return

    def handle1(self,code,midCode,mipsCode):
        src = self.reg(code[1], midCode)
        dst = self.reg(code[3], midCode)
        mipsCode.append('    add {},$zero,{}'.format(dst, src))

    def handle2(self,code,midCode,mipsCode):
        src = self.reg(code[1], midCode) 
        base = code[3][: code[3].index('[')] 
        offset = code[3][code[3].index('[') + 1: -1] 
        dst_offset = self.reg(offset, midCode) 
        mipsCode.append('    la $v1,{}'.format(base)) 
        mipsCode.append('    mul {},{},4'.format(dst_offset, dst_offset))  
        mipsCode.append('    addu {},{},$v1'.format(dst_offset, dst_offset))  
        mipsCode.append('    sw {},'.format(src) + '0({})'.format(dst_offset)) 

    def handle3(self,code,midCOde,mipsCode):
        dst = self.reg(code[3], midCOde) 
        base = code[1][: code[1].index('[')]  
        offset = code[1][code[1].index('[') + 1: -1]   
        src_offset = self.reg(offset, midCOde)  
        mipsCode.append('    la $v1,{}'.format(base))  
        mipsCode.append('    mul {},{},4'.format(src_offset, src_offset))  
        mipsCode.append('    addu {},{},$v1'.format(src_offset, src_offset))  
        mipsCode.append('    lw {},'.format(dst) + '0({})'.format(src_offset)) 
    
    def handle4(self,code,mipsCode):
        if code[0] in self.funcNameTable or code[0][0] == 'f':  # is a function definition
            mipsCode.append('')  # empty line
        mipsCode.append('{}:'.format(code[0]))
    
    def handle5(self,code,midCode,mipsCode):
        if code[3] != 'ra':  # return addr
            register = self.reg(code[3], midCode)
            if str(register)[0] != '$': 
                mipsCode.append("    add $a0, $zero, {}".format(register))
                register = '$a0'
            mipsCode.append('    sw {}, {}($fp)'.format(register, code[2]))
        else:
            mipsCode.append('    sw $ra, {}($fp)'.format(code[2]))  # ra -> mem[fp+ ]

    def handle6(self,code,midCode,mipsCode):
        if code[3] != 'ra':
            register = self.reg(code[3], midCode)
            mipsCode.append('    lw {}, {}($fp)'.format(register, code[2]))
        else:
            mipsCode.append('    lw $ra, {}($fp)'.format(code[2]))  # ra <- mem[fp+ ]
    
    def handle7(self,code,midCode,mipsCode):
        if code[3] != 'ra':
            register = self.reg(code[3], midCode)
            if str(register)[0] != '$':
                mipsCode.append("    add $a0,$zero,{}".format(register))
                register = '$a0'
            mipsCode.append('    sw {}, {}($sp)'.format(register, code[2]))
        else:
            mipsCode.append('    sw $ra, {}($sp)'.format(code[2]))  # ra -> mem[sp+ ]
    
    def handle8(self,code,midCOde,mipsCode):
        if code[3] != 'ra':
            register = self.reg(code[3], midCOde)
            mipsCode.append('    lw {}, {}($sp)'.format(register, code[2]))
        else:
            mipsCode.append('    lw $ra, {}($sp)'.format(code[2]))
    
    def handlePlus(self,code,midCode,mipsCode):
        if code[1] == 'fp':
            mipsCode.append("    add $fp,$fp,{}".format(code[2]))
        elif code[1] == 'sp':
            mipsCode.append("    add $sp,$sp,{}".format(code[2]))
        else:
            param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
            if str(param1)[0] != '$': 
                mipsCode.append("    add $a1,$zero,{}".format(param1))
                param1 = '$a1'
            mipsCode.append("    add {},{},{}".format(param3, param1, param2))
    
    def handleMinus(self,code,midCode,mipsCode):
        if code[1] == 'fp':
            mipsCode.append("    sub $fp,$fp,{}".format(code[2]))
            return
        if code[1] == 'sp':
            mipsCode.append("    sub $sp,$sp,{}".format(code[2]))
            return 
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(self.reg(code[1], midCode))[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(self.reg(code[1], midCode)))
            param1 = '$a1'
        if str(self.reg(code[2], midCode))[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(self.reg(code[2], midCode)))
            param2 = '$a2'
        mipsCode.append("    sub {},{},{}".format(param3, param1, param2))
    
    def handleMulti(self,code,midCode,mipsCode):
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(param1)[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(param1))
            param1 = '$a1'
        if str(param2)[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(param2))
            param2 = '$a2'
        mipsCode.append("    mul {},{},{}".format(param3, param1, param2))
    
    def handleDivide(self,code,midCode,mipsCode):
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(param1)[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(param1))
            param1 = '$a1'
        if str(param2)[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(param2))
            param2 = '$a2'
        mipsCode.append("    div {},{},{}".format(param3, param1, param2))
    
    def handleRemain(self,code,midCode,mipsCode):
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(param1)[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(param1))
            param1 = '$a1'
        if str(param2)[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(param2))
            param2 = '$a2'
        mipsCode.append("    div {},{},{}".format(param3, param1, param2))
        mipsCode.append("    mfhi {}".format(param3))
    
    def handleLess(self,code,midCode,mipsCode):
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(param1)[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(param1))
            param1 = '$a1'
        if str(param2)[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(param2))
            param2 = '$a2'
        mipsCode.append("    slt {},{},{}".format(param3, param1, param2))

    def handleMore(self,code,midCode,mipsCode):
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(param1)[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(param1))
            param1 = '$a1'
        if str(param2)[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(param2))
            param2 = '$a2'
        mipsCode.append("    sgt {},{},{}".format(param3, param1, param2))
    
    def handleNEQ(self,code,midCode,mipsCode):
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(param1)[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(param1))
            param1 = '$a1'
        if str(param2)[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(param2))
            param2 = '$a2'
        mipsCode.append("    sne {},{},{}".format(param3, param1, param2))
    
    def handleEqual(self,code,midCode,mipsCode):
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(param1)[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(param1))
            param1 = '$a1'
        if str(param2)[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(param2))
            param2 = '$a2'
        mipsCode.append("    seq {},{},{}".format(param3, param1, param2))
    
    def handleLEQ(self,code,midCode,mipsCode):
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(param1)[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(param1))
            param1 = '$a1'
        if str(param2)[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(param2))
            param2 = '$a2'
        mipsCode.append("    sgt {},{},{}".format(param3, param1, param2))
        mipsCode.append("    xori {},{},1".format(param3, param3)) 
    
    def handleMEQ(self,code,midCode,mipsCode):
        param1,param2,param3 = self.reg(code[1], midCode),self.reg(code[2], midCode),self.reg(code[3], midCode)
        if str(param1)[0] != '$':
            mipsCode.append("    add $a1,$zero,{}".format(param1))
            param1 = '$a1'
        if str(param2)[0] != '$':
            mipsCode.append("    add $a2,$zero,{}".format(param2))
            param2 = '$a2'
        mipsCode.append("    slt {},{},{}".format(param3, param1, param2))
        mipsCode.append("    xori {},{},1".format(param3, param3))  # ?
    
    # 生成mips目标代码
    def generateObjectCode(self):
        dc = self.mid_Code
        mipsCode = self.mipsCode
        dc.insert(0, ('call', '_', '_', 'programEnd'))
        dc.insert(0, ('call', '_', '_', 'main'))
        mipsCode.append('.data')
        for symbol in self.symbolTable:
            if symbol.type == 'int array':
                size = 4 
                for dim in symbol.dimensions:
                    size *= int(dim)
                mipsCode.append('    ' + symbol.midval + ': .space ' + str(size))
        mipsCode.append('')
        mipsCode.append('.text')
        mipsCode.append('    addiu $sp, $zero, 0x{}'.format(self.DATA_SEGMENT + self.STACK_OFFSET)) 
        mipsCode.append('    or $fp, $sp, $zero')
        while dc: 
            code = dc.pop(0)
            tmp = list()
            for item in code:
                if item == 'v0': 
                    tmp.append('$v0')
                else:
                    tmp.append(item)
            code = tmp
            if code[0] == ':=':
                self.handle1(code,dc,mipsCode)
            elif code[0] == '[]=':  # []=, t21, _, t17[t22]
                self.handle2(code,dc,mipsCode)
            elif code[0] == '=[]':  # =[], t17[t23], -, t24
                self.handle3(code,dc,mipsCode)
            # get args inside the function
            elif code[0] == 'pop':  # pop, _, 0, t1
                self.handle6(code,dc,mipsCode)
            # store var from reg to memory
            elif code[0] == 'store':  # store, _, 0, ra
                self.handle7(code,dc,mipsCode)
            # load var from memory to reg
            elif code[0] == 'load':  # load, _, 0, ra
                self.handle8(code,dc,mipsCode)
            # jump instruction
            elif code[0] == 'j':  # j, _, _, l6
                mipsCode.append('    j {}'.format(code[3]))
            elif code[0] == 'j>':  # j>, t13, 0, l4
                param1 = self.reg(code[1], dc)
                mipsCode.append('    bgt {},$zero,{}'.format(param1, code[3]))  # bgt
            elif code[0] == 'return':
                mipsCode.append('    jr $ra')
            # function or label
            elif code[1] == ':':
                self.handle4(code,mipsCode)
            elif code[0] == 'call':
                mipsCode.append('    jal  {}'.format(code[3]))
            # actual arg of a function call
            elif code[0] == 'push':  # push, _, 0, t31
                self.handle5(code,dc,mipsCode)
            # algorithm operations, has 3 oprand
            else:
                if code[0] == '+':  # +, t23, 1, t23
                    self.handlePlus(code,dc,mipsCode)
                elif code[0] == '-':
                    self.handleMinus(code,dc,mipsCode)
                elif code[0] == '*':
                    self.handleMulti(code,dc,mipsCode)
                elif code[0] == '/':
                    self.handleDivide(code,dc,mipsCode)
                elif code[0] == '%':
                    self.handleRemain(code,dc,mipsCode)
                elif code[0] == '<':
                    self.handleLess(code,dc,mipsCode)
                elif code[0] == '>':
                    self.handleMore(code,dc,mipsCode)
                elif code[0] == '!=':
                    self.handleNEQ(code,dc,mipsCode)
                elif code[0] == '==':
                    self.handleEqual(code,dc,mipsCode)
                elif code[0] == '<=':
                    self.handleLEQ(code,dc,mipsCode)
                elif code[0] == '>=':
                    self.handleMEQ(code,dc,mipsCode)
        mipsCode.append('')
        mipsCode.append('programEnd:')
        mipsCode.append('    nop')
        return