# BitGet Position Tracker for Home Assistant

Track your BitGet cryptocurrency positions directly in Home Assistant. This integration provides real-time monitoring of your futures positions, including unrealized PnL, position sizes, and other key metrics.

## Features

- Real-time position tracking for BitGet USDT-Futures
- Configurable update intervals
- Multiple symbol support
- Detailed position metrics including:
  - Unrealized PnL
  - Position Size
  - Entry Price
  - Liquidation Price
  - Mark Price
  - Margin Ratio

## Installation

1. Copy the `bitget` folder to your `custom_components` directory
2. Restart Home Assistant
3. Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: bitget
    api_key: YOUR_API_KEY
    secret_key: YOUR_SECRET_KEY
    passphrase: YOUR_PASSPHRASE
    symbols:
      - BTCUSDT
      - ETHUSDT
    update_interval: 60  # Optional, defaults to 60 seconds
```

## Configuration Variables

|Variable|Required|Description|Default|
|---|---|---|---|
|`api_key`|Yes|Your BitGet API key||
|`secret_key`|Yes|Your BitGet Secret key||
|`passphrase`|Yes|Your BitGet API passphrase||
|`symbols`|Yes|List of trading pairs to monitor||
|`product_type`|No|Product type to monitor|USDT-FUTURES|
|`margin_coin`|No|Margin coin for futures|USDT|
|`update_interval`|No|Update interval in seconds|60|

## State and Attributes

Each sensor will have the following:

- State: Current unrealized PnL
- Attributes:
  - Position Size
  - Entry Price
  - Leverage
  - Liquidation Price
  - Mark Price
  - Margin Ratio
  - Total Fees
  - Available Margin
  - Locked Margin

## Security Notice

Store your API credentials securely using Home Assistant secrets:

```yaml
sensor:
  - platform: bitget
    api_key: !secret bitget_api_key
    secret_key: !secret bitget_secret_key
    passphrase: !secret bitget_passphrase
    symbols:
      - BTCUSDT
```

## Contributing

Feel free to submit issues and pull requests on the GitHub repository.

## License

This project is licensed under the MIT License.