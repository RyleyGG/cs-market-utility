from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import json
from time import sleep
from math import floor
from piapy import PiaVpn
from services.Config import config


def getOldPrices():
    print('Getting old price change data...')
    oldPriceDf = pd.DataFrame(columns=config.priceCols)
    try:
        priceObj = json.load(open(f'{config.cwd}/data/last_price_check.json', 'r'))
        if len(priceObj.keys()) != 0:
            oldPriceDf['Name'] = priceObj.keys()
            oldPriceDf['Price'] = priceObj.values()
        else:
            raise Exception
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
        avgPrice = item['prices']['safe_ts']['last_30d']
        if avgPrice != 0:
            lastSoldDict[item['market_hash_name'].replace('★ ', '').replace('™', '')] = avgPrice
    allItems = newItems

    # GENERATING CUR PRICE RESULTS
    pageIter = 1
    continueIter = True
    maxRes = 0
    resp = ''
    vpn = PiaVpn()
    vpn.connect(timeout=3)
    vpnSet = set()
    vpnSet.add(vpn.ip())
    print(f'Starting with IP: {vpn.ip()}')
    while continueIter:
        try:
            if maxRes != 0:
                print(f'Scraping page {pageIter} out of {"?" if maxRes == 0 else floor(maxRes / 100)} ({round((pageIter / floor(maxRes / 100)) * 100, 2)}%)')
            else:
                print(f'Scraping page {pageIter} (calculating total result count...)')
            resp = requests.get(config.marketUrl.replace('start=', f'start={pageIter*100}'))
            json = resp.json()
            res = json['results']
            for item in res:
                if item['name'].replace('★ ', '').replace('™', '') not in lastSoldDict.keys() or item['sell_listings'] == 0:
                    continue
                curPriceDict[item['name'].replace('★ ', '').replace('™', '')] = float(item['sell_price_text'].replace('$', '').replace(',', ''))

            pageIter += 1
            maxRes = max(maxRes, json['total_count'])
            if pageIter * 100 >= maxRes:
                continueIter = False
            elif ((pageIter - 1) % 20 == 0):
                print('20 pages iterated. Grabbing new IP...')
                print(f'Old IP: {vpn.ip()}')
                vpn.disconnect()
                vpn.connect()
                while vpn.ip() in vpnSet:
                    vpn.disconnect()
                    vpn.connect()
                print(f'New IP: {vpn.ip()}')
                vpnSet.add(vpn.ip())
        except Exception as e:
            if resp.status_code == 429:
                print('Connection timed out, changing VPN')
                print(f'Old IP: {vpn.ip()}')
                vpn.disconnect()
                vpn.connect()
                while vpn.ip() in vpnSet:
                    vpn.disconnect()
                    vpn.connect()
                print(f'New IP: {vpn.ip()}')
                vpnSet.add(vpn.ip())
            else:
                print('Error when parsing marketplace. Exiting...')
                print(f'ERROR: {str(e)}')
                print(f'Resp object: {resp}')
                exit(1)

    curPriceDf['Name'] = curPriceDict.keys()
    curPriceDf['Price'] = curPriceDict.values()
    lastSoldDf['Name'] = lastSoldDict.keys()
    lastSoldDf['Price'] = lastSoldDict.values()
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
    notableChangesDf = mergedDf[mergedDf['Price Difference'] < 0.85]
    notableChangesDf = notableChangesDf.sort_values(by=['Price Difference'])

    print('\n')
    if len(notableChangesDf) == 0:
        print('No notable changes found')
    else:
        print('!!!Notable changes found!!!')
        for index, row in notableChangesDf.iterrows():
            potentialProfit = row["Price_old"] * 0.85 - row["Price_new"]
            print(f'Name: {row["Name"]}')
            print(f'Old Price: {row["Price_old"]}')
            print(f'New Price: {row["Price_new"]}')
            print(f'Price Difference: {round(row["Price Difference"] * 100, 3)}%')
            print(f'Profit (if sold at old price): {round(potentialProfit, 2)}')
            print(f'Breakeven Price: {round(row["Price_new"] * 1.15, 2)}\n')
    
    print('Updating prices')
    newPriceDict = lastSoldDf.set_index('Name')['Price'].to_dict()
    json.dump(newPriceDict, open(f'{config.cwd}/data/last_price_check.json', 'w'))