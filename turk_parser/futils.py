import sys
import os
import json
import pandas as pd
import hashlib
import spacy
import re
import xlsxwriter
from datetime import datetime
from collections import defaultdict

# load nlp_lib
# nlp = spacy.load('en_core_web_sm')


def printl(_iterable, new_line=False):
    """A function to print an iterable nicely.
    
    Args:
        - _iterable (list or dict)
        - new_line (bool): should we add a newline between?
    
    Prints:
        - each item in list on new line
    """
    
    if new_line:
        if isinstance(_iterable, dict):
            [print(k, v, '\n') for k,v in _iterable.items()]
        else:
            [print(x, '\n') for x in _iterable]
    else:
        if isinstance(_iterable, dict):
            [print(k, v) for k,v in _iterable.items()]
        else:
            [print(x) for x in _iterable]

    
