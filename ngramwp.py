from nltk.corpus import brown
from nltk import bigrams, trigrams
from collections import Counter, defaultdict
from nltk import word_tokenize
import operator
import string

i = 0

subset = []
punct = set(string.punctuation)

for i in range(0, 150):
	sd = brown.sents()[i]
	for el in sd:
		if el in punct:
			sd.remove(el)
	subset.append(sd)

model = defaultdict(lambda: defaultdict(lambda: 0))

for sentence in subset:
    print(sentence)
    for w1, w2, w3 in trigrams(sentence, pad_right=True, pad_left=True):
        model[(w1, w2)][w3] += 1


		
for w1_w2 in model:
    total_count = float(sum(model[w1_w2].values()))
    for w3 in model[w1_w2]:
        model[w1_w2][w3] /= total_count

modelb = defaultdict(lambda: defaultdict(lambda: 0))

for sentence in subset:
	for w1, w2 in bigrams(sentence, pad_right=True, pad_left=True):
		modelb[w1][w2] += 1

for w in modelb:
	tot_count = float(sum(modelb[w].values()))
	for wn in modelb[w]:
		modelb[w][wn] /= tot_count

query = input("Enter Sentence: ")

query = word_tokenize(query)

queryb = query[-1]
queryt = query[-2:]

i = 0

listri = sorted(model[(queryt[0], queryt[1])].items(), key=operator.itemgetter(1), reverse=True)

listbi = sorted(modelb[queryb].items(), key=operator.itemgetter(1), reverse=True)

print(listri)
print(listbi)