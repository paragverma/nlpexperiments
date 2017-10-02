from nltk.parse.stanford import StanfordDependencyParser
import re
import graphd


# 0: Root
# 1: Type of Word
# 2: Modifier Relation
class GTree(object):
	def __init__(self, modif=None, typ=0, ret=False):
		self.children = {}
		self.modifier = modif
		self.type = typ
		self.ret = ret
	
	def printTree(self, index=0):
	
		for i in range(index):
			print("\t", end='')
		
		print(str(self.modifier) + " " + str(self.ret))
		index += 1
		
		for ch in self.children:
			#print(ch)
			self.children[ch].printTree(index)
		
root = GTree()


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

u_inp = "Although the compound is abundant in the environment at large, its presence in the air is not __; only in the form of underwater sediment does it cause damage. "

options = ['harmful',	'harmful',	'provocative',	'witty',	'insipid',	'stimulating']

u_inp_m = u_inp.replace("__", options[1])

u_inp = "Although the compound is abundant in the environment at large, its presence in the air is not __; only in the form of underwater sediment does it *cause* *damage*. "
print(u_inp_m)

imp_parts = re.findall(r"\*[^\*]*\*", u_inp)

for i in range(len(imp_parts)):
	imp_parts[i] = imp_parts[i][1:-1]
print(imp_parts)

result = dependency_parser.raw_parse(u_inp_m)
dep = result.__next__()
i_graph = list(dep.triples())

print(i_graph)

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
print(graph)
#print(spg)

for j in range(len(imp_parts)):
	spg = find_shortest_path(graph, start, imp_parts[j])
	t = []
	i_seq.append(spg)
	for i in range(len(spg) - 1):
		t.append(graph[spg[i]][spg[i + 1]])
	i_rules.append(t)
	

print(i_rules)
print(i_seq)

currnode = root

for i in range(len(i_rules)):
	currnode = root
	wtype = i_seq[i][0].split("_")[1]
	if wtype in currnode.children:
		currnode = root.children[wtype]
	else:
		node = GTree(wtype ,1)
		currnode.children[wtype] = node
		currnode = currnode.children[wtype]
		
	for rl in i_rules[i]:
		
		tf = i_rules[i].index(rl) == (len(i_rules[i]) - 1)
		
		if rl in currnode.children:
			currnode = currnode.children[rl]
		else:
			if tf == True:
				node = GTree(rl, 2, True)
			else:
				node = GTree(rl, 2)
				
			currnode.children[rl] = node
			currnode = currnode.children[rl]
		
#print(root.children['JJ'].children['parataxis'].children['ccomp'].type)

root.printTree()


