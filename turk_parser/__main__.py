""" main file for parsing dataturks annotations """

import sys
import os
import json
import pandas as pd
import hashlib
import argparse
import spacy
import re
import xlsxwriter
from datetime import datetime
import TurkParser

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('dir', nargs='?', default='data/')
    parser.add_argument('nlp_lib', nargs='?', default='en_core_web_sm')
    args = parser.parse_args()
    
    # build the annotation class
    turks = TurkParser.Turk_Parser(args.dir, args.nlp_lib)
    
    
    [print(k,v, '\n') for k,v in turks.LIZ.items()]
    
    
   