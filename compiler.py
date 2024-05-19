from lex import *
from sem import *
from syn import *
from object_generate import *
from itemfamily import *
from item import *
from itemset import *
from cfg import *
import getopt
import os 
import csv
import re
import shutil

def usage():
    print("usage: " + sys.argv[0] + " -i input-file")

def compiler(input_file):
    match = re.match(r"^(.*?)(\.[^.]*$|$)", input_file)
    directoryname = match.group(1)
    if os.path.exists(directoryname):
        for root, dirs, files in os.walk(directoryname):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
        print(f"Directory '{directoryname}' exists, and all files have been removed.")
    else:
        os.mkdir(directoryname)
        print(f"Directory '{directoryname}' created.")
    lex = LexAnalyzer()
    cfg = CFG()
    cfg.Grammer('./productions/productions.txt')
    cfg.getDot()
    cfg.CalculateFirst()
    family  = ItemFamily(cfg)
    family.buildFamily()
    ana = SyntacticAnalyzer(lex,cfg,family)
    ana.getTables()
    with open(input_file,'r') as f :
        originCode = f.read()
    ana.isRecognizable(originCode)
    if ana.syntacticRst == False:
        print('compile failure',ana.syntacticErrMsg)
        return
    if ana.semantic.semanticRst == False:
        print('compile failure',ana.semantic.semanticErrMsg)
        return
    MidCode = 'MidCode.txt'
    ana.semantic.saveMidCodeToFile(os.path.join(directoryname,MidCode))
    print('compile success!')
    ocg = ObjectCodeGenerator(ana.semantic.middleCode,ana.semantic.symbolTable,ana.semantic.funcTable)
    ocg.genMips()
    tokens = lex.origin_tokens(originCode)
    lex_csv = 'lex.csv'
    header = tokens[0].keys()
    with open(os.path.join(directoryname,lex_csv),mode='w',newline='') as f: 
        writer = csv.DictWriter(f,fieldnames=header)
        writer.writeheader()
        for token in tokens:
            writer.writerow(token)
    print('Lex Result has been written into file!')
    parseRes = ana.getParseRst()
    parse_csv = 'parse.csv'
    header = parseRes[0].keys()
    with open(os.path.join(directoryname,parse_csv),mode='w',newline='') as f: 
        writer = csv.DictWriter(f,fieldnames=header)
        writer.writeheader()
        for parse in parseRes:
            sec = []
            thr = []
            for item in parse['shiftStr']:
                sec.append(item['type'])
            parse['shiftStr'] = sec
            for item in parse['inputStr']:
                thr.append(item['type'])
            parse['inputStr'] = thr
            writer.writerow(parse)
    print('Parse Result has been written into file!')
    func = ana.semantic.funcTable
    func_csv = 'func.csv'
    funcs = []
    for i in range(len(func)):
        item = dict()
        item['name'] = func[i].name
        item['type'] = func[i].type
        item['label'] = func[i].label
        item['params'] = str(func[i].params)
        funcs.append(item)
    header = funcs[0].keys()
    with open(os.path.join(directoryname,func_csv),mode='w',newline='') as f: 
        writer = csv.DictWriter(f,fieldnames=header)
        writer.writeheader()
        for item in funcs:
            writer.writerow(item)
    print('Functions has been written into file!')
    symbol = ana.semantic.symbolTable
    symbol_csv = 'symbol.csv'
    symbols = []
    for i in range(len(symbol)):
        item = dict()
        item['name'] = symbol[i].name
        item['type'] = symbol[i].type
        item['size'] = symbol[i].size
        item['offset'] = symbol[i].offset
        item['place'] = symbol[i].place 
        item['function'] = symbol[i].function 
        symbols.append(item)
    header = symbols[0].keys()
    with open(os.path.join(directoryname,symbol_csv),mode='w',newline='') as f: 
        writer = csv.DictWriter(f,fieldnames=header)
        writer.writeheader()
        for item in symbols:
            writer.writerow(item)
    print('Symbols has been written into file!')
    mipsText = ''
    for code in ocg.mipsCode:
        mipsText += code + '\n'
    with open(os.path.join(directoryname,'ObjectCode.s'), "w") as f:
        f.write(mipsText)
    print('Object Code has been generated!')
    return 

input_file = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i':
        input_file  = a
    else:
        assert False, "unhandled option"

if input_file == None :
    usage()
    sys.exit(2)

compiler(input_file)