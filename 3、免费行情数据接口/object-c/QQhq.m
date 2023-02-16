//
//  QQhq.m
//  dsxkline_iphone
//
//  Created by ming feng on 2022/5/11.
//

#import "QQhq.h"


@implementation QQhq


/**
 * 请求第三方实时行情
 * @param code 股票代码
 * @param success 成功
 * @param fail 失败
 * 0: 未知 1: 名字 2: 代码 3: 当前价格 4: 昨收 5: 今开 6: 成交量（手） 7: 外盘 8: 内盘 9: 买一 10: 买一量（手） 11-18: 买二 买五 19: 卖一 20: 卖一量 21-28: 卖二 卖五 29: 最近逐笔成交 30: 时间 31: 涨跌 32: 涨跌% 33: 最高 34: 最低 35: 价格/成交量（手）/成交额 36: 成交量（手） 37: 成交额（万） 38: 换手率 39: 市盈率 40: 41: 最高 42: 最低 43: 振幅 44: 流通市值 45: 总市值 46: 市净率 47: 涨停价 48: 跌停价
 */
+(void)getQuoteWithCode:(NSString*)code success:(void(^)(NSMutableArray *data))success fail:(void(^)(NSError * _Nullable error))fail{
    NSString *api = [NSString stringWithFormat:@"http://qt.gtimg.cn/q=%@",code];
    NSString *resultStart = @"v_{code}=";
    NSString *resultEnd = @";";
    [self get:api success:^(NSString *data) {
        if(data==nil) {
            success(nil);
            return;
        }
        NSMutableArray *list = [NSMutableArray new];
        NSArray *dataList = [data componentsSeparatedByString:resultEnd];
        NSArray *codes = [code componentsSeparatedByString:@","];
        for(int i=0;i<dataList.count;i++){
            NSString *item = dataList[i];
            item = [item stringByReplacingOccurrencesOfString:[resultStart stringByReplacingOccurrencesOfString:@"{code}" withString:code.lowercaseString] withString:@""];
            NSArray *rs = [item componentsSeparatedByString:@"~"];
            if(rs.count<32) continue;
            HqModel *model = [HqModel new];
            model.name = rs[1];
            model.code = codes[i];
            model.price = rs[3];
            model.lastClose = rs[4];
            model.open = rs[5];
            model.high = rs[33];
            model.low = rs[34];
            model.vol = rs[6];
            model.volAmount = rs[37];
            model.date = [rs[30] substringToIndex:8];
            model.time = [rs[30] substringFromIndex:8];
            model.change = rs[31];
            model.changeRatio = rs[32];
            [list addObject:model];
        }
        if (success) {
            success(list);
        }
            
    } fail:^(NSError * _Nullable error) {
        if (fail) {
            fail(error);
        }
    }];
    
}

///
+(void)getTimeLineWithCode:(NSString*)code success:(void(^)(NSMutableArray *data))success fail:(void(^)(NSError * _Nullable error))fail{
    NSString* api = [NSString stringWithFormat:@"https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_%@&code=%@&r=0.%f",code,code,[[NSDate date] timeIntervalSince1970] ];
    if([[code substringToIndex:2] isEqual:@"us"]){
        NSString *dcode = [NSString stringWithFormat:@"%@.%@",[code substringToIndex:2],[code substringFromIndex:2]];
        api = [NSString stringWithFormat:@"https://web.ifzq.gtimg.cn/appstock/app/minute/query?_var=min_data_%@&code=%@&r=0.%f",code,dcode,[[NSDate date] timeIntervalSince1970] ];
        code = dcode;
    }
    [self get:api success:^(NSString *data) {
        data = [data stringByReplacingOccurrencesOfString:[NSString stringWithFormat:@"min_data_%@=",[code stringByReplacingOccurrencesOfString:@"." withString:@""]] withString:@""];
        id jsonObj = [NSJSONSerialization JSONObjectWithData:[data dataUsingEncoding:NSUTF8StringEncoding] options:NSJSONReadingAllowFragments error:nil];
        NSMutableDictionary *d = [[NSMutableDictionary alloc] initWithDictionary:jsonObj];
        NSDictionary *datas = (NSDictionary*)d[@"data"];
        datas = datas[code];
        datas = datas[@"data"];
        NSString *date = datas[@"date"];
        NSArray *ds = (NSArray*)datas[@"data"];
        NSMutableArray *list = [NSMutableArray new];
        for (NSString*item in ds) {
            NSString *row = [NSString stringWithFormat:@"%@,%@",date,[item stringByReplacingOccurrencesOfString:@" " withString:@","]];
            [list addObject:row];
        }
        if (success) {
            success(list);
        }
    } fail:^(NSError * _Nullable error) {
        
    }];
}

