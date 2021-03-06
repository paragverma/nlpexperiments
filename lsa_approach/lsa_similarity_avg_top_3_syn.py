import argparse
import os
import string
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
import numpy as np
import time
import csv
import random
import glob
import pickle
import re
from scipy import spatial
import best_synonym
import operator

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='./data/Holmes_Training_Data/',
                        help='data directory containing input data')
    parser.add_argument('--output_dir', type=str, default='./lsa_similarity/',
                        help='directory for outputs')
    parser.add_argument('--test_file', type=str, default='./data/testing_data.csv',help='testing data path')
    args = parser.parse_args()
    return args

def clean_str(string):
    
        string = re.sub(r"\[([^\]]+)\]", " ", string)
        string = re.sub(r"\(([^\)]+)\)", " ", string)
        string = re.sub(r"[^A-Za-z,!?.;]", " ", string)
        string = re.sub(r",", " , ", string)
        string = re.sub(r"!", " ! ", string)
        string = re.sub(r"\?", " ? ", string)
        string = re.sub(r";", " ; ", string)
        string = re.sub(r"\s{2,}", " ", string)
        return string.strip().lower()

def preprocess(input_files, data_path):
    all_corpus = []
    for input_file in input_files:
        with open(input_file, "r", encoding='utf-8', errors='ignore') as f:
            print("Preprocessing {}".format(input_file))
            
            corpus = f.read()

            corpus = clean_str(corpus)
            sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=[.?;!])\s",corpus)
            clean_sent = []
            for sent in sentences:
                translator = str.maketrans('','',string.punctuation)
                s = sent.translate(translator)
                tokens = s.strip().split()
                important_words = []
                for word in tokens:
                    if word  not in stopwords.words('english'):
                        important_words.append(word)
                if len(important_words) > 5:
                    clean_sent.append(" ".join(important_words)) 
        all_corpus += clean_sent


    with open(data_path, 'wb') as f:
        pickle.dump(all_corpus, f)

    print("Saved clean corpus at {}".format(data_path))

    return all_corpus
    
def load_train(data_dir,save_dir):
    input_files = glob.glob(os.path.join(data_dir, "*.TXT"))
   
    data_file = os.path.join(save_dir, 'clean_data.pkl')
    

    if os.path.exists(data_file): 
        print("Loading preprocessed training data")
        with open(data_file, 'rb') as f:
            clean_corpus = pickle.load(f)
    else: 
        print("Processing training data")
        clean_corpus = preprocess(input_files, data_file)

    return clean_corpus

def build_lsa_feature(corpus, save_dir):
    #dict_file now has path of word_dictionary pickle file
    dict_file = os.path.join(save_dir, 'lsa_word_dict.pkl')
    if os.path.exists(dict_file):
        print("Loading LSA word dictionary")
        with open(dict_file,'rb') as f:
            word_dict = pickle.load(f)
    else:
        print("Building word features with LSA")
    #word_dict has the actual word dictionary
        vectorizer = CountVectorizer(analyzer = 'word', tokenizer = None, preprocessor= None, stop_words = None, max_features = 14000)
        bow_features = vectorizer.fit_transform(corpus)

        lsa = TruncatedSVD(500, algorithm = 'arpack')
        word_features = lsa.fit_transform(bow_features.T)
        word_features = Normalizer(copy=False).fit_transform(word_features)
        
        vocabulary = vectorizer.get_feature_names()
        word_dict = {}
        for i, word in enumerate(vocabulary):
            word_dict[word] = word_features[i]

        with open(dict_file, 'wb') as f:
            pickle.dump(word_dict, f)

    return word_dict


# the second argument passed here usually is word_dict
def word2feature(tokens, embeddings):
    dim = embeddings['word'].size

    word_vec = []
    for word in tokens:
        if word in embeddings:
            word_vec.append(embeddings[word])
        else:
            word_vec.append(np.random.uniform(-0.25,0.25,dim))
    return word_vec

def total_similarity(vec, ques_vec):
    score = 0
    for v in ques_vec:
        score += (1 - spatial.distance.cosine(vec, v))

    return score

