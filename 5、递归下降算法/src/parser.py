from src.tokenizer import Lexer,TokenType

class Parser:
    def __init__(self, lexer:Lexer):
        # 传入词法解析器，把表达式转换为Token集合
        self.lexer = lexer
        # 这里相当于取得第一个词法解析器的Token
        self.current_token = self.lexer.get_next_token()

    def parse(self):
        return self.expr()

    # 表达式字符串 递归开始
    def expr(self):
        # 处理项
        result = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            self.eat(op.type)
            term = self.term()
            if op.type == TokenType.PLUS:
                result = result + term
            elif op.type == TokenType.MINUS:
                result = result - term
        return result

    # 项
    def term(self):
        result = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            op = self.current_token
            self.eat(op.type)
            factor = self.factor()
            if op.type == TokenType.MUL:
                result = result * factor
            elif op.type == TokenType.DIV:
                result = result / factor

        return result

    # 处理因子
    def factor(self):
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return int(token.value)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            result = self.expr()
            self.eat(TokenType.RPAREN)
            return result

    # 继续下一个
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception('Syntax error')