+(void)getFdayLineWithCode:(NSString*)code success:(void(^)(NSMutableDictionary *data))success fail:(void(^)(NSError * _Nullable error))fail{
    NSString* api = [NSString stringWithFormat:@"https://web.ifzq.gtimg.cn/appstock/app/day/query?_var=fdays_data_%@&code=%@&r=0.%f",code,code,[[NSDate date] timeIntervalSince1970] ];
    if([[code substringToIndex:2] isEqual:@"us"]){
        NSString *dcode = [NSString stringWithFormat:@"%@.%@",[code substringToIndex:2],[code substringFromIndex:2]];
        api = [NSString stringWithFormat:@"https://web.ifzq.gtimg.cn/appstock/app/dayus/query?_var=fdays_data_%@&code=%@&r=0.%f",code,dcode,[[NSDate date] timeIntervalSince1970] ];
        code = dcode;
    }
    [self get:api success:^(NSString *data) {
        data = [data stringByReplacingOccurrencesOfString:[NSString stringWithFormat:@"fdays_data_%@=",[code stringByReplacingOccurrencesOfString:@"." withString:@""]] withString:@""];
        id jsonObj = [NSJSONSerialization JSONObjectWithData:[data dataUsingEncoding:NSUTF8StringEncoding] options:NSJSONReadingAllowFragments error:nil];
        NSMutableDictionary *d = [[NSMutableDictionary alloc] initWithDictionary:jsonObj];
        NSDictionary *datas = (NSDictionary*)d[@"data"];
        NSArray *dds = datas[code][@"data"];
        double prec = 0;
        NSMutableArray *list = [NSMutableArray new];
        for (int i=(int)dds.count-1; i>=0; i--) {
            NSDictionary *element = dds[i];
            NSString *date = element[@"date"];
            prec = [element[@"prec"] doubleValue];
            NSArray *ds = (NSArray*)element[@"data"];
            for (NSString*item in ds) {
                NSString *row = [NSString stringWithFormat:@"%@,%@",date,[item stringByReplacingOccurrencesOfString:@" " withString:@","]];
                [list addObject:row];
            }
        }
        NSMutableDictionary *rd = [NSMutableDictionary new];
        [rd setObject:@(prec) forKey:@"lastClose"];
        [rd setObject:list forKey:@"data"];
        if (success) {
            success(rd);
        }
    } fail:^(NSError * _Nullable error) {
        
    }];
}


/**
 * 获取K线图历史数据
 * @param code 股票代码
 * @param cycle 周期 day，week，month
 * @param startDate 开始日期 默认 空
 * @param endDate 结束日期 默认空
 * @param pageSize 每页大小 默认 320
 * @param fqType 复权类型 前复权=qfq，后复权=hfq
 * @param success 返回列表
 * @param fail 返回出错信息
 */

+(void)getKLine:(NSString*)code cycle:(NSString*)cycle startDate:(NSString*)startDate endDate:(NSString*)endDate pageSize:(int)pageSize fqType:(NSString*)fqType success:(void(^)(NSMutableArray *data))success fail:(void(^)(NSError * _Nullable error))fail{
    NSString* api = [NSString stringWithFormat:@"https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_%@%@&param=%@,%@,%@,%@,%d,%@&r=0.%f",cycle,fqType,code,cycle,startDate,endDate,pageSize,fqType,[[NSDate date] timeIntervalSince1970] ];
    if([[code substringToIndex:2] isEqual:@"us"]){
        NSString *dcode = [NSString stringWithFormat:@"%@.%@",[code substringToIndex:2],[code substringFromIndex:2]];
        api = [NSString stringWithFormat:@"https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_%@%@&param=%@,%@,%@,%@,%d,%@&r=0.%f",cycle,fqType,dcode,cycle,startDate,endDate,pageSize,fqType,[[NSDate date] timeIntervalSince1970] ];
        code = dcode;
    }
    [self get:api success:^(NSString *data) {
        data = [data stringByReplacingOccurrencesOfString:[NSString stringWithFormat:@"kline_%@%@=",cycle,fqType] withString:@""];
        id jsonObj = [NSJSONSerialization JSONObjectWithData:[data dataUsingEncoding:NSUTF8StringEncoding] options:NSJSONReadingAllowFragments error:nil];
        NSMutableDictionary *d = [[NSMutableDictionary alloc] initWithDictionary:jsonObj];
        NSDictionary *datas = (NSDictionary*)d[@"data"];
        datas = datas[code];
        //datas = datas[cycle];
        NSArray *ds = (NSArray*)datas[cycle];
        NSMutableArray *list = [NSMutableArray new];
        for (NSArray*item in ds) {
            NSString *row = [NSString stringWithFormat:@"%@,%@,%@,%@,%@,%@,%@",item[0],item[1],item[3],item[4],item[2],item[5],item[8]];
            row = [row stringByReplacingOccurrencesOfString:@"-" withString:@""];
            [list addObject:row];
        }
        if (success) {
            success(list);
        }
    } fail:^(NSError * _Nullable error) {
        
    }];
}

