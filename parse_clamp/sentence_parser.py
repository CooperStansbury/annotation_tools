"""
Customer parsing functions from Huy Anh Pham
"""

# non-local imports
import re
import spacy


def prevent_sentence_boundaries(doc):
    """ Custom pipeline to un-split sentences """
    for token in doc:
        if not can_be_sentence_start(token):
            token.is_sent_start = False
    return(doc)


def can_be_sentence_start(token):
    """ boolean operation to detect sentence starts """
    if token.i > 0 and (token.nbor(-1).text == '_' or \
            token.nbor(-1).text == '•' or \
            token.nbor(-1).text == 'o' or \
            token.nbor(-1).text == '"'):
        return(False)
    return(True)


def custom_sentencizer(doc):
    """ Custom pipeline to customize sentence splitting """
    for i, token in enumerate(doc[:-1]):
        # Define sentence start if pipe + titlecase token
        if not doc[i].is_ascii and doc[i+1].is_title:
            doc[i].is_sent_start = True

        if (token.text[-1] == "." or token.text[-1] == "!" or token.text[-1] == "?") and doc[i+1].is_title:
            doc[i+1].is_sent_start = True

        if token.text[-1] == ':' and doc[i+1].text == '\n':
            doc[i+1].is_sent_start = True

        if token.text.isspace() and doc[i+1].is_title:
            doc[i + 1].is_sent_start = True

        if token.text.count('\n') > 1:
            doc[i + 1].is_sent_start = True

        if token.text.isupper() and doc[i+1].is_upper:
            doc[i + 1].is_sent_start = False

        if (token.text[-1] == "." or token.text[-1] == "!" or token.text[-1] == "?") and (doc[i+1].text == '”' or doc[i+1].text == '"'):
            doc[i+1].is_sent_start = False

        if token.text == ':':
            token.is_sent_start = False

        if doc[i].is_sent_start and doc[i+1].is_title:
            doc[i+1].is_sent_start = False

        if token.text.isdigit() and not doc[i+1].is_space:
            doc[i+1].is_sent_start = False

        if token.text == "." and doc[i-1].is_digit and not doc[i+1].is_space:
            doc[i+1].is_sent_start = False

        if token.text == "." and doc[i-1].is_digit and doc[i+1].is_space and doc[i+2].is_title:
            doc[i+2].is_sent_start = False

    return(doc)
