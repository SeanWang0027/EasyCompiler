import re
from item import *
from itemset import * 

# 最终项目族的DFA
class ItemSetSpecificationFamily:
    def __init__(self, cfg):
        self.TerminalSymbols = cfg.TerminalSymbols  # 终结符表
        self.NonTerminalSymbols = cfg.NonTerminalSymbols  # 非终结符表
        self.StartSymbol = cfg.StartSymbol  # 是program_
        self.EndSymbol = cfg.EndSymbol  # 是#
        self.Epsilon = cfg.Epsilon

        self.symbols = self.TerminalSymbols + self.NonTerminalSymbols
        self.itemPool = cfg.items  # itemPool：由产生式加点后的项目池
        self.itemSets = []  # 从pool中用GO函数划分  DFA不同的状态
        self.edges = []  # 项目集之间的转移  {'start': I.name, 'symbol': X, 'end': tempItemSet.name}
        self.firstSet = cfg.firstSet
        return

    # 获取左边为NT，dot=0的产生式，用于计算闭包
    def getLeftNT(self, NT):
        rst = []
        for item in self.itemPool:
            if item.lhs == NT and item.dot_position == 0:
                rst.append(item)
        return rst

    # 获取字符串的first
    def getFirstSet(self, symbols):
        rst = []
        hasEpsAllBefore = 0

        for s in symbols:  # 遍历字符串中的每一个NT和T
            tempSet = [i for i in self.firstSet[s]]  # 该元素的first集
            if self.Epsilon in tempSet:  # 该元素的first集中有eps
                if hasEpsAllBefore == 0:
                    hasEpsAllBefore = 1
                rst.extend([i for i in tempSet if i != self.Epsilon])  # 在列表后追加多个值
            else:
                hasEpsAllBefore = -1
                rst.extend(tempSet)
                break  # 该元素的first集中有无eps，可以终止遍历了

        if hasEpsAllBefore == 1:  # 字符串中的所有元素的first集全有eps
            rst.append(self.Epsilon)
        return rst

    # 求包含item的闭包里的其他项目
    def extendItem(self, item):
        rst = []
        if item.rhs[item.dot_position]['class'] != 'NT':  # dot后面那个字符不是非终结符
            return rst

        str2BgetFirstSet = []  # dot指向元素的下一个元素开始的字符串
        for rightIdx in range(item.dot_position + 1, len(item.rhs)):  # 遍历dot指向元素的下一个元素 至 末尾
            str2BgetFirstSet.append(item.rhs[rightIdx]['type'])
        nextItem = self.getLeftNT(item.rhs[item.dot_position]['type'])  # 获取左边为NT，dot=0的产生式，用于计算闭包
        str2BgetFirstSet.append(item.terms[0])  # 展望的字符也加上
        tempFirsts = self.getFirstSet(str2BgetFirstSet)  # 求dot指向元素的下一个元素开始的字符串的first集
        for i in nextItem:
            for j in tempFirsts:
                rst.append(Item(i.lhs, i.rhs, 0, [j]))  # 往item的闭包里的添加其他项目

        return rst

    # 计算闭包
    def getLR1Closure(self, I):
        rst = []
        rst.extend(I)  # I项目自己肯定在闭包里

        # toString 已包含terms信息
        rstStr = [item.toStr() for item in rst]  # 作为key值进行比对是否已有了
        while True:
            isAddItem = 0
            for item in rst:
                right = item.rhs  # 引用 为了缩短变量长度

                for i in range(len(right) + 1):
                    if item.dot_position == len(right):  # 产生式的dot在最后面
                        continue
                    if right[item.dot_position]['class'] == 'T':
                        continue
                    tempRst = self.extendItem(item)  # 求包含item的闭包里的其他项目
                    for i in tempRst:  # i可能会重复定义
                        tempStr = i.toStr()
                        if tempStr not in rstStr:
                            rstStr.append(tempStr)
                            rst.append(i)  # tempRst已经求出闭包里的所有项目，但它是字符串，仅仅是为了方便比对，我们需要的还是rst
                            isAddItem = 1
            if isAddItem == 0:
                break

        return rst

    # 状态转换函数GO GO(I，X) ＝ CLOSURE(J)
    def GO(self, I, X):
        J = []

        # 求GOTO函数的时候不要把ε当终结符/非终结符处理，不要引出ε边
        if len(I.items) == 0 or X == self.Epsilon:  # 项目集里没有项目或者转移为eps
            return J

        for item in I.items:
            if item.dot_position == len(item.rhs):
                continue
            # 空产生式
            if len(item.rhs) == 1 and item.rhs[0] == self.Epsilon:
                continue

            if item.rhs[item.dot_position]['type'] == X:
                temp = item.nextItem()
                if temp is not None:
                    J.append(temp)
        return self.getLR1Closure(J)

    # 构造项目集规范族
    # 从起始状态的闭包出发，不断调用GO函数生成新的项目族并计算闭包
    def buildFamily(self):
        iS = self.itemSets  # DFA不同的状态
        startI = []
        startI.append(self.itemPool[0])  # 添加起始项目
        iS.append(ItemSet('s0', self.getLR1Closure([startI[0]] + self.extendItem(startI[0]))))  # 起始项目集

        setCnt = 1
        setStrings = {}
        setStrings['s0'] = iS[0].toStr()  # dot被去掉了,并加了\n分隔项目
        edgeStrings = []

        while True:
            isBigger = 0  # 是否有加新边或者状态
            for I in iS:  # 遍历当前的所有项目集
                for X in self.symbols:  # 遍历所有的字符(非终结符和终结符)
                    rstGO = self.GO(I, X)  # 生成了一个新的项目集
                    if len(rstGO) == 0:
                        continue
                    tempItemSet = ItemSet('s' + str(setCnt), rstGO)  # 新的项目集

                    if tempItemSet.toStr() in setStrings.values():  # 新生成的项目集已经存在了
                        tempItemSet.name = list(setStrings.keys())[list(setStrings.values()).index(tempItemSet.toStr())]
                    else:
                        setStrings[tempItemSet.name] = tempItemSet.toStr()
                        iS.append(tempItemSet)  # 添加新的项目集
                        isBigger = 1
                        setCnt = setCnt + 1

                    tempEdge = {'start': I.name, 'symbol': X, 'end': tempItemSet.name}
                    tempEdgeStr = tempEdge['start'] + '->' + tempEdge['symbol'] + '->' + tempEdge['end']

                    if tempEdgeStr not in edgeStrings:
                        self.edges.append(tempEdge)
                        edgeStrings.append(tempEdgeStr)
                        isBigger = 1
            if isBigger == 0:
                break
        return

    def prtFamily(self):
        print(' ----------- 打印项目集族 --------------')
        for itemSet in self.itemSets:
            print(itemSet.name)
            for item in itemSet.items:
                rightList = [r['type'] for r in item.rhs]
                # print(item.lhs, rightList, item.dot_position, item.terms)
        print('\n')
        for edge in self.edges:
            print(edge['start'], edge['symbol'], edge['end'])
        return