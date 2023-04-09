import os

class Config:
    cwd = os.getcwd().split('/src')[0].split('\src')[0]
config = Config