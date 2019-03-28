from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
from time import sleep
class CMoto(object):
    """
    Motorcycle class to keep all data regarding each machine
    """

    numberOfMotors = 0      #moto object counter

    def __init__(self, rawData):
        """
        Fill all information regarding motorcycle

        @param rawData : xml with all motorcycle parameters 
        """
        self.numberOfMotors += 1     #increment for each new object

        self.data = {
            'brand'    : None,
            'model'    : None,
            'desc'     : None,
            'prodDate' : None,
            'price'    : None,
            'motoType' : None,
            'mileage'  : None,
            'engineCC' : None
        }
 
        info = rawData.find_all('li', class_='offer-item__params-item')
        self.data['prodDate'] = info[0].text.strip('\n').strip()
        self.data['mileage']  = info[1].text.strip('\n').strip('km').strip() 

#@! this solution sucks...
        #sometimes there is no engineCC given
        if len(info) == 4:
            self.data['engineCC'] = info[2].text.strip('\n').strip('cm3').strip()
            self.data['motoType'] = info[3].text.strip('\n')
        else:
            self.data['motoType'] = info[2].text.strip('\n')

        self.data['brand'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[0]
        self.data['model'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[1]

#@! this solution sucks...
        #sometimes there is no description in offert
        if rawData.find('h3', class_='offer-item__subtitle') is not None:       
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


    def downloadAllMotors(self):
        """
        Download all pages of motorcycle types given in config json and use them to create motorcycle objects
        @return motors : list of initialized motorcycle objects scrapped from web
        """
        motors = []     #list of all motorcycles
        for url in self._makeUrl():     #for each motorcycle type in config there is 1 url
            page = self._simpleGetUrl(url)      
            soup = BeautifulSoup(page, 'html.parser')
            for moto in soup.select('article'):
                motors.append(CMoto(moto))

        return motors


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
            #without it page responds with None
            headers = {
                'User-Agent': 'alamakota', 
                'From': 'alama@kota.com'
                }

            with closing(get(url, headers=headers, stream=True)) as resp:
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
    scraper = CScraper('config.json')   #parse json
    motorList = scraper.downloadAllMotors()     #download data and parse it to objects

    for x in range(len(motorList)): #debug print
        print(motorList[x].data)



#starting point
if __name__ == '__main__':
    main()