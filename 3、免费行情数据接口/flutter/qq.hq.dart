// ignore_for_file: unnecessary_type_check

import 'dart:convert';
import 'dart:io';

import 'hqmodel.dart';
import 'package:fast_gbk/fast_gbk.dart'; 

class QqHq {
  static final HttpClient _http = HttpClient();

  /// 请求第三方实时行情
  /// @param {string} code 股票代码
  /// @param {object} success
  /// @param {object} fail
  /// 0: 未知 1: 名字 2: 代码 3: 当前价格 4: 昨收 5: 今开 6: 成交量（手） 7: 外盘 8: 内盘 9: 买一 10: 买一量（手） 11-18: 买二 买五 19: 卖一 20: 卖一量 21-28: 卖二 卖五 29: 最近逐笔成交 30: 时间 31: 涨跌 32: 涨跌% 33: 最高 34: 最低 35: 价格/成交量（手）/成交额 36: 成交量（手） 37: 成交额（万） 38: 换手率 39: 市盈率 40: 41: 最高 42: 最低 43: 振幅 44: 流通市值 45: 总市值 46: 市净率 47: 涨停价 48: 跌停价
  static Future<void> getQuote(
      String code, Function success, Function fail) async {
    String api = "http://qt.gtimg.cn/q=" + code;
    print(api);
    HttpClientRequest request = await _http.getUrl(Uri.parse(api));
    HttpClientResponse res = await request.close();
    String response = await res.transform(gbk.decoder).join();
    // // 关闭client后，通过该client发起的所有请求都会中止。
    // _http.close();
    if (response.isNotEmpty) {
      String data = response;
      List<HqModel> list = [];
      List<String> dataList = data.split(";");
      List<String> codes = code.split(",");
      int i = 0;
      for (var item in dataList) {
        String rss = item.replaceAll(
            "v_{code}=".replaceAll("{code}", code.toLowerCase()), "");
        List<String> rs = rss.split("~");
        if (rs.length > 32) {
          HqModel obj = HqModel(
              name: rs[1],
              code: codes[i],
              price: rs[3],
              lastClose: rs[4], // 昨收
              open: rs[5],
              high: rs[33],
              low: rs[34],
              vol: rs[6],
              volAmount: rs[37] * 10000,
              date: rs[30].replaceAll("-", "").substring(0, 8),
              time: rs[30].replaceAll("-", "").substring(8),
              change: rs[31],
              changeRatio: rs[32]);
          list.add(obj);
          //console.log(obj);
          i++;
        }
      }
      if (success is Function) success(list);
    } else {
      if (fail is Function) fail(response);
    }
  }

  static Future<void> getTimeLine(code, success, fail) async {
    String api =
        "https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_" +
            code +
            "&code=" +
            code +
            "&r=0." +
            DateTime.now().microsecondsSinceEpoch.toString();
    if (code.startsWith("us")) {
      api =
          "https://web.ifzq.gtimg.cn/appstock/app/UsMinute/query?_var=min_data_" +
              code +
              "&code=" +
              code.substring(0, 2) +
              "." +
              code.substring(2) +
              "&r=0." +
              (DateTime.now().microsecondsSinceEpoch.toString());
      code = code.substring(0, 2) + "." + code.substring(2);
    }
    print(api);
    HttpClientRequest request = await _http.getUrl(Uri.parse(api));
    HttpClientResponse res = await request.close();
    String response = await res.transform(gbk.decoder).join();
    if (response.isNotEmpty) {
      String result = response;
      result =
          result.replaceAll("min_data_" + code.replaceAll(".", "") + "=", "");
      Map rs = jsonDecode(result);

      List<dynamic> data = rs["data"][code]["data"]["data"];
      String date = rs["data"][code]["data"]["date"];
      List<String> list = [];
      for (var item in data) {
        
          String low = date + "," + item.replaceAll(" ", ",");
          list.add(low);
        
      }
      data.clear();
      rs.clear();
      
      success(list);
    } else {
      fail(response);
    }
  }

