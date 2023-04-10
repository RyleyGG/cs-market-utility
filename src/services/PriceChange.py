from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import json
from time import sleep
from services.Config import config


def getOldPrices():
    print('Getting old price change data...')
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

    # Before starting full iteration, get number of results (and therefore visitable pages)
    itemDict = {}
    continueIter = True
    maxRes = 0
    while continueIter:
        try:
            print(f'Scraping page {pageIter}')
            resp = requests.get(config.marketUrl.replace('start=', f'start={pageIter*100}')).json()
            res = resp['results']
            for item in res:
                itemDict[item['name'].replace('★ ', '').replace('™', '')] = float(item['sell_price_text'].replace('$', '').replace(',', ''))

            pageIter += 1
            maxRes = max(maxRes, resp['total_count'])
            if pageIter * 100 >= maxRes:
                continueIter = False
            else:
                sleep(3)
        except Exception as e:
            print('Error when parsing marketplace. Exiting...')
            exit(1)

    newPriceDf['Name'] = itemDict.keys()
    newPriceDf['Price'] = itemDict.values()
    return newPriceDf

def comparePrices(oldPriceDf: pd.DataFrame, newPriceDf: pd.DataFrame):
    print('Comparing new and old price change data...')
    mergedDf = pd.merge(left=oldPriceDf, right=newPriceDf, on='Name', how='inner', suffixes=('_old', '_new'))

    if len(mergedDf) == 0:
        print('No original data, so no comparison can occur. Dumping new data...')
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
    mergedPriceDict = mergedDf.set_index('Name')['Price_new'].to_dict()
    json.dump(mergedPriceDict, open(f'{config.cwd}/data/last_price_check.json', 'w'))