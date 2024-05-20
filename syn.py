import copy

from sem import *

# 语法分析器
class synAnalyzer:
    # ACTION[s, a]：当状态s面临输入符号a时，应采取什么动作.
    # GOTO[s, X]：状态s面对文法符号X时，下一状态是什么
    def __init__(self, lex, cfg, family):
        self.lexicalResult = lex
        self.cfg = cfg  
        self.family = family  
        self.End = cfg.End
        self.OriginStart = cfg.OriginStart
        self.Start = cfg.Start
        self.Terminals = cfg.Terminals
        self.NonTerminals = cfg.NonTerminals
        self.sets = family.sets 
        self.edges = family.edges
        self.numSet = len(self.sets)
        ACTIONTable = self.Terminals  
        ACTIONTable.append(self.End)
        self.ACTION = {y.name: {x: ' ' for x in ACTIONTable} for y in self.sets} 
        self.GOTO = {y.name: {x: ' ' for x in self.NonTerminals} for y in self.sets}  
        self.procedures = cfg.procedures
        self.procedurestrs = [i.toStr() for i in self.procedures]
        self.MTitle = self.Terminals + self.NonTerminals
        self.M = {y.name: {x: ' ' for x in self.MTitle} for y in self.sets}
        self.syntacticRst = True
        self.syntacticErrMsg = "Synthetical Analysis Success!"
        self.semantic = SemAnalyzer() 
        return

    def index(self, item):
        tmp = item.lhs + '->@'  
        for right in item.rhs:
            tmp += (right['type'] + ' ')
        tmp += '# '
        return self.procedurestrs.index(tmp)

    def ParseRest(self):
        return self.parseRes

    def acc(self,item,I):
        if item.lhs == self.OriginStart and item.terms[0] == '#':
            if self.M[I.name][item.terms[0]] != ' ':
                print('LR(1) Table has multipy entrances!')
            self.M[I.name][item.terms[0]] = 'acc'
    
    def reduce(self,item,I): 
        if self.M[I.name][item.terms[0]] != ' ':
            print('LR(1) Table has multipy entrances!')
        self.M[I.name][item.terms[0]] = 'reduce ' + str(self.index(item))
    
    def ActionAndGoto(self):
        self.rst = list()
        for e in self.edges:
            if e['symbol'] in self.NonTerminals: 
                self.M[e['start']][e['symbol']] = 'goto ' + e['end']
            if e['symbol'] in self.Terminals: 
                self.M[e['start']][e['symbol']] = 'shift ' + e['end']
        for I in self.sets:
            for item in I.items:
                if item.dot_position == len(item.rhs): 
                    if item.lhs == self.OriginStart and item.terms[0] == '#':
                        self.acc(item,I)
                    else:
                        self.reduce(item,I)
                    continue
                if len(item.rhs) == 1 and item.rhs[0]['type'] == '$':
                    mark = (item.lhs == self.OriginStart and item.terms[0] == '#')
                    if mark:
                        self.acc(item,I)
                    else:
                        self.reduce(item,I)
                    continue
        return

    # 分析语句
    def isRecognizable(self, originCode):
        inputStr = list() 
        inputStr += self.lexicalResult.oneline_tokens(originCode)  
        statusStack = list()  
        shiftStr = list() 
        self.parseRes = list()  
        wallSymbol = {'class': 'T', 'type': '#'} 
        shiftStr.append(wallSymbol)
        statusStack.append('s0')
        curterm = inputStr[0] 
        while True:
            if len(inputStr) <= 2:
                tmpInputStr = self.lexicalResult.oneline_tokens(originCode)
                if len(tmpInputStr) == 0: 
                    inputStr.append(wallSymbol)
                else:
                    inputStr += tmpInputStr
            parsepart = dict()
            parsepart['statusStack'] = copy.deepcopy(statusStack)
            parsepart['shiftStr'] = copy.deepcopy(shiftStr)
            parsepart['inputStr'] = copy.deepcopy(inputStr)
            self.parseRes.append(parsepart)
            actor= self.M[statusStack[-1]][curterm['type']].split(' ')[0]
            goal = None 
            if len(self.M[statusStack[-1]][curterm['type']].split(' ')) == 2:
                goal = self.M[statusStack[-1]][curterm['type']].split(' ')[1]
            if actor== 'shift': 
                statusStack.append(goal)
                inputStr.pop(0)
                shiftStr.append(curterm)
                curterm = inputStr[0]
            elif actor== 'reduce':
                prodIdx = int(goal)
                prod = self.procedures[prodIdx]
                self.semantic.semanticAnalyze(prod, shiftStr)
                if not self.semantic.marksem:
                    return False
                stateLen = len(statusStack)
                rightLen = len(prod.rhs)
                if rightLen == 1 and prod.rhs[0]['type'] == '$':
                    dst = self.M[statusStack[-1]][prod.lhs].split(' ')[1]
                    statusStack.append(dst)
                    shiftStr.append({'class': 'NT', 'type': prod.lhs})
                    curterm = inputStr[0]
                else:
                    statusStack = statusStack[0: stateLen - rightLen]  
                    shiftStr = shiftStr[0: stateLen - rightLen]   
                    curterm = {'class': 'NT', 'type': prod.lhs} 
            elif actor== 'goto': 
                statusStack.append(goal)
                shiftStr.append(curterm)
                curterm= inputStr[0]
            elif actor== 'acc': 
                self.semantic.semanticAnalyze(self.procedures[1], shiftStr)
                return True
            else:
                self.syntacticRst = False
                self.syntacticErrMsg = "Please check the grammar of your code!"
                return False