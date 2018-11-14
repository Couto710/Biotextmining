import subprocess
import string
import json
import time
import re
import io
import os


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

totaldenotations = 0
totalfound = 0
totalreturned = 0

geniatotal = 0
geniatotalrel = 0
metatotal = 0
metatotalrel = 0
spacytotal = 0
spacytotalrel = 0

dic = {'Acetylation': 0, 'Binding': 0, 'DNA': 0, 'Deacetylation': 0, 'Entity': 0, 'Gene_expression': 0, 'Localization': 0, 'Negative_regulation': 0, 'Phosphorylation': 0, 'Positive_regulation': 0, 'Protein': 0, 'Protein_catabolism': 0, 'Protein_domain': 0, 'Protein_modification': 0, 'Regulation': 0, 'Transcription': 0, 'Ubiquitination': 0}
geniadic = {'Acetylation': 0, 'Binding': 0, 'DNA': 0, 'Deacetylation': 0, 'Entity': 0, 'Gene_expression': 0, 'Localization': 0, 'Negative_regulation': 0, 'Phosphorylation': 0, 'Positive_regulation': 0, 'Protein': 0, 'Protein_catabolism': 0, 'Protein_domain': 0, 'Protein_modification': 0, 'Regulation': 0, 'Transcription': 0, 'Ubiquitination': 0}
metadic = {'Acetylation': 0, 'Binding': 0, 'DNA': 0, 'Deacetylation': 0, 'Entity': 0, 'Gene_expression': 0, 'Localization': 0, 'Negative_regulation': 0, 'Phosphorylation': 0, 'Positive_regulation': 0, 'Protein': 0, 'Protein_catabolism': 0, 'Protein_domain': 0, 'Protein_modification': 0, 'Regulation': 0, 'Transcription': 0, 'Ubiquitination': 0}
spacydic = {'Acetylation': 0, 'Binding': 0, 'DNA': 0, 'Deacetylation': 0, 'Entity': 0, 'Gene_expression': 0, 'Localization': 0, 'Negative_regulation': 0, 'Phosphorylation': 0, 'Positive_regulation': 0, 'Protein': 0, 'Protein_catabolism': 0, 'Protein_domain': 0, 'Protein_modification': 0, 'Regulation': 0, 'Transcription': 0, 'Ubiquitination': 0}
totaldic = {'Acetylation': 0, 'Binding': 0, 'DNA': 0, 'Deacetylation': 0, 'Entity': 0, 'Gene_expression': 0, 'Localization': 0, 'Negative_regulation': 0, 'Phosphorylation': 0, 'Positive_regulation': 0, 'Protein': 0, 'Protein_catabolism': 0, 'Protein_domain': 0, 'Protein_modification': 0, 'Regulation': 0, 'Transcription': 0, 'Ubiquitination': 0}

