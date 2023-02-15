
"""
复权的计算
采用wind的涨跌幅复权法
在每次除权发生后，根据除权价和前一收盘价计算一个比率，称为除权因子；
把截止到计算日历次的除权因子连乘，即为截止日的累积除权因子。
计算前复权价，则以价格乘上累积除权因子；
向后复权，则价格除以累积除权因子。
可参考wind数据或者雪球的数据
"""
import json
import os
class KlineFactors:

    def __init__(self,klines:list,sharebonus:list,importants:list,precision=.3) -> None:
        """初始化装载数据

        分红配股数据
        字段说明：
        # anno_date:公告日期
        # per_ten_send:每10股送股，
        # per_ten_incr:每10股转增，
        # per_cash_div:每股派息（现金分红），
        # share_day:除权除息日，
        # reg_day:股权登记日，
        # list_day:红股上市日
        # per_ten_allo:每10股配股
        # allo_price: 配股价

        对股价数据
        字段说明：
        # list_day:送股上市日
        # per_ten_allo:每10股配股
        # allo_price: 配股价


        Args:
            klines (list): k线数据 K线数据需按日期顺序排列
            sharebonus (list): 分红配股数据
            importants (list): 对股价数据
        """
        # k线数据 [[date,open,high,low,close,vol,amount]]
        self.klines = klines
        # 历史分红数据 
        self.sharebonus = sharebonus
        # 对股价数据（针对零几年左右）股改产生的误差
        self.importants = importants
        pass

    def get_qfq(self):
        # 保存复权因子
        factors = {}
        # 前复权最近一次除权除息日除权因子为1
        right_factor = 1.0
        # 复权因子 前复权因子初始值为 1.0
        fq_factor = 1.0
        # 保存前一个分红配股信息
        back_share = None
        # 保存前一个对股价信息
        back_important = None
        # K线数据按日期倒叙排列
        klines = self.klines.copy()
        # 按日期倒序排列
        klines.reverse()
        for kline in klines:
            date,o,h,l,close,v,a = kline
            # 寻找除权登记日分红配股信息
            share = self.get_sharebonus(date)
            if back_share!=None:
                right_factor *= self.get_sharebonus_right_factor(back_share,close)
                # 前复权因子
                fq_factor = right_factor
                # 保存前复权因子
                factors[back_share["share_day"]] = fq_factor
                    
            # 处理早期股改阶段，一般是零几年的时候出现 对价送股派送现金的现象
            important = self.get_important(date)
            if back_important!=None:
                right_factor *= self.get_important_right_factor(back_important,close)
                # 前复权因子
                fq_factor = right_factor
                # 前复权因子
                factors[back_important['list_day']] = fq_factor

            # 保存当前配股和对股价信息
            back_share = share
            back_important = important
        return factors

    def get_hfq(self):
        # 保存复权因子
        factors = {}
        # 最近一次除权除息日除权因子为1
        right_factor = 1.0
        hfq_factor = 1.0
        last_close = 0
        klines = self.klines.copy()
        # 按日期顺序递归
        for kline in klines:
            date,o,h,l,close,v,a = kline
            # 寻找除权登记日分红配股信息
            share = self.get_sharebonus(date)
            if share!=None and last_close>0:
                right_factor *= self.get_sharebonus_right_factor(share,last_close)
                # right_factor = float(("%.7f"%right_factor))
                # 后复权因子
                hfq_factor = 1.0 / right_factor
                # hfq_factor = float(("%.6f"%hfq_factor))
                factors[share["share_day"]] = hfq_factor

            # 处理早期股改阶段，一般是零几年出现 对价送股派送现金的现象
            important = self.get_important(date)
            if important!=None:
                right_factor *= self.get_important_right_factor(important,last_close)
                # right_factor = float(("%.7f"%right_factor))
                # 后复权因子
                hfq_factor = 1.0 / right_factor
                # hfq_factor = float(("%.6f"%hfq_factor))
                factors[important['list_day']] = hfq_factor

            # 保存上一个交易日收盘价
            last_close = close
        return factors
    
    def get_sharebonus_right_factor(self,sharebonus:dict,close:float):
        """根据分红配股计算除权因子

        Args:
            sharebonus (dict): 分红配股数据
            close (float): 股权登记日的收盘价 
            right_factor (float): 上一个 除权因子
        Returns:
            float: 除权因子
        """
        if sharebonus!=None and close>0:
            per_ten_send = float(sharebonus['per_ten_send']) # 每10股送股
            per_ten_incr = float(sharebonus['per_ten_incr']) # 每10股转增
            per_cash_div = float(sharebonus['per_cash_div']) # 分红派息
            per_ten_allo = float(sharebonus['per_ten_allo']) # 每10股配股
            allo_price = float(sharebonus['allo_price']) # 配股价
            # 除权除息价=(股权登记日的收盘价-每股所分红利现金额+配股价×每股配股数)÷(1+每股送红股数+每股配股数+每股转增股数);
            rm_right_close = (close - per_cash_div/10.0 + allo_price * (per_ten_allo/10.0) ) / (1.0+(per_ten_send/10.0) + (per_ten_allo/10.0) + (per_ten_incr/10.0) )
            # 除权因子 = 除权收盘价 / 除权登记日收盘价
            right_factor = rm_right_close / close
            # right_factor = float(("%.4f"%right_factor))
            return right_factor
    
    def get_important_right_factor(self,important:dict,close:float):
        """根据对股价数据计算除权因子

        Args:
            important (dict): 对股价数据
            close (float): 股权登记日的收盘价
        Returns:
            float: 除权因子
        """
        
        if important!=None and close>0:
            per_ten_send = float(important['per_ten_send']) # 每10股送股
            per_ten_cash = float(important['per_ten_cash']) # 每10股派送现金
            # 除权收盘价=除权除息价=(股权登记日的收盘价-每股所分红利现金额+配股价×每股配股数)÷(1+每股送红股数+每股配股数+每股转增股数);
            rm_right_close = (close - per_ten_cash/10.0 ) / (1.0+(per_ten_send/10.0))
            # 除权因子= 除权收盘价 / 除权登记日收盘价
            right_factor = rm_right_close / close
            # right_factor = float(("%.6f"%right_factor))
            return right_factor
            
    
    def get_sharebonus(self,day):
        """取某日的分红配股信息

        Args:
            day (str): 日期 格式：%Y%m%d

        Returns:
            dict: 某日分红配股 ｜ None
        """
        for item in self.sharebonus:
            # 除权除息日
            share_day:str = item['share_day']
            if share_day=='' or share_day==None: continue
            # 每10股配股
            per_ten_allo = item['per_ten_allo']
            # 配股价
            all_price = item['allo_price']
            # 没有配股信息就启用红股上市日
            if 'list_day' in item.keys() and per_ten_allo=='' and all_price=='':
                # 如果有红股上市日，就启用红股上市日
                share_day = item['list_day']
            share_day = share_day.replace('-','')
            # 取当天的
            if share_day==day:
                return item
        return 

    def get_important(self,day):
        """根据上市日获取对股价

        Args:
            day (str): 日期 Ymd

        Returns:
            important_matters: 返回重大事项集合
            
        """
        for item in self.importants:
            list_day:str = item['list_day']
            if list_day!='' and list_day!=None: 
                list_day = list_day.replace('-','')
                if list_day==day:
                    return item
        return None


