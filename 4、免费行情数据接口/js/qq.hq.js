/**
 * 读取第三方行情
 * 感谢腾讯提供行情数据
 */
String.prototype.replaceAll = function(s1, s2) {
    return this.replace(new RegExp(s1, "gm"), s2);
}
var qqhq = {
    
};
qqhq.resultStart = "v_{code}=";
qqhq.resultEnd = ";";
/**
 * 请求第三方实时行情
 * @param {string} code 股票代码
 * @param {object} success 
 * @param {object} fail 
 * 0: 未知 1: 名字 2: 代码 3: 当前价格 4: 昨收 5: 今开 6: 成交量（手） 7: 外盘 8: 内盘 9: 买一 10: 买一量（手） 11-18: 买二 买五 19: 卖一 20: 卖一量 21-28: 卖二 卖五 29: 最近逐笔成交 30: 时间 31: 涨跌 32: 涨跌% 33: 最高 34: 最低 35: 价格/成交量（手）/成交额 36: 成交量（手） 37: 成交额（万） 38: 换手率 39: 市盈率 40: 41: 最高 42: 最低 43: 振幅 44: 流通市值 45: 总市值 46: 市净率 47: 涨停价 48: 跌停价
 */
qqhq.getQuote = function(code,success,fail){
    let api = "http://qt.gtimg.cn/q="+code;
    this.get(api,function(response){
        //console.log(response);
        if(response){
            let data = response;
            let list = [];
            let dataList = data.split(qqhq.resultEnd);
            let codes = code.split(",");
            let i = 0;
            dataList.forEach(item => {
                let rs = item.replace(qqhq.resultStart.replace("{code}",code.toLowerCase()),"");
                rs = rs.split("~");
                if(rs[1]){
                    let obj = {
                        name:rs[1],
                        code:codes[i],
                        price:rs[3],
                        lastClose:rs[4], // 昨收
                        open:rs[5],
                        high:rs[33],
                        low:rs[34],
                        vol:rs[6],
                        volAmount:rs[37]*10000,
                        date:rs[30].replaceAll("-","").substring(0,8),
                        time:rs[30].replaceAll("-","").substring(8),
                        change:rs[31],
                        changeRatio:rs[32]
                    }
                    list.push(obj);
                    //console.log(obj);
                    i++;
                }
            });
            success(list);
        }else{
            fail(response);
        }

    },function(error){
        fail(error);
    })
}

qqhq.getTimeLine = function(code,success,fail){
    let api = "https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_"+code+"&code="+code+"&r=0."+(new Date().getTime());
    if(code.startsWith("us")){
        api = "https://web.ifzq.gtimg.cn/appstock/app/UsMinute/query?_var=min_data_"+code+"&code="+code.substring(0,2)+"."+code.substring(2)+"&r=0."+(new Date().getTime());
        code = code.substring(0,2)+"."+code.substring(2);
    }
    qqhq.get(api,function(response){
        if(response){
            let result = response;
            result = result.replace("min_data_"+code.replace(".","")+"=","");
            result = JSON.parse(result);
            console.log(result);
            let data = result.data[code].data.data;
            let date = result.data[code].data.date;
            let list = [];
            data.forEach(item=>{
                let r = item.split(" ");

                let low = date+","+item.replaceAll(" ",",");
                list.push(low);
            });
            console.log(list);
            success(list);
        }else{
            fail(response);
        }
    },function(error){
        fail(error);
    });
}