if __name__ == '__main__':
    start = time.time()

    args = parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    corpus = load_train(args.data_dir, args.output_dir)
    #corpus now contains the processed corpus, or preprocessed, depending on whether processing has taken place
    print("Total training sentences: {}".format(len(corpus)))

    word_dict = build_lsa_feature(corpus, args.output_dir)

    

    keys = ['a)', 'b)', 'c)', 'd)', 'e)']
    choices = ['a', 'b', 'c', 'd', 'e']
    prediction = []

    k = 0
    print("Predicting answers")
    with open(args.test_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            k += 1
            print("Row: " + str(k))
            if k > 5:
                break

            question = row['question']
            translator = str.maketrans('','',string.punctuation)
            question = question.translate(translator)
            tokens = question.split()
            
            # tokens has the tokens of the current question
            # ques_vec is current question sentence vector
            
            # word2feature function is taking arguments as 1. tokens of the sentence 2. word dictionary (word_dict)
            # it returns the vector of the tokens given
            ques_vec = word2feature(tokens, word_dict)

            # calculate total word similarity
            
            scoressuper = []
            #yaha tak same for all
			
            op1syndict = {}
            op2syndict = {}
            op3syndict = {}
            op4syndict = {}
            op5syndict = {}
			
            op1top3syns = []
            op2top3syns = []
            op3top3syns = []
            op4top3syns = []
            op5top3syns = []
			
            op1fine = True
            op2fine = True
            op3fine = True
            op4fine = True
            op5fine = True
			
            # row is dict of current row in csv file
			
            roptions = [row[x] for x in keys]
			
            i = 0
            for op in roptions:
                try:
                    syn_dict, best_syn = best_synonym.get_synonym(op)
                except Exception as exception:
                    if i == 0:
                        op1fine = False
                        i += 1
                        continue
                    if i == 1:
                        op2fine = False
                        i += 1
                        continue
                    if i == 2:
                        op3fine = False
                        i += 1
                        continue
                    if i == 3:
                        op4fine = False
                        i += 1
                        continue
                    if i == 4:
                        op5fine = False
                        i += 1
                        continue


                if i == 0:
                    op1syndict = syn_dict
                if i == 1:
                    op2syndict = syn_dict
                if i == 2:
                    op3syndict = syn_dict
                if i == 3:
                    op4syndict = syn_dict
                if i == 4:
                    op5syndict = syn_dict

                i += 1

            
            # If checks are for conditions when there are no synonyms in the api
            
            i = 0
            if op1fine == True:
                for key, value in sorted(op1syndict.items(), key = operator.itemgetter(1), reverse=True):
                    i += 1
                    if i > 3:
                        break
                    op1top3syns.append(key)
                    
                #Case when number of synonyms are less than 5
                #Just simply appending the first element
                if i < 4 and i != 0:
                    j = 3 - i
                    while j > 0:
                        op1top3syns.append(op1top3syns[0])
                        j += -1
                
                #Case when api returns 0 results
                if i == 0:
                    j = 0
                    while j < 5:
                        op1top3syns.append(roptions[0])
                        j += 1
            else:
                op1top3syns.append(roptions[0])
                op1top3syns.append(roptions[0])
                op1top3syns.append(roptions[0])
            
            
            i = 0
            if op2fine == True:
                for key, value in sorted(op2syndict.items(), key = operator.itemgetter(1), reverse=True):
                    i += 1
                    if i > 3:
                        break
                    op2top3syns.append(key)
                    
                #Case when number of synonyms are less than 5
                #Just simply appending the first element of sorted
                if i < 4 and i != 0:
                    j = 3 - i
                    while j > 0:
                        op2top3syns.append(op2top3syns[0])
                        j += -1
                
                #Case when api returns 0 results
                if i == 0:
                    j = 0
                    while j < 5:
                        op2top3syns.append(roptions[1])
                        j += 1
            else:
                op2top3syns.append(roptions[1])
                op2top3syns.append(roptions[1])
                op2top3syns.append(roptions[1])

                
            i = 0
            if op3fine == True:
                for key, value in sorted(op3syndict.items(), key = operator.itemgetter(1), reverse=True):
                    i += 1
                    if i > 3:
                        break
                    op3top3syns.append(key)
                    
                #Case when number of synonyms are less than 5
                #Just simply appending the first element
                if i < 4 and i != 0:
                    j = 3 - i
                    while j > 0:
                        op3top3syns.append(op3top3syns[0])
                        j += -1
                
                #Case when api returns 0 results
                if i == 0:
                    j = 0
                    while j < 5:
                        op3top3syns.append(roptions[2])
                        j += 1
            else:
                op3top3syns.append(roptions[2])
                op3top3syns.append(roptions[2])
                op3top3syns.append(roptions[2])


                
            i = 0
            if op4fine == True:
                for key, value in sorted(op4syndict.items(), key = operator.itemgetter(1), reverse=True):
                    i += 1
                    if i > 3:
                        break
                    op4top3syns.append(key)
                    
                #Case when number of synonyms are less than 5
                #Just simply appending the first element
                if i < 4 and i != 0:
                    j = 3 - i
                    while j > 0:
                        op4top3syns.append(op4top3syns[0])
                        j += -1
                
                #Case when api returns 0 results
                if i == 0:
                    j = 0
                    while j < 5:
                        op4top3syns.append(roptions[3])
                        j += 1
            else:
                op4top3syns.append(roptions[3])
                op4top3syns.append(roptions[3])
                op4top3syns.append(roptions[3])


            i = 0
            if op5fine == True:
                for key, value in sorted(op5syndict.items(), key = operator.itemgetter(1), reverse=True):
                    i += 1
                    if i > 3:
                        break
                    op5top3syns.append(key)
                    
                #Case when number of synonyms are less than 5
                #Just simply appending the first element
                if i < 4 and i != 0:
                    j = 3 - i
                    while j > 0:
                        print(roptions[4])
                        print(op5top3syns)
                        print(op5syndict)
                        op5top3syns.append(op5top3syns[0])
                        j += -1
                
                #Case when api returns 0 results
                if i == 0:
                    j = 0
                    while j < 5:
                        op5top3syns.append(roptions[4])
                        j += 1
            else:
                op5top3syns.append(roptions[4])
                op5top3syns.append(roptions[4])
                op5top3syns.append(roptions[4])
                
            
            
            
            
            
            

            #op1top3syns = ['hungry', 'ravenous', 'hunger']
            #                   0         1           2
            for i in range(0, 3):
                scores = []
                
                # candidates is the 5 options list, made by taking from top3 list
                #print(i)
                #print(roptions[4])
                #print(op5syndict)
                #print(op5top3syns[i])
                candidates = []
                candidates.append(op1top3syns[i])
                candidates.append(op2top3syns[i])
                candidates.append(op3top3syns[i])
                candidates.append(op4top3syns[i])
                candidates.append(op5top3syns[i])
                
                #print(question)
                #print(candidates)
                #print("\n")
            
                # candidates is just the list of options
                
                # keys = ['a)', 'b)', 'c)', 'd)', 'e)']
                # choices = ['a', 'b', 'c', 'd', 'e']
                
                # cand_vec is vector of tokens of the options
                cand_vec = word2feature(candidates, word_dict)
            
                # for every word in cand_vec, which is a vector of all the options
                for word in cand_vec:
                
                # total_similarity gives score between question vector and a word from the candidate vector
                   s = total_similarity(word, ques_vec)        
                   scores.append(s)
                
                # scores is a 5 element list
                # scoressuper is 3 elem. Total 5 x 3
                # [[p, q, r, s ,t], [a, b, c, d, e], [g, h, i, j, k]]
                scoressuper.append(scores)
            
            
            #print(scoressuper)
            scores = []
            scores.append(np.mean([scoressuper[0][0], scoressuper[1][0], scoressuper[2][0]]))
            scores.append(np.mean([scoressuper[0][1], scoressuper[1][1], scoressuper[2][1]]))
            scores.append(np.mean([scoressuper[0][2], scoressuper[1][2], scoressuper[2][2]]))
            scores.append(np.mean([scoressuper[0][3], scoressuper[1][3], scoressuper[2][3]]))
            scores.append(np.mean([scoressuper[0][4], scoressuper[1][4], scoressuper[2][4]]))
            
            # scores is a list of scores for each option
            idx = scores.index(max(scores))
            ans = choices[idx]
            prediction.append(ans)
   
    output = os.path.join(args.output_dir, "prediction_top_3_avg.csv")
    with open(output, 'w') as out:
        writer = csv.writer(out, delimiter=',')
        writer.writerow(['id','answer'])
        for i, ans in enumerate(prediction):
            writer.writerow([str(i+1), ans])
    print("Output prediction file: {}".format(output))
    
    print("Done in {:3f}s".format(time.time() - start))

