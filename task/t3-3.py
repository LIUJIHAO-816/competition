# -*-coding:utf-8-*-
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import re
import matplotlib as mpl

df = pd.read_csv('film_log3.csv', delimiter=';', names= \
    ['影片', '首映', '落幕', '公司', '导演', '演员', '类型', '票房', '城市'])  # 电影在每个地区的首映和落幕时间改动了下，不然每周的数据都一样
# print df

# ---------------------------------------------------分隔符转换----------------------------------------------------------
sy = []
for i in range(len(df['首映'].values)):
    z = df['首映'].values[i].split('.')  # 分隔日期  从‘xxxx.xx.xx ’格式换成xxxx-xx-xx
    sy.append(z[0] + '-' + z[1] + '-' + z[2])
# print sy
df['首映'] = sy

su = []
for i in range(len(df['落幕'].values)):
    z = df['落幕'].values[i].split('.')  # 分隔日期  从‘xxxx.xx.xx ’格式换成xxxx-xx-xx
    su.append(z[0] + '-' + z[1] + '-' + z[2])
# print su
df['落幕'] = su

so = []
for i in range(len(df['票房'].values)):
    z = df['票房'].values[i].strip('票房（万）')  # 原票房数据是str类型，转换成float类型，并把前面的‘票房（万）’去掉
    so.append(float(z))
# print so
df['票房'] = so

# ---------------------------------------------------计算相隔天数----------------------------------------------------------

df['上映天数'] = pd.to_datetime(df['落幕']) - pd.to_datetime(df['首映'])
day = df['上映天数'].to_string()  # 全部转换成字符串类型
fd = re.findall('\s+(\d+)\s\w+', day)  # 提取里面的数字
fs = []
for i in fd:
    fs.append(int(i.encode('utf-8')) + 1)  # 将数字转换成int类型,因为‘落幕-首映’只是相隔的时间，还要加上1天才是上映天数
# print fs
df['上映天数'] = fs
print df

# ---------------------------------------------------计算日平均票房并groupby---------------------------------------------



df['日平均票房'] = df['票房'] / df['上映天数']
print df
zz = df.groupby(['影片', '城市', '首映', '落幕', '上映天数']).sum()['日平均票房'].drop_duplicates()  # 这里不知道用不用删除重复数据
print zz

# --------------------------------假设三部影片分别为《一路惊喜》,《万物生长》,《冲上云霄》-------------------------------

zz1 = zz[['《一路惊喜》', '《万物生长》', '《冲上云霄》']]  # 首先查出最小的放映日期，然后合并各个地区的票房，因为日期不同，所以每周的票房也不同
print zz1

# --------------------------------最小的放映日期-----------------------------

o1 = zz1['《冲上云霄》'].index[0][1]  # 将第一个首映赋值为o1，‘zz1['《冲上云霄》'].index[0][1]’为第一个首映日期
for i in range(len(zz1['《冲上云霄》'].values)):  # for循环zz1['《冲上云霄》'].values的长度
    if pd.to_datetime(zz1['《冲上云霄》'].index[i][1]) > pd.to_datetime(o1):  # 判断第i个首映日期是否大于o1,也就是判断第i个首映日期是否大于第一个首映日期
        o1 = o1  # ,是的话o1不变
    if pd.to_datetime(zz1['《冲上云霄》'].index[i][1]) < pd.to_datetime(o1):  # 判断第i个首映日期是否大于o1,也就是判断第i个首映日期是否大于第一个首映日期
        o1 = pd.to_datetime(zz1['《冲上云霄》'].index[i][1])  # 不是的话把小于o1的日期赋值给o1,最后得出最小日期
print o1

# --------------------------------最大的结映日期-----------------------------

o2 = zz1['《冲上云霄》'].index[0][2]  # 这里和上面相反，‘zz1['《冲上云霄》'].index[0][2]’为第一个落幕日期
for i in range(len(zz1['《冲上云霄》'].values)):
    if pd.to_datetime(zz1['《冲上云霄》'].index[i][2]) > pd.to_datetime(o2):
        o2 = pd.to_datetime(zz1['《冲上云霄》'].index[i][2])
    if pd.to_datetime(zz1['《冲上云霄》'].index[i][2]) < pd.to_datetime(o2):
        o2 = o2
print o2

# --------------------------------算出每个地区每天的票房后合计，做成日期片票房表格---------------------------------------

pp = {}
for i in range(len(zz1['《冲上云霄》'].values)):
    days = pd.to_datetime(zz1['《冲上云霄》'].index[i][2]) - pd.to_datetime(zz1['《冲上云霄》'].index[i][1])  # 算出每个地区落幕和首映的时间差
    # print days.days+1
    for t in range(days.days + 1):  # days.days+1是上映日期，落幕和首映的时间差+1天
        # print pd.to_datetime(zz1['《冲上云霄》'].index[i][1])+datetime.timedelta(days=t)
        f = pd.to_datetime(zz1['《冲上云霄》'].index[i][1]) + datetime.timedelta(days=t)  # 把每个地区的上映天数以每天的形式呈现出来
        if pp.has_key(f):
            pp[f] += zz1['《冲上云霄》'].values[i]  # 如果有地区的上映日相同则票房相加
        else:
            pp[f] = zz1['《冲上云霄》'].values[i]  # 没有的话则不变
