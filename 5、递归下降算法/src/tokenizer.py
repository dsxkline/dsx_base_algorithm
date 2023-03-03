import re
import ast

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
    # EOF
    EOF = 'EOF'

class RegRolues:
    # 识别变量名称正则
    VARIABLE = '^[a-zA-Z_0-9]'

# Token类定义
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
        print(self.__repr__())

    def __repr__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
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
        self.equal_left = 1

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
        while self.current_char is not None and re.match(RegRolues.VARIABLE,self.current_char) and self.current_char!="=" and self.current_char!="\n":
            result += self.current_char
            self.advance()
        return str(result)
    
    # 提取字符串，有可能是变量或者字符串值
    def string(self):
        # 遇到等号和换行符必须退出
        result = ''
        while self.current_char is not None and re.match(RegRolues.VARIABLE,self.current_char) and self.current_char!="\n" and self.current_char!="\"" and self.current_char!="\'":
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
                return Token(TokenType.INTEGER, self.integer())

            if self.current_char == '+':
                # 移动字符
                self.advance()
                return Token(TokenType.PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')
            
            # 等号
            if self.current_char == '=':
                self.advance()
                # 进入等号右边
                self.equal_left = 0
                return Token(TokenType.EQUAL, '=')
            # 换行符
            if self.current_char == '\n':
                self.advance()
                # 进入等号左边
                self.equal_left = 0
                return Token(TokenType.EQUAL, '=')

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')
            
            # 单引号或者双引号开头的解析为字符串
            if self.current_char == '\"' or self.current_char == '\'':
                return Token(TokenType.STRING, self.string())
            
            # 字母开头数字下划线组合的变量
            if re.match(RegRolues.VARIABLE, self.current_char):
                return Token(TokenType.VARIABLE, self.variable())

            raise ValueError('Invalid character: ' + self.current_char)

        return Token(TokenType.EOF, None)
