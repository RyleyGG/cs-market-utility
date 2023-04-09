import os
import glob
from services.Config import config

def initDirs():
    if not os.path.exists(f'{config.cwd}/data'):
        os.makedirs(f'{config.cwd}/data')
    
    if not os.path.isfile(f'{config.cwd}/data/last_price_check.json'):
        file = open(f'{config.cwd}/data/historical.json', 'w')
        file.close()

    if not os.path.isfile(f'{config.cwd}/data/historical.json'):
        file = open(f'{config.cwd}/data/historical.json', 'w')
        file.close()