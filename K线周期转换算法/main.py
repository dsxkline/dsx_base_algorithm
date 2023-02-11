import datetime
import os
# 周期
class CYCLE:
    T='t'                           # 分时线
    T5='t5'                         # 五日分时线
    DAY="day"                       # 日K
    WEEK="week"                     # 周K
    MONTH="month"                   # 月K
    YEAR="year"                     # 年K
    M1="m1"                         # 1分钟K
    M5="m5"                         # 5分钟K
    M15="m15"                       # 15分钟K
    M30="m30"                       # 30分钟K
    M60="m60"                       # 60分钟K

class DsxBaseConverKlines:
    def __init__(self,klines:list) -> None:
        # k线历史数据
        # 日线数据 [date,open,high,low,close,vol,amount]
        # 分钟数据 [datetime,open,high,low,close,vol,amount]
        self.klines = klines
        pass
  
    def converkline_to(self,cycle:CYCLE):
        """通过日期归类算法转换k线周期
        通过对日期的周期提取归类，同周期K线归类为一组，再计算即可得到周K数据
        需要防止日期跨周，例如遇到不连续或停牌一段时间的

        Args:
            type (str): week,month,year
            klines (list): 日线数据 [date,open,high,low,close,vol,amount]
        Returns:
            list: 转换后的k线
        """
        klines = self.klines.copy()
        # 日周月年K线的分组标识提取方法
        get_date_group = self.get_date_week_group
        if cycle==CYCLE.WEEK :  get_date_group = self.get_date_week_group
        if cycle==CYCLE.MONTH :  get_date_group = self.get_date_month_group
        if cycle==CYCLE.YEAR :  get_date_group = self.get_date_year_group
        # 分钟线分组周期
        m = None
        if cycle==CYCLE.M5 : m = 5
        if cycle==CYCLE.M15 : m = 15
        if cycle==CYCLE.M30 : m = 30
        if cycle==CYCLE.M60 : m = 60
        # k线滚动缓存
        last_klines = []
        # 分组标识
        last_group = None
        # 保存转换结果
        new_klines = []
        for item in klines:
            # 分组提取
            if not m: group_name = get_date_group(item[0])
            else: group_name = self.get_date_min_group(item[0],m)
            if last_group == None: last_group = group_name
            # 分组归类
            if group_name==last_group:
                # 分组归类合并,分组数据合并成新的开高低收新k线
                last_klines = self.merge_group_klines([last_klines]+[item])
            # 分组滚动
            if group_name!=last_group or item == klines[klines.__len__()-1]:
                # 分组不同表明已滚动到下个分组，这时候需要合并即可得到分组的K线数据
                group_kline = self.merge_group_klines([last_klines])
                # 计算完成清空箱子装新数据进去
                last_klines = item
                # 当前分组开启归类循环
                last_group = group_name
                # 数据保存
                new_klines.append(group_kline)
        return new_klines
    
    def get_date_week_group(self,date:str):
        """提取周分组特征

        Args:
            date (str): 日期格式 %Y%m%d

        Returns:
            str: %Y-%week
        """
        d = datetime.datetime.strptime(date,'%Y%m%d')
        # (2023,45,5)  年 year，周号 week，周几 weekday
        week_group = d.isocalendar()
        return str(week_group[0])+"-"+str(week_group[1])

    def get_date_month_group(self,date:str):
        """提取月分组特征

        Args:
            date (str): 日期格式 %Y%m%d

        Returns:
            str: %Y%m
        """
        return date[:6]

    def get_date_year_group(self,date:str):
        """提取年分组特征

        Args:
            date (str): 日期格式 %Y%m%d

        Returns:
            str: %Y
        """
        return date[:4]

    def get_date_min_group(self,date:str,m:int):
        """提取分钟分组特征

        Args:
            date (str): 日期格式 %Y%m%d%H%M

        Returns:
            str: %Y%m%d%Hmin
        """
        datemin = date[8:12]
        # 分组规则根据N分钟来分组，每隔N分钟一组数据 N=min，所以需要根据当前时间计算相对于开盘时间的顺序编号
        d = (datetime.datetime.strptime(datemin,"%H%M") - datetime.datetime.strptime("0930","%H%M"))
        sort = d.seconds/60
        if int(datemin)>=1300:
            # 中午休盘90分钟
            sort -= 90
        # 换算成所在分组
        y = sort % m
        # 按N分钟一组
        group_name = int(sort/m) + (y>0 and 1 or 0)
        return str(group_name)
    
    def merge_group_klines(self,group_klines:list):
        """合并分组k线

        Args:
            group_klines (list): k线数据

        Returns:
            _type_: _description_
        """
        if group_klines==None : return
        open = 0
        high = 0
        low = 1000000000
        close = 0
        vol = 0
        amount = 0
        i = 0
        date = ""
        for item in group_klines:
            if len(item)>=7:
                if i==0:open = item[1]
                date = item[0]
                high = max(high,item[2])
                low = min(low,item[3])
                close = item[4]
                vol += item[5]
                amount += item[6]
                i+=1
                
        
        return [date,open,high,low,close,vol,amount]

    def converkline_toweek(self):
        """把日线数据转成周线
        通过对日期的周期提取归类，同周期K线归类为一组，再计算即可得到周K数据
        需要防止日期跨周，例如遇到不连续或停牌一段时间的

        Args:
            klines (list): 日线数据 [date,open,high,low,close,vol,amount]
        """
        return self.converkline_to(CYCLE.WEEK)

    def converkline_tomonth(self):
        """把日线数据转成月线
        通过对日期的月度提取归类，同月度K线归类为一组，再计算可能得到月K数据

        Args:
            klines (list): 日线数据 [date,open,high,low,close,vol,amount]
        """

        return self.converkline_to(CYCLE.MONTH)


    def converkline_toyear(self):
        """把日线数据转成年线
        通过对日线的年度提取归类，同年度的K线归位一组，再计算即可得到年K数据

        Args:
            klines (list): 日线数据 [date,open,high,low,close,vol,amount]
        """
        
        return self.converkline_to(CYCLE.YEAR)
    
    def converkline_tomin(self,cycle:CYCLE):
        """把1分钟线数据转成N分钟线
        把时间分成N份，计算每一份的K线数据即可转换

        Args:
            klines (list): 1分钟数据 [datetime,open,high,low,close,vol,amount]
        """
        return self.converkline_to(cycle)


