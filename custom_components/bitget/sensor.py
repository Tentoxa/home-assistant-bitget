"""sensor"""

import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from .const import (
    CONF_API_KEY,
    CONF_SECRET_KEY,
    CONF_PASSPHRASE,
    CONF_SYMBOLS,
    DEFAULT_PRODUCT_TYPE,
    DEFAULT_MARGIN_COIN,
    DEFAULT_UPDATE_INTERVAL
)

from .bitget_position_sensor import BitgetPositionSensor

logger = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_SECRET_KEY): cv.string,
    vol.Required(CONF_PASSPHRASE): cv.string,
    vol.Required(CONF_SYMBOLS): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional('product_type', default=DEFAULT_PRODUCT_TYPE): cv.string,
    vol.Optional('margin_coin', default=DEFAULT_MARGIN_COIN): cv.string,
    vol.Optional('update_interval', default=DEFAULT_UPDATE_INTERVAL): cv.positive_int
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    api_key = config.get(CONF_API_KEY)
    secret_key = config.get(CONF_SECRET_KEY)
    passphrase = config.get(CONF_PASSPHRASE)
    symbols = config.get(CONF_SYMBOLS)
    product_type = config.get('product_type')
    margin_coin = config.get('margin_coin')
    update_interval = config.get('update_interval')

    entities = []
    for symbol in symbols:
        logger.debug("Setup BitgetPositionSensor for %s", symbol)
        entities.append(
            BitgetPositionSensor(
                api_key=api_key,
                secret_key=secret_key,
                passphrase=passphrase,
                symbol=symbol,
                product_type=product_type,
                margin_coin=margin_coin,
                update_interval=update_interval
            )
        )

    add_entities(entities, True)