if __name__=="__main__":
    # 日线
    day = open(os.path.dirname(os.path.abspath(__file__))+"/day.txt")
    datas = day.read()
    datas = json.loads(datas)
    klines = []
    for item in datas:
        date,op,high,low,close,vol,amount = item.split(",")
        klines.append([date,float(op),float(high),float(low),float(close),float(vol),float(amount)])

    # 分红
    sb = open(os.path.dirname(os.path.abspath(__file__))+"/sharebonus.txt")
    datas = sb.read()
    sharebonus = json.loads(datas)
    
    # 对价股
    im = open(os.path.dirname(os.path.abspath(__file__))+"/important.txt")
    datas = im.read()
    importants = json.loads(datas)

    # 前复权
    factors = KlineFactors(klines,sharebonus,importants).get_qfq()
    # print(factors)

    # 根据复权因子计算复权K线
    qfq_kline = []
    # klines.reverse()
    for item in klines:
        date,o,h,l,c,v,a = item
        # 查找日期之后的复权因子，如果查不到即为首次复权为1.0
        factor = 1.0
        fd = ""
        for d in list(factors.keys()):
            if int(date)<int(d.replace("-","")):
                factor = factors.get(d)
                fd = d
        # 计算复权数据
        o *= factor
        h *= factor
        l *= factor
        c *= factor
        a = round(a/v * factor * v,2)
        newitem = [date,round(o,2),round(h,2),round(l,2),round(c,2),v,a,fd,factor]
        if str(date).startswith("1999"):
            print(newitem)
        qfq_kline.append(newitem)
    # print(qfq_kline)

    # 后复权
    # klines = klines[2900:]
    factors = KlineFactors(klines,sharebonus,importants).get_hfq()
    # print(factors)

    # 根据后权因子计算复权K线
    hfq_kline = []
    for item in klines:
        date,o,h,l,c,v,a = item
        # 查找日期之前的复权因子，如果查不到即为首次复权为1.0
        factor = 1.0
        fd = ""
        for d in list(factors.keys()):
            if int(date)>=int(d.replace("-","")):
                factor = factors.get(d)
                fd = d
        # 计算复权数据
        o *= factor
        h *= factor
        l *= factor
        c *= factor
        newitem = [date,round(o,2),round(h,2),round(l,2),round(c,2),v,a,fd,factor]
        if str(date).startswith("2023"):
            print(newitem)
        hfq_kline.append(newitem)
    # print(hfq_kline)

    

        