for filename in os.listdir("./texts/"):

	#opening json file
	with open("./texts/" + filename) as jsonfile:
		print jsonfile
		if os.stat("./texts/" + filename).st_size == 0:
			continue
		jsondata = json.load(jsonfile)

	#getting the "text" part and dividing into sentences for analysis
	fulltext = jsondata["text"]
	sentences = fulltext.split('.')

	#getting denotations
	if "denotations" not in jsondata:
		continue
	fulldenotations = jsondata["denotations"]

	#data to be stored
	geniarelevant = []
	geniaspan = []
	geniafound = []
	metares = []
	metarelevant = []
	metafound = []
	metaspan = []
	denotations = []
	nounchunks = []
	spacyspan = []
	spacyfound = []
	

	#retrieves denotations from original file
	for den in fulldenotations:
		td = fulltext[den['span']['begin']:den['span']['end']]
		denotations.append([[td.lower(), [den['span']['begin'], den['span']['end']]], den['obj']])

	#using Spacy to parse dependencies and getting noun chunks
	spacypro = subprocess.Popen([pythonbin, spacyscript, fulltext], stdout=subprocess.PIPE)
	spacyret, serr = spacypro.communicate()

	spacyres = spacyret.split('\n')

	#starting metamap servers for the cycle
	metaprocess = subprocess.call('exec ../public_mm/bin/skrmedpostctl start' , shell=True)
	metaprocess = subprocess.call('exec ../public_mm/bin/wsdserverctl start' , shell=True)
	time.sleep(2)


	for sr in spacyres:
		if len(sr.split('\'')) > 1:
			spacyaux = open("./util/saux.txt", "w")
			spacyaux.write(sr.split('\'')[1] + "\n")
			spacyaux.close()
			spacyaux = open("./util/saux.txt", "r")
			metaspacy = subprocess.call('exec ../public_mm/bin/metamap16 ./util/saux.txt ./util/spacyresult.txt' , shell=True)
			spacyaux.close()
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

	#cycle that runs genia tagger to get post tags and ner
	for sentence in sentences:

		#calls genia tagger
		pro = subprocess.Popen('(cd ../geniatagger-3.0.2/ && exec echo \"' + sentence + '\" | ./geniatagger)', shell=True, stdout=subprocess.PIPE)
		out, err = pro.communicate()

		results = out.split('\n')
		relevant = []

		#refines results that are elevant
		for result in results:
			relist = result.split('\t')
			if len(relist) == 5:
				if relist[4] != 'O':
					relevant.append(relist)

		for rel in relevant:
			geniarelevant.append(rel)

		#handling files to help in the metamap process
		textfile = io.open("./util/text.txt", "w")
		textfile.write(sentence)
		textfile.close()

		textfile = open("./util/text.txt", "r")

		#calling metamap
		metaprocess = subprocess.call('exec ../public_mm/bin/metamap16 ./util/text.txt ./util/result.txt' , shell=True)
		textfile.close()
		
		resfile = open("./util/result.txt", "r")
		restext = resfile.read()

		#handling metamap results
		splphr = restext.split('Phrase')
		for s in splphr:
			metares.append(s)



	#stopping metamap servers
	metaprocess = subprocess.call('exec ../public_mm/bin/skrmedpostctl stop' , shell=True)
	metaprocess = subprocess.call('exec ../public_mm/bin/wsdserverctl stop' , shell=True)
	print nounchunks
	
	#getting span for spacy+metamap results
	for nc in nounchunks:
		if any(c in inv for c in nc):
			nc = re.escape(nc)
		inits = [m.start() for m in re.finditer(nc.lower(), fulltext.lower())]
		if len(inits) > 0:
			for i in inits:
				elem = [nc.lower(), [i, i+len(nc)]]
				spacyspan.append(elem)


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


	#getting span for genia results
	index = 0
	for gr in geniarelevant:
		init = fulltext.find(unicode(gr[0], "utf-8"), index)
		if init != -1:
			finit = init + len(gr[0])
			elem = [gr[0].lower(), [init, finit]]
			geniaspan.append(elem)
			index = init+1

	#getting span for metamap results
	for mr in metarelevant:
		if any(c in inv for c in mr):
			mr = re.escape(mr)
		inits = [m.start() for m in re.finditer(mr.lower(), fulltext.lower())]
		if len(inits) > 0:
			for i in inits:
				elem = [mr.lower(), [i, i+len(mr)]]
				metaspan.append(elem)

	denotations = deleteDuplicates(denotations)
	geniaspan = deleteDuplicates(geniaspan)
	metaspan = deleteDuplicates(metaspan)
	spacyspan = deleteDuplicates(spacyspan)

	#getting results that are actual denotations
	print len(denotations)
	for de in denotations:
		print de
		dic[de[1]] += 1
		if de[0] in geniaspan:
			geniafound.append(de)
			geniadic[de[1]] += 1
		if de[0] in metaspan:
			metafound.append(de)
			metadic[de[1]] += 1
		if de[0] in spacyspan:
			spacyfound.append(de)
			spacydic[de[1]] += 1

	totalspans1 = mergeLists(geniaspan, metaspan)
	totalspans = mergeLists(totalspans1, spacyspan)

	print '............'

	print len(geniafound)
	for a in geniafound:
		print a

	print '.....................'

	print len(metafound)
	for b in metafound:
		print b

	print '.................'

	print len(spacyfound)
	for c in spacyfound:
		print c

	print '=============='
	allres1 = mergeLists(geniafound, metafound)
	allres = mergeLists(allres1, spacyfound)
	print len(allres)
	for ar in allres:
		print ar
		totaldic[ar[1]] += 1

	print "\n\n all stats"
	print totaldic
	print "\n\n genia stats"
	print geniadic
	print "\n\n meta stats"
	print metadic
	print "\n\n spacy stats"
	print spacydic

	finalres = open("./results/" + filename, "w")

	finalres.write("denotations: " + str(len(denotations)) + "\n")
	for de in denotations:
		print>>finalres, de

	finalres.write("\n\ngeniatagger: " + str(len(geniafound)) + "\n")
	for a in geniafound:
		print>>finalres, a

	finalres.write("\n\nmetamapper: " + str(len(metafound)) + "\n")
	for b in metafound:
		print>>finalres, b

	finalres.write("\n\nspacy + metamapper: " + str(len(spacyfound)) + "\n")
	for c in spacyfound:
		print>>finalres, c

	finalres.write("\n\ntotal: " + str(len(allres)) + "\n")
	for ar in allres:
		print>>finalres, ar

	finalres.close()

	totaldenotations += len(denotations)
	totalreturned += len(totalspans)
	totalfound += len(allres)
	print totalfound, totaldenotations, float(totalfound)/totaldenotations

	geniatotal += len(geniaspan)
	geniatotalrel += len(geniafound)
	metatotal += len(metaspan)
	metatotalrel += len(metafound)
	spacytotal += len(spacyspan)
	spacytotalrel += len(spacyfound)


print "Returned: " + str(totalreturned)
print "Found: " + str(totalfound)
print "Total denotations: " + str(totaldenotations)
print "Recall: " + str(float(totalfound)/totaldenotations)
print "Precision: " + str(float(totalfound)/totalreturned) 

stats = open("stats.txt", "w")

stats.write("Denotations: " + str(totaldenotations) + "\n")
print>>stats, dic
stats.write("\n\n")

stats.write("Genia total: " + str(geniatotal) +"\n")
stats.write("Genia relevant: " + str(geniatotalrel) + "\n")
stats.write("Genia precision: " + str(float(geniatotalrel)/totaldenotations) +"\n")
print>>stats, geniadic
stats.write("\n\n")

stats.write("meta total: " + str(metatotal) +"\n")
stats.write("meta relevant: " + str(metatotalrel) + "\n")
stats.write("meta precision: " + str(float(metatotalrel)/totaldenotations) + "\n")
print>>stats, metadic
stats.write("\n\n")

stats.write("spacy total: " + str(spacytotal) +"\n")
stats.write("spacy relevant: " + str(spacytotalrel) + "\n")
stats.write("spacy precision: " + str(float(spacytotalrel)/totaldenotations) + "\n")
print>>stats, spacydic
stats.write("\n\n")

stats.write("returned: " + str(totalreturned) +"\n")
stats.write("total: " + str(totalfound) +"\n")
stats.write("recall: " + str(float(totalfound)/totaldenotations) + "\n")
stats.write("precision: " + str(float(totalfound)/totalreturned) + "\n")
print>>stats, totaldic

stats.close()