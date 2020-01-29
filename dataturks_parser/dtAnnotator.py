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


class DataTurkAnnotations():
    """A class to process annotations from DataTurks 
    tasks """   
    
    def __init__(self, json_dir_path, nlp_lib):
        """A method to initialize the annotation object """
        # data structure to store each raw file
        # i.e., the files that were annotated
        self.files = {} 
        
        # load the spacy lib
        global nlp 
        nlp = spacy.load(nlp_lib)
       
        # load the annotations from the json_dir_path
        self.f_list = self.get_files(json_dir_path)
        self.annotations = self.load_annotations()
        
        # parse sentences from raw content 
        # idea is to rely on spaCy defaults as much as possible
        self.sentence_frame = self.build_sentence_frame()
        
        self.annotation_map = self.map_annotations()
    
    def store_file(self, file_id, file_content, file_name):
        """A method to capture the file content (whole file)"""
        
        if file_id not in self.files:
            self.files[file_id] = {
                "raw_content":file_content,
                "spacy_doc": nlp(file_content),
                "file_name" : file_name
            }
        else:
            pass

        
    def get_date(self):
        """ return  today's date as an appendable string"""
        return datetime.today().strftime("%m-%d-%Y")

    
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
            self.store_file(file_id, file_content, source_json_file_name)
            
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
            print(f"Processing {file}")
            df_list.append(self.get_JSON_data(file))
            
        # concatenate all df from different source
        # files into a single data frame
        return pd.concat(df_list, ignore_index=True, sort=False)
    
    
    def clean_sentence(self, sent):
        """A function to perform text processing on raw data to new field """
        sent = str(sent).strip().encode(encoding = 'ascii',errors = 'replace')
        sent = sent.decode(encoding='ascii',errors='strict')
        sent = str(sent).replace("?", " ")
        # strip redundant whitespace
        sent = re.sub(' +', ' ', sent)
        return sent
    
    
    def build_sentence_frame(self):
        """A method to build a dataframe of sentences for all files """
        df_list = []
        for file_id, file_content in self.files.items():
            doc = file_content['spacy_doc']
            
            # clean sentences
#             sentences = [self.clean_sentence(i) for i in list(doc.sents)]

            tmp_df = pd.DataFrame({"sentence": list(doc.sents)}) 
            tmp_df['file_id'] = file_id
            df_list.append(tmp_df)
          
        # all files in one frame
        df = pd.concat(df_list, ignore_index=True, sort=False)
        
        # get human readable and start position
        df['sentence_text'] = df['sentence'].map(lambda row: self.clean_sentence(row.text))
        df['sentence_start'] = df['sentence'].map(lambda row: row.start_char)
        return df
    
    
    def format_annotator_name(self, filename):
        """A function to return the formatted name of an annotator given a consistently 
        named file:
        
        Note: this depends on files named like `_NAME.json`
        """
        return filename.split("_")[-1].split(".")[0].upper()
    
    
    def build_annotator_name_map(self, annotators):
        """A functtion to format annotator names given a list of file names.
        
        Note: this depends on files named like `_NAME.json`
        """
        self.source_map = defaultdict(list)
        for name in annotators:
            formatted_name = self.format_annotator_name(name)
            self.source_map[formatted_name].append(name)
            
        
    def map_annotations(self):
        """A method to map annotations onto list of parsed sentences """
        # migrate sentences without modifying the original data frame 
        df = pd.DataFrame()
        df['sentence_text'] = self.sentence_frame['sentence_text']
        df['sentence_start'] = self.sentence_frame['sentence_start']
        df['file_id'] = self.sentence_frame['file_id']
        
        df.reset_index()
        
        # get list of "annotators" from different json files
        annotators = list(set(self.annotations['json_source_file']))
        
        # update annotators names in self.source_map
        self.build_annotator_name_map(annotators)
        
        # build new columns for annotations done 
        # by different "annotators"
        for src in self.source_map.keys():
            df[src] = None
            df[f"{src}_annotation"] = None
    
        for idx, annotation in self.annotations.iterrows():
            # filter by file first 
            file_matches = df[df['file_id'] == annotation['file_id']]
            
            # find the closest starting position
            closest_pos = min(file_matches['sentence_start'],
                              key=lambda x:abs(x-annotation['start_char']))
            
            # get corresponding record
            # we'll just us the index information for now
            match = file_matches[file_matches['sentence_start'] == closest_pos]
            
            # get column name based on source file
            annotator = self.format_annotator_name(annotation['json_source_file'])
            
            # set the values of the 'under construction' dataframe
            df.loc[match.index, annotator] = str(annotation['labels'])
            
            # including stroing the actual annotation
            df.loc[match.index, f'{annotator}_annotation'] = self.clean_sentence(annotation['text'])
                     
        return df
    
    
#     def write_xlsx_report(self, df, save_path=None):
#         """A function to write an xlsx file based on an input dataframe"""
        
#         if save_path is None:
#             save_path = f"output/{self.get_date()}_map.xlsx"

#         with pd.ExcelWriter(save_path, engine='xlsxwriter', mode='w') as writer:
#             df.to_excel(writer, sheet_name='Sheet 1', index=False)
#             writer.save()
#             print(f"Saved output to: {save_path}")