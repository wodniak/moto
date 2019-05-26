"""
OTOMOTO scrapper
Downloads information about motorcycle offerts from otomoto.pl
There is possibility to save data to file and plot it on different charts.

How to configure:
database:
    save : <yes/no>
    mode : <basic/detailed> - TBD
    file : <csv>    - TBD

plotter:
    power : <on/off>
    save  : <yes/no>
    plot  : barplot, simpleplot, heatmapplot

vehicle:
    brand : <any>
    model : <any>, all if not given
"""

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import os

class CMoto(object):
    """
    Motorcycle class to keep all data regarding each machine
    """

    numberOfMotors = 0      #moto object counter
    counterModelNotSpecified = 0

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
        try:
            self.data['id'] = int(rawData.find('a', {'data-ad-id' : True}).get('data-ad-id').strip())
            self.data['brand'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[0]
            self.data['model'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[1]
            self.data['prodDate'] = int(info[0].text.strip('\n').replace(' ',''))
            self.data['mileage']  = int(info[1].text.strip('\n').strip('km').replace(' ','')) 
            self.data['price'] = int(rawData.find('span', class_='offer-price__number').text[:-4].replace(' ','').replace(',','.'))   #get rid of currency
        except ValueError:  #problem z reszta PLN, line 40
            print('{0} model not specified in {1} offert'.format(self.data['brand'], self.data['id']))
            CMoto.counterModelNotSpecified += 1
        except IndexError:  #problem with non specified model, line 42 
            print('{0} model not specified in {1} offert'.format(self.data['brand'], self.data['id']))
            CMoto.counterModelNotSpecified += 1

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

    def __init__(self):
        """
        Parse json config file
        """
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        path_to_file = os.path.join(self.dir_path, "config.json")

        try:
            with open(path_to_file, 'r') as f:
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
            if moto.get('model') is None:
                #get all models
                urls.append(self.mainUrl + moto['brand'] + '/?page=1')
            else:
                #get specified model
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
    Save to file if config option "save" is "yes" 
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

        #save to file
        # if CScraper.config['save'] == 'yes':
        #     pass


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
        plt.ylim(0,10000)
        plt.xlim(1980,2019)
        plt.show()

    def heatmapPlot(self):
        # Calculate correlations
        corr = self.df.corr()
        corr.drop('id')
        # Heatmap
        sns.heatmap(corr)
        plt.show()


    def barPlot(self, x):
        sns.countplot(x=x, hue='model', data=self.df)
        plt.xticks(rotation=-45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.show()



def run():
    scraper = CScraper()   #parse json
    motoList = scraper.downloadAllMotors()     #download data and parse it to objects
    motoDatabase = CDatabase(motoList)
    motoDatabase.showRecords()

    print('Total number of parsed motorcycles : {}'.format(CMoto.numberOfMotors))
    print('Model not specified in {0} offerts'.format(CMoto.counterModelNotSpecified))

    plotter = CPlotter(motoDatabase)
    # plotter.simplePlot('prodDate', 'price')
    # plotter.heatmapPlot()
    plotter.barPlot('prodDate')

def main():
    pass
#starting point
if __name__ == '__main__':
    main()