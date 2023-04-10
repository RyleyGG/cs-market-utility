from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import json
from services.Config import config
from fp.fp import FreeProxy


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
    print('Generating new price change data (this may take a few minutes)...')
    print('Updates will come every 10 items traversed')
    newPriceDf = pd.DataFrame(columns=config.priceCols)
    resp = requests.get(f'https://api.steamapis.com/market/items/730?api_key={config.apiKey}')
    allItems = resp.json()['data']
    newItems = []
    for item in allItems:
        if item['prices']['unstable'] \
        or 'Sticker |' in item['market_name'] \
        or item['prices']['safe_ts']['last_90d'] < 50:
            continue
        newItems.append(item)
    
    allItems = newItems

    itemDict = {}
    itemIter = 0
    for item in allItems:
        if itemIter % 10 == 0:
            print(f'{itemIter} out of {len(allItems)} traversed ({(itemIter / allItems) * 100})%...')

        itemId = item['nameID']
        listingObj = None
        try:
            if itemIter % len(config.proxies) == 1:
                listingObj = requests.get(config.marketUrl.replace('item_nameid=', f'item_nameid={itemId}'), timeout=3).json()
            else:
                proxy = config.proxies.pop(0)
                config.proxies.append(proxy)
                listingObj = requests.get(config.marketUrl.replace('item_nameid=', f'item_nameid={itemId}'), proxies=proxy, timeout=3).json()
        except Exception as e:
            print('Connection error occurred, skipping item...')
            listingObj = None

        if not listingObj or listingObj['sell_order_count'] == 0:
            itemIter += 1
            continue
        
        curPrice = float(listingObj['sell_order_price'].replace('$', '').replace(',', ''))
        itemDict[item['market_name'].replace('★ ', '').replace('™', '')] = curPrice
        itemIter += 1

    newPriceDf['Name'] = itemDict.keys()
    newPriceDf['Price'] = itemDict.values()
    print(newPriceDf)
    return newPriceDf

def comparePrices(oldPriceDf: pd.DataFrame, newPriceDf: pd.DataFrame):
    print('Comparing new and old price change data...')
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
    mergedPriceDict = mergedDf.set_index('Name')['Price_new'].to_dict()
    json.dump(mergedPriceDict, open(f'{config.cwd}/data/last_price_check.json', 'w'))