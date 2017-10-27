from PyDictionary import PyDictionary
import csv
def get_synonym(original_word):
    try:
        data_list = list(csv.reader(open("Newfrequency.csv")))
        # print(data_list)
        synonyms = []
        # antonyms = []
        dictionary = PyDictionary()

        synonyms = dictionary.synonym(original_word)
        #print(set(synonyms))
        max = 0
        best_synonym = original_word
        rdict = {}
        for s in set(synonyms):

            for word, count in data_list:
                if word == s:
                    #print(word, count)
                    rdict[s] = count
                    if(int(count)>max):
                        best_synonym = word
                        max = int(count)
        #print(rdict.items())
        return rdict, best_synonym
     
    except Exception as exception:
        #print(type(exception).__name__)
        #print(original_word)
        print("")