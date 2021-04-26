class TangPoem:
    def __init__(self, poem_id):
        self.__clist = []
        self.__poem_id = poem_id
        self.title_token = ''
        self.tokens = []
    @property
    def id(self):
        return self.__poem_id
    @property
    def title(self):
        return self.__title if not self.__title is None else "UDF"
    @property
    def author(self):
        return self.__author if not self.__author is None else "UDF"
    @property
    def content(self):
        return self.__clist
    
    def update_data(self, op, cont, words):
        if op == -100:
            self.__title = cont.strip("#")
            self.title_token = words
        elif op == -1:
            self.__author = cont.strip("$")
        elif op > 0:
            self.__clist.append(cont)
            self.tokens.append(words)
    
    def __str__(self):
        return f"《{self.title}》{self.author}: {self.content}"

    def __repr__(self):
        return f"《{self.title}》{self.author}: {self.content}"