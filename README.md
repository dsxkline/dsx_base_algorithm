# 量化相关的一些基础算法
  就是整理一些量化相关的基础算法，供刚入坑的朋友参考学习，主要是以学习为主，写的不对的地方还望多指导指导。

## 1、K线周期转换算法
通过时间分组算法转换k线周期

即通过对时间的周期提取分组，同周期K线归类为一组，再计算即可得到目标周期K线数据

https://github.com/dsxkline/dsx_base_algorithm/tree/main/K线周期转换算法
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
        klines = self.klines.copy()
        ...
        # k线滚动缓存
        last_klines = []
        # 分组标识
        last_group = None
        # 保存转换结果
        new_klines = []
        for item in klines:
            # 分组提取
            if not m: group_name = get_date_group(item[0])
            # 分钟线提取
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
```

