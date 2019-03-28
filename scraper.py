from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

class CMoto(object):
    """
    Motorcycle class to keep all data regarding each machine
    """

    numberOfMotors = 0      #moto object counter

    def __init__(self, rawData):
        """
        Fill all information regarding motorcycle
        @param rawData : xml with basic motorcycle parameters 
        """
        CMoto.numberOfMotors += 1     #increment for each new object

        self.data = {
            'id'       : None,
            'brand'    : None,
            'model'    : None,
            'desc'     : None,
            'prodDate' : None,
            'price'    : None,
            'motoType' : None,
            'mileage'  : None,
            'engineCC' : None
        }
 
        info = rawData.find_all('li', class_='offer-item__params-item')     #prodDate, mileage, motoType, engineCC(not always)
        self.data['prodDate'] = int(info[0].text.strip('\n').replace(' ',''))
        self.data['mileage']  = int(info[1].text.strip('\n').strip('km').replace(' ','')) 
        self.data['price'] = int(rawData.find('span', class_='offer-price__number').text[:-4].replace(' ','').replace(',','.'))   #get rid of currency
        self.data['brand'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[0]
        self.data['model'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[1]
        self.data['id'] = int(rawData.find('a', {'data-ad-id' : True}).get('data-ad-id').strip())

#@! this solution sucks...
        #sometimes there is no engineCC given
        if len(info) == 4:
            self.data['engineCC'] = int(info[2].text.strip('\n').strip('cm3').replace(' ',''))
            self.data['motoType'] = info[3].text.strip('\n')
        else:
            self.data['motoType'] = info[2].text.strip('\n')

#@! this solution sucks...
        #sometimes there is no description in offert
        if rawData.find('h3', class_='offer-item__subtitle') is not None:       
            self.data['desc']  = rawData.find('h3', class_='offer-item__subtitle').text



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
            while(True):
                isNextPage = False  #switch for changing pages
                page = self._simpleGetUrl(url)      
                soup = BeautifulSoup(page, 'html.parser')
                
                for moto in soup.select('article'):
                    motors.append(CMoto(moto))
                
                #check if next page exists
                link = soup.find('link', {'rel' : 'next'})
                if link is not None:
                    isNextPage = True   #set flag 
                    url = link.get('href')  #get next page url

                #end loop when there is no more pages
                if not isNextPage:
                    break

        return motors


    def _makeUrl(self):
        """
        Create Urls according to config settings
        @return list of urls
        """
        urls = []
        for moto in self.config['vehicle']:
            urls.append(self.mainUrl + moto['brand'] + '/' + moto['model'] + '/?page=1')    #a little bit too much hardcoded stuff 

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


class CDatabase(object):
    """
    Database of downloaded motorcycles
    """ 

    def __init__(self, motoList):
        """
        Creates database with Pandas DataFrame object from dictionary
        List of objects needs to be transformed to list of dictionaries
        
        @param motoList : list of CMoto objects
        """
        motoData = []   #list of dictionaries with useful data
        for moto in motoList:
            motoData.append(moto.data)

        self.motoDatabase = pd.DataFrame(motoData)
        #set order of columns
        self.motoDatabase = self.motoDatabase[['id', 'brand', 'model', 'prodDate', 'price', 'motoType',
         'mileage', 'engineCC', 'desc' ]]


    def showRecords(self):
        """
        Pretty-print of database
        """

        with pd.option_context('display.max_rows', None, 'display.max_columns', 10):
            print(self.motoDatabase.to_string())

class CPlotter(object):
    """
    Uses matplotlib and seaborn to create diagrams and plots
    """

    def __init__(self, df):
        """
        Apply the default seaborn theme, scaling, and color palette
        """
        sns.set()
        self.df = df.motoDatabase

    def simplePlot(self, x, y):
        """
        Create simple scatterplot
        @param x : data for x axis
        @param y : data for y axis 
        """
        sns.lmplot(x, y, self.df, hue='model')
        # sns.lmplot('prodDate', 'price', self.motoDatabase)
        plt.show()


def main():
    scraper = CScraper('config.json')   #parse json
    motoList = scraper.downloadAllMotors()     #download data and parse it to objects
    motoDatabase = CDatabase(motoList)
    motoDatabase.showRecords()

    print('Total number of parsed motorcycles : {}'.format(CMoto.numberOfMotors))

    plotter = CPlotter(motoDatabase)
    plotter.simplePlot('prodDate', 'price')

#starting point
if __name__ == '__main__':
    main()