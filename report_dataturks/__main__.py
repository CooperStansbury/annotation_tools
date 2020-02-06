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
import dtAnnotator

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('dir', nargs='?', default='data/')
    parser.add_argument('nlp_lib', nargs='?', default='en_core_web_sm')
    args = parser.parse_args()
    
    # build the annotation class
    dataturks = dtAnnotator.DataTurkAnnotations(args.dir, args.nlp_lib)
    
    # simpler report
    save_path = f"output/{dataturks.get_date()}_map.csv"
    dataturks.annotation_map.to_csv(save_path, index=False)
    print(f"Saved output to: {save_path}")
    
    
    # simpler report
    save_path = f"output/{dataturks.get_date()}_annotations.csv"
    dataturks.annotations.to_csv(save_path, index=False)
    print(f"Saved output to: {save_path}")
    
    # save the report
#     dataturks.write_xlsx_report(dataturks.annotation_map)
    
    
    
   