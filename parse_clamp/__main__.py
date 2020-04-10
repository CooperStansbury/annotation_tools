# non-local imports
import argparse
import pandas as pd
import numpy as np
import re
import os
import spacy
from datetime import datetime

# local imports
import parse_xmi_files as pxmi
import rater_dataframe_ops as rdfo

### NOTE: this silences numpy divide errors
np.seterr(divide='ignore', invalid='ignore')


def get_date():
    """A funtion to return today's date as a stringself.

    Args:
        - NA

    Returns:
        today (sting): the date as a string

    """
    return datetime.today().strftime("%m-%d-%Y")


def get_rater_name(dir_name):
    """A function to retreive the 'rater name' from an
    input directory label.

    Args:
        - dir_name (string): the string representing the input path

    Returns:
        - rater_name (string) a label to use for the 'rater'

     use input dirname as rater name """
    return str(os.path.dirname(dir_name)).split("/")[1]


def get_annotation_values(nested_annotation_column1, nested_annotation_column2):
    """A function to retrieve the annotation values (unique). This is
    Used to build a one-hot map.

    Args:
        - nested_annotation_column1 (pd.Series)
        - nested_annotation_column2 (pd.Series)

    Returns:
        - annotation labels (list of string)
    """
    flat_list1 = [item for sublist in nested_annotation_column1 for item in sublist]
    flat_list2 = [item for sublist in nested_annotation_column2 for item in sublist]
    return  list(set(flat_list1 + flat_list2))

def write_agreement_summary(p_df, p_name, q_df, q_name, annotation_values):
    """A function to compile and write the annotations to a cvs file.

    Args:
        - p_df (pd.DataFrame): a dataframe of annotation for rater 1
        - p_name (string): the label representing annotator 1
        - q_df (pd.DataFrame): a dataframe of annotation for rater 2
        - q_name (string): the label representing annotator 2
        - annotation_values (list of string): a list of unique annotation values

    Returns:
        NA. writes a csv file out.
    """

    # get annotation map object
    print('Making annotation map object...')
    annotation_map_df = p_df[['file_name']].copy()

    # sort the annotation list to make sure order
    # doesn't affect the Kappa score
    annotation_map_df[p_name] = p_df['annotation_list_with_empty'].apply(lambda x: sorted(x)).copy()
    annotation_map_df[q_name] = q_df['annotation_list_with_empty'].apply(lambda x: sorted(x)).copy()

    # add simple flag for easy identification of disagreements
    annotation_map_df['Agree?'] = np.where(annotation_map_df[p_name] == annotation_map_df[q_name] ,"Yes", "No")
    annotation_map_df['Sentence'] = p_df[['raw_text']].copy()

    # write csv object
    save_path = 'annotation_summary' + get_date() + '.csv'

    annotation_map_df.to_csv(save_path)

    print('DONE. Wrote output to: ', save_path)


if __name__ == '__main__':
    program_description = "A command-line tool to calculate kappa values based \
    on CLAMP annotations."
    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument("--p", help="directory of annotations for annotator 1")
    parser.add_argument("--q", help="directory of annotations for annotator 2")

    args = parser.parse_args()

    p_name = get_rater_name(args.p)
    q_name = get_rater_name(args.q)

    # parse CLAMP files (xmi)
    p_list = pxmi.parse_xmi_dir(args.p)
    q_list = pxmi.parse_xmi_dir(args.q)

    # convert annotations to dataframes for easier use
    p_df = rdfo.get_rater_dataframe(p_list, p_name)
    q_df = rdfo.get_rater_dataframe(q_list, q_name)

    # detect annotation values
    annotation_values = get_annotation_values(p_df['annotation_list_with_empty'],
                                              q_df['annotation_list_with_empty'])
    p_df = rdfo.correct_for_missing_labels(p_df, annotation_values)
    q_df = rdfo.correct_for_missing_labels(q_df, annotation_values)


    # write report
    write_agreement_summary(p_df, p_name, q_df, q_name, annotation_values)
