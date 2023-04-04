import numpy as np 

import numpy as np

def rounder(dig):
    """
    Returns a function that rounds a given floating point number to the specified number of decimal places.
    
    Parameters:
    dig (int): number of decimal places to round to.
    
    Returns:
    function: A function that rounds a given floating point number to the specified number of decimal places.
    """
    def rounder_to_dig(float):
        """
        Rounds a given floating point number to the specified number of decimal places.
        
        Parameters:
        float (float): The number to round.
        
        Returns:
        float: The rounded number.
        """
        return np.around(float, dig)
    return rounder_to_dig


def getNextCol(col, prefix = None):
    """Return the next column name after the given column name.

    Args:
        col (str): The column name to get the next column from.
        prefix (str, optional): A prefix for the column name. Defaults to None.

    Returns:
        str: The next column name.
    """
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