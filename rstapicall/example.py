import hpost

mysent = "There are some people who think that only the poor and less educated people use slang, but this idea is erroneous."

res = hpost.getRST(mysent)
print(res)

phrase = hpost.getphrase(mysent, res, 20)

print(phrase)
