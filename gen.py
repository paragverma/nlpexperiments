from nltk.parse.stanford import StanfordDependencyParser
import re
import graphd
import csv
import nltk
from nltk import word_tokenize




# 0: Root
# 1: Type of Word
# 2: Modifier Relation
class GTree(object):
	def __init__(self, modif=None, typ=0, ret=False):
		self.children = {}
		self.modifier = modif
		self.type = typ
		self.ret = ret
		self.tag = ""
	
	def printTree(self, index=0):
	
		for i in range(index):
			print("\t", end='')
		
		print(str(self.modifier) + "|" + str(self.ret) + "|" + str(self.tag))
		index += 1
		
		for ch in self.children:
			#print(ch)
			self.children[ch].printTree(index)
		
root = GTree()

eparts = ['a', 'an', 'is', 'the', 'and']
def find_shortest_path(graph, start, end, path=[]):
		path = path + [start]
		if start == end:
			return path
		if not start in graph:
			return None
		shortest = None
		for node in graph[start]:
			if node not in path:
				newpath = find_shortest_path(graph, node, end, path)
				if newpath:
					if not shortest or len(newpath) < len(shortest):
						shortest = newpath
		return shortest


dependency_parser = StanfordDependencyParser()

def getkey(item):
		return len(item)


finit = 0
with open("canc.tsv") as tsv:

	for line in csv.reader(tsv, dialect="excel-tab"):
		
		if finit == 0:
			finit += 1
			continue
		
		#print(line)

		u_inp = line[0]

		options = []
		options.append(line[1])
		options.append(line[2])
		options.append(line[3])
		options.append(line[4])
		options.append(line[5])
		options.append(line[6])


		# is good
		# is __
		# banal one
		#
		#
		fw = ""
		for w in options[1].split(" "):
			if w in eparts:
				u_inp = u_inp.replace("__", eparts[eparts.index(w)] + " __")
			else:
				options[1] = w
			
		u_inp_m = u_inp.replace("__", options[1])

		u_inp = line[10]
		
		#print(u_inp_m)

		imp_parts = re.findall(r"\*[^\*]*\*", u_inp)

		for i in range(len(imp_parts)):
			imp_parts[i] = imp_parts[i][1:-1]

		#print(imp_parts)
		print(u_inp_m)
		print(u_inp)
		
		result = dependency_parser.raw_parse(u_inp_m)
		dep = result.__next__()
		i_graph = list(dep.triples())

		#print(i_graph)

		graph = {}

		for node in i_graph:
			#print(node[0][0] + " " + node[2][0])
			
			if node[0][0] == options[1]:
				start = node[0][0] + "_" + node[0][1]
				
			if node[2][0] == options[1]:
				start = node[2][0] + "_" + node[2][1]
				
			if node[0][0] in imp_parts:
				imp_parts[imp_parts.index(node[0][0])] = node[0][0] + "_" + node[0][1]
			
			if node[2][0] in imp_parts:
				imp_parts[imp_parts.index(node[2][0])] = node[2][0] + "_" + node[2][1]
			
			el1 = node[0][0] + "_" + node[0][1]
			el2 = node[2][0] + "_" + node[2][1]
			
			if el1 not in graph:
				graph[el1] = {}
			if el2 not in graph:
				graph[el2] = {}
			
			graph[el1][el2] = node[1]
			graph[el2][el1] = node[1]

		print(options)
		print(imp_parts)
		print(start)

		i_rules = []
		i_seq = []
		
		#print(graph)
		#print(spg)

		for j in range(len(imp_parts)):
			spg = find_shortest_path(graph, start, imp_parts[j])
			t = []
			i_seq.append(spg)
			for i in range(len(spg) - 1):
				t.append(graph[spg[i]][spg[i + 1]])
			i_rules.append(t)
	
		i_rules.sort(key=getkey)
		i_seq.sort(key=getkey)

		print(i_rules)
		print(i_seq)

		currnode = root

		for i in range(len(i_rules)):
		
			#proper pos bucket
			currnode = root
			wtype = i_seq[i][0].split("_")[1]
			if wtype in currnode.children:
				currnode = root.children[wtype]
			else:
				node = GTree(wtype ,1)
				currnode.children[wtype] = node
				currnode = currnode.children[wtype]
			
			j = 1
			print(len(i_rules[i]))
			for rl in i_rules[i]:
				
				#tf = True if rl is last rule
				tf = i_rules[i].index(rl) == (len(i_rules[i]) - 1)
				tf = (j == len(i_rules[i]))
				print("index: " + str(i_rules[i].index(rl)) + " last: " + str((len(i_rules[i]) - 1)) + " j: " + str(j)) 
				
				if rl in currnode.children:
					currnode = currnode.children[rl]
				else:
					if tf == True:
						node = GTree(rl, 2, True)
						node.tag = i_seq[i][j].split("_")[1]
					else:
						print(rl + " |rule not last " + i_seq[i][j] + "| " + i_rules[i][len(i_rules[i]) - 1])
						node = GTree(rl, 2)
						
					currnode.children[rl] = node
					currnode = currnode.children[rl]
				j += 1
		
#print(root.children['JJ'].children['parataxis'].children['ccomp'].type)

root.printTree()