if __name__=="__main__":
    
    with open(os.path.dirname(os.path.abspath(__file__))+"/day.txt") as f:
        # 取原始日线数据
        datas = f.read()
        datas = datas.split("\n")
        klines = [] 
        for item in datas:
            date,op,high,low,close,vol,amount = item.split(",")
            klines.append([date,float(op),float(high),float(low),float(close),float(vol),float(amount)])

        # 转成周线数据
        week_klines = DsxBaseConverKlines(klines).converkline_toweek()
        # 转成周线数据
        month_klines = DsxBaseConverKlines(klines).converkline_tomonth()
        # 转成周线数据
        year_klines = DsxBaseConverKlines(klines).converkline_toyear()

        # print(year_klines)
    
    with open(os.path.dirname(os.path.abspath(__file__))+"/min.txt") as f:
        # 取原始一分钟数据
        datas = f.read()
        datas = datas.split("\n")
        klines = [] 
        for item in datas:
            date,m,op,high,low,close,vol,amount = item.split(",")
            klines.append([date+m,float(op),float(high),float(low),float(close),float(vol),float(amount)])
        # # 转成5分钟数据
        # min5_klines = DsxBaseConverKlines(klines).converkline_tomin(CYCLE.M5)
        # # 转成15分钟数据
        # min15_klines = DsxBaseConverKlines(klines).converkline_tomin(CYCLE.M15)
        # # 转成30分钟数据
        # min30_klines = DsxBaseConverKlines(klines).converkline_tomin(CYCLE.M30)
        # 转成60分钟数据
        min60_klines = DsxBaseConverKlines(klines).converkline_tomin(CYCLE.M60)

        print(min5_klines)