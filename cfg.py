from item import *
import re

# 穿线表节点
class CFG:
    def __init__(self):
        self.lhs = []
        self.prods = []  # 产生式
        self.items = []  # 所有item项 (dot不同的都算)
        self.startProd = None  # 广义文法起始符
        self.firstSet = {}  # first集，{symbol:[],}
        # 保留字
        self.reservation = {
            'if': 'IF',
            'else': 'ELSE',
            'while': 'WHILE',
            'int': 'INT',
            'return': 'RETURN',
            'void': 'VOID'
        }
        # 类别
        self.type = ['seperator', 'operator', 'identifier', 'int']
        # 词法分析所使用的正则表达式
        self.regexs = [
            '\{|\}|\[|\]|\(|\)|,|;'  # 界符
            , '\+|-|\*|/|==|!=|>=|<=|>|<|='  # 操作符
            , '[a-zA-Z][a-zA-Z0-9]*'  # 标识符
            , '\d+'  # 整数
        ]

        self.TerminalSymbols = []  # 终结符表
        self.NonTerminalSymbols = []  # 非终结符表
        self.StartSymbol = None
        self.OriginStartSymbol = None
        self.EndSymbol = None
        self.Epsilon = None
        return

    # 读取产生式
    def readGrammerFile(self, path):
        # 拓展成广义语法
        # 更改语法时需要修改此函数
        self.StartSymbol = 'program_'
        self.OriginStartSymbol = 'program'
        self.prods.append(Item(self.StartSymbol, [{'type': self.OriginStartSymbol, 'class': 'NT', 'name': ''}]))
        self.NonTerminalSymbols.append(self.StartSymbol)
        fd = open(path, 'r')
        self.cntProd = 0  # 产生式数量

        tokens = []  # {'left': token1, 'right': token3}
        while True:
            line = fd.readline().replace('\n', '')  # 读一行
            if not line:
                break
            token1 = []  # 产生式左边
            token3 = []  # 产生式右边(合并左边相同的产生式，因此可能有很多右边)
            token1.append({'type': line, 'class': 'NT', 'name': line})  # 产生式左边
            while True:
                token2 = []  # 一条产生式右边
                line = fd.readline().replace('\n', '')  # 读一行
                if not line:
                    break
                if line[0] == '\t':  # 开头一定得是/t
                    line = line.strip('\t').split(' ')  # 可能产生式右边有多个变量
                    if line[0] == '#':  # 产生式结束
                        tokens.append({'left': token1, 'right': token3})  # 加入一类产生式
                        break

                    self.cntProd = self.cntProd + 1  # 产生式数量+1
                    for item in line:
                        match = 0
                        for regex in self.regexs[0: 2]:  # 匹配是不是操作符和界符
                            result = re.match(regex, item)
                            if result:  # 是操作符和界符
                                match = 1
                                break

                        if match == 1:  # 界符 操作符
                            tempToken2 = {'type': item, 'class': 'T',
                                          'name': self.type[self.regexs.index(regex)].upper()}
                        elif item in self.reservation:  # 保留字
                            tempToken2 = {'type': item, 'class': 'T', 'name': item}
                        elif item == 'id':  # 标识符
                            tempToken2 = {'type': 'IDENTIFIER', 'class': 'T', 'name': 'IDENTIFIER'}
                        elif item == '$':  # 空
                            tempToken2 = {'type': item, 'class': 'T', 'name': item}
                        elif item == 'num':  # 整数
                            tempToken2 = {'type': 'INT', 'class': 'T', 'name': 'INT'}
                        else:  # 变元
                            tempToken2 = {'type': item, 'class': 'NT', 'name': item}
                        token2.append(tempToken2)
                    token3.append(token2)

        for t in tokens:  # {'left': token1, 'right': token3}
            if t['left'][0]['type'] not in self.NonTerminalSymbols:  # 添加变元 产生式左边不是终结符
                self.NonTerminalSymbols.append(t['left'][0]['type'])  # 0：因为token1中只有一个元素

            for rightIdx in range(len(t['right'])):  # 对同一个产生式的左边 遍历每一个右边
                self.prods.append(Item(t['left'][0]['type'], t['right'][rightIdx]))  # 添加每一条产生式
                for rightIdx2 in range(len(t['right'][rightIdx])):  # 添加非变元
                    if t['right'][rightIdx][rightIdx2]['class'] == 'T' and t['right'][rightIdx][rightIdx2]['type'] not in self.TerminalSymbols:
                        self.TerminalSymbols.append(t['right'][rightIdx][rightIdx2]['type'])

        self.EndSymbol = '#'  # 终止符
        self.TerminalSymbols.append(self.EndSymbol)
        self.Epsilon = '$'
        return

    # 计算所有T和NT的first集
    def calFirstSet(self):
        for symbol in self.TerminalSymbols:  # 包括空串
            self.firstSet[symbol] = [symbol]
        for symbol in self.NonTerminalSymbols:
            self.firstSet[symbol] = []
        for symbol in self.NonTerminalSymbols:
            self.calNTFirstSet(symbol)
        return

    # 计算单个NT的first集
    def calNTFirstSet(self, symbol):
        eps = {'class': 'T', 'name': '', 'type': self.Epsilon}
        hasEpsAllBefore = -1  # 前面的非终结符是否全都能推出eps
        prods = [prod for prod in self.prods if prod.lhs == symbol]  # 左边符合条件的产生式
        if len(prods) == 0:
            return

        is_add = 1
        while is_add:
            is_add = 0
            for prod in prods:  # 遍历符合的产生式
                hasEpsAllBefore = 0

                for right in prod.rhs:  # 遍历产生式右边的每个符号
                    # 2. 若X∈VN，且有产生式X->a…，a∈VT，则 a∈FIRST(X)
                    #    X->ε,则ε∈FIRST(X)
                    if right['class'] == 'T' or (right['type'] == self.Epsilon and len(prod.rhs) == 1):  # A->epsilon
                        # 有就加
                        if right['type'] not in self.firstSet[symbol]:
                            self.firstSet[symbol].append(right['type'])
                            is_add = 1
                        break

                    # 3. 对NT, 之前已算出来过, 但有可能是算到一半的
                    if len(self.firstSet[right['type']]) == 0:
                        if right['type'] != symbol:  # 防止陷入死循环
                            self.calNTFirstSet(right['type'])  # 先算NT自己的first集

                    # X->Y…是一个产生式且Y ∈VN  则把FIRST(Y)中的所有非空符号串ε元素都加入到FIRST(X)中。
                    if self.Epsilon in self.firstSet[right['type']]:
                        hasEpsAllBefore = 1

                    for f in self.firstSet[right['type']]:
                        if f != self.Epsilon and f not in self.firstSet[symbol]:
                            self.firstSet[symbol].append(f)
                            is_add = 1

                # 到这里说明整个产生式已遍历完毕 看是否有始终能推出eps
                # 中途不能推出eps的已经break了   (例如Ba还是会来到这里，加e可能会有问题)
                # 所有right(即Yi) 能够推导出ε,(i=1,2,…n)，则
                if hasEpsAllBefore == 1:
                    if self.Epsilon not in self.firstSet[symbol]:
                        self.firstSet[symbol].append(self.Epsilon)
                        is_add = 1

        return

    # 给产生式加点，转化为项目item LR0
    def getDotItems(self):
        for prod in self.prods:
            if len(prod.rhs) == 1 and prod.rhs[0]['type'] == self.Epsilon:  # 产生式右边只有eps
                self.items.append(Item(prod.lhs, prod.rhs, 0, ['#']))  # 只用把dot加在eps前就行了
                continue
            for i in range(len(prod.rhs) + 1):
                self.items.append(Item(prod.lhs, prod.rhs, i, ['#']))
        return

    # 输出测试
    def prtGrammer(self):
        print('------------ 打印语法详情 --------------')
        print("产生式个数", len(self.prods), self.cntProd)

        print('非终结符个数:', len(self.NonTerminalSymbols), '终结符个数:', len(self.TerminalSymbols))
        print(self.NonTerminalSymbols)
        print(self.TerminalSymbols)

        for item in self.items:
            rightList = [r['type'] for r in item.rhs]
            print(item.lhs, rightList, item.dot_position)  #
        return

    # 输出测试
    def prtFirstSet(self):
        print('---------- 打印First集 --------------')
        for key in self.firstSet.keys():
            prtList = [value for value in self.firstSet[key]]
            print(key, prtList)
        return