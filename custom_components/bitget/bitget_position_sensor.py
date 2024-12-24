"""bitget_position_sensor"""

import logging
from datetime import timedelta
from .bitget_api import BitgetPositionAPI, BitgetAPIError
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import STATE_UNKNOWN

logger = logging.getLogger(__name__)


class BitgetPositionSensor(Entity):
    def __init__(self, api_key, secret_key, passphrase, symbol, product_type="USDT-FUTURES", margin_coin="USDT",
                 update_interval=60):
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._name = f"BitGet Position {symbol.upper()}"
        self._symbol = symbol
        self._product_type = product_type
        self._margin_coin = margin_coin
        self._update_interval = update_interval
        self._state = STATE_UNKNOWN
        self._data = {}

        self._api = BitgetPositionAPI(
            api_key=api_key,
            secret_key=secret_key,
            api_passphrase=passphrase,
            debug=False
        )

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._data

    async def async_added_to_hass(self):
        self.hass.helpers.event.async_track_time_interval(
            self.update, timedelta(seconds=self._update_interval)
        )

    @staticmethod
    def format_position_size(value) -> str:
        value = float(value)
        if value == 0:
            return "0.0000"
        elif value < 0.01:
            return f"{value:.4f}"
        elif value < 0.1:
            return f"{value:.4f}"
        elif value < 1:
            return f"{value:.4f}"
        elif value < 10:
            return f"{value:.4f}"
        elif value < 100:
            return f"{value:.3f}"
        elif value < 1000:
            return f"{value:.2f}"
        elif value < 10000:
            return f"{value / 1000:.2f}k"
        else:
            return f"{value / 1000:.1f}k"

    def format_numeric_field(self, value: str) -> str:
        """Safely format numeric fields from the API response."""
        if value is None or value == '' or value == 'null':
            return '0.000'
        try:
            return self.format_position_size(value)
        except (ValueError, TypeError):
            return '0.000'

    def update(self, *args):
        logger.debug("Updating %s - args", self._name, args)

        try:
            position = self._api.get_single_position(
                symbol=self._symbol,
                product_type=self._product_type,
                margin_coin=self._margin_coin
            )

            if position.data:
                pos_data = position.data[0].__dict__

                numeric_fields = [
                    'openDelegateSize', 'marginSize', 'available', 'locked',
                    'total', 'leverage', 'achievedProfits', 'openPriceAvg',
                    'unrealizedPL', 'liquidationPrice', 'keepMarginRate',
                    'markPrice', 'breakEvenPrice', 'totalFee', 'deductedFee',
                    'marginRatio'
                ]

                for field in numeric_fields:
                    if field in pos_data:
                        pos_data[f'formatted_{field}'] = self.format_numeric_field(pos_data[field])

                self._data = pos_data
                self._state = float(pos_data.get('unrealizedPL', 0))
            else:
                self._state = 0
                self._data = {}

        except (BitgetAPIError, ConnectionError) as error:
            logger.error("Error updating %s - %s", self._name, error)