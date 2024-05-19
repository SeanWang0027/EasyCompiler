import re
from item import *
from itemset import * 

class ItemFamily:
    def __init__(self, cfg):
        self.Terminals = cfg.Terminals  
        self.NonTerminals = cfg.NonTerminals 
        self.Start = cfg.Start  
        self.End = cfg.End 
        self.Epsilon = cfg.Epsilon
        self.symbols = self.Terminals + self.NonTerminals
        self.items = cfg.items
        self.sets = []  
        self.edges = []
        self.firstSet = cfg.firstSet
        return

    def build(self):
        iS = self.sets
        startI = [self.items[0]]
        iS.append(ItemSet('s0', self.getLR1([startI[0]] + self.elseItem(startI[0]))))
        Cnt = 1
        setStrings = dict()
        setStrings['s0'] = iS[0].toStr()
        edgeStrings = list()
        while True:
            huger = 0 
            for I in iS:
                for X in self.symbols:
                    rstGO = self.GO(I, X)
                    if len(rstGO) != 0:
                        pass 
                    else: 
                        continue
                    tempItemSet = ItemSet('s' + str(Cnt), rstGO) 
                    if tempItemSet.toStr() in setStrings.values(): 
                        tempItemSet.name = list(setStrings.keys())[list(setStrings.values()).index(tempItemSet.toStr())]
                    else:
                        setStrings[tempItemSet.name] = tempItemSet.toStr()
                        iS.append(tempItemSet)
                        huger = 1
                        Cnt += 1
                    tempEdge = {'start': I.name, 'symbol': X, 'end': tempItemSet.name}
                    tempEdgeStr = tempEdge['start'] + '->' + tempEdge['symbol'] + '->' + tempEdge['end']
                    if tempEdgeStr not in edgeStrings:
                        huger = 1
                        self.edges.append(tempEdge)
                        edgeStrings.append(tempEdgeStr)
            if huger == 0:
                break
        return


    # 计算闭包
    def getLR1(self, I):
        res = list()
        res.extend(I) 
        rstStr = list()
        for i in range(len(res)):
            rstStr.append(res[i].toStr())
        while True:
            isAdd = 0
            for item in res:
                right = item.rhs
                for i in range(len(right) + 1):
                    if item.dot_position == len(right):
                        continue
                    if right[item.dot_position]['class'] == 'T':
                        continue
                    tmpRst = self.elseItem(item)
                    for i in tmpRst:
                        tmpStr = i.toStr()
                        if tmpStr not in rstStr:
                            isAdd = 1
                            rstStr.append(tmpStr)
                            res.append(i)  
            if isAdd == 0:
                break
        return res

    # 状态转换函数GO GO(I，X) ＝ CLOSURE(J)
    def GO(self, I, X):
        J = list()
        mark = len(I.items) == 0 or X == self.Epsilon
        if mark:
            return J
        for item in I.items:
            if item.dot_position == len(item.rhs) or (len(item.rhs) == 1 and item.rhs[0] == self.Epsilon):
                continue
            if item.rhs[item.dot_position]['type'] == X:
                tmp = item.nextItem()
                if tmp is None:
                    continue
                else: 
                    J.append(tmp)
        return self.getLR1(J)
    
    def elseItem(self, item):
        res = list()
        if item.rhs[item.dot_position]['class'] != 'NT':
            return res
        rawFirst = list()
        for rightIdx in range(item.dot_position + 1, len(item.rhs)):
            rawFirst.append(item.rhs[rightIdx]['type'])
        nextItem = [term for term in  self.items if term.lhs==item.rhs[item.dot_position]['type'] and term.dot_position == 0] 
        rawFirst.append(item.terms[0])
        tmpFirst = list() 
        hasEps = 0
        for s in rawFirst: 
            tempSet = [i for i in self.firstSet[s]] 
            if self.Epsilon in tempSet:
                if hasEps == 0:
                    hasEps = 1
                tmpFirst.extend([i for i in tempSet if i != self.Epsilon])
            else:
                hasEps = -1
                tmpFirst.extend(tempSet)
                break
        if hasEps == 1:
            tmpFirst.append(self.Epsilon)
        for i in nextItem:
            for j in tmpFirst:
                res.append(Item(i.lhs, i.rhs, 0, [j]))
        return res