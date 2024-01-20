#DO STRING
from PyQt5.QtWidgets import *
import sys
import os

symbols = []

class Token():
    def __init__(self, lexeme, line):
        self.lexeme = lexeme
        self.line = line

def tokenize(string):
    tokens = []
    idx = 0
    line = 1
    while idx < len(string):
        if string[idx] == '\n':
            line +=1
        if string[idx] == '+':
            tokens.append(Token('+',line))
            idx +=1
        elif string[idx] == '-':
            tokens.append(Token('-',line))
            idx +=1
        elif string[idx] == '*':
            tokens.append(Token('*',line))
            idx +=1
        elif string[idx] == '/':
            tokens.append(Token('/',line))
            idx +=1
        elif string[idx] == '//':
            tokens.append(Token('//',line))
            idx +=1
        elif string[idx] == '%':
            tokens.append(Token('%',line))
            idx +=1
        elif string[idx] == '^':
            tokens.append(Token('^',line))
            idx +=1
        elif string[idx] == '(':
            tokens.append(Token('(',line))
            idx +=1
        elif string[idx] == ')':
            tokens.append(Token(')',line))
            idx +=1
        elif string[idx] in '0123456789.': #string[idx].isdigit() and floats
            number = ''
            while idx < len(string) and string[idx] in '0123456789.':
                number += string[idx]
                idx +=1
            tokens.append(Token(number,line))

        elif string[idx].isalpha() or string[idx] == '_': #identifiers and keywords
            start = idx
            while idx < len(string) and (string[idx].isdigit() or string[idx] == '_' or string[idx].isalpha()):
                idx +=1
            tokens.append(Token(string[start: idx],line))

        elif string[idx] == "<" or string[idx] == ">" or string[idx] == "=" or string[idx] == "~":
            if idx+1 < len(string) and string[idx+1] == "=":
                tokens.append(Token(string[idx:idx+2],line))
                idx +=1
            else:
                tokens.append(Token(string[idx],line))
            idx +=1
        else:
            idx +=1
    tokens.append(Token('EOF',line))
    return tokens

class PrimaryExpr(): #Numbers
    def __init__(self, token):
        self.token = token

    def eval(self):
        if self.token.lexeme == "true":
            return True
        elif self.token.lexeme == "false":
            return False
        else:
            return int(self.token.lexeme)

class BinaryExpr(): #Operations (contain - Numbers or Op)
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def eval(self):
        left_value = self.left.eval()
        right_value = self.right.eval()
        if self.op.lexeme == '+':
            return left_value + right_value
        elif self.op.lexeme == '-':
            return left_value - right_value
        elif self.op.lexeme == '*':
            return left_value * right_value
        elif self.op.lexeme == '/':
            return left_value / right_value
        elif self.op.lexeme == '//':
            return left_value // right_value
        elif self.op.lexeme == '%':
            return left_value % right_value
        elif self.op.lexeme == '^' or self.op.lexeme == '**':
            return left_value ** right_value
        if self.op.lexeme == '<':
            return left_value < right_value
        if self.op.lexeme == '>':
            return left_value > right_value
        if self.op.lexeme == '<=':
            return left_value <= right_value
        if self.op.lexeme == '>=':
            return left_value >= right_value
        if self.op.lexeme == '==':
            return left_value == right_value
        if self.op.lexeme == '~=':
            return left_value != right_value

class UnaryExpr(): # 2--1
    def __init__(self, op, right):
        self.op = op
        self.right = right
    def eval(self):
        if self.op.lexeme == '-':
            return -self.right.eval() #-1 * self.right.eval()

class RefVarExpr():
    def __init__(self, name):
        self.name = name
    def eval(self):
        for i in range(len(symbols) -1, -1, -1):
            if self.name.lexeme in symbols[i]:
                return symbols[i][self.name.lexeme]
            
        print("Error: [line:"+str(self.name.line)+"] Variable '" + self.name.lexeme + "' not defined")
        sys.exit(1)

class PrintStmt():
    def __init__(self, arg):
        self.arg = arg
    def exec(self):#execute
        global output
        result = self.arg.eval()
        output += str(result)
        output += "\n"

class BlockStmt():
    def __init__ (self, stmt_list):
        self.stmt_list = stmt_list
    def exec(self):
        symbols.append({})
        for stmt in self.stmt_list:
            stmt.exec()
        symbols.pop()

