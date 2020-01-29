# non-local imports
import argparse
import pandas as pd
import numpy as np
import xlsxwriter
import re
import os
import spacy
from datetime import datetime
from tabulate import tabulate
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import cohen_kappa_score

# local imports
import parse_xmi_files as pxmi
import rater_dataframe_ops as rdfo

### NOTE: this silences numpy divide errors
np.seterr(divide='ignore', invalid='ignore')


def get_date():
    """ return  today's date as an appendable string"""
    return datetime.today().strftime("%m-%d-%Y")


def get_rater_name_from_input_arg(input_arg):
    """ use input dirname as rater name """
    rater_name = str(os.path.dirname(input_arg)).split("/")[1]
    return(rater_name)


def get_annotation_values(nested_annotation_column1, nested_annotation_column2):
    """ return a set of unique annotation labels used """
    flat_list1 = [item for sublist in nested_annotation_column1 for item in sublist]
    flat_list2 = [item for sublist in nested_annotation_column2 for item in sublist]
    uniques = set(flat_list1 + flat_list2)
    return(list(uniques))


def get_total_agreement(p_df, q_df, annotation_values):
    """ calculate Cohen's Kappa on all sets of annotations """
    new_rows = []
    for label in annotation_values:
        kappa = cohen_kappa_score(p_df[label], q_df[label])
        row = {
            "Summary Level":"All Files",
            "Label":label,
            "Cohen's Kappa": round(kappa, 3)
            }
        new_rows.append(row)
    return(pd.DataFrame(new_rows))


def get_agreement_by_file(p_df, q_df, annotation_values):
    """ calculate Cohen's Kappa on all files annotated """
    new_rows = []
    p_files = list(p_df['file_name'].unique())
    q_files = list(q_df['file_name'].unique())
    files = list(set(p_files + q_files)) # get list of uniques, no errs handled
    for file in files:
        p_tmp = p_df.loc[p_df['file_name'] == str(file)] # subset by file
        q_tmp = q_df.loc[q_df['file_name'] == str(file)] # subset by file
        for label in annotation_values:
            kappa = cohen_kappa_score(p_tmp[label], q_tmp[label])
            row = {
                "Summary Level":file,
                "Label":label,
                "Cohen's Kappa": round(kappa, 3)
                }
            new_rows.append(row)
    return(pd.DataFrame(new_rows))


def get_label_counts(p_df, q_df, annotation_values):
    """ get dataframe with counts for each label """
    new_rows = []
    for label in annotation_values:
        row = {
            "Summary Level":"All Files",
            "Label":label,
            "Rater (p) n Annotations": sum(p_df[label]),
            "Rater (q) n Annotations": sum(q_df[label]),
            }
        new_rows.append(row)
    df = pd.DataFrame(new_rows)
    df['Total Sentences'] = len(p_df)
    return(df)


def get_label_counts_by_file(p_df, q_df, annotation_values):
    """ get dataframe with counts for each label by file """
    new_rows = []
    p_files = list(p_df['file_name'].unique())
    q_files = list(q_df['file_name'].unique())
    files = list(set(p_files + q_files)) # get list of uniques, no errs handled
    for file in files:
        p_tmp = p_df.loc[p_df['file_name'] == str(file)] # subset by file
        q_tmp = q_df.loc[q_df['file_name'] == str(file)] # subset by file
        for label in annotation_values:
            row = {
                "Summary Level":file,
                "Label":label,
                "Rater (p) n Annotations": sum(p_tmp[label]),
                "Rater (q) n Annotations": sum(q_tmp[label]),
                "Total Sentences": len(p_tmp)
                }
            new_rows.append(row)
    return(pd.DataFrame(new_rows))


def print_agreement_summary(p_df, q_df, annotation_values):
    """ print summary to screen """
    total_df = get_total_agreement(p_df, q_df, annotation_values)
    by_file_df = get_agreement_by_file(p_df, q_df, annotation_values)
    summary_df = pd.concat([total_df, by_file_df], ignore_index=True)
    print(tabulate(summary_df, headers='keys', tablefmt='fancy_grid', showindex=False))


def sort_by_label(df):
    """ sort a dataframe by the label values """
    df['tmp'] = df['Label'].str.replace("Q", "").replace("blank", "0").astype(int)
    df = df.sort_values(by=['tmp'])
    df = df.drop(['tmp'], axis=1)
    return(df)


def write_agreement_summary(p_df, p_name, q_df, q_name, annotation_values):
    """ write out excel sheet with agreement notes """

    # get summary objects
    print('Making Kappa summary object...')
    total_df = get_total_agreement(p_df, q_df, annotation_values)
    total_df = sort_by_label(total_df)
    by_file_df = get_agreement_by_file(p_df, q_df, annotation_values)
    by_file_df = sort_by_label(by_file_df)
    summary_df = pd.concat([total_df, by_file_df], ignore_index=True)

    print('Making summary statistics object...')
    total_label_df = get_label_counts(p_df, q_df, annotation_values)
    total_label_df = sort_by_label(total_label_df)
    labels_by_file_df = get_label_counts_by_file(p_df, q_df, annotation_values)
    labels_by_file_df = sort_by_label(labels_by_file_df)
    label_summary_df = pd.concat([total_label_df, labels_by_file_df], ignore_index=True)

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

    # write excel object to output folder
    save_path = 'outputs/annotation_summary' + get_date() + '.xlsx'

    print('Writing to Excel...')
    with pd.ExcelWriter(save_path, engine='xlsxwriter', mode='w') as writer:
        summary_df.to_excel(writer, sheet_name='Kappa Summary Statistics', index=False)
        annotation_map_df.to_excel(writer, sheet_name='Annotation Map', index=False)
        label_summary_df.to_excel(writer, sheet_name='Label Statistics', index=False)

        # conditionally format the disagreemets
        workbook  = writer.book
        map_worksheet = writer.sheets['Annotation Map']

        format1 = workbook.add_format({'bg_color':   '#FFC7CE',
                                   'font_color': '#9C0006'})

        cell_range = 'D1:D' + str(len(annotation_map_df))

        map_worksheet.conditional_format(cell_range, {'type':     'cell',
                                                  'criteria': 'equal to',
                                                  'value':    '"No"',
                                                  'format': format1})

        writer.save()

    print('DONE. Wrote output to: ', save_path)


if __name__ == '__main__':
    program_description = "A command-line tool to calculate kappa values based \
    on CLAMP annotations."
    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument("--p", help="directory of annotations for annotator 1")
    parser.add_argument("--q", help="directory of annotations for annotator 2")
    parser.add_argument("--print", action='store_true', \
                help="if present: print output to console")
    args = parser.parse_args()

    p_name = get_rater_name_from_input_arg(args.p)
    q_name = get_rater_name_from_input_arg(args.q)

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

    # optional, print report to cli
    if args.print:
        print_agreement_summary(p_df, q_df, annotation_values)

    # write report
    write_agreement_summary(p_df, p_name, q_df, q_name, annotation_values)
