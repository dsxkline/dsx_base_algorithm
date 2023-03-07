from src.tokenizer import Direction
from src.tokenizer import Lexer,TokenType

class Parser:
    def __init__(self, lexer:Lexer):
        # 传入词法解析器，把表达式转换为Token集合
        self.lexer = lexer
        # 这里相当于取得第一个词法解析器的Token
        self.current_token = self.lexer.get_next_token()
        # 这里我们声明一个缓存，保存变量地址等信息
        self.caches = {}

    def parse(self):
        return self.expr()

    # 表达式字符串 递归开始
    def expr(self):
        # 处理项
        result = self.term()
        # 处理加减
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            self.eat(op.type)
            # 处理加减符号右边项
            term = self.term()
            if op.type == TokenType.PLUS:
                result = result + term
            elif op.type == TokenType.MINUS:
                result = result - term
        # 处理换行,换行就是一个新语句的开始
        if self.current_token.type==TokenType.NEWLINE:
            self.eat(self.current_token.type)
            result = self.expr()
        return result

    # 项
    def term(self):
        # 处理因子
        result = self.factor()
        # 处理乘除，因为先乘除后加减，乘除符号连接成一个因子处理
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            op = self.current_token
            self.eat(op.type)
            # 处理乘除号右边因子
            factor = self.factor()
            if op.type == TokenType.MUL:
                result = result * factor
            elif op.type == TokenType.DIV:
                result = result / factor
        
        # 处理赋值符号
        if self.current_token.type == TokenType.EQUAL:
            # 需要解析赋值符号右边的表达式的值赋值给左边的变量
            op = self.current_token
            self.eat(op.type)
            # 处理等号右边的表达式
            result = self.term()
            # 取出等号左边的变量名
            var_name,var_value = self.caches.popitem()
            # 赋值变量
            self.caches[var_name] = result
        
        return result
    
    # 处理因子
    def factor(self):
        token = self.current_token
        # 处理整形数字，直接返回整形结果
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return int(token.value)
        # 处理左括号，进入括号继续递归解析表达式
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            # 解析括号后面表达式，遇到右括号会自动停止递归并返回值
            result = self.expr()
            self.eat(TokenType.RPAREN)
            return result
        # 处理变量名
        elif token.type == TokenType.VARIABLE:
            self.eat(TokenType.VARIABLE)
            # 如果是在等号左边,缓存变量
            var_name = str(token.value)
            result = None
            if token.direction==Direction.LEFT:
                # 缓存变量并初始化为None
                self.caches[var_name] = None
                result = var_name
            else:
                # 如果在等号右边，从缓存中取值
                if var_name in self.caches.keys():
                    var_value = self.caches.get(var_name)
                    result = var_value
                else:
                    # 是系统变量属性值
                    if hasattr(self,var_name):
                        result = getattr(self,var_name)
            return result
        # 处理函数解析
        elif token.type == TokenType.FUNCTION:
            self.eat(TokenType.FUNCTION)
            functions:str = token.value
            # 解析函数名和参数
            func_name = functions.split("(")[0]
            func_params = functions[len(func_name)+1:-1]
            # 解析每个参数
            args = []
            for param in func_params.split(","):
                # 这里直接从缓存中获取变量值即可
                if param in self.caches.keys():
                    pval = self.caches.get(param)
                    args.append(pval)
                # 缓存中没有，从系统变量属性中查找
                elif hasattr(self,param):
                    pval = getattr(self,param)
                    args.append(pval)
                else:
                    args.append(pval)
            # 寻找系统函数并执行函数
            if hasattr(self,func_name):
                method = getattr(self,func_name)
                result = method(*args)
            return result
    # 实现属性变量
    # 这里是模拟，具体生产自己实现
    @property
    def LOW(self):
        return 10
    @property
    def HIGH(self):
        return 20
    @property
    def CLOSE(self):
        return 30
    # 实现公式的函数
    def LLV(self,X,N):
        # 这里假设实现一个简单的算法
        return X * N
    # 实现公式的函数
    def HHV(self,X,N):
        # 这里假设实现一个简单的算法
        return X / N
    # 实现公式的函数
    def SMA(self,X,N,M):
        # 这里假设实现一个简单的算法
        return X + N + M

    # 继续下一个
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception('Syntax error')




