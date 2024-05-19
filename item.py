class Item:
    def __init__(self, left, right, dotPos=0, terms=['#']):
        self.lhs = left  
        self.rhs = right  
        self.dot_position = dotPos 
        self.terms = terms
        return

    def nextItem(self):
        if self.dot_position <= len(self.rhs):
            return Item(self.lhs, self.rhs, self.dot_position + 1, self.terms) 
        else:
            return None

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs), self.dot_position, self.terms))

    def __repr__(self):
        rhs_with_dot = self.rhs[:self.dot_position] + ['.'] + self.rhs[self.dot_position:]
        if self.terms:
            return f"{self.lhs} -> {' '.join(rhs_with_dot)}, {self.terms}"
        else:
            return f"{self.lhs} -> {' '.join(rhs_with_dot)}"

    def toStr(self):
        rst = self.lhs + '->'
        pos = 0
        for right in self.rhs:
            if pos == self.dot_position:
                rst += '@' 
            rst += right['type'] + ' '
            pos += 1
        if pos == self.dot_position:
            rst += '@'
        for term in self.terms:
            rst += term + ' '
        return rst
