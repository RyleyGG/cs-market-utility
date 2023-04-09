from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import json
from services.Config import config
from time import sleep


def getOldPrices():
    oldPriceDf = pd.DataFrame(columns=config.priceCols)
    try:
        priceObj = json.load(open(f'{config.cwd}/data/last_price_check.json', 'r'))
        oldPriceDf['Name'] = priceObj.keys()
        oldPriceDf['Price'] = priceObj.values()
    except Exception as e:
        print('Unable to get existing price check data. Continuing with empty object...')
    return oldPriceDf

def getNewPrices():
    newPriceDf = pd.DataFrame(columns=config.priceCols)

    pageIter = 1
    pageSuffix = f'#p{pageIter}_price_asc'
    
    # Before starting full iteration, get number of results (and therefore visitable pages)
    resp = requests.get(config.marketUrl + pageSuffix, config.requestHeaders)
    soup = bs(resp.content, 'html.parser')
    resultsElem = int(soup.find("span", {"id": "searchResults_total"}).contents[0].replace(',', ''))
    maxPage = resultsElem / 10
    itemDict = {}

    while pageIter <= maxPage:
        try:
            print(f'Scraping page {pageIter}')
            resp = requests.get(config.marketUrl + pageSuffix, config.requestHeaders)
            soup = bs(resp.content, 'html.parser')
            itemResp = soup.find_all("span", {"class": "market_listing_item_name"})
            saleResp = soup.find_all("span", {"class": "sale_price"})
            if len(itemResp) != len(saleResp):
                print('Uneven item and price count. Exiting...')
                exit(1)

            for i in range(len(itemResp)):
                itemDict[itemResp[i].text.replace('★ ', '').replace('™', '')] = float(saleResp[i].text.replace('$', '').replace(',', ''))
            
            pageIter += 1
            pageSuffix = f'#p{pageIter}_price_asc'
            sleep(1.2)
        except Exception as e:
            print('Error when parsing marketplace. Exiting...')
            exit(1)
    
    newPriceDf['Name'] = itemDict.keys()
    newPriceDf['Price'] = itemDict.values()
    return newPriceDf

def comparePrices(oldPriceDf: pd.DataFrame, newPriceDf: pd.DataFrame):
    mergedDf = pd.merge(left=oldPriceDf, right=newPriceDf, on='Name', how='inner', suffixes=('_old', '_new'))

    if len(mergedDf) == 0:
        newPriceDict = newPriceDf.set_index('Name')['Price'].to_dict()
        json.dump(newPriceDict, open(f'{config.cwd}/data/last_price_check.json', 'w'))
        return

    mergedDf['Price Difference'] = mergedDf['Price_new'] / mergedDf['Price_old']
    notableChangesDf = mergedDf[mergedDf['Price Difference'] <= 0.9]

    print('\n')
    if len(notableChangesDf) == 0:
        print('No notable changes found')
    else:
        print('!!!Notable changes found!!!')
        for index, row in notableChangesDf.iterrows():
            print(f'Name: {row["Name"]}')
            print(f'Old Price: {row["Price_old"]}')
            print(f'New Price: {row["Price_new"]}')
            print(f'Price Difference: {row["Price Difference"]}\n')
    
    print('Updating prices')
    mergedPriceDict = newPriceDf.set_index('Name')['Price_new'].to_dict()
    json.dump(mergedPriceDict, open(f'{config.cwd}/data/last_price_check.json', 'w'))