""" main file for parsing dataturks annotations """

import sys
import os
import json
import pandas as pd
import hashlib
import spacy
import re
import xlsxwriter
from datetime import datetime

def get_date():
    """ return  today's date as an appendable string"""
    return datetime.today().strftime("%m-%d-%Y")


class DataTurkAnnotations():
    """A class to process annotations from DataTurks 
    tasks """   
    
    def store_file(self, file_id, file_content):
        """A method to capture the file content (whole file)"""
        
        if file_id not in self.files:
            self.files[file_id] = {
                "raw_content":file_content,
                "spacy_doc": nlp(file_content)
            }
        else:
            pass

    
    def get_JSON_data(self, json_path):
        """A method to return a dataframe with file IDs, sentences,
        and annotation text from a JSON DataTurk output """
        new_records = []
        
        # the aggregate json file name
        source_json_file_name = os.path.basename(json_path)
        
        # Each record/line in the "JSON" file is a separate
        # JSON object representing an annotated document. For 
        # each document there may be multiple annotations.
        for annotated_file in open(json_path):
            file_dict = json.loads(annotated_file)
            file_content = file_dict['content']
            
            # hash the content (str) into a file_id
            file_id = int(hashlib.sha256(file_content.encode('utf-8')).hexdigest(), 16) % 10**8
            
            # store the raw file
            self.store_file(file_id, file_content)
            
            # 'Handle' missing annotations
            if file_dict['annotation'] is not None:
                for annotation in file_dict['annotation']:
                    labels = annotation['label']
                    
                    # it seems like I could always assume a single 
                    # point per label, but best to be robust...
                    for pt in annotation['points']:
                        start_char = pt['start']
                        end_char = pt['end']
                        text = pt['text']
                        
                        record = {
                            'json_source_file':source_json_file_name,
                            'file_id': file_id,
                            'labels':labels,
                            'start_char':start_char,
                            'end_char':end_char,
                            'text':text
                        }
                        # add new record
                        new_records.append(record)
            
        return pd.DataFrame(new_records)
          
                  
    def get_files(self, json_dir_path):
        """A method to return a list of relative file paths """
        f_list = []
        for subdir, dirs, files in os.walk(json_dir_path):
            for file in files:
                f_list.append(os.path.join(subdir, file))
        return f_list
    
    def load_annotations(self):
        """A method to load JSON-like objects into memory"""
        # create data frames for all annotations
        df_list = []
        for file in self.f_list:
            df_list.append(self.get_JSON_data(file))
            
        # concatenate all df from different source
        # files into a single data frame
        return pd.concat(df_list, ignore_index=True, sort=False)
    
    def build_sentence_frame(self):
        """A method to build a dataframe of sentences for all files """
        df_list = []
        for file_id, file_content in self.files.items():
            doc = file_content['spacy_doc']
            tmp_df = pd.DataFrame({"sentence":list(doc.sents)}) 
            tmp_df['file_id'] = file_id
            df_list.append(tmp_df)
          
        # all files in one frame
        df = pd.concat(df_list, ignore_index=True, sort=False)
        
        # get human readable and start position
        df['sentence_text'] = df['sentence'].map(lambda row: re.sub(' +', ' ', row.text.strip()))
        df['sentence_start'] = df['sentence'].map(lambda row: row.start_char)
       
    
        return df

    
    def __init__(self, json_dir_path):
        """A method to initialize the annotation object """
        # data structure to store each raw file
        # i.e., the files that were annotated
        self.files = {} 
       
        # load the annotations from the json_dir_path
        self.f_list = self.get_files(json_dir_path)
        self.annotations = self.load_annotations()
        
        # parse sentences from raw content 
        # idea is to rely on spaCy defaults as much as possible
        self.sentence_frame = self.build_sentence_frame()
        
        self.annotation_map = self.map_annotations()
        
        
    def map_annotations(self):
        """A method to map annotations onto list of parsed sentences """
        
        # migrate sentences without modifying the original 
        # data frame 
        df = pd.DataFrame()
        df['sentence_text'] = self.sentence_frame['sentence_text']
        df['sentence_start'] = self.sentence_frame['sentence_start']
        df['file_id'] = self.sentence_frame['file_id']
        df['annotation'] = None
        
        df.reset_index()
        
        # get list of "annotators" from different json files
        sources = list(set(self.annotations['json_source_file']))
        # format new column names
        new_sources = [''.join([i for i in src.replace("json", "") if i.isalpha()]) for src in sources]
        # preserve the map between old and new names
        self.source_map = dict(zip(sources, new_sources))
        
        
        # build new columns for annotations done 
        # by different "annotators"
        for src in self.source_map.values():
            df[src] = None
    
        for idx, annotation in self.annotations.iterrows():
            # filter by file first 
            file_matches = df[df['file_id'] == annotation['file_id']]
            
            # find the closest starting position
            closest_pos = min(file_matches['sentence_start'], key=lambda x:abs(x-annotation['start_char']))
            
            # get corresponding record
            # we'll just us the index information for now
            match = file_matches[file_matches['sentence_start'] == closest_pos]
            
            # get column name based on source file
            annotator = self.source_map[annotation['json_source_file']]
            
            # set the values of the 'under construction' dataframe
            # including stroing the actual annotation
            df.loc[match.index, annotator] = str(annotation['labels'])
            df.loc[match.index, 'annotation'] = str(annotation['text'])
            
        return df
    
    
def write_report(df, save_path=f"output/{get_date()}_map.xlsx"):
    """A function to write an xlsx file based on an input dataframe"""
    
    with pd.ExcelWriter(save_path, engine='xlsxwriter', mode='w') as writer:
        df.to_excel(writer, sheet_name='Sheet 1', index=False)
        writer.save()
        
    
        
if __name__ == "__main__":
    
    # data path spec (from command line)
    json_dir_path = sys.argv[1]
    
    # spacy model spec
    # default to the small model, but allow large 
    if len(sys.argv) > 2:
        if sys.argv[2] == 'lg':
            nlp = spacy.load('en_core_web_lg')
    else: 
        nlp = spacy.load('en_core_web_sm')
    
    # build the annotation class
    dataturks = DataTurkAnnotations(json_dir_path)
    
    # save the report
    write_report(dataturks.annotation_map)
    
    
    
   