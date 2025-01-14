"""bitget_position_sensor"""

import logging
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import STATE_UNKNOWN
from bitpy import BitgetAPI, BitgetAPIError

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

        self._api = BitgetAPI(
            api_key=api_key,
            secret_key=secret_key,
            api_passphrase=passphrase,
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
            position = self._api.position.get_single_position(
                symbol=self._symbol,
                product_type=self._product_type,
                margin_coin=self._margin_coin
            )

            if position.data:
                pos_data = position.data[0]
                value = float(pos_data.unrealizedPL if pos_data.unrealizedPL not in (None, '', 'null') else 0)
                pos_data.formatted_unrealizedPL = (f"+{self.format_numeric_field(str(value))}"
                                                   if value > 0
                                                   else self.format_numeric_field(str(value)))

                self._data = pos_data
                self._state = value
            else:
                self._state = 0
                self._data = None

        except (BitgetAPIError, ConnectionError) as error:
            logger.error("Error updating %s - %s", self._name, error)
