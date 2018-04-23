import json
import nltk
import math
import re
from pycorenlp import StanfordCoreNLP
from textblob import TextBlob
from nltk.corpus import wordnet
#defining regex for matching POS tags of Noun, Adjective and Verb
pattern_noun = r'^[N]{2}(S|P|PS)?$'
pattern_adj = r'^[J]{2}(R|S)?$'
pattern_verb = r'^VB(D|G|N|P|Z)?$'
pattern_adverb = r'^RB(R|S)?$'

def getAntonym(word):
    word = str(word)
    max = 999999
    desirable = ""
    polarity = math.fabs(TextBlob(word).sentiment.polarity)
    antonyms = []
    synonyms = []
    definition = []
    syns = wordnet.synsets(word)
    ##Extracting Lemmatized list of antonyms of given word
    for each in syns:
        definition.append(each.definition())
        for l in each.lemmas():
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    for ind_word in antonyms:
        blob_wrapped_word = TextBlob(ind_word)
        ind_rating = blob_wrapped_word.sentiment.polarity
        diff = math.fabs(polarity - math.fabs(ind_rating))
        if(diff < max):
            max = diff
            desirable = ind_word
    return desirable

def insert_asp_sent(asp,sent,asp_sent):
    if asp not in asp_sent:
        asp_sent[asp] = []
    asp_sent[asp].append(sent)
    return asp_sent

def existsNegative(adj,negatives):
    if adj not in negatives:
        return False
    return True

def getAntonym(word):
    word = str(word)
    max = 999999
    desirable = ""
    polarity = math.fabs(TextBlob(word).sentiment.polarity)
    antonyms = []
    synonyms = []
    definition = []
    syns = wordnet.synsets(word)
    ##Extracting Lemmatized list of antonyms of given word
    for each in syns:
        definition.append(each.definition())
        for l in each.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    ##Finding desirable word
    for ind_word in antonyms:
        blob_wrapped_word = TextBlob(ind_word)
        ind_rating = blob_wrapped_word.sentiment.polarity
        diff = math.fabs(polarity - math.fabs(ind_rating))
        if(diff < max):
            max = diff
            desirable = ind_word
    return desirable

def testConj(noun,adj,pos_dict,rel_dict,neg,asp_sent):
    if 'conj' in rel_dict:
        conj_arr = rel_dict.get('conj')
        for j in conj_arr:
            temp_gov = j['gov']
            temp_dep = j['dep']
            if temp_gov == adj:
                if existsNegative(temp_dep,neg):
                    new_adj = getAntonym(temp_dep)
                    asp_sent = insert_asp_sent(noun,new_adj,asp_sent)
                else:
                    asp_sent = insert_asp_sent(noun,temp_dep,asp_sent)
    if existsNegative(adj,neg):
        new_adj = "not "+adj
        asp_sent = insert_asp_sent(noun,new_adj,asp_sent)
    else:
        asp_sent = insert_asp_sent(noun,adj,asp_sent)
    return asp_sent

def testCompound(noun,adj,pos_dict,rel_dict,neg,asp_sent):
    if 'compound' in rel_dict:
        compound_arr = rel_dict.get('compound')
        for j in compound_arr:
            temp_gov = j['gov']
            temp_dep = j['dep']
            if temp_gov == noun and re.match(pattern_noun,pos_dict[temp_dep]):
                if existsNegative(adj,neg):
                    neg_adj = getAntonym(adj)
                    new_adj = neg_adj+" "+temp_dep
                else:
                    new_adj = adj+" "+temp_dep
                asp_sent = insert_asp_sent(noun,new_adj,asp_sent)
    return asp_sent

def testAdvModAdj(noun,adj,pos_dict,rel_dict,neg,asp_sent):
    if 'advmod' in rel_dict:
        advmod_arr = rel_dict.get('advmod')
        for j in advmod_arr:
            temp_gov = j['gov']
            temp_dep = j['dep']
            if temp_gov == adj and re.match(pattern_adverb,pos_dict[temp_dep]):
                if existsNegative(adj,neg):
                    neg_adj = getAntonym(adj)
                    new_adj = temp_dep+" "+neg_adj
                else:
                    new_adj = temp_dep+" "+adj
                asp_sent = insert_asp_sent(noun,new_adj,asp_sent)
    return asp_sent

