import json

#opening json file
with open("c04-dataset.json") as jsonfile:
	print jsonfile
	jsondata = json.load(jsonfile)

counter = 0

for text in jsondata:	

	file = open("./c04/" + str(text['pmid']) + ".txt", "w")

	file.write(text['title'].encode('utf-8'))
	file.write(text['abs'].encode('utf-8'))
	file.write(text['Introduction'].encode('utf-8'))
	file.write(text['methods'].encode('utf-8'))
	file.write(text['results'].encode('utf-8'))
	file.write(text['conclusions'].encode('utf-8'))

	file.close()

	counter += 1
	print counter
	print text['pmid']
	print text['title']

