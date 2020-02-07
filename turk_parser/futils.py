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

        
def format_annotator_name(filename):
    """A function to return the formatted name of an annotator given a consistently 
    named file.
    
    Note: this depends on files named like `_NAME.json`
    
    Args:
        - filename (str): a file name, expects name after last `_`
            character

    Returns:
        - name (str): a formated string 
    """
    return filename.split("_")[-1].split(".")[0].upper()
    

                
def load_annotations(name, json_file):
    """A function to load annotations from a single
    json file
    
    Args:
        - name (str): annotators' name
        - json_file (str): file path to the json file
        
    Returns:
        - annotations (pd.DataFrame)
        - document_map (dict): a dict of doc_ids and 
            raw content
    """

    new_rows = []
    document_map = {}
    
    for annotated_doc in open(json_file):
        json_dump = json.loads(annotated_doc)
    
        # save the file by a doc_id 
        content = json_dump['content']
        doc_id = int(hashlib.sha256(content.encode('utf-8')).hexdigest(), 16) % 10**8
    
    
        document_map[doc_id] = content
        # 'Handle' missing annotations
        if json_dump['annotation'] is not None:

            for annotation in json_dump['annotation']:
                label_list = annotation['label']

                # it seems like I could always assume a single 
                # point per label, but best to be robust...
                for pt in annotation['points']:
                    start_char = pt['start']
                    end_char = pt['end']
                    text = pt['text']

                    record = {
                        'doc_id' : doc_id,
                        'json_filename':json_file,
                        f'{name}_A': 1 if 'A' in label_list else 0,
                        f'{name}_B': 1 if 'B' in label_list else 0,
                        f'{name}_C': 1 if 'B' in label_list else 0,
                        f'{name}_start':start_char,
                        f'{name}_end':end_char,
                        f'{name}_text':text,
                    }

                    new_rows.append(record)

    df = pd.DataFrame(new_rows)
    return df, document_map
#     df.to_csv("tmp.csv")
                            
                
    