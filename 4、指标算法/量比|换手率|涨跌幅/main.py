"""
量比的计算公式很简单
量比 =（现成交总手数 / 现累计开市时间(分) ）/ 过去5日平均每分钟成交量
所以只要知道历史K线就能算出每天的历史量比指标数据了

# 换手率 成交股数/流通股数×100%
流通股数整理在 dsx_stock_structure.csv 文件里了，只有 688开头的科创版数据

"""


import os
import qqhq
import pandas

path = os.path.dirname(os.path.abspath(__file__))
stock_structures = {}

def load_structures():
    structures = pandas.read_csv(path+'/dsx_stock_structure.csv',encoding="utf-8")
    for item in structures.values:
        try:
            code = item[2]
            date = int(item[0])
            flow = float(item[3])
            if flow>0:
                if code not in stock_structures.keys():
                    stock_structures[code] = {}
                o:dict = stock_structures.get(code)
                o[date] = flow
                stock_structures[code] = o
        except Exception as e:
            pass

    pass

def get_stock_tradables(code,finddate):
    """获取流通股数据
    需要查找小于日期的流通股进行计算
    Args:
        code (_type_): 证券代码
    """
    if code in stock_structures.keys():
        flows:dict = stock_structures.get(code)
        dates:list = list(flows.keys())
        dates.sort(reverse=False)
        # dates.reverse()
        date = dates[0]
        for item in dates:
            if int(item)>=int(finddate.replace("-","")):
                break
            date = item
        return flows[date]

def convert_klines(code):
    datas = qqhq.get_kline_datas(code,"1999-01-01","2023-03-01")
    klines = []
    last = 0
    min = 240 # 累积开市时间 240 分钟，这里不考虑中途停牌了
    avg_vols = []
    for item in datas:
        date,op,high,low,close,vol,amount = item.split(",")
        # 涨跌额
        rf = float(close) - last
        # 涨跌幅
        raf = round((last>0 and rf / last or 0) * 100,2)
        # 换手率 成交股数/流通股数×100%
        flow = get_stock_tradables(code,date)
        turnrate = round(float(vol) / flow * 100,2)
        # 量比 =（现成交总手数 / 现累计开市时间(分) ）/ 过去5日平均每分钟成交量
        qr = 0
        if avg_vols.__len__()>0:
            avg_vols_last_five_days:list = avg_vols[max(-5,-len(avg_vols)):]
            if avg_vols_last_five_days.__len__()>0:
                avg_five_day = 0
                for av in avg_vols_last_five_days:
                    avg_five_day += av
                avg = avg_five_day / avg_vols_last_five_days.__len__() / min
                qr = float(vol) / min / avg

        avg_vols.append(float(vol))
        last = float(close)
        klines.append([date,float(op),float(high),float(low),float(close),float(vol),float(amount),round(rf,2),raf,turnrate,qr])
    # print(klines)
    return klines

# 加载股本结构
load_structures()
# 计算 涨跌幅，量比，换手率等指标
stocks = pandas.read_csv(path+"/dsx_stocks.csv")
for item in stocks.values:
    code = item[0]
    klines = convert_klines(code)
    rs = pandas.DataFrame(klines,columns=["日期","开","高","低","收","成交量","成交额","涨跌额","涨跌幅","换手率","量比"])
    rs.to_csv(path+"/datas/"+code+".csv")
    print(code)
    print(rs)
    pass