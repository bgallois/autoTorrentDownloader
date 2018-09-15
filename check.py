from ettvScraper import Scraper
import requests
from bs4 import BeautifulSoup



def checkSearch(query):
	query = query.replace(' ', '+')
	searchPage = requests.get('https://ettvtorrents.com/?s=' + query)
	soup = BeautifulSoup(searchPage.text, 'html.parser')
	searchResults = soup.find_all(class_ = 'link-image')

	s = [i.get('href') for i in searchResults]

	if len(s) > 1: # Severale series found
		[print(i, j.find('img', alt=True)['alt']) for i, j in enumerate(searchResults)]
		choice = input("Choose the serie: ")
		# Input series file
		return [j.find('img', alt=True)['alt'] for i, j in enumerate(searchResults)][int(choice)], True
            
	elif len(s) == 0: # Not serie found
		print(query + "not found")
		choice = input("New keywords: ")
		return choice, False
	else:
		return query.replace('+', ' '), True

def readConf():
        
	with open("series.txt") as f:
		lines = f.readlines()
		lines = [line.rstrip('\n') for line in lines]
	return lines

def checkConf():
	lines = readConf()
	print(lines)
	newConf = []
	for line in lines:
		serie = line.split('\t')
		a, b = checkSearch(serie[0])
		while not b: 
			a, b = checkSearch(a)
			print(line)
		newConf.append(a + '\t' + serie[1] + '\t' + serie[2] + '\n')
	with open("series.txt", 'w') as f:
		f.writelines(newConf)

def main():
	checkConf()
	lines = readConf()
	for line in lines:
		serie = line.split('\t')
		Scraper(serie[0], serie[1], serie[2])


main()
