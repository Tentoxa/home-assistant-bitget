import requests
from dataclasses import dataclass, fields
from typing import List, Optional
from datetime import datetime
import logging
import base64
import hmac


@dataclass
class PositionData:
    marginCoin: str
    symbol: str
    holdSide: str
    openDelegateSize: str
    marginSize: str
    available: str
    locked: str
    total: str
    leverage: str
    achievedProfits: str
    openPriceAvg: str
    marginMode: str
    posMode: str
    unrealizedPL: str
    liquidationPrice: str
    keepMarginRate: str
    markPrice: str
    breakEvenPrice: str
    totalFee: str
    deductedFee: str
    marginRatio: str
    assetMode: str
    autoMargin: str
    grant: str
    takeProfit: str
    stopLoss: str
    takeProfitId: str
    stopLossId: str
    cTime: str
    uTime: str

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                # Convert None to empty string to match API behavior
                setattr(self, k, v if v is not None else '')


@dataclass
class AllPositionsResponse:
    code: str
    msg: str
    requestTime: int
    data: List[PositionData]


@dataclass
class SinglePositionResponse:
    code: str
    msg: str
    requestTime: int
    data: List[PositionData]


logger = logging.getLogger(__name__)

class BitgetAPIError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"BitgetAPI Error {code}: {message}")

class BitgetPositionAPI:
    """
    BitgetPositionAPI is a class that provides methods to interact with the Bitget Position API.

    Args:
        api_key (str): Your API key.
        secret_key (str): Your API secret key.
        api_passphrase (str): Your API passphrase.
        base_url (str): Base URL for the API. Default is "https://api.bitget.com".
        debug (bool): Enable debug mode. Default is False

    Attributes:
        base_url (str): Base URL for the API.
        api_key (str): Your API key.
        secret_key (str): Your API secret key.
        api_passphrase (str): Your API passphrase.
        debug (bool): Enable debug mode.
        session (requests.Session): A session for connection pooling.

    Methods:
        get_all_positions: Get all positions information.
        get_single_position: Get single position information for a specific trading pair.


    """
    def __init__(self, api_key: str, secret_key: str, api_passphrase: str, base_url: str = "https://api.bitget.com",
                 debug: bool = False):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.secret_key = secret_key
        self.api_passphrase = api_passphrase
        self.debug = debug
        # Create a session for connection pooling
        self.session = requests.Session()
        self._setup_logging()

    def _setup_logging(self):
        if not self.debug:
            return

        logger.setLevel(logging.DEBUG)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    @staticmethod
    def _clean_symbol(symbol: str) -> str:
        return symbol.lower().strip().replace("-", "").replace("_", "").replace("/", "").replace("\\", "")

    def _get_headers(self, method: str, request_path: str, query_string: str = "", body: str = "") -> dict:
        """Generate headers with signature for each request"""
        timestamp = str(int(datetime.now().timestamp() * 1000))
        signature = self._generate_signature(timestamp, method, request_path, query_string, body)

        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.api_passphrase,
            "Content-Type": "application/json",
            "locale": "en-US"
        }

    def _generate_signature(self, timestamp: str, method: str, request_path: str,
                            query_string: str = "", body: str = "") -> str:
        """Generate signature for API request"""
        message = timestamp + method.upper() + request_path
        if query_string:
            message += "?" + query_string
        if body:
            message += body

        if self.debug:
            logger.debug(f"Signature message: {message}")

        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                digestmod='sha256'
            ).digest()
        ).decode('utf-8')

        return signature

    def get_all_positions(self, product_type: str, margin_coin: Optional[str] = None) -> AllPositionsResponse:
        """Get all positions information"""
        request_path = "/api/v2/mix/position/all-position"
        params = {"productType": product_type}
        if margin_coin:
            params["marginCoin"] = margin_coin.upper()

        # Sort query parameters alphabetically
        query_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))

        if self.debug:
            logger.debug(f"Request path: {request_path}")
            logger.debug(f"Query string: {query_string}")

        try:
            headers = self._get_headers("GET", request_path, query_string)
            response = requests.get(
                f"{self.base_url}{request_path}?{query_string}",
                headers=headers
            )
            if self.debug:
                logger.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
            response_data = response.json()

            if self.debug:
                logger.debug(f"Response data: {response_data}")

            if response_data["code"] != "00000":
                raise ValueError(f"API Error: {response_data['msg']}")

            return AllPositionsResponse(
                code=response_data["code"],
                msg=response_data["msg"],
                requestTime=response_data["requestTime"],
                data=[PositionData(**item) for item in response_data["data"]]
            )

        except requests.exceptions.RequestException as e:
            if self.debug:
                logger.error(f"HTTP Request failed: {str(e)}")
            raise ConnectionError(f"HTTP Request failed: {str(e)}")
        except (KeyError, ValueError) as e:
            if self.debug:
                logger.error(f"Response parsing error: {str(e)}")
            raise ValueError(f"Response parsing error: {str(e)}")

    def get_single_position(self, symbol: str, product_type: str, margin_coin: str) -> SinglePositionResponse:
        """Get single position information for a specific trading pair."""
        request_path = "/api/v2/mix/position/single-position"
        params = {
            "symbol": self._clean_symbol(symbol),
            "productType": product_type,
            "marginCoin": margin_coin.upper()
        }

        # Sort query parameters alphabetically
        query_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))

        if self.debug:
            logger.debug(f"Request path: {request_path}")
            logger.debug(f"Query string: {query_string}")

        try:
            headers = self._get_headers("GET", request_path, query_string)
            response = requests.get(
                f"{self.base_url}{request_path}?{query_string}",
                headers=headers
            )
            if self.debug:
                logger.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
            response_data = response.json()

            if self.debug:
                logger.debug(f"Response data: {response_data}")

            if response_data["code"] != "00000":
                raise ValueError(f"API Error: {response_data['msg']}")

            return SinglePositionResponse(
                code=response_data["code"],
                msg=response_data["msg"],
                requestTime=response_data["requestTime"],
                data=[PositionData(**item) for item in response_data["data"]]
            )

        except requests.exceptions.RequestException as e:
            if self.debug:
                logger.error(f"HTTP Request failed: {str(e)}")
            raise ConnectionError(f"HTTP Request failed: {str(e)}")
        except (KeyError, ValueError) as e:
            if self.debug:
                logger.error(f"Response parsing error: {str(e)}")
            raise ValueError(f"Response parsing error: {str(e)}")
