# 量化相关的一些基础算法
  就是整理一些量化相关的基础算法，供刚入坑的朋友参考学习，主要是以学习为主，写的不对的地方还望多指导指导。

## 1、K线周期转换算法

通过时间分组算法转换k线周期

即通过对时间的周期提取分组，同周期K线归类为一组，再合并计算即可得到目标周期K线数据

### 流程图

![alt K线转换周期算法流程图](https://raw.githubusercontent.com/dsxkline/dsx_base_algorithm/main/1%E3%80%81K%E7%BA%BF%E5%91%A8%E6%9C%9F%E8%BD%AC%E6%8D%A2%E7%AE%97%E6%B3%95/K%E7%BA%BF%E5%91%A8%E6%9C%9F%E8%BD%AC%E6%8D%A2%E5%9F%BA%E7%A1%80%E7%AE%97%E6%B3%95%E6%B5%81%E7%A8%8B%E5%9B%BE%20.png)

### 核心代码


```python

# 核心代码片段
def converkline_to(self,cycle:CYCLE):
        """通过时间段分组算法转换k线周期
        通过对日期的周期提取分组，同周期K线归类为一组，再计算即可得到目标周期K线数据

        日线数据 [[date,open,high,low,close,vol,amount],...]
        分钟数据 [[datetime,open,high,low,close,vol,amount],...]

        Args:
            cycle (CYCLE): 周期枚举
        Returns:
            list: 转换后的k线
        """
        ...
        # k线滚动缓存
        last_klines = []
        # 分组标识
        last_group = None
        # 保存转换结果
        new_klines = []
        # 滚动开始
        for item in klines:
            # 分组提取
            if not m: group_name = get_date_group(item[0])
            else: group_name = self.get_date_min_group(item[0],m)
            if last_group == None: last_group = group_name
            # 分组合并
            if group_name==last_group:
                # 始终合并上一个周期
                last_klines = self.merge_group_klines([last_klines]+[item])
            else:
                # 保存上个周期
                new_klines.append(last_klines)
                # 传递新周期数据
                last_klines = item
                # 传递新周期分组
                last_group = group_name
            # 终止
            if item == klines[-1]:
                if group_name==last_group:
                    # 保存新周期
                    new_klines.append(last_klines)

        return new_klines
```

## 2、K线涨跌幅复权算法

算法简单直接：在每次除权发生后， 根据除权价和前一收盘价计算一个比率，称为除权因子；把截止到计算日历次的除权因子连乘，即为截止日的累积除权因子。计算前复权价，则以价格乘上累积除权因子；向后复权，则价格除以累积除权因子。

根据涨跌幅复权法，首先要计算除权因子：

**除权收盘价** = 除权除息价 = (股权登记日的收盘价-每股所分红利现金额+配股价×每股配股数)÷(1+每股送红股数+每股配股数+每股转增股数)

**除权因子** = 除权收盘价 / 除权登记日收盘价

```
后复权上市首日后除权因子为1，前复权最近一次除权除息日后的交易日前复权因子为1。
除权会不断发生，所以需要计算出累积除权因子
累积除权因子 = 上一个除权因子 * (除权收盘价 / 除权登记日收盘价)
```
**前复权因子** = 累积除权因子

**后复权因子** = 1.0 / 累积除权因子

``` 
因为后复权价=价格 / 累积除权因子，所以后复权因子=1.0/累积除权因子，这样就能用后复权因子*价格来计算每个k线的后复权价格了 
```

**前复权价格** = 价格 * 前复权因子

**后复权价格** = 价格 * 后复权因子

### 核心代码

``` python
    # 除权除息价=(股权登记日的收盘价-每股所分红利现金额+配股价×每股配股数)÷(1+每股送红股数+每股配股数+每股转增股数);
    price = (close - per_cash_div/10.0 + allo_price * (per_ten_allo/10.0) ) / (1.0+(per_ten_send/10.0) + (per_ten_allo/10.0) + (per_ten_incr/10.0) )
    # 通过上面的计算得到除权除息价，也就是计算出了除权除息日的前收价,除权登记日的除权收盘价，用除权登记日的收盘价除以除权价得到单次除权因子；
    # 除权因子= 除权收盘价 / 除权登记日收盘价
    right_factor = price / close
```