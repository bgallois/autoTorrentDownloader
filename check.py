
''' autoTorrentDownloader 
Copyright (C) 2018 Benjamin GALLOIS
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''


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
		return [j.find('img', alt=True)['alt'] for i, j in enumerate(searchResults)][0], True


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
