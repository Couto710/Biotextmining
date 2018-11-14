import subprocess
import string
import json
import time
import re
import io

#function that deletes duplicates in a list
def deleteDuplicates(lst):

	seen = []
	for l in lst:
		if l not in seen:
			seen.append(l)
	
	return seen

#function to merge 2 lists
def mergeLists(lst1, lst2):

	res = list(lst1)
	for l in lst2:
		if l not in res:
			res.append(l)

	return res

pythonbin = "../Spacy/.env/bin/python"
spacyscript = "../Spacy/post.py"

inv = set(string.punctuation)
inv.remove("-")
inv.remove("_")

#data to be stored
geniarelevant = []
geniaspan = []
metares = []
metarelevant = []
nounchunks = []
spacyspan = []

file = open("17400334.txt", "r")
text = file.read()
file.close()

#using Spacy to parse dependencies and getting noun chunks
spacypro = subprocess.Popen([pythonbin, spacyscript, text], stdout=subprocess.PIPE)
spacyret, serr = spacypro.communicate()

spacyres = spacyret.split('\n')
spacyresfin = []
for tup in spacyres:
	if len(tup.split('\'')) > 1:
		spacyresfin.append(tup.split('\'')[1].lower())

spacyresfin = deleteDuplicates(spacyresfin)

#starting metamap servers for the cycle
metaprocess = subprocess.call('exec ../public_mm/bin/skrmedpostctl start' , shell=True)
metaprocess = subprocess.call('exec ../public_mm/bin/wsdserverctl start' , shell=True)
time.sleep(2)

for sr in spacyresfin:
	spacyaux = open("./util/saux.txt", "w")
	spacyaux.write(sr + "\n")
	spacyaux.close()
	metaspacy = subprocess.call('exec ../public_mm/bin/metamap16 ./util/saux.txt ./util/spacyresult.txt' , shell=True)
	spacyaux = open("./util/spacyresult.txt", "r")
	spacyrestext = spacyaux.read()
	spacyaux.close()
	spacylines = spacyrestext.split('\n')
	temp = []
	for sl in spacylines:
		if sl.startswith(" "):
			nsl = sl[9:]
			temp.append(nsl.split('(')[0].split('[')[0].lower())
	temp = deleteDuplicates(temp)
	for t in temp:
		nounchunks.append(t[:len(t)-1])

#stopping metamap servers
metaprocess = subprocess.call('exec ../public_mm/bin/skrmedpostctl stop' , shell=True)
metaprocess = subprocess.call('exec ../public_mm/bin/wsdserverctl stop' , shell=True)

#calls genia tagger
pro = subprocess.Popen('(cd ../geniatagger-3.0.2/ && exec echo \"' + text + '\" | ./geniatagger)', shell=True, stdout=subprocess.PIPE)
out, err = pro.communicate()

results = out.split('\n')
relevant = []

#refines results that are relevant
for result in results:
	relist = result.split('\t')
	if len(relist) == 5:
		if relist[4] != 'O':
			relevant.append(relist)

for rel in relevant:
	geniarelevant.append(rel)


"""
#calling metamap
metaprocess = subprocess.call('exec ../public_mm/bin/metamap16 17363114.txt ./util/result.txt' , shell=True)
resfile = open("./util/result.txt", "r")
restext = resfile.read()	
#handling metamap results
splphr = restext.split('Phrase')
for s in splphr:
	metares.append(s)

#stopping metamap servers
metaprocess = subprocess.call('exec ../public_mm/bin/skrmedpostctl stop' , shell=True)
metaprocess = subprocess.call('exec ../public_mm/bin/wsdserverctl stop' , shell=True)

#filtering relevant results from metamap
for f in metares:
	fl = f.split('\n')
	temp = []
	for l in fl:
		if l.startswith(" "):
			nl = l[9:]
			temp.append(nl.split('(')[0].split('[')[0])
	temp = deleteDuplicates(temp)
	for t in temp:
		metarelevant.append(t[0:len(t)-1])
"""

#getting span for spacy+metamap results
for nc in nounchunks:
	if any(c in inv for c in nc):
		nc = re.escape(nc)
	inits = [m.start() for m in re.finditer(nc.lower(), text.lower())]
	if len(inits) > 0:
		for i in inits:
			elem = [nc.lower(), [i, i+len(nc)]]
			spacyspan.append(elem)

#getting span for genia results
geniarelevant = map(lambda x: x[0].lower(), geniarelevant)
deleteDuplicates(geniarelevant)
index = 0
for gr in geniarelevant:
	if any(c in inv for c in gr):
		gr = re.escape(gr)
	inits = [m.start() for m in re.finditer(gr.lower(), text.lower())]
	if len(inits) > 0:
		for i in inits:
			elem = [gr.lower(), [i, i+len(gr)]]
			geniaspan.append(elem)

allres = mergeLists(geniaspan, spacyspan)

final = open("./c04-results/17400334.txt", "w")
final.write("genia tagger: " + str(len(geniaspan)))
for g in geniaspan:
	print>>final, g
final.write("\n\nspacy + metamap: " + str(len(spacyspan)))
for s in spacyspan:
	print>>final, s
final.write("\n\ntotal: " + str(len(allres)))
for a in allres:
	print>>final, a
final.close()

