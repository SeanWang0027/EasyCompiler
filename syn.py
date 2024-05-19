import copy
import sys

from sem import *

# 语法分析器
class SyntacticAnalyzer:
    # ACTION[s, a]：当状态s面临输入符号a时，应采取什么动作.
    # GOTO[s, X]：状态s面对文法符号X时，下一状态是什么
    def __init__(self, lex, cfg, family):
        self.lex = lex  # 词法分析结果
        self.cfg = cfg  # 文件读入类实例化 产生式
        self.family = family  # 项目集族 LR0项目集
        self.End = cfg.End
        self.OriginStart = cfg.OriginStart
        self.Start = cfg.Start
        self.Terminals = cfg.Terminals
        self.NonTerminals = cfg.NonTerminals

        self.sets = family.sets  # 状态集合
        self.edges = family.edges
        self.numSet = len(self.sets)

        ACTIONTitle = self.Terminals  # ACTION表面临的输入符号
        ACTIONTitle.append(self.End)

        self.ACTION = {y.name: {x: ' ' for x in ACTIONTitle} for y in self.sets}  # ACTION表
        self.GOTO = {y.name: {x: ' ' for x in self.NonTerminals} for y in self.sets}  # GOTO表

        self.procedures = cfg.procedures  # 产生式
        self.procedurestrs = [i.toStr() for i in self.procedures]

        self.MTitle = self.Terminals + self.NonTerminals
        self.M = {y.name: {x: ' ' for x in self.MTitle} for y in self.sets}  # 总表

        self.syntacticRst = True
        self.syntacticErrMsg = "语法分析成功！"
        self.semantic = SemanticAnalyser()  # 语法分析的同时进行语义分析

        return

    # 给出一个产生式，返回这个产生式是原文法的第几个产生式
    def item2prodIdx(self, item):
        tempStr = item.lhs + '->@'  # 代替点
        for right in item.rhs:
            tempStr += (right['type'] + ' ')
        tempStr += '# '
        return self.procedurestrs.index(tempStr)

    # 输入字符串分析 S05 P92
    def getParseRst(self):
        return self.parseRst

    # 得到ACTION表和GOTO表
    def getTables(self):
        self.rst = []
        for e in self.edges:
            if e['symbol'] in self.Terminals:  # symbol是终结符，构建ACTION表
                self.M[e['start']][e['symbol']] = 'shift ' + e['end']

            if e['symbol'] in self.NonTerminals:  # symbol是非终结符，构建GOTO表
                self.M[e['start']][e['symbol']] = 'goto ' + e['end']

        for I in self.sets:
            for item in I.items:
                if item.dot_position == len(item.rhs):  # dot在最后,要规约了
                    if item.lhs == self.OriginStart and item.terms[0] == '#':
                        if self.M[I.name][item.terms[0]] != ' ':
                            print('LR(1)分析表有多重入口！')
                        self.M[I.name][item.terms[0]] = 'acc'
                    else:
                        if self.M[I.name][item.terms[0]] != ' ':
                            print('LR(1)分析表有多重入口！')
                        self.M[I.name][item.terms[0]] = 'reduce ' + str(self.item2prodIdx(item))
                    continue

                if len(item.rhs) == 1 and item.rhs[0]['type'] == '$':
                    if item.lhs == self.OriginStart and item.terms[0] == '#':
                        if self.M[I.name][item.terms[0]] != ' ':
                            print('LR(1)分析表有多重入口！')
                        self.M[I.name][item.terms[0]] = 'acc'
                    else:
                        if self.M[I.name][item.terms[0]] != ' ':
                            print('LR(1)分析表有多重入口！')
                        self.M[I.name][item.terms[0]] = 'reduce ' + str(self.item2prodIdx(item))
                    continue
        return

    # 分析语句
    def isRecognizable(self, originCode):
        inputStr = []  # 输入串
        inputStr += self.lex.oneline_tokens(originCode)  # 一行源代码
        sys.stdout.flush()
        stateStack = []  # 栈内状态序列
        shiftStr = []  # 移进规约串
        self.parseRst = []  # 记录步骤

        # 开始
        wallSymbol = {'class': 'T', 'type': '#'}  # 规约的起始符
        shiftStr.append(wallSymbol)
        stateStack.append('s0')
        X = inputStr[0]  # X为当前单词

        while True:
            if len(inputStr) <= 2:
                tmpInputStr = self.lex.oneline_tokens(originCode)
                if len(tmpInputStr) == 0:  # 源代码结束
                    inputStr.append(wallSymbol)
                else:
                    inputStr += tmpInputStr

            self.parseRst.append({'stateStack': copy.deepcopy(stateStack),
                                  'shiftStr': copy.deepcopy(shiftStr),
                                  'inputStr': copy.deepcopy(inputStr)})

            act = self.M[stateStack[-1]][X['type']].split(' ')[0]
            target = self.M[stateStack[-1]][X['type']].split(' ')[1] if len(self.M[stateStack[-1]][X['type']].split(' ')) == 2 else None

            if act == 'shift':  # 移进操作
                stateStack.append(target)
                inputStr.pop(0)
                shiftStr.append(X)
                X = inputStr[0]

            elif act == 'goto':  # 转移操作
                stateStack.append(target)
                shiftStr.append(X)
                X = inputStr[0]

            elif act == 'reduce':  # 规约操作
                prodIdx = int(target)  # 产生式序号
                prod = self.procedures[prodIdx]  # 根据序号找到对应的产生式
                self.semantic.semanticAnalyze(prod, shiftStr)
                if not self.semantic.semanticRst:
                    return False

                rightLen = len(prod.rhs)
                stateLen = len(stateStack)

                if rightLen == 1 and prod.rhs[0]['type'] == '$':
                    # 是空串, 有问题, stateStack和shiftStr在这个分支中就处理好
                    dst = self.M[stateStack[-1]][prod.lhs].split(' ')[1]  # 因为是空串，没有pop，还是-1
                    stateStack.append(dst)
                    shiftStr.append({'class': 'NT', 'type': prod.lhs})
                    X = inputStr[0]

                else:  # 不是空串
                    stateStack = stateStack[0: stateLen - rightLen]  # 出栈
                    shiftStr = shiftStr[0: stateLen - rightLen]     # 出栈
                    X = {'class': 'NT', 'type': prod.lhs}  # 产生式的左边

            elif act == 'acc':  # 接受操作
                self.semantic.semanticAnalyze(self.procedures[1], shiftStr)
                return True

            else:
                self.syntacticRst = False
                sys.stdout.flush()
                self.syntacticErrMsg = "语法分析错误,请检查语法"
                return False