+(void)getMinLine:(NSString*)code cycle:(NSString*)cycle pageSize:(int)pageSize fqType:(NSString*)fqType success:(void(^)(NSMutableArray *data))success fail:(void(^)(NSError * _Nullable error))fail{
    
    NSString* api = [NSString stringWithFormat:@"https://ifzq.gtimg.cn/appstock/app/kline/mkline?_var=%@_today&param=%@,%@,,%d&r=0.%f",cycle,code,cycle,pageSize,[[NSDate date] timeIntervalSince1970] ];
    if([[code substringToIndex:2] isEqual:@"us"]){
        NSString *dcode = [NSString stringWithFormat:@"%@.%@",[code substringToIndex:2],[code substringFromIndex:2]];
        api = [NSString stringWithFormat:@"https://ifzq.gtimg.cn/appstock/app/kline/mkline?_var=%@_today&param=%@,%@,,%d&r=0.%f",cycle,code,cycle,pageSize,[[NSDate date] timeIntervalSince1970] ];
        code = dcode;
    }
    [self get:api success:^(NSString *data) {
        data = [data stringByReplacingOccurrencesOfString:[NSString stringWithFormat:@"%@_today=",cycle] withString:@""];
        id jsonObj = [NSJSONSerialization JSONObjectWithData:[data dataUsingEncoding:NSUTF8StringEncoding] options:NSJSONReadingAllowFragments error:nil];
        NSMutableDictionary *d = [[NSMutableDictionary alloc] initWithDictionary:jsonObj];
        NSDictionary *datas = (NSDictionary*)d[@"data"];
        datas = datas[code];
        NSArray *ds = (NSArray*)datas[cycle];
        NSMutableArray *list = [NSMutableArray new];
        for (NSArray*item in ds) {
            NSString *date = [item[0] substringToIndex:8];
            NSString *time = [item[0] substringFromIndex:8];
            NSString *row = [NSString stringWithFormat:@"%@,%@,%@,%@,%@,%@,%@,%@",date,time,item[1],item[3],item[4],item[2],item[5],item[7]];
            row = [row stringByReplacingOccurrencesOfString:@"-" withString:@""];
            [list addObject:row];
        }
        if (success) {
            success(list);
        }
    } fail:^(NSError * _Nullable error) {
        
    }];
}

// 请求
+ (void)get:(NSString*)url success:(void(^)(NSString *data))success fail:(void(^)(NSError * _Nullable error))fail{
    NSURL *uri = [NSURL URLWithString:url];
    NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:uri];
    [request setHTTPMethod:@"GET"];
    [request setTimeoutInterval:10];
    NSURLSession *session = [NSURLSession sharedSession];
    NSStringEncoding gbk =CFStringConvertEncodingToNSStringEncoding(kCFStringEncodingGB_18030_2000);
    
    NSURLSessionDataTask *task = [session dataTaskWithRequest:request completionHandler:^(NSData * _Nullable data, NSURLResponse * _Nullable response, NSError * _Nullable error) {
        
        dispatch_async(dispatch_get_main_queue(), ^{
            if (error) {
                NSLog(@"请求错误：%@", error);
                if (fail) {
                    fail(error);
                }
                return;
            }else{
                NSString *d = [[NSString alloc] initWithData:data encoding:gbk];
                //NSLog(@"结果：\n%@", dataString);
//                id jsonObj = [NSJSONSerialization JSONObjectWithData:data options:NSJSONReadingAllowFragments error:nil];
//                NSMutableDictionary *d = [[NSMutableDictionary alloc] initWithDictionary:jsonObj];
                if(success)success(d);
            }
        });
        
        
    }];
    // 执行请求任务

    [task resume];
}

@end
