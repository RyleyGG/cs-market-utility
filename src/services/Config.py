import os

class Config:
    cwd = os.getcwd().split('/src')[0].split('\src')[0]
    priceCols = ['Name', 'Price']
    historicalCols = ['Name', 'Month', 'Price']
    marketUrl = 'https://steamcommunity.com/market/search/render?query=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_Rarity%5B%5D=tag_Rarity_Legendary_Weapon&category_730_Rarity%5B%5D=tag_Rarity_Ancient_Weapon&category_730_Rarity%5B%5D=tag_Rarity_Ancient&category_730_Rarity%5B%5D=tag_Rarity_Legendary_Character&category_730_Rarity%5B%5D=tag_Rarity_Ancient_Character&category_730_Rarity%5B%5D=tag_Rarity_Legendary&category_730_Rarity%5B%5D=tag_Rarity_Contraband&start=&count=1000&norender=1&appid=730'
    apiKey = None
    proxies = []

    def __init__(self):
        try:
            file = open(f'{self.cwd}/.env', 'r')
            self.apiKey = file.readline().split('api_key: ')[1].strip()
        except Exception as e:
            print('Unable to grab API key from local .env file. Exiting...')
            exit(1)
config = Config()