#coding:utf-8
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import re
import matplotlib as mpl

df=pd.read_csv('film_log3.csv', delimiter=';',names=\
    ['影片','首映','落幕','公司','导演','演员','类型','票房','城市'])
# print df

#---------------------------------------------------分隔符转换----------------------------------------------------------
sy = []
for i in range(len(df['首映'].values)):
     z = df['首映'].values[i].split('.')  # 分隔日期  从‘xxxx.xx.xx ’格式换成xxxx-xx-xx
     sy.append(z[0]+'-'+z[1]+'-'+z[2])
# print sy
df['首映'] = sy

su = []
for i in range(len(df['落幕'].values)):
     z = df['落幕'].values[i].split('.')    # 分隔日期  从‘xxxx.xx.xx ’格式换成xxxx-xx-xx
     su.append(z[0]+'-'+z[1]+'-'+z[2])
# print su
df['落幕'] = su

so = []
for i in range(len(df['票房'].values)):
     z = df['票房'].values[i].strip('票房（万）')     # 原票房数据是str类型，转换成float类型，并把前面的‘票房（万）’去掉
     so.append(float(z))
# print so
df['票房'] = so


#---------------------------------------------------计算相隔天数----------------------------------------------------------


df['上映天数'] = pd.to_datetime(df['落幕']) - pd.to_datetime(df['首映'])
day = df['上映天数'].to_string()   #全部转换成字符串类型
fd = re.findall('\s+(\d+)\s\w+',day)   #提取里面的数字
fs = []
for i in fd:
    fs.append(int(i.encode('utf-8'))+1)    #将数字转换成int类型,因为‘落幕-首映’只是相隔的时间，还要加上1天才是上映天数
#print fs
df['上映天数'] = fs
# print df

#---------------------------------------------------计算日平均票房并groupby---------------------------------------------



df['日平均票房'] = df['票房']/df['上映天数']
# print df
zz = df.groupby(['城市','影片','首映','落幕','日平均票房']).sum()['票房']
# print zz


#---------------在所有城市中筛选出首映在2016-1-1~2016-4-1之间，或者首映小于2016-1-1但是落幕却大于2016-1-1的电影---------
uu = []
for i in range(len(df['首映'].values)):
    if pd.to_datetime('2016-4-1')>pd.to_datetime(df['首映'].values[i])>pd.to_datetime('2016-1-1'):
        uu.append(df.ix[i])
    elif (pd.to_datetime(df['首映'].values[i])<pd.to_datetime('2016-1-1'))&(pd.to_datetime(df['落幕'].values[i])>pd.to_datetime('2016-1-1')):
        uu.append(df.ix[i])
#print len(uu)


#-------------------------------------------把筛选的结果做成二维表单并groupby-------------------------------------------


ee = pd.DataFrame(uu)
#print ee
yy = ee.groupby(['城市','影片','首映','落幕','日平均票房']).sum()['票房']



#----------------------------------------------假设地区为'上海'，'福州'-------------------------------------------------



yy1 = yy[['上海','福州']]
# print yy1



#-------------------------------------------判断上海2016年1、2、3月票房总收入-------------------------------------------
# 注：题目中的日票房都是日平均票房，(y-(2016-1-1))的天数+1为上映日期
# 思路是：
#     假设x为上海的其中一部电影的首映日期,y为电影的落幕日期
#     那么想要知道电影在2016年1-3月的票房，首先得判定电影上映日属于1-3月中的哪一个月或者哪几个月（如果x和y都在2016年1-3月，并且）
#     （1）如果x小于2016年1月，而y在2016年1-3月中的1月，那么这部电影的票房就是： 一月：‘((y-(2016-1-1))的天数+1)*这部影片的日平均票房’
#     （2）如果x小于2016年1月，而y在2016年1-3月中的2月，那么这部电影的票房就是： 一月：‘(((2016-2-1)-(2016-1-1))的天数)*这部影片的日平均票房’ 二月： ‘((y-(2016-2-1))的天数+1)*这部影片的日平均票房’
#     （3）如果x小于2016年1月，而y在2016年1-3月中的3月，那么这部电影的票房就是： 一月：‘(((2016-2-1)-(2016-1-1))的天数)*这部影片的日平均票房’ 二月： ‘(((2016-3-1)-(2016-2-1))的天数)*这部影片的日平均票房’,三月：‘((y-(2016-3-1))的天数+1)*这部影片的日平均票房’
#     （4）如果x在2016年1-3月中的1月，而y在2016年1-3月中的1月......（后面和前面的后面差不多,也是分一月：加上这个月的票房,二月：加上这个月的票房,三月：加上这个月的票房;这里就省略了）
#     （5）如果x在2016年1-3月中的1月，而y在2016年1-3月中的2月......
#     （6）如果x在2016年1-3月中的1月，而y在2016年1-3月中的3月......
#     （7）如果x在2016年1-3月中的2月，而y在2016年1-3月中的2月......
#     （8）如果x在2016年1-3月中的2月，而y在2016年1-3月中的3月......
#     （9）如果x在2016年1-3月中的3月，而y在2016年1-3月中的3月......
#      最后把所有的一月合并为上海一月放映电影的总票房;二月合并为上海二月放映电影的总票房;三月合并为上海三月放映电影的总票房
# 下面数据中：pd.to_datetime(yy1['上海'].index[i][1])为首映日期，pd.to_datetime(yy1['上海'].index[i][2])为落幕日期，yy1['上海'].index[i][3]为日平均票房


