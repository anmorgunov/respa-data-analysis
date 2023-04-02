import numpy as np 

def rounder(dig):
    def rounder_to_dig(float):
        return np.around(float, dig)
        return format(np.around(float, dig), f'.{dig}f')
    return rounder_to_dig

def getNextCol(col, prefix = None):
    if prefix is None:
        prefix = ''
    strings = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if not col:
        return 'A'
    if len(col) == 1:
        if col == 'Z':
            return getNextCol(prefix, prefix=None) + getNextCol('', prefix=None)
        else:
            return prefix + strings[strings.index(col)+1]
    else:
        return getNextCol(col[1:], prefix = prefix + col[0])