class DeclVarStmt():
    def __init__(self, name, value, is_local):
        self.name = name
        self.value = value
        self.is_local = is_local
    def exec(self):
        if not self.is_local:#Check all outer scopes to see if this was declared anywhere
            found_outside = False
            for i in range(len(symbols) -1, -1, -1):
                if self.name.lexeme in symbols[i]:
                    found_outside = True
                    symbols[i][self.name.lexeme] = self.value.eval()
                    break
            if not found_outside:
                #global declaration
                symbols[0][self.name.lexeme] = self.value.eval()
        else:
            #reassignment
            symbols[len(symbols) -1][self.name.lexeme] = self.value.eval()

class CondStmt():
    def __init__(self, cond, then_block, else_block):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block
    def exec(self):
        global output
        #if self.cond.eval() == True:
        cond_value = self.cond.eval()
        if cond_value:
            self.then_block.exec()
        elif not cond_value and self.else_block != None:
            self.else_block.exec()

class WhileStmt():
    def __init__ (self, cond, thenblock):
        self.cond = cond
        self.thenblock = thenblock
    def exec(self):
        while self.cond.eval():
            self.thenblock.exec()

class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0

    def peek_token(self):
        return self.tokens[self.idx]
    
    def next_token(self):
        t = self.tokens[self.idx]
        self.idx += 1
        return t
    
    def consume_token(self, expected_lexeme, error_msg):
        t = self.tokens[self.idx]
        self.next_token()
        if expected_lexeme != t.lexeme:
            print(error_msg)
            sys.exit(1)

    def parse_primary(self):
        if self.peek_token().lexeme == '(':
            self.next_token() #(
            expr = self.parse_expr()
            self.next_token() #)
            return expr
        elif self.peek_token().lexeme == 'true' or self.peek_token().lexeme == 'false' or self.peek_token().lexeme.isdigit():
            return PrimaryExpr(self.next_token())
        else:
            return RefVarExpr(self.next_token())
    
    def parse_unary(self):
        if self.peek_token().lexeme == '-':
            op = self.next_token()
            return UnaryExpr(op, self.parse_unary())
        else:
            return self.parse_primary()
        
    def parse_power(self): #Luy thua - w/ or w/out the () is different
        left = self.parse_unary()
        if self.peek_token().lexeme == '^':
            op = self.next_token()
            return BinaryExpr(op, left, self.parse_power())
        return left

    def parse_factor(self): #Multiplication and division
        left = self.parse_power()
        while self.peek_token().lexeme == "*" or self.peek_token().lexeme == "/" or self.peek_token().lexeme == "//" or self.peek_token().lexeme == "%" or self.peek_token().lexeme == "^":
            op_token = self.next_token()
            right = self.parse_power()
            left = BinaryExpr(op_token, left, right)
        return left

    def parse_term(self): #addition and subtraction
        left = self.parse_factor()
        while self.peek_token().lexeme == "+" or self.peek_token().lexeme == "-":
            op_token = self.next_token()
            right = self.parse_factor()
            left = BinaryExpr(op_token, left, right)
        return left

    def parse_relational(self): #less or greater than (and equal to)
        left = self.parse_term()
        while self.peek_token().lexeme == "<" or self.peek_token().lexeme == ">" or self.peek_token().lexeme == "<=" or self.peek_token().lexeme == ">=":
            op_token = self.next_token()
            right = self.parse_term()
            left = BinaryExpr(op_token, left, right)
        return left

    def parse_equality(self): #equal or not equal
        left = self.parse_relational()
        while self.peek_token().lexeme == "==" or self.peek_token().lexeme == "~=":
            op_token = self.next_token()
            right = self.parse_relational()
            left = BinaryExpr(op_token, left, right)
        return left

    def parse_expr(self):
        return self.parse_equality()
    
    def parse_stmt(self):
        if self.peek_token().lexeme == 'print':
            self.next_token()
            self.consume_token('(', "Error: '(' is expected")
            arg = self.parse_expr()
            self.consume_token(')', "Error: ')' is expected")
            return PrintStmt(arg)
        
        elif self.peek_token().lexeme == 'if':
            self.next_token()
            cond = self.parse_expr()
            self.consume_token('then', "Error: [line:"+str(self.peek_token().line)+"] Condition must be followed by 'then' keyword")
            stmt_list1 = [] #then block
            while self.peek_token().lexeme != 'end' and self.peek_token().lexeme != 'else':
                stmt_list1.append(self.parse_stmt())

            if self.peek_token().lexeme == 'end':
                self.next_token()
                return CondStmt(cond, BlockStmt(stmt_list1), None)
            elif self.peek_token().lexeme == 'else':
                self.next_token()
                stmt_list2 = [] #else block
                while self.peek_token().lexeme != 'end':
                    stmt_list2.append(self.parse_stmt())
                self.next_token()
                return CondStmt(cond, BlockStmt(stmt_list1), BlockStmt(stmt_list2))
            
        elif self.peek_token().lexeme == 'while':
            self.next_token()
            epr = self.parse_expr()
            self.consume_token('do', "Error: [line:"+str(self.peek_token().line)+"] Condition must be followed by 'do' keyword")
            stmt_list = [] #then block
            while self.peek_token().lexeme != 'end':
                stmt_list.append(self.parse_stmt())
            self.consume_token('end', "Error: [line:"+str(self.peek_token().line)+"] while loop must end with 'end' keyword")
            return WhileStmt(epr, BlockStmt(stmt_list))
            
        elif self.peek_token().lexeme == 'local':
            self.next_token()
            name = self.next_token()
            self.consume_token('=', "Error: [line:"+str(self.peek_token().line)+"] expect '=' after variable name")
            value = self.parse_expr()
            return DeclVarStmt(name, value, True)
        
        else: #Error check & Variable declaration
            name = self.next_token()
            self.consume_token('=', "Error: [line:"+str(self.peek_token().line)+"] expect '=' after variable name")
            value = self.parse_expr()
            return DeclVarStmt(name, value, False)
    
    def parse_source(self):
        stmts = []
        while self.peek_token().lexeme != 'EOF':
            stmts.append(self.parse_stmt())
        return BlockStmt(stmts)

