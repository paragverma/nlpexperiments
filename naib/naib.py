from nltk.parse.stanford import StanfordDependencyParser
import csv
from nltk import word_tokenize

dependency_parser = StanfordDependencyParser()

def headWord(i_graph):
	wdic = {}
	
	for t in i_graph:
		l_word = t[0][0] + "_" + t[0][1]
		r_word = t[2][0] + "_" + t[2][1]
		if l_word not in wdic:
			wdic[l_word] = {}
			wdic[l_word]['in'] = False
		if r_word not in wdic:
			wdic[r_word] = {}

		wdic[r_word]['in'] = True
		
	for w in wdic:
		if wdic[w]['in'] == False:
			return w
ofile = open("out.tsv", "w")

c_file = open("contrast_words.txt", "r")

contr_set = set()
for line in c_file.readlines():
	contr_set.add(line.lower().split("\n")[0])
print (contr_set)
c_file.close()

c_file = open("contin_words.txt", "r")
conti_set = set()
for line in c_file.readlines():
	conti_set.add(line.lower().split("\n")[0])
print (conti_set)

b_set = conti_set.union(contr_set)
print(b_set)

with open("sat.tsv") as tsv:
	i = 0
	for line in csv.reader(tsv, dialect="excel-tab"):
		if i == 0:
			i += 1
			ofile.write("Sentence\tRW\tHW\tKI\tRWtoHW\tRWtoKI\n")
			continue
		sent = line[0].replace("______", line[6])
		i += 1
		print(i)
		print (sent)
		
			
		result = dependency_parser.raw_parse(sent)
		dep = result.__next__()
		i_graph = list(dep.triples())
		
		#print(i_graph)
		
		head_word = headWord(i_graph)
		
		print(head_word)
		
		ofile.write(sent)
		ofile.write("\t")
		
		ofile.write(line[6])
		ofile.write("\t")
		
		head_word = head_word.split("_")[0]
		ofile.write(head_word)
		ofile.write("\t")
		
		#Contrast or Continuity Word
		cwflag = 0
		keyin = ""
		for cw in b_set:
			cw = cw.lower()
			if len(cw.split(" ")) > 1:
				if cw in sent.lower():
					
					ofile.write(cw)
					ofile.write("\t")
					keyin = cw
					cwflag = 1
					break
			else:
				st1 = cw + " "
				st2 = " " + cw
				if st1 in sent.lower() or st2 in sent.lower():
					ofile.write(cw)
					ofile.write("\t")
					keyin = cw
					cwflag = 1
					break

		if cwflag == 0:
			kipres = 0
			ofile.write("notpresent")
			ofile.write("\t")
		
		slist = word_tokenize(sent)
		
		rwtohw = ""
		state = 0
		for sl in slist:
			if sl.lower() == head_word.lower() or sl.lower() == line[6].lower():
				state += 1
				if state >= 2:
					break
				continue
			
			if state > 0:
				rwtohw = rwtohw + sl + " "
		
		ofile.write(rwtohw)
		ofile.write("\t")
			
		rwtoki = ""
		
		state = 0
		for sl in slist:
			if sl.lower() == keyin or sl.lower() == line[6].lower():
				#print("marked")
				state += 1
				if state >= 2:
					break
				if cwflag == 0 and state >= 1:
					break
				continue
			
			if state > 0 or cwflag == 0:
				rwtoki = rwtoki + sl + " "
		
		#print(rwtoki)
		ofile.write(rwtoki)
		ofile.write("\t")
		
		
		
		
		
		ofile.write("\n")
		if i > 50:
			break