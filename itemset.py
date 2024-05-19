class ItemSet:
    def __init__(self, name, items):
        self.name = name 
        self.items = items
        self.string = []
        
    def toString(self):
        for item in self.items:
            itemStr = item.toStr()
            if itemStr not in self.string:
                self.string.append(itemStr)
        self.string = sorted(self.string)
        return

    def toStr(self):
        self.toString()
        return "\n".join(self.string)

    def __repr__(self) -> str:
         pass 