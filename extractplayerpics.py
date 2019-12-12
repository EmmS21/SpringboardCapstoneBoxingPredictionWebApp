import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
from time import sleep
path = 'https://raw.githubusercontent.com/EmmS21/SpringboardCapstoneBoxingPredictionWebApp/master/boxingdata/df2.csv'
file = pd.read_csv(path)
for index,row in file.iterrows():
    sleep(7)
    site = row['players_links']
    response = requests.get(site)
    soup = BeautifulSoup(response.text, 'html.parser')
    pics = soup.find('img')
    try:
        pic_url = pics['src']
    except:
        image = 'https://chapters.theiia.org/central-mississippi/About/ChapterOfficers/_w/person-placeholder_jpg.jpg'
        urllib.request.urlretrieve(image,'C:\\Users\\User\\Documents\\GitHub\\SpringboardCapstoneBoxingPredictionWebApp\\pictures\\'+str(site.split('/')[-1])+'.jpg')
    try:
        urllib.request.urlretrieve(pic_url,'C:\\Users\\User\\Documents\\GitHub\\SpringboardCapstoneBoxingPredictionWebApp\\pictures\\'+ str(site.split('/')[-1])+'.jpg')
    except:
        image = 'https://chapters.theiia.org/central-mississippi/About/ChapterOfficers/_w/person-placeholder_jpg.jpg'
        urllib.request.urlretrieve(image,'C:\\Users\\User\\Documents\\GitHub\\SpringboardCapstoneBoxingPredictionWebApp\\pictures\\'+str(site.split('/')[-1])+'.jpg')