sh1 = []
sh2 = []
sh3 = []
for i in range(len(yy1['上海'].values)):
    if (pd.to_datetime('2016-1-1')>pd.to_datetime(yy1['上海'].index[i][1]))& \
        (pd.to_datetime('2016-2-1') > pd.to_datetime(yy1['上海'].index[i][2]) > pd.to_datetime('2016-1-1')):
        io = pd.to_datetime(yy1['上海'].index[i][2]) - pd.to_datetime('2016-1-1')
        sh1.append((io.days + 1)*yy1['上海'].index[i][3])
    if (pd.to_datetime('2016-1-1') > pd.to_datetime(yy1['上海'].index[i][1])) & \
        (pd.to_datetime('2016-3-1') > pd.to_datetime(yy1['上海'].index[i][2]) > pd.to_datetime('2016-2-1')):
        io1 = pd.to_datetime('2016-2-1') - pd.to_datetime('2016-1-1')
        io2 = pd.to_datetime(yy1['上海'].index[i][2]) - pd.to_datetime('2016-2-1')
        sh1.append(io1.days*yy1['上海'].index[i][3])
        sh2.append((io2.days + 1)*yy1['上海'].index[i][3])
    if (pd.to_datetime('2016-1-1') > pd.to_datetime(yy1['上海'].index[i][1])) & \
        (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['上海'].index[i][2]) > pd.to_datetime('2016-3-1')):
        io1 = pd.to_datetime('2016-2-1') - pd.to_datetime('2016-1-1')
        io2 = pd.to_datetime('2016-3-1') - pd.to_datetime('2016-2-1')
        io3 = pd.to_datetime(yy1['上海'].index[i][2]) - pd.to_datetime('2016-3-1')
        sh1.append(io1.days*yy1['上海'].index[i][3])
        sh2.append(io2.days*yy1['上海'].index[i][3])
        sh3.append((io3.days + 1)*yy1['上海'].index[i][3])

    if (pd.to_datetime('2016-2-1')>pd.to_datetime(yy1['上海'].index[i][1])>pd.to_datetime('2016-1-1'))& \
        (pd.to_datetime('2016-2-1') > pd.to_datetime(yy1['上海'].index[i][2]) > pd.to_datetime('2016-1-1')):
        io = pd.to_datetime(yy1['上海'].index[i][2]) - pd.to_datetime(yy1['上海'].index[i][1])
        sh1.append((io.days + 1)*yy1['上海'].index[i][3])
    if (pd.to_datetime('2016-2-1') > pd.to_datetime(yy1['上海'].index[i][1]) > pd.to_datetime('2016-1-1')) & \
        (pd.to_datetime('2016-3-1') > pd.to_datetime(yy1['上海'].index[i][2]) > pd.to_datetime('2016-2-1')):
        io1 = pd.to_datetime('2016-2-1') - pd.to_datetime(yy1['上海'].index[i][1])
        io2 = pd.to_datetime(yy1['上海'].index[i][2]) - pd.to_datetime('2016-2-1')
        sh1.append(io1.days*yy1['上海'].index[i][3])
        sh2.append((io2.days + 1)*yy1['上海'].index[i][3])
    if (pd.to_datetime('2016-2-1') > pd.to_datetime(yy1['上海'].index[i][1]) > pd.to_datetime('2016-1-1')) & \
        (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['上海'].index[i][2]) > pd.to_datetime('2016-3-1')):
        io1 = pd.to_datetime('2016-2-1') - pd.to_datetime(yy1['上海'].index[i][1])
        io2 = pd.to_datetime('2016-3-1') - pd.to_datetime('2016-2-1')
        io3 = pd.to_datetime(yy1['上海'].index[i][2]) - pd.to_datetime('2016-3-1')
        sh1.append(io1.days*yy1['上海'].index[i][3])
        sh2.append(io2.days*yy1['上海'].index[i][3])
        sh3.append((io3.days + 1)*yy1['上海'].index[i][3])

    if (pd.to_datetime('2016-3-1')>pd.to_datetime(yy1['上海'].index[i][1])>=pd.to_datetime('2016-2-1'))&\
        (pd.to_datetime('2016-3-1') > pd.to_datetime(yy1['上海'].index[i][2]) > pd.to_datetime('2016-2-1')):
        io = pd.to_datetime(yy1['上海'].index[i][2]) - pd.to_datetime(yy1['上海'].index[i][1])
        sh1.append((io.days + 1)*yy1['上海'].index[i][3])
    if (pd.to_datetime('2016-3-1') > pd.to_datetime(yy1['上海'].index[i][1]) > pd.to_datetime('2016-2-1')) & \
        (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['上海'].index[i][2]) > pd.to_datetime('2016-3-1')):
        io1 = pd.to_datetime('2016-3-1') - pd.to_datetime(yy1['上海'].index[i][1])
        io2 = pd.to_datetime(yy1['上海'].index[i][2]) - pd.to_datetime('2016-3-1')
        sh1.append(io1.days*yy1['上海'].index[i][3])
        sh2.append((io2.days + 1)*yy1['上海'].index[i][3])

    if (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['上海'].index[i][1]) > pd.to_datetime('2016-3-1')) & \
        (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['上海'].index[i][2]) > pd.to_datetime('2016-3-1')):
        io = pd.to_datetime(yy1['上海'].index[i][2]) - pd.to_datetime(yy1['上海'].index[i][1])
        sh1.append((io.days + 1)*yy1['上海'].index[i][3])

