import requests
import sys
import re

url = "http://alt.qcri.org/demos/Discourse_Parser_Demo/"

def getRST(sent):

	payload = {}
	payload["textdata"] = sent
	payload["discourse"] = "b"
	payload["submitsave"] = "Execute"

	#print(payload)
	r = requests.post(url, data=payload)

	res = str(r.text.encode(sys.stdout.encoding, errors='replace'))

	#fl = open("op.txt", "w")

	#fl.write(res)
	#imp_parts = re.findall(r"\*[^\*]*\*", u_inp)

	ind = res.index("<script type=\"text/javascript\">rhetoricParsingOutput=\"")

	ind = ind + len("<script type=\"text/javascript\">rhetoricParsingOutput=\"")
	#print(ind)

	op = ""

	
	while True:
		if res[ind] == "\"":
			break
		
		op += res[ind]
		ind += 1
		
	return(op)

def getphrase(sent, res, indexx):
	slist = re.split(' |; |, |\:|\.|\*|\n', sent)
	
	#print(slist)
	kword = slist[indexx]
	
	#print(kword)
	
	ind = res.index(kword)
	
	while res[ind] != "!":
		ind += -1
	
	op2 = ""
	
	ind += 1
	
	while res[ind] != "_":
		#print(res[ind])
		op2 += res[ind]
		ind += 1
	
	return(op2)
