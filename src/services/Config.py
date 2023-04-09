import os

class Config:
    cwd = os.getcwd().split('/src')[0].split('\src')[0]
    priceCols = ['Name', 'Price']
    historicalCols = ['Name', 'Month', 'Price']
    marketUrl = 'https://steamcommunity.com/market/search?q=&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_Quality%5B%5D=tag_unusual&category_730_Quality%5B%5D=tag_unusual_strange&category_730_Rarity%5B%5D=tag_Rarity_Legendary_Weapon&category_730_Rarity%5B%5D=tag_Rarity_Ancient_Weapon&category_730_Rarity%5B%5D=tag_Rarity_Ancient&category_730_Rarity%5B%5D=tag_Rarity_Legendary_Character&category_730_Rarity%5B%5D=tag_Rarity_Ancient_Character&category_730_Rarity%5B%5D=tag_Rarity_Legendary&category_730_Rarity%5B%5D=tag_Rarity_Contraband&appid=730'
    requestHeaders = 'headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}'
config = Config