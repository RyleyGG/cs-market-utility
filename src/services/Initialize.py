import os
import json
import datetime
import requests
import bs4 as bs
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
    print('Initializing proxies (this may take a few minutes)...')
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
        print('No valid proxy list found. Generating new list...')
        genProxies()
    else:
        print('Existing proxy list found. Verifying...')
        proxyList = []
        for item in proxyObj:
            if 'http' in item:
                if testProxy(item['http']):
                    proxyList.append(item)
        config.proxies = proxyList
        if len(config.proxies) < 3:
            print('Existing proxy list too short. Generating new items...')
            genProxies()
    proxyReturnObj = list(config.proxies)
    proxyReturnObj.append({'datetime_generated': str(datetime.datetime.now())})
    json.dump(proxyReturnObj, open(f'{config.cwd}/data/proxy_list.json', 'w'))


def genProxies():
    # First, get list of potential proxies from sites
    potentialProxies = []
    proxySites = [
        'https://www.sslproxies.org/',
        'https://www.us-proxy.org/',
        'https://free-proxy-list.net/uk-proxy.html',
        'https://free-proxy-list.net/'
    ]

    for site in proxySites:
        resp = requests.get(site)
        soup = bs.BeautifulSoup(resp.text, 'html.parser')
        ipTable = soup.find_all('table', {'class': 'table table-striped table-bordered'})[0]
        for row in ipTable.find_all('tr')[1:]:
            cols = row.find_all('td')
            if cols[6].text.strip().lower() == 'yes':
                ipAddr = f'{cols[0].text.strip()}:{cols[1].text.strip()}'
                if ipAddr not in potentialProxies:
                    potentialProxies.append(ipAddr)


    # Second, validate all found proxies
    totalAttempts = 0
    while len(config.validProxies) < 5 and totalAttempts <= 25 and len(potentialProxies) > 0:
        proxyStr = potentialProxies.pop(0)
        if proxyStr in config.validProxies or proxyStr in config.invalidProxies:
            continue
        proxyDict = {'http': proxyStr, 'https': proxyStr}

        if testProxy(proxyStr):
            config.validProxies.add(proxyStr)
            config.proxies.append(proxyDict)
        else:
            config.invalidProxies.add(proxyStr)
        totalAttempts += 1


def testProxy(proxy: str):
    proxyDict = {'http': proxy, 'https': proxy}
    validSuccess = False

    try:
        resp = requests.get('https://steamcommunity.com/market/search', proxies=proxyDict, timeout=3)
        if resp.status_code == 200:
            validSuccess = True
    except Exception as e:
        validSuccess = False

    print(f'Validating {proxy}... {"SUCCESS" if validSuccess else "FAILED"}')

    if validSuccess:
        return True
    else:
        return False