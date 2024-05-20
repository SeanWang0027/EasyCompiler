import copy
from TreeNode import TreeNode
from sym import Symbol
from func import Func

# 语义分析类
class SemAnalyzer:
    def __init__(self):
        self.sStack = list() 
        self.symbolTable = list()
        self.funcTable = list()
        self.midValid = 0  
        self.curLabelId = 0 
        self.curFuncId = 0 
        self.curOffset = 0 
        f = Func()
        f.name = 'global'  # 函数标识符
        f.label = 'global'  # 函数入口处标签
        self.updateFuncTable(f) 
        self.curFunction = f 
        self.mid_Code = list()  # 生成的中间代码
        self.marksem = True
        self.semlog = "Semantic Analyze Success!"
        return

    def handelarrayDeclaration(self,nt,r,shiftStr):
        if len(r) == 3:
            n = TreeNode()
            n.name = nt
            n.type = 'int array' 
            n.dimensions = [int(shiftStr[-2]['data'])] 
            self.sStack.append(n)
            # self.prtTreeNodeCode(n)
        elif len(r) == 4:
            n = self.popStack()  
            n.name = nt
            n.type = 'int array'
            n.dimensions.insert(0, int(shiftStr[-3]['data']))
            self.sStack.append(n)
    
    def handleArray(self,shiftStr):
        new_exp = self.popStack() 
        self.calExp(new_exp)  
        array_n = copy.deepcopy(self.sStack[-1])  
        if shiftStr[-4]['type'] == 'array':  
            self.popStack()
            new_exp.name  = new_exp.type = 'array'
            new_exp.arrayname = array_n.arrayname  
            new_exp.pos = copy.deepcopy(array_n.pos)
            if new_exp.midval:
                new_exp.pos.append(new_exp.midval)
            else:
                new_exp.pos.append(new_exp.statistics)
            new_exp.midval = array_n.midval  
            self.sStack.append(new_exp)
        else:  
            new_exp.name = 'array'
            new_exp.arrayname = shiftStr[-4]['data']
            nTmp = self.findSymbol(shiftStr[-4]['data'], self.curFunction.label)  
            if nTmp == None:
                self.marksem = False
                self.semlog = "Not Defined Array:" + shiftStr[-4]['data']
                print('Using Array that are not defined!')
                return
            if new_exp.midval:
                new_exp.pos.append(new_exp.midval)
            else:
                new_exp.pos.append(new_exp.statistics)
            new_exp.midval = shiftStr[-4]['data']
            new_exp.type = 'array'
            self.sStack.append(new_exp)
    
    def popStack(self):
        return self.sStack.pop(-1)
    
    def handleProgram(self,nt):
        n = self.popStack()
        n.name = nt
        for treenode in n.tmpstack:
            for code in treenode.midcode:
                n.midcode.append(code)
        self.sStack.append(n)
        self.mid_Code = copy.deepcopy(n.midcode)
        
    def handleDeclarationChain(self,r,nt):
        newTreeNode = TreeNode()
        if len(r) != 2:
            pass 
        else: 
            newTreeNode = self.popStack()
            newTreeNode.tmpstack.insert(0, self.popStack())
        newTreeNode.name = nt
        self.sStack.append(newTreeNode)
    
    def defineSam(self,name,midval,type,function,size,offset,sam):
        sam.name = name
        sam.midval = midval
        sam.type = type
        sam.function = function
        sam.size = size
        sam.offset = offset
    
    def handleDeclaration(self,r,nt,shiftStr):
        if len(r) == 3:  # -> typeSpecifier id ;
            node = self.popStack()  # typeSpecifier
            node.name = nt
            curType = node.type
            curName = shiftStr[-2]['data'] 
            sam = self.findSymbol(curName, self.curFunction.label)
            if sam is None:
                sam = Symbol()
            else :
                print("The val has been declared!")
                self.marksem = False
                self.semlog = "Declared Variable!"  
                return
            if node.midval == None:
                self.defineSam(curName,self.getNewTmp(),curType,self.curFunction.label,4,self.curOffset,sam)
                self.curOffset += sam.size
                self.updateSymbolTable(sam)
                if node.statistics is not None: 
                    code = (':=', node.statistics, '_', sam.midval)
                    node.midcode.append(code)
            else:
                self.defineSam(curName,node.midval,curType,self.curFuncId.label,4,self.curOffset,sam)
                self.curOffset += sam.size
                self.updateSymbolTable(sam)
                for code in node.midcode:
                    node.midcode.tmpstack.insert(0, code)

        if len(r) == 4:
            array_n = self.popStack()
            node = self.popStack()
            node.name = nt
            curType = array_n.type
            curName = shiftStr[-3]['data']
            sam = self.findSymbol(curName, self.curFunction.label)
            if sam is not None:
                print("The Array has been Declared!")
                self.marksem = False
                self.semlog = "Decalred Array."  
                return
            else:
                sam = Symbol()
            if node.midval is None:
                self.defineSam(curName,self.getNewTmp(),curType,self.curFunction.label,4,self.curOffset,sam)
                for ndim in array_n.dimensions:
                    sam.size *= ndim
                sam.dimensions = copy.deepcopy(array_n.dimensions)
                self.curOffset += sam.size
                self.updateSymbolTable(sam)
                if node.statistics is not None:
                    code = (':=', node.statistics, '_', sam.midval)
                    node.midcode.append(code)
            else:
                self.defineSam(curName,node.midval,curType,self.curFuncId,4,self.curOffset,sam)
                for ndim in array_n.dimensions:
                    sam.size *= ndim
                sam.dimensions = copy.deepcopy(array_n.dimensions)
                self.curOffset += sam.size
                self.updateSymbolTable(sam)
                for code in node.midcode:
                    node.midcode.tmpstack.insert(0, code)
        if len(r) == 1:  # -> completeFunction
            node = self.popStack()
            node.name = nt
        self.sStack.append(node)

    def handleCompleteFunction(self,nt):
        node = self.popStack()  # block
        declareFunction = self.popStack()  # declareFunction
        node.name = nt
        tmp = list()
        tmp.append((declareFunction.statistics, ':', '_', '_'))
        for treenode in declareFunction.tmpstack:  # para
            tmp.append(('pop', '_', 4 * declareFunction.tmpstack.index(treenode), treenode.midval))
        if len(declareFunction.tmpstack) > 0:
            tmp.append(('-', 'fp', 4 * len(declareFunction.tmpstack), 'fp'))
        for code in reversed(tmp):
            node.midcode.insert(0, code)
        code_end = node.midcode[-1]
        if code_end[0][0] == 'l':
            label = code_end[0]
            node.midcode.remove(code_end)
            for code in node.midcode:
                if code[3] == label:
                    node.midcode.remove(code)
        self.sStack.append(node)
    
    def handleFormalParalist(self,r,nt):
        node = TreeNode()
        if len(r) == 3:  # formalParaList -> para , formalParaList
            node = self.popStack()
            node.name = nt
            node.tmpstack.insert(0, self.popStack())
        elif len(r) == 1 and (r[0]['type'] in ['$', 'void']):  # $ | void
            node.name = nt
        elif len(r) == 1 and r[0]['type'] == 'para':  # para
            node.tmpstack.insert(0, self.popStack())
            node.name = nt
        self.sStack.append(node)

    
    def handleDeclareFunction(self,nt,shiftStr):
        node = self.popStack()  # formalParaList
        node.name = nt
        nFuncReturnType = self.popStack()  # typeSpecifier
        f = Func()
        f.name = shiftStr[-4]['data']  # id
        f.type = nFuncReturnType.type
        if f.name == 'main':
            f.label = 'main'
        else:
            self.curFuncId += 1  
            f.label = 'f' + str(self.curFuncId)
        for arg in node.tmpstack:
            sam = Symbol()
            self.defineSam(arg.statistics,arg.midval,arg.type,f.label,4,self.curOffset,sam)
            self.curOffset += sam.size
            self.updateSymbolTable(sam)
            f.params.append((arg.statistics, arg.type, arg.midval))
        node.statistics = f.label
        self.updateFuncTable(f)
        self.tmpstack = list()  # 清空
        self.curFunction = f
        self.sStack.append(node)

    def handleStatBlock(self,nt):
        node = self.popStack()
        node.name = nt
        self.sStack.append(node)
    
    def handleTypeSpecifier(self,nt,shiftStr):
        newTreeNode = TreeNode()
        newTreeNode.name = nt
        newTreeNode.type = shiftStr[-1]['type']
        self.sStack.append(newTreeNode)
    
    def handlePara(self,nt,shiftStr):
        node = self.popStack()  # typeSpecifier treenode
        node.name = nt
        node.midval = self.getNewTmp()
        node.statistics = shiftStr[-1]['data']
        self.sStack.append(node)
    
    def handleStatementChain(self,r,nt):
        if len(r) == 1:  
            newTreeNode = TreeNode()
            newTreeNode.name = nt
            self.sStack.append(newTreeNode)
        elif len(r) == 2: 
            newTreeNode = self.popStack()
            newTreeNode.tmpstack.insert(0, self.popStack())
            newTreeNode.name = nt
            for code in reversed(newTreeNode.tmpstack[0].midcode):
                newTreeNode.midcode.insert(0, code)
            self.sStack.append(newTreeNode)
    
    def handleAssignStatement(self,nt,shiftStr):
        test = shiftStr[-4]['type']
        if test != 'array':  # id = expression ;
            id = shiftStr[-4]['data']
            node = copy.deepcopy(self.popStack())  # expression
            node.name = nt
            self.calExp(node)
            sam = self.findSymbol(id, self.curFunction.label)
            if sam is None:
                print("Use Val that is not defined!")
                self.marksem = False
                self.semlog = "Use Variable that is not defined."
                return
            if sam.type != node.type:
                token = shiftStr[-4]
                self.marksem = False
                self.semlog = "Wrong type of variable when assigning " + token['data']  
                return
            code = None
            if node.midval is not None:
                code = (':=', node.midval, '_', sam.midval)
            else:
                code = (':=', node.statistics, '_', sam.midval)
            node.midcode.append(code)
            self.sStack.append(node)
        else:  # -> array = expression ;
            node = copy.deepcopy(self.popStack())  # expression
            node.name = nt
            array_n = self.popStack()
            array_name = array_n.arrayname 
            self.calExp(node) 
            sam = self.findSymbol(array_name, self.curFunction.label)
            if sam is None:
                print("Use Array Val that is not defined!")
                self.marksem = False
                self.semlog = "Wrong type of Array when assigning " + array_name
                return
            t_offset = self.getNewTmp() 
            if len(array_n.pos) == 1:
                node.midcode.append((':=', str(array_n.pos[0]), '-', t_offset))
            elif len(array_n.pos) == 2:
                node.midcode.append(('*', str(array_n.pos[0]), str(sam.dimensions[1]), t_offset))
                node.midcode.append(('+', t_offset, str(array_n.pos[1]), t_offset))
            if node.midval is not None:
                code = ('[]=', node.midval, '_', sam.midval + '[' + t_offset + ']')
            else:
                t = self.getNewTmp()
                code = (':=', node.statistics, '_', t)
                node.midcode.append(code)
                code = ('[]=', t, '_', sam.midval + '[' + t_offset + ']')
            node.midcode.append(code)
            self.sStack.append(node)
    
    def handleReturnStatement(self,r,nt):
        node = None
        if len(r) == 3:  # return expression
            node = self.popStack()  # expression    
            self.calExp(node)
            node.type = r[0]['type']  # == return

            n_Rst = None
            if node.midval != None:
                n_Rst = node.midval
            else:
                n_Rst = node.statistics
            node.midcode.append((':=', n_Rst, '_', 'v0'))
        elif len(r) == 2:  # return
            node = TreeNode()
            node.type = r[0]['type']
        node.midcode.append((node.type, '_', '_', '_'))  # return
        node.name = nt
        self.sStack.append(node)
    
    def handleExpression(self,r,nt):
        node = None
        if len(r) == 1:  # expression -> primaryExpression
            node = copy.deepcopy(self.sStack[-1])  # primaryExpression
            node.tmpstack.insert(0, self.popStack())  # primaryExpression
        elif len(r) == 3:  # expression -> primaryExpression operator expression
            node = copy.deepcopy(self.popStack())  # expression
            for i in range(2):
                node.tmpstack.insert(0, self.popStack())  # operator
        node.name = nt
        self.sStack.append(node)
    
    def handlePrimaryExpression(self,r,nt,shiftStr):
        newTreeNode = TreeNode()
        if len(r) == 1 and r[0]['type'] == 'INT':  # num
            newTreeNode.type = shiftStr[-1]['type'].lower()  # int
            newTreeNode.statistics = shiftStr[-1]['data']  
        # id ( actualParaList )
        elif len(r) == 4 and r[0]['type'] == 'IDENTIFIER':  # 找定义过的
            function = None
            for f in self.funcTable:
                if f.name == shiftStr[-4]['data']:
                    function =  f
            newTreeNode = self.popStack()  # actualParaList
            newTreeNode.name = nt
            if function is None:
                print('Not Defined Function!')
                self.marksem = False
                self.semlog = "Not Defined Function: " + shiftStr[-4]['data']
                return
            if len(function.params) != len(newTreeNode.tmpstack):
                print('Not Compatiable use of function!')
                self.marksem = False
                self.semlog = "Not Compatiable use of function: " + shiftStr[-4]['data']
                return
            code_tmp = list()
            symbol_tmp_list = copy.deepcopy(self.curFunction.params)
            code_tmp.append(('-', 'sp', 4 * len(symbol_tmp_list) + 4, 'sp'))
            code_tmp.append(('store', '_', 4 * len(symbol_tmp_list), 'ra'))
            for symbol in symbol_tmp_list: 
                code_tmp.append(('store', '_', 4 * symbol_tmp_list.index(symbol), symbol[2])) 
            for code in reversed(code_tmp):
                newTreeNode.midcode.insert(0, code)
            if len(function.params) > 0:
                newTreeNode.midcode.append(('+', 'fp', 4 * len(function.params), 'fp')) 
            for treenode in newTreeNode.tmpstack:
                if treenode.midval is not None:
                    treenode_result = treenode.midval
                else:
                    treenode_result = treenode.statistics
                newTreeNode.midcode.append(('push', '_', 4 * newTreeNode.tmpstack.index(treenode), treenode_result))
            newTreeNode.midcode.append(('call', '_', '_', function.label))
            symbol_tmp_list.reverse()
            for symbol in symbol_tmp_list:
                newTreeNode.midcode.append(('load', '_', 4 * symbol_tmp_list.index(symbol), symbol[2]))  # n.midval = symbol[2]
            newTreeNode.midcode.append(('load', '_', 4 * len(symbol_tmp_list), 'ra'))  # mem[sp+4 * len(symbol_tmp_list)] -> ra
            newTreeNode.midcode.append(('+', 'sp', 4 * len(self.curFunction.params) + 4, 'sp'))

            newTreeNode.midval = self.getNewTmp()
            newTreeNode.midcode.append((':=', 'v0', '_', newTreeNode.midval)) 
            newTreeNode.tmpstack = list()

        elif len(r) == 1 and r[0]['type'] == 'IDENTIFIER':
            newTreeNode.statistics = shiftStr[-1]['data']
            nTmp = self.findSymbol(newTreeNode.statistics, self.curFunction.label)
            if nTmp is None:
                print('Use Val that is not defined!')
                self.marksem = False
                self.semlog = "Undefined Variable: " + shiftStr[-1]['data']
                return
            newTreeNode.type = nTmp.type
            newTreeNode.midval = nTmp.midval
        elif len(r) == 3 and r[1]['type'] == 'expression':
            newTreeNode = self.popStack()
            self.calExp(newTreeNode)
        else:  # -> array
            newTreeNode = self.popStack()
            nTmp = self.findSymbol(newTreeNode.arrayname, self.curFunction.label)
            if nTmp is None:
                print('Not Defined Array')
                self.marksem = False
                self.semlog = "Not Defined Array: " + newTreeNode.arrayname
                return
            t_offset = self.getNewTmp()
            if len(newTreeNode.pos) == 1:
                newTreeNode.midcode.append((':=', str(newTreeNode.pos[0]), '-', t_offset))
            elif len(newTreeNode.pos) == 2: 
                newTreeNode.midcode.append(('*', str(newTreeNode.pos[0]), str(nTmp.dimensions[1]), t_offset))
                newTreeNode.midcode.append(('+', t_offset, str(newTreeNode.pos[1]), t_offset))
            t = self.getNewTmp()
            newTreeNode.midcode.append(('=[]', nTmp.midval + '[' + t_offset + ']', '-', t))
            newTreeNode.type = 'int'
            newTreeNode.midval = t
            newTreeNode.tmpstack = []

        newTreeNode.name = nt
        self.sStack.append(newTreeNode)
    
    def handleOperator(self,r,shiftStr):
        newTreeNode = TreeNode()
        newTreeNode.name = 'operator'
        newTreeNode.type = ''
        for i in range(len(r)):
            token = shiftStr[-(len(r) - i)]
            newTreeNode.type += token['type']
        self.sStack.append(newTreeNode)
    
    def handleActualParametre(self,r,nt):
        node = None
        if len(r) == 3:  # formalParaList -> expression , formalParaList
            node = self.popStack()
            nExp = self.popStack()
            self.calExp(nExp)
            node.tmpstack.insert(0, nExp)
        elif len(r) == 1 and (r[0]['type'] in ['$']):  # $
            node = TreeNode()
        elif len(r) == 1 and r[0]['type'] == 'expression':  # expression
            node = copy.deepcopy(self.popStack())
            self.calExp(node)
        node.name = nt
        self.sStack.append(node)
    
    def handleIf(self,r,nt):
        newTreeNode = TreeNode()
        newTreeNode.name = nt
        # if ( expression ) block
        if len(r) == 5:
            newTreeNode.true = self.getNewLabel()
            newTreeNode.end = self.getNewLabel()
            nT = self.popStack()  # True
            nExp = self.popStack()
            self.calExp(nExp)
            newTreeNode.midcode.extend(nExp.midcode)
            newTreeNode.midcode.append(('j>', nExp.midval, '0', newTreeNode.true))
            newTreeNode.midcode.append(('j', '_', '_', newTreeNode.end))
            newTreeNode.midcode.append((newTreeNode.true, ':', '_', '_'))
            for code in nT.midcode: 
                newTreeNode.midcode.append(code)
            newTreeNode.midcode.append((newTreeNode.end, ':', '_', '_')) 
        # if ( expression ) block else block
        elif len(r) == 7:
            newTreeNode.true = self.getNewLabel()
            newTreeNode.false = self.getNewLabel()
            newTreeNode.end = self.getNewLabel()
            nF = self.popStack()  # False
            nT = self.popStack()  # True
            nExp = self.popStack()
            self.calExp(nExp)
            sent = ('j', '_', '_', newTreeNode.false)
            newTreeNode.midcode.extend(nExp.midcode)
            newTreeNode.midcode.append(('j>', nExp.midval, '0', newTreeNode.true))
            newTreeNode.midcode.append(sent)
            newTreeNode.midcode.append((newTreeNode.true, ':', '_', '_'))
            for code in nT.midcode: 
                newTreeNode.midcode.append(code)
            newTreeNode.midcode.append(('j', '_', '_', newTreeNode.end)) 
            newTreeNode.midcode.append((newTreeNode.false, ':', '_', '_'))
            for code in nF.midcode:  # false的code
                newTreeNode.midcode.append(code)
            newTreeNode.midcode.append((newTreeNode.end, ':', '_', '_'))
        self.sStack.append(newTreeNode)
    
    def handleLoop(self,r,nt):
        newTreeNode = TreeNode()  # 生成新节点
        newTreeNode.name = nt
        newTreeNode.true = self.getNewLabel()  # 四个分支的入口
        newTreeNode.false = self.getNewLabel()
        newTreeNode.beg = self.getNewLabel()
        newTreeNode.end = self.getNewLabel()
        sent = ('j', '_', '_', newTreeNode.false)
        sent2 = ('j', '_', '_', newTreeNode.beg)
        if r[0]['type'] == 'while':
            statement = self.popStack()  # block
            expression = self.popStack()  # expression
            self.calExp(expression)
            newTreeNode.midcode.append((newTreeNode.beg, ':', '_', '_'))
            for code in expression.midcode:
                newTreeNode.midcode.append(code)
            newTreeNode.midcode.append(('j>', expression.midval, '0', newTreeNode.true))
            newTreeNode.midcode.append(sent)
            newTreeNode.midcode.append((newTreeNode.true, ':', '_', '_'))
            for code in statement.midcode:
                if code[0] == 'break':
                    newTreeNode.midcode.append(sent)
                elif code[0] == 'continue':
                    newTreeNode.midcode.append(sent2)
                else:
                    newTreeNode.midcode.append(code)
            newTreeNode.midcode.append(sent2)
            newTreeNode.midcode.append((newTreeNode.false, ':', '_', '_'))
        self.sStack.append(newTreeNode)
    
    def semanticAnalyze(self, prod, shiftStr):
        nt = prod.lhs
        r = prod.rhs
        if nt == 'arrayDeclaration':
            self.handelarrayDeclaration(nt,r,shiftStr)
        # array -> id [ expression ] | array [ expression ]
        if nt == 'array':
            self.handleArray(shiftStr)
        # program -> declarationChain
        if nt == 'program':
            self.handleProgram(nt)
        # block -> { statementChain }
        # statement -> declaration | ifStatement | iterStatement | returnStatement | assignStatement
        elif nt in ['statement', 'block']:
            self.handleStatBlock(nt)
        # declarationChain -> $ | declaration declarationChain
        elif nt == 'declarationChain':
            self.handleDeclarationChain(r,nt)
        # typeSpecifier -> int | void
        elif nt == 'typeSpecifier':
            self.handleTypeSpecifier(nt,shiftStr)
        # declaration -> typeSpecifier id ; | completeFunction | typeSpecifier id arrayDeclaration ;
        elif nt == 'declaration':  # variable or function
            self.handleDeclaration(r,nt,shiftStr)
        # completeFunction -> declareFunction block
        elif nt == 'completeFunction':
            self.handleCompleteFunction(nt)
        # declareFunction -> typeSpecifier id ( formalParaList )
        elif nt == 'declareFunction':
            self.handleDeclareFunction(nt,shiftStr)
        # formalParaList -> $ | para | para, formalParaList | void
        elif nt == 'formalParaList':
            self.handleFormalParalist(r,nt)
        # para -> typeSpecifier id
        elif nt == 'para':
            self.handlePara(nt,shiftStr)
        # statementChain -> $ | statement statementChain
        elif nt == 'statementChain':
            self.handleStatementChain(r,nt)
        # assignStatement -> id = expression ; | array = expression ;
        elif nt == 'assignStatement':
            self.handleAssignStatement(nt,shiftStr)
        # returnStatement -> return expression; | return;
        elif nt == 'returnStatement':
            self.handleReturnStatement(r,nt)
        # expression -> primaryExpression | primaryExpression operator expression
        elif nt == 'expression':
            self.handleExpression(r,nt)
        # primaryExpression -> num | ( expression ) | id ( actualParaList ) | id | array
        elif nt == 'primaryExpression':
            self.handlePrimaryExpression(r,nt,shiftStr)
        # operator -> + | - | * | / | < | <= | >= | > | == | !=
        elif nt == 'operator':
            self.handleOperator(r,shiftStr)
        # actualParaList -> $ | expression | expression, actualParaList
        elif nt == 'actualParaList':
            self.handleActualParametre(r,nt)
        # ifStatement | if ( expression ) block | if ( expression ) block else block
        elif nt == 'ifStatement':
            self.handleIf(r,nt)
        # iterStatement -> while ( expression ) block
        elif nt == 'iterStatement':
            self.handleLoop(r,nt)
        return

    def findSymbol(self, name, function):
        for func in self.symbolTable:
            condition = (func.name == name and func.function == function)
            if condition :
                return func
        return None

    def updateSymbolTable(self, symbol):
        for s in self.symbolTable:
            if s.name == symbol.name and s.function == symbol.function:
                self.symbolTable.remove(s)
                break
        self.symbolTable.append(symbol)
        return

    def updateFuncTable(self, func):
        for f in self.funcTable:
            condition = f.name == func.name
            if condition: 
                self.funcTable.remove(f)
                break
        self.funcTable.append(func)
        return

    def getNewTmp(self):
        time = "t" + str(self.midValid + 1)
        self.midValid += 1 
        return time 

    def getNewLabel(self):
        self.curLabelId += 1
        return 'l' + str(self.curLabelId)

    def calExp(self, n):
        if len(n.tmpstack) == 1:
            n = copy.deepcopy(n.tmpstack[0])
            n.tmpstack = list()
            return True
        n.midcode = list()
        nLeft = n.tmpstack.pop(0)
        while len(n.tmpstack) > 0:
            t = n.tmpstack.pop(0)
            nRight = n.tmpstack.pop(0)
            arg1 = nLeft.statistics if nLeft.midval is None else nLeft.midval
            arg2 = nRight.statistics if nRight.midval is None else nRight.midval
            if len(nLeft.midcode) > 0:
                for code in nLeft.midcode:
                    n.midcode.append(code)
            if len(nRight.midcode) > 0:
                for code in nRight.midcode:
                    n.midcode.append(code)
            newTreeNode = TreeNode()
            newTreeNode.name = None 
            newTreeNode.midval = self.getNewTmp()
            newTreeNode.type = nRight.type
            code = (t.type, arg1, arg2, newTreeNode.midval)
            n.midcode.append(code)
            nLeft = newTreeNode
            n.type = nRight.type
        n.midval = n.midcode[-1][3]
        return True

    # 将中间代码保存到文件中
    def savecodeFile(self,midcode):
        text = ''
        for code in self.mid_Code:
            text += '{}, {}, {}, {}\n'.format(code[0], code[1], code[2], code[3])
        middleCodeObj = open(midcode, 'w+')
        middleCodeObj.write(text)
        middleCodeObj.close()
        return True