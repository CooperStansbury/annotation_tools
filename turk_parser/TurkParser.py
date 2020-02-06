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


class Turk_Parser():
    """A class to process annotations from DataTurks 
    tasks """   
    
    def _get_date(self):
        """ return  today's date as an appendable string"""
        return datetime.today().strftime("%m-%d-%Y")
    
    
    def _format_annotator_name(self, filename):
        """A function to return the formatted name of an annotator given a consistently 
        named file:
        
        Note: this depends on files named like `_NAME.json`
        """
        return filename.split("_")[-1].split(".")[0].upper()
    
    def __init__(self, json_dir_path, nlp_lib):
        """A method to initialize the annotation object """
        
        # load the spaCy object
        nlp = spacy.load(nlp_lib)
    
        self.json_files = []
        self.annotators = []
        
        self.docs = defaultdict()
        self.annotations = defaultdict()

        self.load_json_files(json_dir_path)
        self.load_annotators()
        
        # create attributes for each annotator
        [setattr(self, annotator, defaultdict()) for annotator in self.annotators] 
        
        # save annotations
        self.load_annotations()
        
#         [print(k,v) for k,v in self.annotators.items()]
    
    
    def load_json_files(self, json_dir_path):
        """A method to return a list of relative file paths
        given a directory path"""
        for subdir, dirs, files in os.walk(json_dir_path):
            for file in files:
                self.json_files.append(os.path.join(subdir, file))
    
        
    def load_annotators(self):
        """A function to store annotator names and the
        json files that contain their annotations """
        
        for file in self.json_files:
            clean_name = self._format_annotator_name(file)
            if not clean_name in self.annotators:
                self.annotators.append(clean_name)
                
    def load_annotations(self):
        """A function to load annotations """
        
        new_rows = []
        
        for json_file in self.json_files:
            annotator_name = self._format_annotator_name(json_file)
            annotator_attr = getattr(self, annotator_name)
            for annotated_file in open(json_file):
                
                json_dump = json.loads(annotated_file)
                
                # save the file by a doc_id 
                content = json_dump['content']
                doc_id = int(hashlib.sha256(content.encode('utf-8')).hexdigest(), 16)
                
                if not doc_id in self.docs:            
                    self.docs[doc_id] = content
                
                # 'Handle' missing annotations
                if json_dump['annotation'] is not None:
                    
                    label_count = 0
                    for label in json_dump['annotation']:
                        label_list = label['label']

                        # it seems like I could always assume a single 
                        # point per label, but best to be robust...
                        for pt in label['points']:
                            label_count += 1
                            start_char = pt['start']
                            end_char = pt['end']
                            text = pt['text']

                            record = {
                                'doc_id' : doc_id,
                                'annotation_id':label_count,
                                'labels':label_list,
                                'start_char':start_char,
                                'end_char':end_char,
                                'text':text
                            }
                            
                            new_rows.append(record)
                            
        df = pd.DataFrame(new_rows)
        
        df.to_csv("tmp.csv")
                            
                
    