# non-local imports
import argparse
import pandas as pd
import numpy as np
import re
import os
import spacy
from datetime import datetime
from sklearn.preprocessing import MultiLabelBinarizer

# local imports
import parse_xmi_files as pxmi

### NOTE: this silences numpy divide errors
np.seterr(divide='ignore', invalid='ignore')

def get_date():
    """A funtion to return today's date as a string.

    Args:
        - NA

    Returns:
        today (sting): the date as a string

    """
    return datetime.today().strftime("%m-%d-%Y")


def mark_empty_annotations(df):
    """A function to mark sentences that were not annotated
    using apply design pattern, replace with string 'blank'

    Args:
        - df (pd.DataFrame): a data frame with annotations (including blanks)

    Returns:
        - df (pd.DataFrame): modified in place
    """

    def apply_check_annotation_list(row):
        """ apply function to test if len(annotations) = 0 """
        if len(row) == 0:
            return(['blank'])
        else:
            return(row)

    df['annotation_list_with_empty'] = df['annotation_list'].apply(lambda row:apply_check_annotation_list(row))
    return df


def normalize_annotations(df):
    """A function to convert list of annotations into new columns (one-hot).

    NOTE: this does not account for labels that were defined in the TypeDef,
    but were not used by the annotator.

    Args:
        - df (pd.DataFrame): a data frame with annotations (including blanks)

    Returns:
        - df (pd.DataFrame): modified, returns new (may be a shallow copy)
     """
    nested_list = df['annotation_list_with_empty']
    mlb = MultiLabelBinarizer()
    ont_hot_df = pd.DataFrame(mlb.fit_transform(df.pop('annotation_list_with_empty')),
                          columns=mlb.classes_,
                          index=df.index)
    new_df = pd.concat([df, ont_hot_df], axis=1)
    new_df['annotation_list_with_empty'] = nested_list
    return new_df


def get_rater_dataframe(annotations):
    """A function to build the rater data structure from a
    list of parsed annotations.

    Args:
        - annotations (list): a list of annotations

    Returns:
        - df (pd.DataFrame): a data frame of annotations
    """
    list_df = []
    for parsed_files in annotations:
        file_name = parsed_files[0]
        annotations = parsed_files[1]
        tmp_df = pd.DataFrame(annotations, columns=['raw_text','annotation_list'])
        tmp_df['file_name'] = file_name
        list_df.append(tmp_df)
    df = pd.concat(list_df)

    # handle blank annotations and make one-hot encoded
    # columns
    df = mark_empty_annotations(df)
    df = normalize_annotations(df)
    return df


if __name__ == '__main__':
    desc = """ A Python3 commandline tool to parse CLAMP files (.xmi)
    into .csv format. """

    # handle input arguments
    # defaults to 'input_data/' dir, but can handle a different target
    default_path = "parse_clamp/input_data/"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--i",  nargs='?', default=default_path,
                        help="directory of annotations")
    args = parser.parse_args()

    # parse CLAMP files into list and normalize
    # into a dataframe
    annotation_list = pxmi.parse_xmi_dir(args.i)
    df = get_rater_dataframe(annotation_list)

    # write the csv out to a new file (with today's date)
    save_path = 'annotations' + get_date() + '.csv'
    df.to_csv(save_path)
