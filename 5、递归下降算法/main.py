

from src.tokenizer import Lexer
from src.parser import Parser
if __name__=="__main__":

    expressions = """
    a = 3+4*(2-1)+1000
    b = 3+4*(2-1)+10001
    c = a+b
    """
    expressions = """
    a1_e& = 3+4*(2-1)+1000
    """
    # 词法分析器
    lexer = Lexer(expressions)
    # 语法解析器
    parser = Parser(lexer)
    # 解析并返回结果
    result = parser.parse()
    print(result)  # Output: 11