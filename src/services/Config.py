import os

class Config:
    cwd = os.getcwd().split('/src')[0].split('\src')[0]
    priceCols = ['Name', 'Price']
    historicalCols = ['Name', 'Month', 'Price']
    marketUrl = 'https://steamcommunity.com/market/itemordershistogram?country=PK&language=english&currency=1&item_nameid=&two_factor=0&norender=1'
    apiKey = None
    proxySet = set()
    proxies = []

    def __init__(self):
        try:
            file = open(f'{self.cwd}/.env', 'r')
            self.apiKey = file.readline().split('api_key: ')[1]
        except Exception as e:
            print('Unable to grab API key from local .env file. Exiting...')
            exit(1)
config = Config()