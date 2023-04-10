import os
import json
import datetime
import requests
from fp.fp import FreeProxy
from services.Config import config

def initDirs():
    print('Initializing local directories...')
    if not os.path.exists(f'{config.cwd}/data'):
        os.makedirs(f'{config.cwd}/data')
    
    if not os.path.isfile(f'{config.cwd}/data/last_price_check.json'):
        file = open(f'{config.cwd}/data/last_price_check.json', 'w')
        file.close()

    if not os.path.isfile(f'{config.cwd}/data/historical.json'):
        file = open(f'{config.cwd}/data/historical.json', 'w')
        file.close()

    if not os.path.isfile(f'{config.cwd}/data/proxy_list.json'):
        file = open(f'{config.cwd}/data/proxy_list.json', 'w')
        file.close()

def initProxies():
    print('Initializing proxies...')
    findNewProxies = False
    proxyObj = ''
    try:
        proxyObj = json.load(open(f'{config.cwd}/data/proxy_list.json', 'r'))
    except Exception as e:
        pass

    if len(proxyObj) != 0:
        oldDate = ''
        for item in proxyObj:
            if 'datetime_generated' in item:
                oldDate = datetime.datetime.strptime(item['datetime_generated'], '%Y-%m-%d %H:%M:%S.%f')
        newDate = datetime.datetime.now()
        dayDiff = newDate - oldDate
        dayDiff = dayDiff.days
        if dayDiff >= 5:
            findNewProxies = True
    else:
        findNewProxies = True

    if findNewProxies:
        print('Current proxy list does not meet constraints. Generating new list...')
        totalAttempts = 0
        while len(config.proxySet) < 5 and totalAttempts <= 25:
            proxyStr = FreeProxy(https=True, rand=True).get().replace('http://', '')
            proxyDict = {'http': proxyStr, 'https': proxyStr}
            print(f'Proxy found: {proxyStr}')

            stepOneSuccess = False
            stepTwoSuccess = False
            requestSuccess = True

            try:
                # Step one - Check that proxy IP is applying
                resp = requests.get('http://ident.me/', proxies=proxyDict)
                foundIp = str(resp.content)[2:-1]
                if foundIp == proxyStr.split(':')[0]:
                    stepOneSuccess = True
                
                # Step two - Check that proxy does not have a self-signed SSL cert by checking https secured site
                resp = requests.get('https://steamcommunity.com', proxies=proxyDict)
                if resp.status_code == 200:
                    stepTwoSuccess = True
            except Exception as e:
                requestSuccess = False

            print(f'Proxy validation step one... {"SUCCESS" if stepOneSuccess else "FAILED"}')
            print(f'Proxy validation step two... {"SUCCESS" if stepOneSuccess else "FAILED"}')
            print(f'Request... {"SUCCESS" if requestSuccess else "FAILED"}')

            if stepOneSuccess and stepTwoSuccess and requestSuccess and proxyStr not in config.proxySet:
                print('Proxy valid... ADDED')
                config.proxySet.add(proxyStr)
                config.proxies.append(proxyDict)
            elif proxyStr in config.proxySet:
                print('Proxy duplicate... SKIPPED')
            else:
                print('Proxy invalid... SKIPPED')
            totalAttempts += 1
        
        proxyReturnObj = list(config.proxies)
        proxyReturnObj.append({'datetime_generated': str(datetime.datetime.now())})
        json.dump(proxyReturnObj, open(f'{config.cwd}/data/proxy_list.json', 'w'))
    else:
        print('Current proxy list meets constraints. Continuing...')
        proxyList = []
        for item in proxyObj:
            if 'http' in item:
                proxyList.append(item)
        config.proxies = proxyList