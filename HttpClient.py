import os
import requests
import re
import html2text
import sys
import json
from urllib.parse import urlparse
# from bs4 import BeautifulSoup
import time

class HttpClient:

    _url_base = 'https://genshin.honeyhunterworld.com'
    _endpoint = ''
    _json_folder = ''

    def __init__(self):
        self._response = self.requestResource()

    def cleanHtml(self, html):
        text = html2text.html2text(html)
        text = text.replace('\n', '')
        text = text.replace('*', '')
        text = text.replace('#', '')
        text = text.replace('_', '')
        return text

    def cleanText(self, text):
        text = text.replace('"', '')
        return text

    def requestResource(self):
        time.sleep(2)
        print('Trying to request: '+self._endpoint)
        response = self.requestUrl(self._url_base+'/'+self._endpoint)
        return response.text

    def requestUrl(self, url):
        try:
            r = requests.get(url)
            if(r.status_code == 200):
                return r
            
            print('Error Response. Sleeping 30 seconds. and retrying '+url+'.')
            time.sleep(30)
            return self.requestUrl(url)
        except Exception as e:
            print('Sleeping 5 seconds. and retrying '+url+'.')
            print(e)
            time.sleep(5)
            return self.requestUrl(url)

    
    def findAll(self, regex, text):
        return re.findall(regex, text)
    
    def findCleanedAll(self, regex, text):
        match = re.search(regex, self._response, re.DOTALL)

        if match:
            html_content = match.group(0)
            pattern = r'<script.*?<\/script>'
            cleaned_html = re.sub(pattern, '', html_content, flags=re.DOTALL)
            return [cleaned_html] 
        else:
            return []
    
    def parseSufixes(self, quantity):
        if('K' in quantity):
            quantity = quantity.replace('K', '000')
        return quantity
    
    def getFileFullURL(self, image_endpoint):
        return self._url_base+image_endpoint
    
    def dumpJSON(self, data):
        return json.dumps(data)
    
    def mapAscensionMaterials(self, material):
        return { 'id': material[1], 'name': material[0] }

    def cleanMaterialId(self, id):
        return id[0:(len(id)-3)]
        