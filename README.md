# 量化相关的一些基础算法
  就是整理一些量化相关的基础算法，供刚入坑的朋友参考学习，主要是以学习为主，写的不对的地方还望多指导指导。

## 1、K线周期转换算法
通过时间分组算法转换k线周期

即通过对时间的周期提取分组，同周期K线归类为一组，再计算即可得到目标周期K线数据

https://github.com/dsxkline/dsx_base_algorithm/tree/main/K线周期转换算法

### 流程图

![alt K线转换周期算法流程图](https://raw.githubusercontent.com/dsxkline/dsx_base_algorithm/main/K%E7%BA%BF%E5%91%A8%E6%9C%9F%E8%BD%AC%E6%8D%A2%E7%AE%97%E6%B3%95/K%E7%BA%BF%E5%91%A8%E6%9C%9F%E8%BD%AC%E6%8D%A2%E5%9F%BA%E7%A1%80%E7%AE%97%E6%B3%95%E6%B5%81%E7%A8%8B%E5%9B%BE%20.png)

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

