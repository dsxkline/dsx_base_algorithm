package com.dsxkline.android.dsxkline;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Array;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class QQhq {


    /**
     * 请求第三方实时行情
     * @param {string} code 股票代码
     * @param {object} success
     * @param {object} fail
     * 0: 未知 1: 名字 2: 代码 3: 当前价格 4: 昨收 5: 今开 6: 成交量（手） 7: 外盘 8: 内盘 9: 买一 10: 买一量（手） 11-18: 买二 买五 19: 卖一 20: 卖一量 21-28: 卖二 卖五 29: 最近逐笔成交 30: 时间 31: 涨跌 32: 涨跌% 33: 最高 34: 最低 35: 价格/成交量（手）/成交额 36: 成交量（手） 37: 成交额（万） 38: 换手率 39: 市盈率 40: 41: 最高 42: 最低 43: 振幅 44: 流通市值 45: 总市值 46: 市净率 47: 涨停价 48: 跌停价
     */
    public static List<HqModel> getQuote(String code){
        String api = "https://qt.gtimg.cn/q="+code;
        String resultStart = "v_{code}=";
        String resultEnd = ";";
        String data = get(api);
        //console.log(response);
        List<HqModel> list = null;
        if(data!=null){
            list = new ArrayList<>();
            String[] dataList = data.split(resultEnd);
            String[] codes = code.split(",");
            for (int i = 0; i < dataList.length; i++) {
                String item = dataList[i];
                String rss = item.replace(resultStart.replace("{code}",code.toLowerCase()),"");
                String[] rs = rss.split("~");
                if(rs[1]!=""){
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
                    obj.date = rs[30].substring(0,8);
                    obj.time = rs[30].substring(8);
                    obj.change = rs[31];
                    obj.changeRatio = rs[32];

                    list.add(obj);
                    //console.log(obj);
                    i++;
                }
            }
        }
        return list;
    }

    public static List<String> getTimeLine(String code) throws JSONException {
        String api = "https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_"+code+"&code="+code+"&r=0."+(new Date().getTime());
        if(code.startsWith("us")){
            api = "https://web.ifzq.gtimg.cn/appstock/app/UsMinute/query?_var=min_data_"+code+"&code="+code.substring(0,2)+"."+code.substring(2)+"&r=0."+(new Date().getTime());
            code = code.substring(0,2)+"."+code.substring(2);
        }
        List<String> list = null;
        String result = get(api);
        if(result!=null){
            result = result.replace("min_data_"+code.replace(".","")+"=","");
            JSONObject rss = new JSONObject(result);
            JSONArray data = rss.getJSONObject("data").getJSONObject(code).getJSONObject("data").getJSONArray("data");
            String date = rss.getJSONObject("data").getJSONObject(code).getJSONObject("data").getString("date");
            list = new ArrayList<>();
            for (int i = 0; i < data.length(); i++) {
                String item = data.getString(i);
                String[] r = item.split(" ");
                String low = date+","+item.replaceAll(" ",",");
                list.add(low);
            }
        }
        return list;
    }

    public static Map<String,Object> getFdayLine(String code) throws JSONException {
        String api = "https://web.ifzq.gtimg.cn/appstock/app/day/query?_var=fdays_data_"+code+"&code="+code+"&r=0."+(new Date().getTime());
        if(code.startsWith("us")){
            api = "https://web.ifzq.gtimg.cn/appstock/app/dayus/query?_var=fdays_data_"+code+"&code="+code.substring(0,2)+"."+code.substring(2)+"&r=0."+(new Date().getTime());
            code = code.substring(0,2)+"."+code.substring(2);
        }
        Map map = new HashMap();
        List<String> list = null;
        String result = get(api);
        double prec = 0;
        if(result!=null){
            result = result.replace("fdays_data_"+code.replace(".","")+"=","");
            JSONObject rss = new JSONObject(result);
            JSONArray data = rss.getJSONObject("data").getJSONObject(code).getJSONArray("data");
            list = new ArrayList<>();
            for (int i = data.length()-1; i >=0; i--) {
                JSONObject item = data.getJSONObject(i);
                String date = item.getString("date");
                prec = item.getDouble("prec");
                JSONArray d = item.getJSONArray("data");
                for (int j = 0; j < d.length(); j++) {
                    String subitem = d.getString(j);
                    String low = date+","+subitem.replaceAll(" ",",");
                    list.add(low);
                }
            }
        }
        map.put("lastClose",prec);
        map.put("data",list);
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
    public static List<String> getkLine(String code,String cycle,String startDate,String endDate,int pageSize,String fqType) throws JSONException {
        String api = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_"+cycle+fqType+"&param="+code+","+cycle+","+startDate+","+endDate+","+pageSize+","+fqType+"&r=0.36592503777267116"+(new Date().getTime());
        if(code.startsWith("us")){
            code = code.substring(0,2)+"."+code.substring(2);
            api = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_"+cycle+fqType+"&param="+code+","+cycle+","+startDate+","+endDate+","+pageSize+","+fqType+"&r=0.36592503777267116"+(new Date().getTime());
        }

        List<String> list = null;
        String result = get(api);
        if(result!=null){
            result = result.replace("kline_"+cycle+fqType+"=","");
            JSONObject rss = new JSONObject(result);
            JSONArray data = rss.getJSONObject("data").getJSONObject(code).getJSONArray(cycle);
            list = new ArrayList<>();
            for (int i = 0; i < data.length(); i++) {
                JSONArray d = data.getJSONArray(i);
                String r = d.getString(0)+","+d.getString(1)+","+d.getString(3)+","+d.getString(4)+","+d.getString(2)+","+d.getString(5)+","+d.getString(8);
                r = r.replaceAll("-","");
                list.add(r);
            }
        }
        return list;
    }

    public static List<String> getMinLine (String code,String cycle,int pageSize) throws JSONException {

        if(code.startsWith("us")){
            code = code.substring(0,2)+"."+code.substring(2);
        }
        String api = "https://ifzq.gtimg.cn/appstock/app/kline/mkline?param="+code+","+cycle+",,"+pageSize+"&_var="+cycle+"_today&r=0.36592503777267116"+(new Date().getTime());

        List<String> list = null;
        String result = get(api);
        if(result!=null){
            result = result.replace(cycle+"_today=","");
            JSONObject rss = new JSONObject(result);
            JSONArray data = rss.getJSONObject("data").getJSONObject(code).getJSONArray(cycle);
            list = new ArrayList<>();
            for (int i = 0; i < data.length(); i++) {
                JSONArray d = data.getJSONArray(i);
                String date = d.getString(0).substring(0,8);
                String time = d.getString(0).substring(8);
                String r = date+","+time+","+d.getString(1)+","+d.getString(3)+","+d.getString(4)+","+d.getString(2)+","+d.getString(5)+","+d.getString(7);
                r = r.replaceAll("-","");
                list.add(r);
            }
        }
        return list;
    }



    private static String get(String urlstr){
        StringBuffer sb = new StringBuffer();
        try {
            URL url = new URL(urlstr);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setConnectTimeout(30 * 1000);
            con.setReadTimeout(20*1000);
            InputStream is = con.getInputStream();
            BufferedReader in = new BufferedReader(new InputStreamReader(is));
            String line;
            while ((line = in.readLine()) != null) {
                sb.append(line);
            }
            is.close();
            is = null;
            in.close();
            in = null;
            if (con != null) {
                con.disconnect();
            }
            con = null;

            url = null;
            line = null;
        } catch (Exception e) {
            e.printStackTrace();
        }
        String res = sb.toString();
        sb = null;
        return res;
    }
}
