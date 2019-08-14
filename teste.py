f = open("palavras")

a = []
for l in f:
	if "_" in l:
		a.append(l[0:-1])

for w in a:
	print(w)
