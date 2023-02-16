using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using Newtonsoft.Json.Linq;

namespace DsxKline_WinForm.dsxkline
{
    class QqHq
    {
        /**
         * 请求第三方实时行情
         * @param {string} code 股票代码
         * @param {object} success
         * @param {object} fail
         * 0: 未知 1: 名字 2: 代码 3: 当前价格 4: 昨收 5: 今开 6: 成交量（手） 7: 外盘 8: 内盘 9: 买一 10: 买一量（手） 11-18: 买二 买五 19: 卖一 20: 卖一量 21-28: 卖二 卖五 29: 最近逐笔成交 30: 时间 31: 涨跌 32: 涨跌% 33: 最高 34: 最低 35: 价格/成交量（手）/成交额 36: 成交量（手） 37: 成交额（万） 38: 换手率 39: 市盈率 40: 41: 最高 42: 最低 43: 振幅 44: 流通市值 45: 总市值 46: 市净率 47: 涨停价 48: 跌停价
         */
        public static List<HqModel> getQuote(String code)
        {
            String api = "http://qt.gtimg.cn/q=" + code;
            String resultStart = "v_{code}=";
            String resultEnd = ";";
            String data = get(api);
            //console.log(response);
            List<HqModel> list = null;
            if (data != null)
            {
                list = new List<HqModel>();
                String[] dataList = data.Split(resultEnd.ToCharArray());
                String[] codes = code.Split(',');
                for (int i = 0; i < dataList.Length; i++)
                {
                    String item = dataList[i];
                    String rss = item.Replace(resultStart.Replace("{code}", code.ToLower()), "");
                    String[] rs = rss.Split('~');
                    if (rs[1] != "")
                    {
                        HqModel obj = new HqModel();
                        obj.name = rs[1];
                        obj.code = codes[i];
                        obj.price = rs[3];
                        obj.lastClose = rs[4];
                        obj.open = rs[5];
                        obj.high = rs[33];
                        obj.low = rs[34];
                        obj.vol = rs[6];
                        obj.volAmount = rs[37];
                        obj.date = rs[30].Substring(0, 8);
                        obj.time = rs[30].Substring(8);
                        obj.change = rs[31];
                        obj.changeRatio = rs[32];

                        list.Add(obj);
                        //console.log(obj);
                        i++;
                    }
                }
            }
            return list;
        }

        public static List<String> getTimeLine(String code)
        {
            String api = "https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_" + code + "&code=" + code + "&r=0." + (new DateTime().Millisecond);
            if (code.StartsWith("us"))
            {
                api = "https://web.ifzq.gtimg.cn/appstock/app/UsMinute/query?_var=min_data_" + code + "&code=" + code.Substring(0, 2) + "." + code.Substring(2) + "&r=0." + (new DateTime().Millisecond);
                code = code.Substring(0, 2) + "." + code.Substring(2);
            }
            List<String> list = null;
            String result = get(api);
            if (result != null)
            {
                result = result.Replace("min_data_" + code.Replace(".", "") + "=", "");
                Dictionary<String, dynamic> rss = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<String, dynamic>>(result);
                JArray data = rss["data"][code]["data"]["data"];
                String date = rss["data"][code]["data"]["date"];
                list = new List<string>();
                for (int i = 0; i < data.Count; i++)
                {
                    String item = data[i].ToString();
                    String[] r = item.Split(' ');
                    String low = date + "," + item.Replace(" ", ",");
                    list.Add(low);
                }
            }
            return list;
        }

