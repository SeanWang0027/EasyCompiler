import re

dict_reserved = {'if': '','else': '','while': '','int': '','return': '','void': ''}
for key,value in dict_reserved.items():
    dict_reserved[key] = key.upper()

class LexAnalyzer:
    def __init__(self):
        self.curline = 0  
        self.reservation = dict_reserved
        self.input = 0
        self.regexs = ['\{|\}|\[|\]|\(|\)|,|;','\+|-|\*|/|==|!=|>=|<=|>|<|=','[a-zA-Z][a-zA-Z0-9]*','\d+']
        self.type = ['seperator', 'operator', 'identifier', 'int']
        

    def tokenize(self, input_line):
        longest_match = ''
        selected_regex = self.regexs[0]
        remaining_input = 0
        is_matched = False
        # Iterate over all regular expressions to find the longest match
        for pattern in self.regexs:
            match_result = re.match(pattern, input_line)
            if match_result:
                matched_text = match_result.group(0)
                if len(matched_text) > len(longest_match):
                    is_matched = True
                    longest_match = matched_text
                    selected_regex = pattern
        # Handle the case where no match is found
        if not is_matched:
            print(u"Illegal character " + input_line[0])
            return {"data": input_line[0], "regex": None, "remain": input_line[1:]}
        else:
            # Return the longest match and the remaining input line
            return {"data": longest_match, "regex": selected_regex, "remain": input_line[remaining_input + len(longest_match):]}
    
    def eraseComment(self, codes): 
        comment = re.findall('//.*?\n', codes, flags=re.DOTALL)
        if len(comment) > 0:
            codes = codes.replace(comment[0], "") 
        comment = re.findall('/\*.*?\*/', codes, flags=re.DOTALL)
        if len(comment) > 0:
            codes = codes.replace(comment[0], "")
        return codes.strip()

    def analyze_line(self, line):
        ans = []
        res = line.strip().strip('\t')
        origin = res
        while True:
            if res != "":
                before = res
                res = self.tokenize(res)
                if res['regex']:
                    token = {}
                    token['class'] = "T"
                    token['row'] = self.curline
                    token['colum'] = origin.find(before) + 1
                    token['name'] = self.type[self.regexs.index(res['regex'])].upper()
                    token['data'] = res['data']
                    token['type'] = token['name']
                    if res['data'] in self.reservation: 
                        token['name'] = self.reservation[res['data']].lower()
                        token['type'] = token['name'] 
                    if token['name'] == "OPERATOR" or token['name'] == "SEPERATOR":
                        token['type'] = token['data']
                    if token['name'] == "INT":
                        token['data'] = token['data']
                    ans.append(token)
                res = res['remain'].strip().strip('\t')
                if res == "":
                    return ans
            else: 
                break
        return ans

    def origin_tokens(self, codes): 
        texts = self.eraseComment(codes)
        lines = texts.split('\n')
        terms = []
        self.curline += len(lines)
        for line in lines:
            tokens_OneLine = self.analyze_line(line)
            terms += tokens_OneLine
        return terms

    def oneline_tokens(self, codes): 
        if len(codes) <= self.input:
            return list()
        while True:
            index = codes.find('\n', self.input)
            if index != -1:
                pass 
            else: 
                index = len(codes) - 1
            line = codes[self.input:index + 1].strip()
            self.input = index + 1
            if line != '':
                break
            else:
                continue
        ans = self.analyze_line(line)
        return ans