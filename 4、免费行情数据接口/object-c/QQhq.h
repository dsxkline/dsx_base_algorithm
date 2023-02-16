//
//  QQhq.h
//  dsxkline_iphone
//
//  Created by ming feng on 2022/5/11.
//

#import <Foundation/Foundation.h>
#import "HqModel.h"
NS_ASSUME_NONNULL_BEGIN

@interface QQhq : NSObject

/**
 * 请求第三方实时行情
 * @param code 股票代码
 * @param success 成功
 * @param fail 失败
 * 0: 未知 1: 名字 2: 代码 3: 当前价格 4: 昨收 5: 今开 6: 成交量（手） 7: 外盘 8: 内盘 9: 买一 10: 买一量（手） 11-18: 买二 买五 19: 卖一 20: 卖一量 21-28: 卖二 卖五 29: 最近逐笔成交 30: 时间 31: 涨跌 32: 涨跌% 33: 最高 34: 最低 35: 价格/成交量（手）/成交额 36: 成交量（手） 37: 成交额（万） 38: 换手率 39: 市盈率 40: 41: 最高 42: 最低 43: 振幅 44: 流通市值 45: 总市值 46: 市净率 47: 涨停价 48: 跌停价
 */
+(void)getQuoteWithCode:(NSString*)code success:(void(^)(NSMutableArray *data))success fail:(void(^)(NSError * _Nullable error))fail;
+(void)getTimeLineWithCode:(NSString*)code success:(void(^)(NSMutableArray *data))success fail:(void(^)(NSError * _Nullable error))fail;
+(void)getFdayLineWithCode:(NSString*)code success:(void(^)(NSMutableDictionary *data))success fail:(void(^)(NSError * _Nullable error))fail;
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

+(void)getKLine:(NSString*)code cycle:(NSString*)cycle startDate:(NSString*)startDate endDate:(NSString*)endDate pageSize:(int)pageSize fqType:(NSString*)fqType success:(void(^)(NSMutableArray *data))success fail:(void(^)(NSError * _Nullable error))fail;

+(void)getMinLine:(NSString*)code cycle:(NSString*)cycle pageSize:(int)pageSize fqType:(NSString*)fqType success:(void(^)(NSMutableArray *data))success fail:(void(^)(NSError * _Nullable error))fail;
@end

NS_ASSUME_NONNULL_END
