"""
Functions adapted from Huy Anh Pham
"""

# non-local imports
import xml.dom.minidom
import os
from os.path import isfile, join
import spacy

# local imports
import sentence_parser as sp

# ------------------------------- set up spacy ------------------------------- #
nlp = spacy.load("en_core_web_sm")

# use custom sentence coundary detection and parsing
nlp.add_pipe(sp.prevent_sentence_boundaries, before='parser')
nlp.add_pipe(sp.custom_sentencizer, before="parser")


def get_sentence_list(doc, xmi_str):
    """ return start, end, and spam for each sentence based on spacy parsing """
    sentences = []
    for sent in doc.sents:
        start = sent.start_char
        end = sent.end_char
        while xmi_str[start:end][-1:].isspace() or \
                xmi_str[start:end][:1].isspace():

            if xmi_str[start:end][-1:].isspace():
                end = end - 1
            if xmi_str[start:end][:1].isspace():
                start = start + 1
        sentences.append([start, end, xmi_str[start:end]])
    return(sentences)


def get_annoations(UIMA, xmi_str):
    """ return tags from UIMA object and xmi_str values """
    tagend = []
    tagstart = []

    annotation = {}
    annotation['start'] = {}
    annotation['end'] = {}

    for i in range(0, len(UIMA)):
        semanticTag = UIMA[i].getAttribute('semanticTag').split('_')[0]
        start = int(UIMA[i].getAttribute('begin'))
        end = int(UIMA[i].getAttribute('end'))

        while xmi_str[start:end][-1:].isspace() or \
                 xmi_str[start:end][:1].isspace():

            if xmi_str[start:end][-1:].isspace():
                end = end - 1
            if xmi_str[start:end][:1].isspace():
                start = start + 1

        tagstart.append(start)
        tagend.append(end)

        if start in annotation['start']:
            annotation['start'][start].append(semanticTag)
        else:
            annotation['start'][start] = [semanticTag]

        if end in annotation['end']:
            annotation['end'][end].append(semanticTag)
        else:
            annotation['end'][end] = [semanticTag]

        if semanticTag in annotation:
            annotation[semanticTag].append((start, end))
        else:
            annotation[semanticTag] = [(start, end)]
    return(annotation)


def get_evaluation_list(sentences, annotation):
    """ return joined list of sentences and annotation """
    tag = 'O'
    marker = 0
    taglist = []
    evaluationlist = []
    for value in sentences:
        for svalue in annotation['start']:
            if value[0] <= svalue < value[1]:
                taglist = list(set(taglist + annotation['start'][svalue]))
        evaluationlist.append([value[2], taglist])
        for evalue in annotation['end']:
            if value[0] < evalue <= value[1]:
                taglist = list(set(taglist) - set(annotation['end'][evalue]))
    return(evaluationlist)


def xmi_tag(xmifile):
    """ function to parse xmi file and return nested list of
    sentences and annotations """
    dom = xml.dom.minidom.parse(xmifile)
    xmlFile = dom.documentElement
    casSofa = xmlFile.getElementsByTagName('cas:Sofa')
    xmi_string = casSofa[0].getAttribute('sofaString')
    textspan = xmlFile.getElementsByTagName('textspan:Sentence')
    clampNameEntityUIMA = xmlFile.getElementsByTagName('typesystem:ClampNameEntityUIMA')
    doc = nlp(xmi_string)
    sentences = get_sentence_list(doc, xmi_string)
    annotation = get_annoations(clampNameEntityUIMA, xmi_string)
    return(get_evaluation_list(sentences, annotation))


def parse_xmi_dir(dir_path):
    """ parse input args (directories) and return data struture with
    annotations """
    print("Parsing ", dir_path)
    file_name_and_annotations_list = []
    for subdir, dirs, files in os.walk(dir_path):
        for file in files:
            filepath = subdir + os.sep + file
            if str(filepath).endswith(".xmi"):
                p_list = xmi_tag(filepath)
                tup = (file, p_list)
                file_name_and_annotations_list.append(tup)

    return(file_name_and_annotations_list)
