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

pos_data = position.data[0].__dict__


def format_position_size(value) -> str:
    value = float(value)
    abs_value = abs(value)

    if value == 0:
        return "0.000"

    if abs_value < 1:
        return f"{value:.3f}"[:6]

    elif abs_value < 10:
        return f"{value:.3f}"[:6]

    elif abs_value < 100:
        return f"{value:.2f}"[:6]

    elif abs_value < 1000:
        return f"{value:.2f}"[:6]

    elif abs_value < 10000:
        k_value = f"{value / 1000:.2f}k"
        if len(k_value) > 6:
            k_value = f"{value / 1000:.1f}k"
        return k_value

    else:
        k_value = f"{value / 1000:.1f}k"
        if len(k_value) > 6:
            k_value = f"{value / 1000:.0f}k"
        return k_value


def format_numeric_field(value: str) -> str:
    """Safely format numeric fields from the API response."""
    if value is None or value == '' or value == 'null':
        return '0.000'
    try:
        return format_position_size(value)
    except (ValueError, TypeError):
        return '0.000'

numeric_fields = [
    'openDelegateSize', 'marginSize', 'available', 'locked',
    'total', 'leverage', 'achievedProfits', 'openPriceAvg',
    'unrealizedPL', 'liquidationPrice', 'keepMarginRate',
    'markPrice', 'breakEvenPrice', 'totalFee', 'deductedFee',
    'marginRatio'
]

for field in numeric_fields:  # Only iterate through numeric fields
    if field in pos_data:  # Check if field exists in pos_data
        if field == 'unrealizedPL':
            value = float(pos_data[field] if pos_data[field] not in (None, '', 'null') else 0)
            pos_data[f'formatted_{field}'] = f"+{format_numeric_field(str(value))}" if value > 0 else format_numeric_field(str(value))
        else:
            pos_data[f'formatted_{field}'] =format_numeric_field(pos_data[field])


print(pos_data)