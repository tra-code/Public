#for loop in lua
#comma for print

import sys
returned_value = None
symbols = [] #statements with line number

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

        elif string[idx] == '"' or string[idx] == "'":
            start = idx
            idx +=1
            while idx < len(string) and (string[idx] != '"' and string[idx] != "'"):
                idx +=1
            idx +=1
            tokens.append(Token(string[start:idx], line))

        elif string[idx] == ',':
            tokens.append(Token(',',line))
            idx +=1
        
        elif string[idx] == '..':
            tokens.append(Token('..',line))
            idx +=1

        else:
            idx +=1

    tokens.append(Token('EOF',line))
    return tokens


class Stmt():
    def __init__(self):
        raise Exception("Statements must implement an 'exec' mehtod")
class Expr():
    def __init__(self):
        raise Exception("Expressions must implement an 'eval' mehtod")


class PrimaryExpr(Expr): #Numbers
    def __init__(self, token):
        self.token = token

    def eval(self):
        if self.token.lexeme == "true":
            return True
        elif self.token.lexeme == "false":
            return False
        elif self.token.lexeme.isdigit():
            return int(self.token.lexeme)
        elif self.token.lexeme[0] == '"' or self.token.lexeme[0] == "'":
            return str(self.token.lexeme[1:len(self.token.lexeme)-1])

class BinaryExpr(Expr): #Operations (contain - Numbers or Op)
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

class UnaryExpr(Expr): # 2--1
    def __init__(self, op, right):
        self.op = op
        self.right = right

    def eval(self):
        if self.op.lexeme == '-':
            return -self.right.eval() #-1 * self.right.eval()

class RefVarExpr(Expr):
    def __init__(self, name):
        self.name = name

    def eval(self):
        for i in range(len(symbols) -1, -1, -1):
            if self.name.lexeme in symbols[i]:
                return symbols[i][self.name.lexeme]
            
        print("Error: [line:"+str(self.name.line)+"] Variable '" + self.name.lexeme + "' is not defined")
        sys.exit(1)

class CallExprStmt(Stmt, Expr):
    def __init__(self, fcn_name, arg_list):
        self.fcn_name = fcn_name
        self.arg_list = arg_list

    def call(self):
        global returned_value
        for i in range(len(symbols) -1, -1, -1):
            if self.fcn_name.lexeme in symbols[i]:
                try:
                    evaluated_args = []
                    for arg in self.arg_list:
                        evaluated_args.append(arg.eval())
                    fcn = symbols[i][self.fcn_name.lexeme]
                    fcn.call(evaluated_args)
                except:
                    return returned_value

    def exec(self):
        return self.call()
    def eval(self):
        return self.call()
    
class PrintStmt(Stmt):
    def __init__(self, arg):
        self.arg = arg

    def exec(self):#execute
        result = self.arg.eval()
        print(result)

class BlockStmt(Stmt):
    def __init__ (self, stmt_list):
        self.stmt_list = stmt_list
    
    def exec(self):
        symbols.append({})
        for stmt in self.stmt_list:
            stmt.exec()
        symbols.pop()

class DeclVarStmt(Stmt):
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

class Fcn(): #Function
    def __init__(self, param_list, body_stmts):
        self.param_list = param_list
        self.body_stmts = body_stmts
    def call(self, arg_list):
        if len(arg_list) != len(self.param_list):
            print('Error: Non-matching number of arguments/parameters')
            sys.exit(1)
        #assign arguements to parameters
        symbols.append({})
        i = 0
        for p in self.param_list:
            symbols[len(symbols) -1][p.lexeme] = arg_list[i]
            i+=1
        #run function body
        self.body_stmts.exec()
        symbols.pop()

class DeclFcnStmt(Stmt):
    def __init__(self, name, param_list, body):
        self.name = name
        self.fcn = Fcn(param_list, body)
    
    def exec(self):
        symbols[len(symbols) -1][self.name.lexeme] = self.fcn

class ReturnStmt(Stmt):
    def __init__(self, value):
        self.value = value

    def exec(self):
        global returned_value
        returned_value = self.value.eval()
        raise Exception('Function returned')

class CondStmt(Stmt):
    def __init__(self, cond, then_block, else_block):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block

    def exec(self):
        #if self.cond.eval() == True:
        cond_value = self.cond.eval()
        if cond_value:
            self.then_block.exec()
        elif not cond_value and self.else_block != None:
            self.else_block.exec()

