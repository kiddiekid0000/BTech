import os
import json
from tqdm import tqdm
from config import *

os.makedirs(RAW_DATA_DIR, exist_ok=True)
blocks = os.listdir(RAW_DATA_DIR)

for block in tqdm(blocks):
    with open(os.path.join(RAW_DATA_DIR, block), 'r', encoding='utf-8') as file:
        data = json.load(file)

    print(len(data['data']['transactions']))