# for i in sh1:
#     print i
# print sum(sh1[:])


#-------------------------------------------判断福州2016年1、2、3月票房总收入-------------------------------------------
# 注：因为福州三月份没有电影上映,所以三月份的票房为0
# 思路和上面一样
# 下面数据中：pd.to_datetime(yy1['福州'].index[i][1])为首映日期，pd.to_datetime(yy1['福州'].index[i][2])为落幕日期，yy1['福州'].index[i][3]为日平均票房

fz1 = []
fz2 = []
fz3 = []
for i in range(len(yy1['福州'].values)):
    if (pd.to_datetime('2016-1-1')>pd.to_datetime(yy1['福州'].index[i][1]))& \
        (pd.to_datetime('2016-2-1') > pd.to_datetime(yy1['福州'].index[i][2]) > pd.to_datetime('2016-1-1')):
        io = pd.to_datetime(yy1['福州'].index[i][2]) - pd.to_datetime('2016-1-1')
        fz1.append((io.days + 1)*yy1['福州'].index[i][3])
    if (pd.to_datetime('2016-1-1') > pd.to_datetime(yy1['福州'].index[i][1])) & \
        (pd.to_datetime('2016-3-1') > pd.to_datetime(yy1['福州'].index[i][2]) > pd.to_datetime('2016-2-1')):
        io1 = pd.to_datetime('2016-2-1') - pd.to_datetime('2016-1-1')
        io2 = pd.to_datetime(yy1['福州'].index[i][2]) - pd.to_datetime('2016-2-1')
        fz1.append(io1.days*yy1['福州'].index[i][3] )
        fz2.append((io2.days + 1)*yy1['福州'].index[i][3])
    if (pd.to_datetime('2016-1-1') > pd.to_datetime(yy1['福州'].index[i][1])) & \
        (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['福州'].index[i][2]) > pd.to_datetime('2016-3-1')):
        io1 = pd.to_datetime('2016-2-1') - pd.to_datetime('2016-1-1')
        io2 = pd.to_datetime('2016-3-1') - pd.to_datetime('2016-2-1')
        io3 = pd.to_datetime(yy1['福州'].index[i][2]) - pd.to_datetime('2016-3-1')
        fz1.append(io1.days*yy1['福州'].index[i][3] )
        fz2.append(io2.days*yy1['福州'].index[i][3] )
        fz3.append((io3.days + 1)*yy1['福州'].index[i][3])

    if (pd.to_datetime('2016-2-1')>pd.to_datetime(yy1['福州'].index[i][1])>pd.to_datetime('2016-1-1'))& \
        (pd.to_datetime('2016-2-1') > pd.to_datetime(yy1['福州'].index[i][2]) > pd.to_datetime('2016-1-1')):
        io = pd.to_datetime(yy1['福州'].index[i][2]) - pd.to_datetime(yy1['福州'].index[i][1])
        fz1.append((io1.days +1)*yy1['福州'].index[i][3])
    if (pd.to_datetime('2016-2-1') > pd.to_datetime(yy1['福州'].index[i][1]) > pd.to_datetime('2016-1-1')) & \
        (pd.to_datetime('2016-3-1') > pd.to_datetime(yy1['福州'].index[i][2]) > pd.to_datetime('2016-2-1')):
        io1 = pd.to_datetime('2016-2-1') - pd.to_datetime(yy1['福州'].index[i][1])
        io2 = pd.to_datetime(yy1['福州'].index[i][2]) - pd.to_datetime('2016-2-1')
        fz1.append(io1.days*yy1['福州'].index[i][3] )
        fz2.append((io2.days +1)*yy1['福州'].index[i][3])
    if (pd.to_datetime('2016-2-1') > pd.to_datetime(yy1['福州'].index[i][1]) > pd.to_datetime('2016-1-1')) & \
        (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['福州'].index[i][2]) > pd.to_datetime('2016-3-1')):
        io1 = pd.to_datetime('2016-2-1') - pd.to_datetime(yy1['福州'].index[i][1])
        io2 = pd.to_datetime('2016-3-1') - pd.to_datetime('2016-2-1')
        io3 = pd.to_datetime(yy1['福州'].index[i][2]) - pd.to_datetime('2016-3-1')
        fz1.append(io1.days *yy1['福州'].index[i][3])
        fz2.append(io2.days *yy1['福州'].index[i][3])
        fz3.append((io3.days + 1)*yy1['福州'].index[i][3])

    if (pd.to_datetime('2016-3-1')>pd.to_datetime(yy1['福州'].index[i][1])>=pd.to_datetime('2016-2-1'))&\
        (pd.to_datetime('2016-3-1') > pd.to_datetime(yy1['福州'].index[i][2]) > pd.to_datetime('2016-2-1')):
        io = pd.to_datetime(yy1['福州'].index[i][2]) - pd.to_datetime(yy1['福州'].index[i][1])
        fz1.append((io1.days +1)*yy1['福州'].index[i][3])
    if (pd.to_datetime('2016-3-1') > pd.to_datetime(yy1['福州'].index[i][1]) > pd.to_datetime('2016-2-1')) & \
        (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['福州'].index[i][2]) > pd.to_datetime('2016-3-1')):
        io1 = pd.to_datetime('2016-3-1') - pd.to_datetime(yy1['福州'].index[i][1])
        io2 = pd.to_datetime(yy1['福州'].index[i][2]) - pd.to_datetime('2016-3-1')
        fz1.append(io1.days*yy1['福州'].index[i][3] )
        fz2.append((io2.days +1)*yy1['福州'].index[i][3])

    if (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['福州'].index[i][1]) > pd.to_datetime('2016-3-1')) & \
        (pd.to_datetime('2016-4-1') > pd.to_datetime(yy1['福州'].index[i][2]) > pd.to_datetime('2016-3-1')):
        io = pd.to_datetime(yy1['福州'].index[i][2]) - pd.to_datetime(yy1['福州'].index[i][1])
        fz1.append((io1.days +1)*yy1['福州'].index[i][3])

# for i in fz3:
#     print i
# print sum(fz3[:])


#---------------------------------------------------绘制图表----------------------------------------------------------
zhfont = mpl.font_manager.FontProperties(fname='/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf')
fig = plt.figure()
ax = fig.add_subplot(1,2,1)
plt.plot([1,2,3],[sum(sh1[:]),sum(sh2[:]),sum(sh3[:])],'r--*')  #sum(sh1[:])为上海1月票房，sum(sh2[:])为上海2月票房，sum(sh3[:])为上海3月票房
ax.set_xticks([1,2,3])
plt.xlabel(u'月份')
plt.ylabel(u'票房（万）')
plt.title(u'上海市1-3月票房图')
plt.grid()
ax = fig.add_subplot(1,2,2)
ax.set_xticks([1,2,3])
plt.xlabel(u'月份')
plt.ylabel(u'票房（万）')
plt.title(u'福州市1-3月票房图')
plt.grid()
plt.plot([1,2,3],[sum(fz1[:]),sum(fz2[:]),sum(fz3[:])],'--o')#sum(fz1[:])为福州1月票房，sum(fz2[:])为福州2月票房，sum(fz3[:])为福州3月票房
plt.show()