        public static Dictionary<String, Object> getFdayLine(String code)
        {
            String api = "https://web.ifzq.gtimg.cn/appstock/app/day/query?_var=fdays_data_" + code + "&code=" + code + "&r=0." + (new DateTime().Millisecond);
            if (code.StartsWith("us"))
            {
                api = "https://web.ifzq.gtimg.cn/appstock/app/dayus/query?_var=fdays_data_" + code + "&code=" + code.Substring(0, 2) + "." + code.Substring(2) + "&r=0." + (new DateTime().Millisecond);
                code = code.Substring(0, 2) + "." + code.Substring(2);
            }
            Dictionary<String, dynamic> map = new Dictionary<string, dynamic>();
            List<String> list = null;
            String result = get(api);
            double prec = 0;
            if (result != null)
            {
                result = result.Replace("fdays_data_" + code.Replace(".", "") + "=", "");
                Dictionary<String, dynamic> rss = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<String, dynamic>>(result);
                JArray data = rss["data"][code]["data"];
                list = new List<string>();
                for (int i = data.Count - 1; i >= 0; i--)
                {
                    Dictionary<String, dynamic> item = data[i].ToObject<Dictionary<String,dynamic>>();
                    String date = item["date"];
                    prec = double.Parse(item["prec"]);
                    JArray d = item["data"];
                    for (int j = 0; j < d.Count; j++)
                    {
                        String subitem = d[j].ToString();
                        String low = date + "," + subitem.Replace(" ", ",");
                        list.Add(low);
                    }
                }
            }
            map.Add("lastClose", prec);
            map.Add("data", list);
            return map;
        }

        /**
         * 获取K线图历史数据
         * @param {string} code 股票代码
         * @param {string} cycle 周期 day，week，month
         * @param {string} startDate 开始日期 默认 空
         * @param {string} endDate 结束日期 默认空
         * @param {int} pageSize 每页大小 默认 320
         * @param {string} fqType 复权类型 前复权=qfq，后复权=hfq
         * @param {*} success
         * @param {*} fail
         */
        public static List<String> getkLine(String code, String cycle, String startDate, String endDate, int pageSize, String fqType)
        {
            String api = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_" + cycle + fqType + "&param=" + code + "," + cycle + "," + startDate + "," + endDate + "," + pageSize + "," + fqType + "&r=0.36592503777267116" + (new DateTime().Millisecond);
            if (code.StartsWith("us"))
            {
                code = code.Substring(0, 2) + "." + code.Substring(2);
                api = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_" + cycle + fqType + "&param=" + code + "," + cycle + "," + startDate + "," + endDate + "," + pageSize + "," + fqType + "&r=0.36592503777267116" + (new DateTime().Millisecond);
            }

            List<String> list = null;
            String result = get(api);
            if (result != null)
            {
                result = result.Replace("kline_" + cycle + fqType + "=", "");
                Dictionary<String, dynamic> rss = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<String, dynamic>>(result);
                JArray data = rss["data"][code][cycle];
                list = new List<string>();
                for (int i = 0; i < data.Count(); i++)
                {
                    JToken[] d = data[i].ToArray();
                    String r = d[0] + "," + d[1] + "," + d[3] + "," + d[4] + "," + d[2] + "," + d[5] + "," + d[8];
                    r = r.Replace("-", "");
                    list.Add(r);
                }
            }
            return list;
        }

        public static List<String> getMinLine(String code, String cycle, int pageSize)
        {

            if (code.StartsWith("us"))
            {
                code = code.Substring(0, 2) + "." + code.Substring(2);
            }
            String api = "https://ifzq.gtimg.cn/appstock/app/kline/mkline?param=" + code + "," + cycle + ",," + pageSize + "&_var=" + cycle + "_today&r=0.36592503777267116" + (new DateTime().Millisecond);

            List<String> list = null;
            String result = get(api);
            if (result != null)
            {
                result = result.Replace(cycle + "_today=", "");
                Dictionary<String, dynamic> rss = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<String, dynamic>>(result);
                JArray data = rss["data"][code][cycle];
                list = new List<string>();
                for (int i = 0; i < data.Count(); i++)
                {
                    JToken[] d = data[i].ToArray();
                    String date = d[0].ToString().Substring(0, 8);
                    String time = d[0].ToString().Substring(8);
                    String r = date + "," + time + "," + d[1] + "," + d[3] + "," + d[4] + "," + d[2] + "," + d[5] + "," + d[7];
                    r = r.Replace("-", "");
                    list.Add(r);
                }
            }
            return list;
        }



        public static String get(String url)
        {
            try
            {
                String result = "";
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
                request.Method = "GET";
                request.Timeout = 20000;
                HttpWebResponse response = (HttpWebResponse)request.GetResponse();
                Stream stream = response.GetResponseStream();
                //结果
                using (StreamReader reader = new StreamReader(stream, Encoding.UTF8))
                {
                    result = reader.ReadToEnd();
                    return result;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("GET请求错误：" + ex);
                return null;
            }
        }
    }
}