def run():
    global output
    output = ""
    text = input.toPlainText()
    tokens = tokenize(text)
    parser = Parser(tokens)
    src = parser.parse_source()
    src.exec()

    result.clear()
    result.append(output)

def save():
    word, ok = QInputDialog.getText(win, "Save File", "Lue File Name: ")
    if ok:
        with open(word+".lua", "w") as f:
            f.write(input.toPlainText())

        files_list.addItem(word+".lua")
        with open(word+".lua","r") as file:
            s = file.read()
        dic[word+".lua"] = s

def select_folder():
    folder = QFileDialog.getExistingDirectory()
    if folder != '':
        files = os.listdir(folder)

        filtered_files = []
        for f in files:
            if f[len(f)-4:len(f)] == '.lua':
                filtered_files.append(f)
                with open(f,"r") as file:
                    s = file.read()
                dic[f] = s
        files_list.clear()
        files_list.addItems(filtered_files)

def item_clicked():
    l = files_list.selectedItems()
    input.setText(dic[l[0].text()])

dic = {}
app = QApplication([])
win = QWidget()#Window
win.setWindowTitle('Lua Interpreter')
win.resize(1200,800)

input = QTextEdit('Type your Lua code here')
result = QTextBrowser()
result.append('Result will be shown here')
run_button = QPushButton('RUN')
run_button.clicked.connect(run)
save_button = QPushButton('Save File')
save_button.clicked.connect(save)
folder_button = QPushButton('Select Folder')
folder_button.clicked.connect(select_folder)
files_list = QListWidget()
files_list.itemClicked.connect(item_clicked)

layout1 = QVBoxLayout()
layout2 = QVBoxLayout()
layout11 = QHBoxLayout()
layout12 = QVBoxLayout()

layout1.addLayout(layout12, stretch=10)
layout1.addLayout(layout11, stretch=1)
layout11.addWidget(result, stretch=8)
layout11.addWidget(run_button, stretch=1)
layout12.addWidget(input)
layout2.addWidget(save_button)
layout2.addWidget(folder_button)
layout2.addWidget(files_list)

final_layout = QHBoxLayout()
final_layout.addLayout(layout2, stretch=1)
final_layout.addLayout(layout1, stretch=5)

win.setLayout(final_layout)
win.show()
app.exec()