"""
Get a list of files from the `data/` directory.
Each is a `.json. file with annotations for multiple informed consent documents. 
Each `.json` file is a single annotator.
"""

import sys
import os
import json
import pandas as pd
import hashlib
import spacy
import re
import random
from importlib import reload
from datetime import datetime
from collections import defaultdict
from pprint import pprint

class Raw_Annotations():
    """A class to help manage annotations from DataTurks"""
    
    def _get_date(self):
        """ return  today's date as an appendable string"""
        return datetime.today().strftime("%m-%d-%Y")
    
    def __init__(self, data_dir = "../data/", nlp_lib="en_core_web_lg"):
        """
        Args: 
            - data_dir (str): a path to a directory of json files 
                containing annotations        
        """
        self.nlp = spacy.load(nlp_lib)
        self.data_dir = data_dir
        self.annotated_files = self.get_json_files()
        self.annotators = self.get_annotators()

        # load annotations into a list. 
        # THIS IS THE WORKHORSE OF THIS CLASS
        self.annotations = self.load_annotations()
        
        # map all document raw content to it's ID
        self.document_map = self.build_document_map()
        
        
    def format_annotator_name(self, filename):
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

    def get_json_files(self):
        """A function to initialize a dictionary for storing annotations 

        Returns:
            - annotated_files (default dict): primary keys are annotators names
        """
        annotated_files = []

        for subdir, dirs, files in os.walk(self.data_dir):
                for file in files:
                    annotated_files.append(os.path.join(subdir, file))

        return annotated_files
    
    def get_annotators(self):
        """A function to get the names of annotators"""
        annotators = []
        for file in self.annotated_files:
            name = self.format_annotator_name(file)
            if name not in annotators:
                annotators.append(name)
                
        return annotators
    
    def get_document_id(self, raw_content, digits=8):
        """A function to facilitate conversion of raw text into document ids

        Args:
             - raw_content (str): a sufficient portion of the document as to 
                 be unique with a high probability
             - digits (int): number of digits to return

         Returns:
             - doc_id (int): a document id
        """
        return int(hashlib.sha256(raw_content.encode('utf-8')).hexdigest(), 16) % 10**digits
    
    def build_document_map(self):
        """ A function to get a map of documents and ids """
        
        document_map = {}
        
        for json_file in self.annotated_files:
             for annotated_doc in open(json_file):
                json_dump = json.loads(annotated_doc)
                # get raw content
                content = json_dump['content']
                doc_id = self.get_document_id(content)
                document_map[doc_id] = {'raw_content': content,
                                        'from_file':json_file}
                
        return document_map
    
    def get_dumps(self, json_file):
        """A function to return a list of json_dumps
        from a given json_file
        
        Args:
            - json_file (str): the path to the json file
            
        Returns:
            - json_dumps (list): list of json dumps 
        """
        return [json.loads(dump) for dump in open(json_file)]
    
    
    def _clean_raw_annotation_text(self, raw_text_annotation):
        """A function to clean sentences
        
        Args: 
            - raw_text_annotation (str): may be multi-sentence annotations
            
        Returns:
            - clean_list (list): a list of clean sentences   
        """
        dirty_str = str(raw_text_annotation).strip().encode(encoding = 'ascii',
                                                       errors = 'replace')
        dirty_str = dirty_str.decode(encoding='ascii', 
                           errors='strict')
        
        dirty_str = str(dirty_str).replace("?", " ")
        # strip redundant whitespace and signature lines 
        dirty_str = re.sub(' +', ' ', dirty_str).replace("_", "")
        
        clean_list = []
        
        for sent in self.nlp(" ".join(dirty_str.split())).sents:
            clean_list.append(sent.text)
        
        return clean_list
    
    def load_annotations(self):
        """A function to load all annotations into a list
        """
        
        processed_annotations = []
        
#         for json_file in random.sample(self.annotated_files, 1):
        for json_file in self.annotated_files:
            name = self.format_annotator_name(json_file)
            
            # each json file contains multiple
            # informed consent forms
            # iterate through consent docs in
            # a json file
            for icd_doc in self.get_dumps(json_file):
                             
                # handle None annotations
                if icd_doc['annotation'] is None:
                    continue 
                
                # hash document content to create ID
                doc_id = self.get_document_id(icd_doc['content'])
                    
                for annotation in icd_doc['annotation']:
                    
                    # perform preprocessing on sentences in annotation
                    # primarily to handle multiple sentence annotations
                    sentences = self._clean_raw_annotation_text(annotation['points'][0]['text'])
                    
                    # start and end character positions recorded
                    # only for the first sentence, everything else
                    # will require an offset during alignment
                    start_char = annotation['points'][0]['start']
                    end_char = annotation['points'][0]['end']
                    
                    # track the number of sentences
                    # with the index
                    for idx, sent in enumerate(sentences):
                        
                        processed_annotations.append({
                            'ICD_doc_id' : doc_id,
                            'json_filename':json_file,
                            'annotator': name,
                            'annotation_id': self.get_document_id(annotation['points'][0]['text'], 8),
                            'A': 1 if 'A' in annotation['label'] else 0,
                            'B': 1 if 'B' in annotation['label'] else 0,
                            'C': 1 if 'C' in annotation['label'] else 0,
                            'start_char':start_char,
                            'end_char':end_char,
                            'text':sent,
                            'sentence_count': (idx + 1)
                        })
                        
        return processed_annotations
    
            
    def save_annotations(self, out_dir="processed_annotations/"):
        """A function to save files
        
        Args:
            - outdir (str): the directory path of the output
        """
        filename = f"{out_dir}ANNOTATIONS_{self._get_date()}.csv"
        df = pd.DataFrame(self.annotations)
        df.to_csv(filename, index=False)
        print(f"Saved to: `{filename}`")
        
    def save_document_map(self, out_dir="processed_annotations/"):
        """A function to save the document map. 
        
        Args:
            - outdir (str): the directory path of the output
        """
        filename = f"{out_dir}DOCUMENT_MAP_{self._get_date()}.json"
        json.dump(self.document_map, open(filename, 'w'))
        print(f"Saved to: `{filename}`")
