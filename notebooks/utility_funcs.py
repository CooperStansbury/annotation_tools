"""
Inclusion exclusion rules
"""

def include_exclude(row):
    """A function to return [0,1] based on inclusion exclusion criteria """
    
    if row['char_count'] < 9:
        return 0
    elif not any(c.isalpha() for c in row['sentence']):
        return 0
    else:
        return 1