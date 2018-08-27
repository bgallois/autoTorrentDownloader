from ettvScraper import Scraper



def readConf():
        
    with open("series.txt") as f:
        lines = f.readlines()
        lines = [line.rstrip('\n') for line in lines]
    for line in lines:
        serie = line.split('\t') 
        print(serie)
        Scraper(serie[0], serie[1])


readConf()
