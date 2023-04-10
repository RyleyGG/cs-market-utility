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
    ###
    # We need to know both the current lowest listing price and the price at which the item was last sold
    # We need the current lowest so we can actually take advantage of the large price differentials
    # We need the last sold price to overwrite the currently-stored prices.
    # Generating both of these lists will help avoid cases like the following:
    # 1. Stored price of $1750, new price of $1350. If we only use current lowest, the script will assume there was a significant price drop.
    # 2. However, it's possible that its a low-volume item and $1750 was a vast overpricing, with $1350 actually being the average price people actually buy.
    ###
    curPriceDf = pd.DataFrame(columns=config.priceCols)
    lastSoldDf = pd.DataFrame(columns=config.priceCols)
    lastSoldDict = {}
    curPriceDict = {}

    # GENERATING LAST SOLD RESULTS
    resp = requests.get(f'https://api.steamapis.com/market/items/730?api_key={config.apiKey}')
    allItems = resp.json()['data']
    newItems = []
    for item in allItems:
        lastSoldDict[item['market_hash_name'].replace('★ ', '').replace('™', '')] = item['prices']['latest']
    allItems = newItems

    # GENERATING CUR PRICE RESULTS
    pageIter = 1
    continueIter = True
    maxRes = 0
    while continueIter:
        try:
            print(f'Scraping page {pageIter}')
            resp = requests.get(config.marketUrl.replace('start=', f'start={pageIter*100}')).json()
            res = resp['results']
            for item in res:
                if item['name'].replace('★ ', '').replace('™', '') not in lastSoldDict.keys():
                    print(f'Name not found: {item["name"]}')
                    continue
                curPriceDict[item['name'].replace('★ ', '').replace('™', '')] = float(item['sell_price_text'].replace('$', '').replace(',', ''))

            pageIter += 1
            maxRes = max(maxRes, resp['total_count'])
            if pageIter * 100 >= maxRes:
                continueIter = False
            else:
                sleep(3)
        except Exception as e:
            print('Error when parsing marketplace. Exiting...')
            exit(1)

    curPriceDf['Name'] = curPriceDict.keys()
    curPriceDf['Price'] = curPriceDict.values()
    return [curPriceDf, lastSoldDf]

def comparePrices(oldPriceDf: pd.DataFrame, lastSoldDf: pd.DataFrame, curPriceDf: pd.DataFrame):
    print('Comparing new and old price change data...')
    mergedDf = pd.merge(left=oldPriceDf, right=curPriceDf, on='Name', how='inner', suffixes=('_old', '_new'))

    if len(mergedDf) == 0:
        print('No original data, so no comparison can occur. Dumping new data...')
        newPriceDict = lastSoldDf.set_index('Name')['Price'].to_dict()
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
    newPriceDict = lastSoldDf.set_index('Name')['Price'].to_dict()
    json.dump(newPriceDict, open(f'{config.cwd}/data/last_price_check.json', 'w'))