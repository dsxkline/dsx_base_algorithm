import datetime
import dsxquant

dsxquant.dataser.set_debug(True)
dd = dsxquant.dataser()
if dd.connect():
   result = dd.get_quotes("sh000001").dataframe()
   print(result)

# 异步订阅模式，订阅模式请求是异步进行的，订阅成功后服务器会主动推送信息到您的回调函数中,注意请不要手动调用关闭连接方法
dd_async = dsxquant.dataser.asyncconnect()
if dd_async:
    # 异步请求实时行情接口，服务器会主动推送实时行情
    def quotes_callback(response:dsxquant.parser):
        # print(response.get("msg"))
        result = response.dataframe()
        print(result)
    # 批量订阅股票代码,批量订阅最多支持50个股票代码
    result = dd_async.sub_quotes("sh000001,sh600000,sz000001,bj430047,bj430090",quotes_callback)
    print(result)
        
    def quotes_all_callback(response:dsxquant.parser):
        dd = response.dataframe()
        # 第一行默认是字段名称数组 ["amount","close",.....]
        names:list = list(dd.values[0])
        # 第二行开始是数据
        quote = dd.loc[1,:]
        code = quote[names.index("code")]
        t = quote[names.index("lasttime")]
        d = quote[names.index("lastdate")]
        t = datetime.datetime.strptime(d+" "+t,"%Y-%m-%d %H:%M:%S")
        s = datetime.datetime.now() - t
        print("%s 笔 %s 时间 %s 当前时间 %s 延时 %s s" % (dd.__len__(),code,t,datetime.datetime.now(),s.seconds))
    # 全量订阅全市场所有股票实时行情
    dd_async.sub_all_quotes(quotes_all_callback)