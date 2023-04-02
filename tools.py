import numpy as np 

def rounder(dig):
    def rounder_to_dig(float):
        return np.around(float, dig)
        return format(np.around(float, dig), f'.{dig}f')
    return rounder_to_dig