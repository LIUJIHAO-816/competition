# -*-coding:utf-8-*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import re

# header:电影名称;上映时间;闭映时间;出品公司;导演;主角;影片类型;票房/万;评分;
df = pd.read_csv('film-csv.txt', delimiter=';', header=0)
data = df.iloc[:, 0:9]  # 去除最后一列无效数据
# print data

# --------------------------------------------计算影片类型和票房的数据---------------------------------------------------
# 手动设置影片类型
film_type = ['校园', '喜剧', '荒诞', '爱情', '运动',
             '剧情', '社会', '浪漫', '推理', '悬疑',
             '动作', '科幻', '冒险', '家庭', '动画',
             '犯罪', '惊悚', '历史', '战争', '古装',
             '青春', '血腥', '言情']

# 自动提取影片类型（用该方法有个问题，有些类型不规则，要特别处理）
# film_type = []
# for i in data['影片类型'].values:
#     for k in re.split('、|，|/|\s', i):
#         film_type.append(k)

# 初始化每种类型的票房为0
type_box = []
for i in range(len(film_type)):
    type_box.append(0)

# 计算每种类型电影的票房（这里并不考虑时间、类型权重等因素，且一个影片是属于多种类型的）
for i in range(len(data['影片类型'].values)):
    for t in range(len(film_type)):
        if film_type[t] in str(data['影片类型'].values[i]):
            type_box[t] += data['票房/万'].values[i]
            # print data['票房/万'].values[i]

# ----------------------------------------------计算导演和票房的数据-----------------------------------------------------
# 提取导演数据到列表中
director = []
for i in data['导演'].values:
    for k in re.split('、|，|/|\s', i):
        if k not in director:
            director.append(k)

# 初始化每个导演的票房为0
director_box = []
for i in range(len(director)):
    director_box.append(0)

for i in range(len(data['导演'].values)):
    for k in range(len(director)):
        if director[k] in str(data['导演'].values[i]):
            director_box[k] += data['票房/万'].values[i]

# ---------------------------------------------计算导演和影片类型数据----------------------------------------------------
types = []
for i in range(len(director)):
    types.append("")
for n in range(len(director)):
    for i in range(len(data['导演'].values)):
        if director[n] in data['导演'].values[i]:
            for k in film_type:
                if k in str(data['影片类型'].values[i]):
                    types[n] = types[n] + '/' + k

director_type_dict = dict(zip(director, types))
# for k,v in director_type_dict.items():
#     print k,v


# ---------------------------------------------计算相关数据的{最值、均值、中位数}-----------------------------------------
##--------------------------------------计算score.log中每部电影的最值、均值、中位数值-------------------------------------
df = pd.read_csv('score.log', delimiter=',', header=0, names=['film', 'userid', 'socre'])
d_t_dict = dict.fromkeys(df['film'].drop_duplicates(), '')

for k, v in d_t_dict.items():
    for i in df.values:
        if k == i[0]:
            d_t_dict[k] += str(i[2]) + ','

scores_dict = {}
for k, v in d_t_dict.items():
    score_list = v.split(',')
    df = pd.DataFrame(score_list, columns=['score'])
    sdf = df[df['score'] != '']
    scores = sdf['score'].astype(np.float64)
    max = float('%.2f' % scores.max())
    min = float('%.2f' % scores.min())
    mean = float('%.2f' % scores.mean())
    median = float('%.2f' % scores.median())
    scores_dict[k] = [max, min, mean, median]


##-------------------------------------------计算每种类型包含哪些电影及相关值---------------------------------------------
type_film = []
for i in range(len(film_type)):
    types.append("")
for k in range(len(film_type)):
    current_film = ""
    for m in range(len(data['影片类型'].values)):
        if film_type[k] in str(data['影片类型'].values[m]):
            current_film += str(data['电影名称'].values[m]) + ','
    type_film.append(current_film)

# --类型和影片的字典
type_films_dict = dict(zip(film_type, type_film))

type_scores = {}
for k, v in type_films_dict.items():
    # print k,v
    score_list = []
    films = v.split(',')
    for f in films:
        if f != '':
            for k2, v2 in scores_dict.items():
                if f in k2:
                    score_list.append(v2)
    df = pd.DataFrame(score_list, columns=['max', 'min', 'mean', 'median'])
    current_max = float('%.1f' % df['max'].max())
    current_min = float('%.1f' % df['min'].min())
    current_mean = float('%.1f' % df['mean'].mean())
    current_median = float('%.1f' % df['median'].median())
    type_scores[k] = [current_max, current_min, current_mean, current_median]

##--打印每个类型的评分相关值，为nan的说明没有符合该类型的电影
for k, v in type_scores.items():
    print k.decode('utf-8'), v

# -------------------------------------------------------作图-----------------------------------------------------------
mpl.rcParams['font.sans-serif'] = ['simhei']

fig = plt.figure(1)
##图1 各种类型片票房收入比较
ax = fig.gca()
plt.bar(range(len(film_type)), type_box)
ax.set_xticks(range(len(film_type)))
ax.set_xticklabels(film_type, rotation=40)
plt.xlabel(u'影片类型')
plt.ylabel(u'票房/万')
plt.title(u'各种类型片票房收入比较')
plt.grid()

##图2 导演票房收入比较（此处有个问题是导演太多导致图的X轴看着很臃肿）
fig = plt.figure(2)
ax = fig.gca()
plt.bar(range(len(director)), director_box)
ax.set_xticks(range(len(director)))
ax.set_xticklabels(director, rotation=60)
plt.xlabel(u'导演')
plt.ylabel(u'票房/万')
plt.title(u'导演票房收入比较')
plt.grid()

##图3 导演执导过的影片类型，我觉得无法用图表示；不过单个导演的可以用饼图画出来
fig = plt.figure(3)
ax = fig.gca()
# labels = director_type_dict['申太罗'][1:].split('/')
# sizes = []
# for i in labels:
#     sizes.append(1)
# print labels
# pie = plt.pie(sizes, labels=labels)
# plt.axis('equal')
# print len(director_type_dict.keys()), len(director_type_dict.values())

x = range(len(director_type_dict.keys())/2)
y = range(len(director_type_dict.values())/2)
# for k in director_type_dict.values():
#     points = []
#     for m in k[1:].split('/'):
#         for num in range(len(type_film)):
#             # print film_type[num], m
#             if film_type[num] == m:
#                 points.append(num)
#     y.append(points)
# print y

plt.scatter(x[0:20], y[0:20], s=30)
plt.scatter(x[10:30], y[20:40], s=30)
plt.scatter(x[15:25], y[30:40], s=30)
plt.scatter(x[5:40], y[0:35], s=30)
ax.set_xticks(range(len(x)))
ax.set_yticks(range(len(y)))
plt.grid()

plt.show()

#---------------------------------------------------预测功能的实现-------------------------------------------------------
#题目中没有要求要怎么做推荐，但文档开头提到了python的scikit包，经了解，该包是基于python的机器学习算法库，所以应该要求用这个来实现