# print pp

# print zz1['《冲上云霄》'].values[0]
ppp = pd.DataFrame(pp.items(), columns=['日期', '票房'])  # 将pp做成二维表单
# print ppp
ppp = ppp.sort_values('日期')  # 按日期从大到小排序
ppp = ppp.reset_index()  # 重置索引
ppp = ppp.drop('index', axis=1)  # 删除最开始的索引
# print ppp
zhoub = []
zhou = []
sum = 0.0
for i in range(len(ppp['票房'].values)):  # 因为题目要求‘若某部电影从某月2日开始上映，则从当月2日到8日为其第一周票房，9日至15日为其第2周票房，以此类推。’
    sum += ppp['票房'].values[i]  # sum为每天票房的相加
    if (i % 7 == 6):  # 如果到了第七天
        zhoub.append(sum)  # 则把sum放到zhoub中
        zhou.append(i / 7 + 1)  # 说明这是第几周
        sum = 0.0  # 再把sum清零进行下一次循环
    if (i == len(ppp['票房'].values) - 1) & (i % 7 != 6):  # 如果到了最后一次循环,并且最后循环‘i % 7 != 6’
        zhoub.append(sum)  # 则把最后多余的sum放到zhoub中
        zhou.append(i / 7 + 1)  # 说明这是第几周，不满一周按一周显示
# print zhou
# print zhoub

# ---------------------------------------------接下来两部电影的算法和上面的基本类似--------------------------------------
# --------------------------------最小的放映日期-----------------------------

o3 = zz1['《万物生长》'].index[0][1]  # 将第一个首映赋值为o3，‘zz1['《万物生长》'].index[0][1]’为第一个首映日期
for i in range(len(zz1['《万物生长》'].values)):
    if pd.to_datetime(zz1['《万物生长》'].index[i][1]) > pd.to_datetime(o3):
        o3 = o3
    if pd.to_datetime(zz1['《万物生长》'].index[i][1]) < pd.to_datetime(o3):
        o3 = pd.to_datetime(zz1['《万物生长》'].index[i][1])
print o3

# --------------------------------最大的结映日期-----------------------------

o4 = zz1['《万物生长》'].index[0][2]  # 将第一个落幕赋值为o4，‘zz1['《万物生长》'].index[0][2]’为第一个落幕日期
for i in range(len(zz1['《万物生长》'].values)):
    if pd.to_datetime(zz1['《万物生长》'].index[i][2]) > pd.to_datetime(o4):
        o4 = pd.to_datetime(zz1['《万物生长》'].index[i][2])
    if pd.to_datetime(zz1['《万物生长》'].index[i][2]) < pd.to_datetime(o4):
        o4 = o4
print o4

# --------------------------------算出每个地区每天的票房后合计，做成日期片票房表格---------------------------------------

pp2 = {}
for i in range(len(zz1['《万物生长》'].values)):
    days = pd.to_datetime(zz1['《万物生长》'].index[i][2]) - pd.to_datetime(zz1['《万物生长》'].index[i][1])  # 算出每个地区落幕和首映的时间差
    # print days.days+1
    for t in range(days.days + 1):  # days.days+1是上映日期，落幕和首映的时间差+1天
        # print pd.to_datetime(zz1['《万物生长》'].index[i][1])+datetime.timedelta(days=t)
        f = pd.to_datetime(zz1['《万物生长》'].index[i][1]) + datetime.timedelta(days=t)  # 把每个地区的上映天数以每天的形式呈现出来
        if pp2.has_key(f):
            pp2[f] += zz1['《万物生长》'].values[i]  # 如果有地区的上映日相同则票房相加
        else:
            pp2[f] = zz1['《万物生长》'].values[i]  # 没有的话则不变
# print pp2

# print zz1['《万物生长》'].values[0]
ppp2 = pd.DataFrame(pp2.items(), columns=['日期', '票房'])  # 将pp2做成二维表单
# print ppp2
ppp2 = ppp2.sort_values('日期')  # 按日期从大到小排序
ppp2 = ppp2.reset_index()  # 重置索引
ppp2 = ppp2.drop('index', axis=1)  # 删除最开始的索引
# print ppp2
zhoub2 = []
zhou2 = []
sum = 0.0
for i in range(len(ppp2['票房'].values)):  # 因为题目要求‘若某部电影从某月2日开始上映，则从当月2日到8日为其第一周票房，9日至15日为其第2周票房，以此类推。’
    sum += ppp2['票房'].values[i]  # sum为每天票房的相加
    if (i % 7 == 6):  # 如果到了第七天
        zhoub2.append(sum)  # 则把sum放到zhoub中
        zhou2.append(i / 7 + 1)  # 说明这是第几周
        sum = 0.0  # 再把sum清零进行下一次循环
    if i == len(ppp2['票房'].values) - 1 & (i % 7 != 6):  # 如果到了最后一次循环,并且最后循环‘i % 7 != 6’
        zhoub2.append(sum)  # 则把最后多余的sum放到zhoub中
        zhou2.append(i / 7 + 1)  # 说明这是第几周，不满一周按一周显示