def testConjVerb(noun,verb,pos_dict,rel_dict,neg,asp_sent):
    if existsNegative(verb,neg):
        new_adj = getAntonym(verb)
    else:
        new_adj = verb

    if 'conj' in rel_dict:
        conj_arr = rel_dict.get('conj')
        for j in conj_arr:
            temp_gov = j['gov']
            temp_dep = j['dep']

        if temp_gov == noun and re.match(pattern_noun,pos_dict[temp_dep]):
            insert_asp_sent(temp_dep,new_adj,asp_sent)

    insert_asp_sent(noun,new_adj,asp_sent)
    return asp_sent

def testXcompAcomp(noun,verb,pos_dict,rel_dict,neg,asp_sent):
    comp_arr = ''
    if 'xcomp' in rel_dict:
        comp_arr = rel_dict.get('xcomp')
    elif 'acomp' in rel_dict:
        comp_arr = rel_dict.get('acmop')

    if comp_arr != '':
        for j in comp_arr:
            temp_gov = j['gov']
            temp_dep = j['dep']
            if temp_gov == verb:
                asp_sent = testConj(noun,temp_dep,pos_dict,rel_dict,neg,asp_sent)
                asp_sent = testCompound(noun, temp_dep, pos_dict, rel_dict, neg, asp_sent)
                asp_sent = testAdvModAdj(noun, temp_dep, pos_dict, rel_dict, neg, asp_sent)
    return asp_sent

def testAdvmod(noun,verb,pos_dict,rel_dict,neg,asp_sent):
    if 'advmod' in rel_dict:
        advmod_arr = rel_dict.get('advmod')
        for j in advmod_arr:
            temp_gov = j['gov']
            temp_dep = j['dep']
            if temp_gov == verb:
                asp_sent = testConj(noun,temp_dep,pos_dict,rel_dict,neg,asp_sent)
                asp_sent = testCompound(noun,temp_dep,pos_dict,rel_dict,neg,asp_sent)
                asp_sent = testAdvModAdj(noun,temp_dep,pos_dict,rel_dict,neg,asp_sent)
    return asp_sent

def amodRules(gov,dep,pos_dict,rel_dict,neg,asp_sent):
    if (re.match(pattern_adj,pos_dict[dep]) or re.match(pattern_verb,pos_dict[dep])) and re.match(pattern_noun,pos_dict[gov]):
        asp_sent = testConj(gov,dep,pos_dict,rel_dict,neg,asp_sent)
        asp_sent = testCompound(gov,dep,pos_dict,rel_dict,neg,asp_sent)
        asp_sent = testAdvModAdj(gov,dep,pos_dict,rel_dict,neg,asp_sent)
    return asp_sent

def nsubjRules(gov,dep,pos_dict,rel_dict,neg,asp_sent):
    if re.match(pattern_adj,pos_dict[gov]) and re.match(pattern_noun,pos_dict[dep]):
        asp_sent = testConj(dep, gov, pos_dict, rel_dict, neg, asp_sent)
        asp_sent = testCompound(dep, gov, pos_dict, rel_dict, neg, asp_sent)
        asp_sent = testAdvModAdj(dep, gov, pos_dict, rel_dict, neg, asp_sent)

    elif re.match(pattern_verb,pos_dict[gov])and re.match(pattern_noun,pos_dict[dep]):
        asp_sent = testXcompAcomp(dep,gov,pos_dict,rel_dict,neg,asp_sent)
        asp_sent = testAdvmod(dep,gov,pos_dict,rel_dict,neg,asp_sent)
    return asp_sent

def aclReclRules(gov,dep,pos_dict,rel_dict,neg,asp_sent):
    if re.match(pattern_noun,pos_dict[gov]) and (re.match(pattern_adj,pos_dict[dep]) or re.match(pattern_verb,pos_dict[dep])):
        asp_sent = testConj(gov,dep,pos_dict,rel_dict,neg,asp_sent)
        asp_sent = testCompound(gov,dep,pos_dict,rel_dict,neg,asp_sent)
        asp_sent = testAdvModAdj(gov,dep,pos_dict,rel_dict,neg,asp_sent)
    return asp_sent

def dobjRules(gov,dep,pos_dict,rel_dict,neg,asp_sent):
    if re.match(pattern_verb,pos_dict[gov]) and re.match(pattern_noun,pos_dict[dep]):
        asp_sent = testConjVerb(dep,gov,pos_dict,rel_dict,neg,asp_sent)
    return asp_sent

# def nsubjpassRules(gov,dep,pos_dict,rel_dict,neg,asp_sent):
#     if re.match(pattern_verb,pos_dict[gov]) and re.match(pattern_noun,pos_dict[dep]):
#         asp_sent = testConjNpssVerb(dep,gov,pos_dict,rel_dict,neg,asp_sent)
#     return asp_sent