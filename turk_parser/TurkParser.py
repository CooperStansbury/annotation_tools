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
        
        self.raw_text = defaultdict()
        self.annotations = defaultdict()

        self.load_json_files(json_dir_path)
        self.load_annotators()
        
        
        print(self.annotators)
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
        
        for json_file in self.json_files:
            for annotated_file in open(json_file):
                print(annotated_file)
            
        
#         # Each record/line in the "JSON" file is a separate
#         # JSON object representing an annotated document. For 
#         # each document there may be multiple annotations.
#         for annotated_file in open(json_path):
#             file_dict = json.loads(annotated_file)
#             file_content = file_dict['content']
            
#             # hash the content (str) into a file_id
#             file_id = int(hashlib.sha256(file_content.encode('utf-8')).hexdigest(), 16) % 10**8
            
#             # store the raw file
#             self.store_file(file_id, file_content, source_json_file_name)
            
#             # 'Handle' missing annotations
#             if file_dict['annotation'] is not None:
#                 for annotation in file_dict['annotation']:
#                     labels = annotation['label']
                    
#                     # it seems like I could always assume a single 
#                     # point per label, but best to be robust...
#                     for pt in annotation['points']:
#                         start_char = pt['start']
#                         end_char = pt['end']
#                         text = pt['text']
                        
#                         record = {
#                             'json_source_file':source_json_file_name,
#                             'file_id': file_id,
#                             'labels':labels,
#                             'start_char':start_char,
#                             'end_char':end_char,
#                             'text':text
#                         }
#                         # add new record
#                         new_records.append(record)
            
#         return pd.DataFrame(new_records)
    
    
#     def load_annotations(self):
#         """A method to load JSON-like objects into memory"""
#         # create data frames for all annotations
#         df_list = []
#         for file in self.json_file_list:
#             print(f"Processing {file}")
#             df_list.append(self.get_JSON_data(file))
            
#         # concatenate all df from different source
#         # files into a single data frame
#         return pd.concat(df_list, ignore_index=True, sort=False)
    
    
#     def clean_sentence(self, sent):
#         """A function to perform text processing on raw data to new field """
#         sent = str(sent).strip().encode(encoding = 'ascii',errors = 'replace')
#         sent = sent.decode(encoding='ascii',errors='strict')
#         sent = str(sent).replace("?", " ")
#         # strip redundant whitespace
#         sent = re.sub(' +', ' ', sent)
#         return sent
    
    
#     def build_sentence_frame(self):
#         """A method to build a dataframe of sentences for all files """
#         df_list = []
#         for file_id, file_content in self.files.items():
#             doc = file_content['spacy_doc']
            
#             # clean sentences
# #             sentences = [self.clean_sentence(i) for i in list(doc.sents)]

#             tmp_df = pd.DataFrame({"sentence": list(doc.sents)}) 
#             tmp_df['file_id'] = file_id
#             df_list.append(tmp_df)
          
#         # all files in one frame
#         df = pd.concat(df_list, ignore_index=True, sort=False)
        
#         # get human readable and start position
#         df['sentence_text'] = df['sentence'].map(lambda row: self.clean_sentence(row.text))
#         df['sentence_start'] = df['sentence'].map(lambda row: row.start_char)
#         return df
    
    
#     def format_annotator_name(self, filename):
#         """A function to return the formatted name of an annotator given a consistently 
#         named file:
        
#         Note: this depends on files named like `_NAME.json`
#         """
#         return filename.split("_")[-1].split(".")[0].upper()
    