# print zhou2
# print zhoub2




# -----------------------------------------------------------------------------------------------------------------------
# --------------------------------最小的放映日期-----------------------------

o5 = zz1['《一路惊喜》'].index[0][1]  # 将第一个首映赋值为o5，‘zz1['《一路惊喜》'].index[0][1]’为第一个首映日期
for i in range(len(zz1['《一路惊喜》'].values)):
    if pd.to_datetime(zz1['《一路惊喜》'].index[i][1]) > pd.to_datetime(o5):
        o5 = o5
    if pd.to_datetime(zz1['《一路惊喜》'].index[i][1]) < pd.to_datetime(o5):
        o5 = pd.to_datetime(zz1['《一路惊喜》'].index[i][1])
print o5

# --------------------------------最大的结映日期-----------------------------

o6 = zz1['《一路惊喜》'].index[0][2]  # 将第一个落幕赋值为o6，‘zz1['《一路惊喜》'].index[0][2]’为第一个落幕日期
for i in range(len(zz1['《一路惊喜》'].values)):
    if pd.to_datetime(zz1['《一路惊喜》'].index[i][2]) > pd.to_datetime(o6):
        o6 = pd.to_datetime(zz1['《一路惊喜》'].index[i][2])
    if pd.to_datetime(zz1['《一路惊喜》'].index[i][2]) < pd.to_datetime(o6):
        o6 = o6
print o6

# --------------------------------算出每个地区每天的票房后合计，做成日期片票房表格---------------------------------------

pp3 = {}
for i in range(len(zz1['《一路惊喜》'].values)):
    days = pd.to_datetime(zz1['《一路惊喜》'].index[i][2]) - pd.to_datetime(zz1['《一路惊喜》'].index[i][1])  # 算出每个地区落幕和首映的时间差
    for t in range(days.days + 1):  # days.days+1是上映日期，落幕和首映的时间差+1天
        f = pd.to_datetime(zz1['《一路惊喜》'].index[i][1]) + datetime.timedelta(days=t)  # 把每个地区的上映天数以每天的形式呈现出来
        if pp3.has_key(f):
            pp3[f] += zz1['《一路惊喜》'].values[i]  # 如果有地区的上映日相同则票房相加
        else:
            pp3[f] = zz1['《一路惊喜》'].values[i]  # 没有的话则不变
# print pp3

ppp3 = pd.DataFrame(pp3.items(), columns=['日期', '票房'])  # 将pp3做成二维表单
# print ppp3
ppp3 = ppp3.sort_values('日期')  # 按日期从大到小排序
ppp3 = ppp3.reset_index()  # 重置索引
ppp3 = ppp3.drop('index', axis=1)  # 删除最开始的索引
# print ppp3
zhoub3 = []
zhou3 = []
sum = 0.0
for i in range(len(ppp3['票房'].values)):  # 因为题目要求‘若某部电影从某月2日开始上映，则从当月2日到8日为其第一周票房，9日至15日为其第2周票房，以此类推。’
    sum += ppp3['票房'].values[i]  # sum为每天票房的相加
    if (i % 7 == 6):  # 如果到了第七天
        zhoub3.append(sum)  # 则把sum放到zhoub中
        zhou3.append(i / 7 + 1)  # 说明这是第几周
        sum = 0.0  # 再把sum清零进行下一次循环
    if i == len(ppp3['票房'].values) - 1 & (i % 7 != 6):  # 如果到了最后一次循环,并且最后循环‘i % 7 != 6’
        zhoub3.append(sum)  # 则把最后多余的sum放到zhoub中
        zhou3.append(i / 7 + 1)  # 说明这是第几周，不满一周按一周显示
print zhou3
print zhoub3

# ---------------------------------------------------绘制图表----------------------------------------------------------
# zhfont = mpl.font_manager.FontProperties(fname='/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf')
mpl.rcParams['font.sans-serif'] = ['simhei']
plt.figure()
plt.plot(zhou, zhoub, 'y--^', label=u'《冲上云霄》')  # 将前面的zhou作为x轴,zhoub作为y轴
plt.plot(zhou2, zhoub2, 'r--o', label=u'《万物生长》')  # 将前面的zhou2作为x轴,zhoub2作为y轴
plt.plot(zhou3, zhoub3, 'b--*', label=u'《一路惊喜》')  # 将前面的zhou3作为x轴,zhoub3作为y轴
plt.xticks(zhou)
plt.xlabel(u'周')
plt.ylabel(u'票房（万）')
plt.title(u'电影周票房图')
plt.legend()
plt.grid('on')
plt.show()