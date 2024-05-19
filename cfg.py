from item import *
import re

dict_reserved = {'if': '','else': '','while': '','int': '','return': '','void': ''}
for key,value in dict_reserved.items():
    dict_reserved[key] = key.upper()

class CFG:
    def __init__(self):
        self.lhs = list()
        self.procedures = list()
        self.items = list()
        self.startProd = None
        self.firstSet = dict()
        self.reservation = dict_reserved
        self.type = ['seperator', 'operator', 'identifier', 'int']
        self.regexs = ['\{|\}|\[|\]|\(|\)|,|;','\+|-|\*|/|==|!=|>=|<=|>|<|=','[a-zA-Z][a-zA-Z0-9]*','\d+']
        self.Terminals = list()
        self.NonTerminals = list()
        self.Start = None
        self.OriginStart = None
        self.End = None
        self.Epsilon = None
        return

    def readfile(self,f):
        self.cntProd = 0
        tokens = list()
        while True:
            line = f.readline().replace('\n', '')
            if not line:
                break
            tokenA = [{'type': line, 'class': 'NT', 'name': line}]
            tokenC = list()
            while True:
                tokenB = [] 
                line = f.readline().replace('\n', '') 
                if not line:
                    break
                if line[0] == '\t': 
                    line = line.strip('\t').split(' ')
                    if line[0] == '#':
                        tokens.append({'left': tokenA, 'right': tokenC})
                        break
                    self.cntProd = self.cntProd + 1
                    for item in line:
                        match = 0
                        for regex in self.regexs[0: 2]: 
                            result = re.match(regex, item)
                            if result:
                                match = 1
                                break
                        if match == 1:
                            tmp = {'type': item, 'class': 'T','name': self.type[self.regexs.index(regex)].upper()}
                            tokenB.append(tmp)
                            continue 
                        if item == 'id':
                            tmp = {'type': 'IDENTIFIER', 'class': 'T', 'name': 'IDENTIFIER'}
                            tokenB.append(tmp)
                            continue 
                        if item == '$':
                            tmp = {'type': item, 'class': 'T', 'name': item}
                            tokenB.append(tmp)
                            continue 
                        if item == 'num':
                            tmp = {'type': 'INT', 'class': 'T', 'name': 'INT'}
                            tokenB.append(tmp)
                            continue 
                        if item in self.reservation:
                            tmp = {'type': item, 'class': 'T', 'name': item}
                            tokenB.append(tmp)
                            continue 
                        tmp = {'type': item, 'class': 'NT', 'name': item}
                        tokenB.append(tmp)
                    tokenC.append(tokenB)

        for t in tokens: 
            if t['left'][0]['type'] not in self.NonTerminals:
                self.NonTerminals.append(t['left'][0]['type'])

            for rightIdx in range(len(t['right'])):
                self.procedures.append(Item(t['left'][0]['type'], t['right'][rightIdx]))
                for rightIdx2 in range(len(t['right'][rightIdx])): 
                    if t['right'][rightIdx][rightIdx2]['class'] == 'T' and t['right'][rightIdx][rightIdx2]['type'] not in self.Terminals:
                        self.Terminals.append(t['right'][rightIdx][rightIdx2]['type'])
        return 

    def Grammer(self, path):
        self.Start = 'program_'
        self.OriginStart = 'program'
        self.NonTerminals.append(self.Start)
        self.procedures.append(Item(self.Start, [{'type': self.OriginStart, 'class': 'NT', 'name': ''}]))
        with open(path,'r') as f: 
            self.readfile(f)
            
        self.End = '#'
        self.Terminals.append(self.End)
        self.Epsilon = '$'
        return

    def CalculateFirst(self):
        for symbol in self.Terminals:
            self.firstSet[symbol] = [symbol]
        for symbol in self.NonTerminals:
            self.firstSet[symbol] = list()
        for symbol in self.NonTerminals:
            self.calNT(symbol)
        return

    def calNT(self, symbol):
        haseps = -1
        prods = list()
        for prod in self.procedures:
            if prod.lhs==symbol:
                prods.append(prod)
        if len(prods) == 0:
            return
        mark = 1
        while mark:
            mark = 0
            for prod in prods:
                haseps = 0
                for right in prod.rhs:
                    sign = right['type'] == self.Epsilon and len(prod.rhs) == 1
                    if right['class'] == 'T' or sign:
                        if right['type'] not in self.firstSet[symbol]:
                            mark = 1
                            self.firstSet[symbol].append(right['type'])
                        break
                    if len(self.firstSet[right['type']]) == 0:
                        if right['type'] != symbol:
                            self.calNT(right['type'])
                    if self.Epsilon in self.firstSet[right['type']]:
                        haseps = 1
                    for f in self.firstSet[right['type']]:
                        if f != self.Epsilon and f not in self.firstSet[symbol]:
                            mark = 1
                            self.firstSet[symbol].append(f)
                if haseps == 1:
                    if self.Epsilon not in self.firstSet[symbol]:
                        mark = 1
                        self.firstSet[symbol].append(self.Epsilon)
        return

    def getDot(self):
        for prod in self.procedures:
            if len(prod.rhs) == 1 and prod.rhs[0]['type'] == self.Epsilon:
                self.items.append(Item(prod.lhs, prod.rhs, 0, ['#']))
                continue
            for i in range(len(prod.rhs) + 1):
                self.items.append(Item(prod.lhs, prod.rhs, i, ['#']))
        return