  static Future<void> getFdayLine(code, success, fail) async {
    String api =
        "https://web.ifzq.gtimg.cn/appstock/app/day/query?_var=fdays_data_" +
            code +
            "&code=" +
            code +
            "&r=0." +
            (DateTime.now().microsecondsSinceEpoch.toString());
    if (code.startsWith("us")) {
      api =
          "https://web.ifzq.gtimg.cn/appstock/app/dayus/query?_var=fdays_data_" +
              code +
              "&code=" +
              code.substring(0, 2) +
              "." +
              code.substring(2) +
              "&r=0." +
              (DateTime.now().microsecondsSinceEpoch.toString());
      code = code.substring(0, 2) + "." + code.substring(2);
    }
    print(api);
    HttpClientRequest request = await _http.getUrl(Uri.parse(api));
    HttpClientResponse res = await request.close();
    String response = await res.transform(gbk.decoder).join();
    if (response.isNotEmpty) {
      String result = response;
      result =
          result.replaceAll("fdays_data_" + code.replaceAll(".", "") + "=", "");
      Map? rs = jsonDecode(result);
      List<dynamic> data = rs!["data"][code]["data"];
      double prec = 0;
      List<String> list = [];
      for (int i = data.length - 1; i >= 0; i--) {
        List<dynamic>? d = data[i]["data"];
        String date = data[i]["date"];
        prec = double.parse(data[i]["prec"]);
        for (var item in d!) {
          String low = date + "," + item.replaceAll(" ", ",");
          list.add(low);
        }
        d.clear();
        d = null;
      }
      rs.clear();
      rs = null;
      data.clear();
      success({"lastClose": prec, "data": list});
    } else {
      fail(response);
    }
  }

  /// 获取K线图历史数据
  /// @param {string} code 股票代码
  /// @param {string} cycle 周期 day，week，month
  /// @param {string} startDate 开始日期 默认 空
  /// @param {string} endDate 结束日期 默认空
  /// @param {int} pageSize 每页大小 默认 320
  /// @param {string} fqType 复权类型 前复权=qfq，后复权=hfq
  /// @param {*} success
  /// @param {*} fail
  static Future<void> getKLine(
      code, cycle, startDate, endDate, pageSize, fqType, success, fail) async {
    String api =
        "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_" +
            cycle +
            fqType +
            "&param=" +
            code +
            "," +
            cycle +
            "," +
            startDate +
            "," +
            endDate +
            "," +
            pageSize.toString() +
            "," +
            fqType +
            "&r=0." +
            (DateTime.now().microsecondsSinceEpoch.toString());
    print(api);
    if (code.startsWith("us")) {
      code = code.substring(0, 2) + "." + code.substring(2);
      api =
          "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_" +
              cycle +
              fqType +
              "&param=" +
              code +
              "," +
              cycle +
              "," +
              startDate +
              "," +
              endDate +
              "," +
              pageSize +
              "," +
              fqType +
              "&r=0." +
              (DateTime.now().microsecondsSinceEpoch.toString());
    }

    HttpClientRequest request = await _http.getUrl(Uri.parse(api));
    HttpClientResponse res = await request.close();
    String response = await res.transform(gbk.decoder).join();
    if (response.isNotEmpty) {
      String result = response;
      result = result.replaceAll("kline_" + cycle + fqType + "=", "");
      Map rs = jsonDecode(result);
      //print(rs);
      List<dynamic> data = rs["data"][code][cycle];
      List<String> list = [];
      for (var d in data) {
        String low = d[0] +
            "," +
            d[1] +
            "," +
            d[3] +
            "," +
            d[4] +
            "," +
            d[2] +
            "," +
            d[5] +
            "," +
            d[8];
        low = low.replaceAll("-", "");
        list.add(low);
      }
      data.clear();
      success(list);
    } else {
      fail(response);
    }
  }

  static Future<void> getMinLine(code, cycle, pageSize, success, fail) async {
    if (code.startsWith("us")) {
      code = code.substring(0, 2) + "." + code.substring(2);
    }
    String api = "https://ifzq.gtimg.cn/appstock/app/kline/mkline?param=" +
        code +
        "," +
        cycle +
        ",," +
        pageSize.toString() +
        "&_var=" +
        cycle +
        "_today&r=0." +
        (DateTime.now().microsecondsSinceEpoch.toString());
    print(api);
    HttpClientRequest request = await _http.getUrl(Uri.parse(api));
    HttpClientResponse res = await request.close();
    String response = await res.transform(gbk.decoder).join();
    if (response.isNotEmpty) {
      String result = response;
      result = result.replaceAll(cycle + "_today=", "");
      Map rs = jsonDecode(result);
      //print(rs);
      List<dynamic> data = rs["data"][code][cycle];
      List<String> list = [];
      for (var d in data) {
        String low = d[0].substring(0, 8) +
            "," +
            d[0].substring(8) +
            "," +
            d[1] +
            "," +
            d[3] +
            "," +
            d[4] +
            "," +
            d[2] +
            "," +
            d[5] +
            "," +
            d[7];
        low = low.replaceAll("-", "");
        list.add(low);
      }
      data.clear();
      success(list);
    } else {
      fail(response);
    }
  }
}
