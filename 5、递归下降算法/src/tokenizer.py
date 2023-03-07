import re
import ast

# 一些正则
class RegRolues:
    # 识别变量名称正则
    VARIABLE = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    VARIABLE_NAME = r'^[a-zA-Z0-9_]*$'
    OPERATIONS = r'^(\+|\-|\*|\/|\%|\=\=|\!\=|\>|\<|\>\=|\<\=|\&\&|\|\|)$'

# Token 类型定义，就是定义表达式字符串每个字符是什么类型
class TokenType:
    # 整形数字
    INTEGER = 'INTEGER'
    # 字符
    STRING = 'STRING'
    # 浮点数
    FLOAT = 'FLOAT'
    # 加号操作符
    PLUS = 'PLUS'
    # 见好操作符
    MINUS = 'MINUS'
    # 乘号操作符
    MUL = 'MUL'
    # 除号操作符
    DIV = 'DIV'
    # 左括号
    LPAREN = 'LPAREN'
    # 右括号
    RPAREN = 'RPAREN'
    # 等于号
    EQUAL = 'EQUAL'
    # 等号左边为变量
    VARIABLE = 'VARIABLE'
    # 换行符
    NEWLINE = 'NEWLINE'
    # 函数
    FUNCTION = 'FUNCTION'
    # EOF
    EOF = 'EOF'

# 表达式项的方向，意思是在等号的左边还是右边，用来区分是变量还是表达式
class Direction:
    DEFAULT = 0
    LEFT = 1
    RIGHT = 2
# Token类定义
class Token:
    def __init__(self, type, value,direction:Direction=Direction.DEFAULT):
        self.type = type
        self.value = value
        self.direction = direction
        print(self.__repr__())

    def __repr__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            direction = self.direction,
            value=repr(self.value)
        )

# 词法分析器类定义
# 主要功能是解析字符表达式的每个字符，生成记号TOKEN序列，并提供记号流转
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char:str = self.text[self.pos]
        # 目前是在等号的左边还是右边，默认在左边，用来判断是变量名称还是字符串
        self.direction = Direction.LEFT

    # 辅助函数，用于向前移动指针并更新当前字符
    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    # 辅助函数，用于跳过空白字符
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # 辅助函数，用于解析一个整数
    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)
    
    # 提取变量名
    def variable(self):
        # 遇到等号和换行符必须退出
        result = ''
        while self.current_char is not None and self.current_char!=TokenType.NEWLINE and self.current_char!=":" and self.current_char!="\n":
            if re.match(RegRolues.VARIABLE_NAME,self.current_char):
                result += self.current_char
            else:
                # 遇到左括号表明是函数
                if self.current_char=="(":
                    return self.functions(result)
                else:
                    break
            self.advance()
        return Token(TokenType.VARIABLE, result,self.direction)
    
    # 提取函数表达式
    def functions(self,result):
        # 提取函数括号内所有字符
        i = 0
        while self.current_char is not None and self.current_char!=TokenType.NEWLINE and self.current_char!="\n":
            result += self.current_char
            if self.current_char=="(": i+=1
            if self.current_char==")":
                i -= 1
                if i<=0:
                    self.advance()
                    break
            self.advance()
            
        return Token(TokenType.FUNCTION, result,self.direction)
    # 提取字符串，有可能是变量或者字符串值
    def string(self):
        # 遇到等号和换行符必须退出
        result = ''
        while self.current_char is not None and self.current_char!=TokenType.NEWLINE and self.current_char!="\"" and self.current_char!="\'":
            result += self.current_char
            self.advance()
        return str(result)

    # 核心函数，用于将输入的字符序列分割为一个个Token
    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # 是否数字字符
            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer(),self.direction)

            if self.current_char == '+':
                # 移动字符
                self.advance()
                return Token(TokenType.PLUS, '+',self.direction)

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-',self.direction)

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MUL, '*',self.direction)

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIV, '/',self.direction)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(',self.direction)
            
            # 赋值符号
            if self.current_char == ':':
                self.advance()
                if self.current_char=="=":
                    self.advance()
                    # 进入等号右边
                    self.direction = Direction.RIGHT
                    return Token(TokenType.EQUAL, ':=',self.direction)
            # 换行符
            if self.current_char == ';':
                self.advance()
                # 进入等号左边
                self.direction = Direction.LEFT
                return Token(TokenType.NEWLINE, ';',self.direction)
            # 处理括号
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(',self.direction)
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')',self.direction)
            
            # 单引号或者双引号开头的解析为字符串
            if self.current_char == '\"' or self.current_char == '\'':
                return Token(TokenType.STRING, self.string(),self.direction)
            
            # 字母开头数字下划线组合的变量
            if re.match(RegRolues.VARIABLE, self.current_char):
                return self.variable()

            raise ValueError('Invalid character: ' + self.current_char)

        return Token(TokenType.EOF, None,self.direction)

