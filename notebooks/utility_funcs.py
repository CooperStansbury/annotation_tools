"""
Inclusion exclusion rules
"""



def force_encoding(text_string):
    """A function to force standard encoding for an input string
    
    NOTE: this strictly handles encoding errors by replacing them, 
    then stripping the character (`?`) they are replaced with. There
    is some collateral damage.
    
    Args: 
        - text_string (str): input string (NOT BYTES)
    
    Returns:
        - decoded_str (str): encoded string with errors handled
    """
    endcoded_str = (text_string).encode(encoding='ascii', errors='replace')
    decoded_str = endcoded_str.decode(encoding='ascii', errors='strict')
    return str(decoded_str).replace("?", " ")

def include_exclude(row):
    """A function to return [0,1] based on inclusion exclusion criteria """
    
    if row['char_count'] < 9:
        return 0
    elif not any(c.isalpha() for c in row['sentence']):
        return 0
    else:
        return 1