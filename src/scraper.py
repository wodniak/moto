from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

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
        'mileage'   : None,
        'engineCC' : None
    }

    def __init__(self, rawData):
        """
        Fill all information regarding motorcycle

        @param rawData : xml with all motorcycle parameters 
        """

        info = rawData.find_all('li', class_='offer-item__params-item')
        self.data['prodDate'] = info[0].text.strip('\n').strip()
        self.data['mileage']   = info[1].text.strip('\n').strip('km').strip()
        self.data['engineCC'] = info[2].text.strip('\n').strip('cm3').strip()
        self.data['motoType'] = info[3].text.strip('\n')
    
        self.data['brand'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[0]
        self.data['model'] = rawData.find('a', class_ = 'offer-title__link').text.strip().split(' ')[1]
        self.data['desc']  = rawData.find('h3', class_='offer-item__subtitle').text
        self.data['price'] = rawData.find('span', class_='offer-price__number').text.strip('PLN').strip()


def simpleGetUrl(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if isGoodResponse(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def isGoodResponse(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def main():
    url = 'https://www.otomoto.pl/motocykle-i-quady/honda/cm/?search%5Bcountry%5D='
    rawHtml = simpleGetUrl(url)    #get whole page
    if rawHtml is not None:
        html = BeautifulSoup(rawHtml, 'html.parser')
        for nr, moto in enumerate(html.select('article')):
            machine = CMoto(moto)
            print(machine.data)


#starting point
if __name__ == '__main__':
    main()