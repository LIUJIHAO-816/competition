__author__ = 'Liujuhao'
import re


s= "\'name\':\'liujihao\'"
pos = s.index(':')
print s[pos:]

def load_file():
    f = open("test.js")
    for line in f:
        pos_1 = line.index('\'')
        print line.rstrip('\n')

    f.close()

# load_file()