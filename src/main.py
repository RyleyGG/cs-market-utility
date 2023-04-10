import sys
from services.Initialize import *
from services.HistoricalData import *
from services.PriceChange import *
from services.Config import config

def main():
    argList = sys.argv[1:]
    if len(argList) == 0:
        return
    runParam = argList[0]
    if runParam not in ['historical', 'prices']:
        print(f'Invalid run parameter "{runParam}". Valid choices are "historical" and "prices". Exiting...')
        exit(1)
    
    initDirs()
    initProxies()
    if runParam == 'historical':
        existingPricesDf = pullExistingPrices()
        newPriceDf = getNewPrices()
        pushHistorical(existingPricesDf, newPriceDf)
    elif runParam == 'prices':
        oldPriceDf = getOldPrices()
        newPriceDf = getNewPrices()
        comparePrices(oldPriceDf, newPriceDf)
            

if __name__ == '__main__':
    main()