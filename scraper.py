from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json

class CMoto(object):
    """
    Motorcycle class to keep all data regarding each machine
    """

    data = {
        'brand'    : None,
        'model'    : None,
        'desc'     : None,
        'prodDate' : None,
        'price'    : None,
        'motoType' : None,
        'mileage'  : None,
        'engineCC' : None
    }

    def __init__(self, rawData):
        """
        Fill all information regarding motorcycle

        @param rawData : xml with all motorcycle parameters 
        """

        info = rawData.find_all('li', class_='offer-item__params-item')
        self.data['prodDate'] = info[0].text.strip('\n').strip()
        self.data['mileage']  = info[1].text.strip('\n').strip('km').strip()
        self.data['engineCC'] = info[2].text.strip('\n').strip('cm3').strip()
        self.data['motoType'] = info[3].text.strip('\n')
    
        self.data['brand'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[0]
        self.data['model'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[1]
        self.data['desc']  = rawData.find('h3', class_='offer-item__subtitle').text
        self.data['price'] = rawData.find('span', class_='offer-price__number').text[:-4].strip()   #get rid of currency

class CScraper(object):
    """
    Get data from web page with http requests
    """

    mainUrl = 'https://www.otomoto.pl/motocykle-i-quady/'
    config = None

    def __init__(self, configPath):
        """
        Parse json config file
        """

        try:
            with open(configPath, 'r') as f:
                self.config = json.load(f)
        except ValueError:
            print('Decoding JSON config file has failed')


    def downloadAllPages(self):
        """
        Download all pages of motorcycles given in config json

        @return rawMotoInfo : list of raw motorcycle information scrapped from web
        """
        rawMotoInfo = []
        for url in self._makeUrl():
            page = self._simpleGetUrl(url)
            print(url)
            print(page)
            soup = BeautifulSoup(page, 'html.parser')
            for rawInfo in soup.select('article'):
                rawMotoInfo.append(rawInfo)
        
        return rawMotoInfo


    def _makeUrl(self):
        """
        Create Urls according to config settings
        @return list of urls
        """
        urls = []
        for moto in self.config['vehicle']:
            urls.append(self.mainUrl + moto['brand'] + '/' + moto['model'] + '/')
        return urls


    def _simpleGetUrl(self, url):
        """
        Attempts to get the content at `url` by making an HTTP GET request.
        If the content-type of response is some kind of HTML/XML, return the
        text content, otherwise return None.
        """
        try:
            with closing(get(url, stream=True)) as resp:
                if self._isGoodResponse(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            print('Error during requests to {0} : {1}'.format(url, str(e)))
            return None


    def _isGoodResponse(self, resp):
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('html') > -1)





def main():
    scraper = CScraper('config.json')
    allRawMotos = scraper.downloadAllPages()

    listOfMoto = []
    for moto in allRawMotos:
        listOfMoto.append(CMoto(moto))

    for x in listOfMoto:
        print(x.data)
        


#starting point
if __name__ == '__main__':
    main()