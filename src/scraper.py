from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

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
    rawHtml = simpleGetUrl(url)
    if rawHtml is not None:
        html = BeautifulSoup(rawHtml, 'html.parser')    #get whole page
        for nr, moto in enumerate(html.select('article')):
            print(nr, moto.find('h3').text)

#starting point
if __name__ == '__main__':
    main()