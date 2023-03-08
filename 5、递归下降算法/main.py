import traceback
from src.tokenizer import Lexer
from src.parser import Parser
if __name__=="__main__":
    expressions = """
    1+2*(3-4)/5
    """
    expressions = """
    N:=9; M1:=3; M2:=3;
    RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
    K:=SMA(RSV,M1,1);
    D:=SMA(K,M2,1);
    J:=3*K-2*D;
    """
    try:
        # 词法分析器
        lexer = Lexer(expressions)
        # 语法解析器
        parser = Parser(lexer)
        # 解析并返回结果
        result = parser.parse()
        print(parser.caches)  # Output: 0.6
        # CLOSE=30,LLV(10,9)=90,HHV(20,9)=2.22,LLV(10,9)=90
        # RSV = (30-90)/(2.22-90) * 100 = 68.354
    except Exception as e:
        traceback.print_exc()


