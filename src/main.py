import sys
import subprocess
from services.Initialize import *
from services.HistoricalData import *
from services.PriceChange import *
from services.Config import config
from piapy import PiaVpn

def main():
    argList = sys.argv[1:]
    if len(argList) == 0:
        print('No run parameters supplied. Valid choices are "historical" and "prices". Exiting...')
        exit(1)
    runParam = argList[0]
    if runParam not in ['historical', 'prices']:
        print(f'Invalid run parameter "{runParam}". Valid choices are "historical" and "prices". Exiting...')
        exit(1)
    
    initDirs()
    initVpn()
    if runParam == 'historical':
        existingPricesDf = getOldHistorical()
        newPriceDf = getNewHistorical()
        pushHistorical(existingPricesDf, newPriceDf)
    elif runParam == 'prices':
        oldPriceDf = getOldPrices()
        newDfs = getNewPrices()
        curPriceDf = newDfs[0]
        lastSoldDf = newDfs[1]
        comparePrices(oldPriceDf, lastSoldDf, curPriceDf)
            

if __name__ == '__main__':
    main()