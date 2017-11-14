__author__ = 'Liujuhao'



keys = ['a', 'b', 'c']
value = []
#
d1 = {key:list(value) for key in keys}
d1['a'].append(123)
d1['b'].append(456)

#该方式的值都相同
d2 = dict.fromkeys(keys,list(value))
d2['c'].append(666)
print d2
print d1