class WhileStmt(Stmt):
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

    def parse_fnc_call(self, name):
        self.next_token()
        arg_list = []
        while self.peek_token().lexeme != ')':
            arg_list.append(self.parse_expr())
            if self.peek_token().lexeme == ',':
                self.next_token()
        self.next_token()
        return CallExprStmt(name, arg_list)

    def parse_primary(self):
        if self.peek_token().lexeme == '(':
            self.consume_token('(','')
            expr = self.parse_expr()
            self.consume_token(')','')
            return expr
        elif self.peek_token().lexeme == 'true' or self.peek_token().lexeme == 'false' or self.peek_token().lexeme.isdigit():
            return PrimaryExpr(self.next_token())
        elif self.peek_token().lexeme.isdigit():
            return PrimaryExpr(self.next_token())
        elif self.peek_token().lexeme[0] == '"' or self.peek_token().lexeme[0] == "'":
            return PrimaryExpr(self.next_token())
        else:
            identifier = self.next_token()
            if self.peek_token().lexeme == '(': #function call
                return self.parse_fnc_call(identifier)
            else:#variable refernece
                return RefVarExpr(identifier)
    
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
    
    def parse_print_stmt(self):
        self.consume_token('print', '')
        self.consume_token('(', "Error: '(' is expected")
        arg = self.parse_expr()
        self.consume_token(')', "Error: ')' is expected")
        return PrintStmt(arg)
    
    def parse_if_stmt(self):
        self.consume_token('if', '')
        cond = self.parse_expr()
        self.consume_token('then', "Error: [line:"+str(self.peek_token().line)+"] Condition must be followed by 'then' keyword")
        stmt_list1 = [] #then block
        while self.peek_token().lexeme != 'end' and self.peek_token().lexeme != 'else':
            stmt_list1.append(self.parse_stmt())

        if self.peek_token().lexeme == 'end':
            self.consume_token('end','')
            return CondStmt(cond, BlockStmt(stmt_list1), None)
        elif self.peek_token().lexeme == 'else':
            self.consume_token('else','')
            stmt_list2 = [] #else block
            while self.peek_token().lexeme != 'end':
                stmt_list2.append(self.parse_stmt())
            self.consume_token('end','')
            return CondStmt(cond, BlockStmt(stmt_list1), BlockStmt(stmt_list2))
        
    def parse_while_stmt(self):
        self.consume_token('while','')
        epr = self.parse_expr()
        self.consume_token('then', "Error: [line:"+str(self.peek_token().line)+"] Condition must be followed by 'then' keyword")
        stmt_list = [] #then block
        while self.peek_token().lexeme != 'end':
            stmt_list.append(self.parse_stmt())
        self.consume_token('end', "Error: [line:"+str(self.peek_token().line)+"] while loop must end with 'end' keyword")
        return WhileStmt(epr, BlockStmt(stmt_list))

    def pasre_function_stmt(self):
        self.next_token()#'function' keyword
        fcn_name = self.next_token()
        #parse function parameters
        self.consume_token('(',"Error: [line:"+str(self.peek_token().line)+"] expect '(' before parameter list")
        param_list = []
        while self.peek_token().lexeme != ')':
            param_list.append(self.next_token())
            if self.peek_token().lexeme == ',':
                self.next_token()
        self.consume_token(')','')
        #Parse body of function
        body_stmts = []
        while self.peek_token().lexeme != 'end':
            body_stmts.append(self.parse_stmt())
        self.consume_token('end','')
        return DeclFcnStmt(fcn_name, param_list, BlockStmt(body_stmts))

    def parse_stmt(self):
        if self.peek_token().lexeme == 'print':
            return self.parse_print_stmt()
        elif self.peek_token().lexeme == 'if':
            return self.parse_if_stmt()
        elif self.peek_token().lexeme == 'while':
            return self.parse_while_stmt()
        elif self.peek_token().lexeme == 'function':
            return self.pasre_function_stmt()
        elif self.peek_token().lexeme == 'return':
            self.next_token()
            value = self.parse_expr()
            return ReturnStmt(value)

        elif self.peek_token().lexeme == 'local':
            self.next_token()
            name = self.next_token()
            self.consume_token('=', "Error: [line:"+str(self.peek_token().line)+"] expect '=' after variable name")
            value = self.parse_expr()
            return DeclVarStmt(name, value, True)
        
        else: #Error check & Variable declaration - function call
            name = self.next_token()
            if self.peek_token().lexeme == '(':
                return self.parse_fnc_call(name)
            else:
                self.consume_token('=', "Error: [line:"+str(self.peek_token().line)+"] expect '=' after variable name")
                value = self.parse_expr()
                return DeclVarStmt(name, value, False)
    
    def parse_source(self):
        stmts = []
        while self.peek_token().lexeme != 'EOF':
            stmts.append(self.parse_stmt())
        return BlockStmt(stmts)

with open('test.lua','r') as f:
    s = f.read()[:-1]
    tokens = tokenize(s)
    #for t in tokens:
    #    print(t.lexeme,t.line)
    parser = Parser(tokens)
    src = parser.parse_source()
    src.exec()
#hello