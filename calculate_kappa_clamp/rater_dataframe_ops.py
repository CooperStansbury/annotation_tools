# non-local imports
import pandas as pd
import numpy as np
import re
import os
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import cohen_kappa_score

def mark_empty_annotations(df):
    """ mark sentences that were not annotated using apply design pattern,
    replace with string 'blank' """

    def apply_check_annotation_list(row):
        """ apply function to test if len(annotations) = 0 """
        if len(row) == 0:
            return(['blank'])
        else:
            return(row)

    df['annotation_list_with_empty'] = df['annotation_list'].apply(lambda row:apply_check_annotation_list(row))
    return(df)


def normalize_annotations(df):
    """ function to convert list of annotations into new columns """
    print('Converting labels to one-hot enconding...')
    nested_list = df['annotation_list_with_empty']
    mlb = MultiLabelBinarizer()
    ont_hot_df = pd.DataFrame(mlb.fit_transform(df.pop('annotation_list_with_empty')),
                          columns=mlb.classes_,
                          index=df.index)
    new_df = pd.concat([df, ont_hot_df], axis=1)
    new_df['annotation_list_with_empty'] = nested_list
    return(new_df)


def get_annotation_values(nested_annotation_column1, nested_annotation_column2):
    """ return a set of unique annotation labels used """
    flat_list1 = [item for sublist in nested_annotation_column1 for item in sublist]
    flat_list2 = [item for sublist in nested_annotation_column2 for item in sublist]
    uniques = set(flat_list1 + flat_list2)
    return(list(uniques))


def correct_for_missing_labels(df, annotation_values):
    """ create a column of "0" in the case that a label was not used by an
    annotator """
    columns = list(df.columns)
    missing_labels = [x for x in annotation_values if x not in columns]

    if not len(missing_labels) > 0:
        return(df)
    else:
        for msslbl in missing_labels:
            df[msslbl] = 0
        return(df)


def get_rater_dataframe(parsed_dir, rater_name):
    """ get dataframes with annotations """
    print('Converting to dataframe: ', rater_name)
    list_df = []
    for parsed_files in parsed_dir:
        file_name = parsed_files[0]
        annotations = parsed_files[1]
        tmp_df = pd.DataFrame(annotations, columns=['raw_text','annotation_list'])
        tmp_df['file_name'] = file_name
        tmp_df['rater_name'] = rater_name
        list_df.append(tmp_df)
    df = pd.concat(list_df)

    df = mark_empty_annotations(df)
    df = normalize_annotations(df)
    return(df)
