import os
import subprocess
from piapy import PiaVpn
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

def initVpn():
    print('Verifying VPN configuration...')
    try:
        subprocess.check_output(f'"{config.piaLoc}" --version', shell=True)
    except Exception as e:
        print('PIA verification command failed. See ReadME for details.')

    piaRunning = True
    try:
        runCmd = str(subprocess.check_output(f'TASKLIST /FI "IMAGENAME eq pia-client.exe" /FI "STATUS eq running"', shell=True))
        if 'INFO: No tasks are running which match the specified criteria.' in runCmd:
            piaRunning = False
    except Exception as e:
        piaRunning = False
    if not piaRunning:
        print('PIA application is not running (or there was an error detecting it). Exiting...')
        exit(1)
    
    vpn = PiaVpn()

    try:
        vpn.connect(timeout=3)
    except Exception as e:
        print('There was an error connecting to the PIA VPN. Ensure you are logged in and try again. Exiting...')
        exit(1)