qqhq.getFdayLine = function(code,success,fail){
    let api = "https://web.ifzq.gtimg.cn/appstock/app/day/query?_var=fdays_data_"+code+"&code="+code+"&r=0."+(new Date().getTime());
    if(code.startsWith("us")){
        api = "https://web.ifzq.gtimg.cn/appstock/app/dayus/query?_var=fdays_data_"+code+"&code="+code.substring(0,2)+"."+code.substring(2)+"&r=0."+(new Date().getTime());
        code = code.substring(0,2)+"."+code.substring(2);
    }
    qqhq.get(api,function(response){
        if(response){
            let result = response;
            result = result.replace("fdays_data_"+code.replace(".","")+"=","");
            result = JSON.parse(result);
            console.log(result);
            let data = result.data[code].data;
            let prec = 0;
            let flist = [];
            data.reverse();
            data.forEach(element=>{
                let d = element.data;
                let date = element.date;
                prec = element.prec;
                // let list = [];
                d.forEach(item=>{
                    let r = item.split(" ");
                    let low = date+","+item.replaceAll(" ",",");
                    // list.push(low);
                    flist.push(low);
                });
                
                // console.log(list);
            });
            //flist.reverse();
            success({data:flist,lastClose:prec});
        }else{
            fail(response);
        }
    },function(error){
        fail(error);
    });
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
qqhq.getLine = function(code,cycle,startDate,endDate,pageSize,fqType,success,fail){
    let api = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_"+cycle+fqType+"&param="+code+","+cycle+","+startDate+","+endDate+","+pageSize+","+fqType+"&r=0.36592503777267116"+(new Date().getTime());
    if(code.startsWith("us")){
        code = code.substring(0,2)+"."+code.substring(2);
        api = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_"+cycle+fqType+"&param="+code+","+cycle+","+startDate+","+endDate+","+pageSize+","+fqType+"&r=0.36592503777267116"+(new Date().getTime());
    }
    
    qqhq.get(api,function(response){
        if(response){
            let result = response;
            result = result.replace("kline_"+cycle+fqType+"=","");
            result = JSON.parse(result);
            console.log(result);
            let data = result.data[code][cycle];
            let flist = [];
            data.forEach(element=>{
                let d = element;
                let r = d[0]+","+d[1]+","+d[3]+","+d[4]+","+d[2]+","+d[5]+","+d[8];
                r = r.replaceAll("-","");
                // list.push(low);
                flist.push(r);
                
                // console.log(list);
            });
            //flist.reverse();
            success(flist);
        }else{
            fail(response);
        }
    },function(error){
        fail(error);
    });
}

qqhq.getMinLine = function(code,cycle,pageSize,success,fail){
    
    if(code.startsWith("us")){
        code = code.substring(0,2)+"."+code.substring(2);
    }
    let api = "https://ifzq.gtimg.cn/appstock/app/kline/mkline?param="+code+","+cycle+",,"+pageSize+"&_var="+cycle+"_today&r=0.36592503777267116"+(new Date().getTime());
    
    qqhq.get(api,function(response){
        if(response){
            let result = response;
            result = result.replace(cycle+"_today=","");
            result = JSON.parse(result);
            console.log(result);
            let data = result.data[code][cycle];
            let flist = [];
            data.forEach(element=>{
                let d = element;
                let r = d[0].substring(0,8)+","+d[0].substring(8)+","+d[1]+","+d[3]+","+d[4]+","+d[2]+","+d[5]+","+d[7];
                r = r.replaceAll("-","");
                // list.push(low);
                flist.push(r);
                
                // console.log(list);
            });
            //flist.reverse();
            success(flist);
        }else{
            fail(response);
        }
    },function(error){
        fail(error);
    });
}

qqhq.get = function(url,success,fail){
    var xmlHttp = null;
    if(window.XMLHttpRequest){
        xmlHttp = new XMLHttpRequest;
    }else if(window.ActiveXObject){
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    if(xmlHttp == null){
        alert("浏览器不支持xmlHttp");
        return;
    }
    var httpMethod = "GET";
    var async = true;
    if(httpMethod=="POST"){
        var data = {};
        var requestData = '';
        for(var key in data){
            requestData = requestData + key + "=" + data[key] + "&";
        }
        if(requestData == ''){
            requestData = '';
        }else{
            requestData = requestData.subString(0,requestData.length - 1);
        }
    }
    xmlHttp.onreadystatechange = function(){
        if(xmlHttp.readyState == 4){
            if(xmlHttp.status == 200){
                if(typeof(success)=="function")
                success(xmlHttp.responseText);
            }else{
                //请求失败的回调函数
                if(typeof(fail)=="function") fail();
            }
        }
    }
    //请求接口
    if(httpMethod == 'GET'){
        xmlHttp.open("GET",url,async);
        xmlHttp.send(null);
    }else if(httpMethod == "POST"){
        xmlHttp.open("POST",url,async);
        xmlHttp.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
        xmlHttp.send(requestData);
    }
}
