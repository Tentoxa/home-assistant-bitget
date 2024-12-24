import os

from dotenv import load_dotenv
from custom_components.bitget.bitget_api import BitgetPositionAPI

load_dotenv()

api_key = os.getenv("ACCESS_KEY")
api_sign = os.getenv("ACCESS_SIGN")
api_passphrase = os.getenv("ACCESS_PASSPHRASE")

bitget_position_api = BitgetPositionAPI(api_key, api_sign, api_passphrase, debug=False)

productType = "USDT-FUTURES"
symbol = "BTC-USDT"
marginCoin = "USDT"

# get single position
position = bitget_position_api.get_single_position(
    symbol="BTC-USDT",           # Trading pair name
    product_type="USDT-FUTURES", # Product type
    margin_coin="USDT"          # Margin coin
)

# get all positions
positions = bitget_position_api.get_all_positions(
    product_type=productType,  # Product type
    margin_coin=marginCoin     # Margin coin
)

print(positions)