import logging
from roborock import DeviceData, RoborockCommand
from roborock.version_1_apis import RoborockMqttClientV1
from roborock.web_api import RoborockApiClient
from app.config import USERNAME, PASSWORD, LOG_LEVEL

# Configure logging for RoborockInfo
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RoborockInfo:
    def __init__(self):
        self.api_client = RoborockApiClient(USERNAME)
        self.user_data = None
        self.home_data = None
        self.device_data = None
        self.mqtt_client = None

    async def initialize(self):
        """Initialize API client."""
        try:
            await self._authenticate()
        except Exception as e:
            logger.error("Failed to initialize RoborockInfo: %s", e)
            raise Exception("Failed to initialize RoborockInfo")

    async def _authenticate(self):
        """Log in and fetch home data."""
        try:
            self.user_data = await self.api_client.pass_login(PASSWORD)
            self.home_data = await self.api_client.get_home_data(self.user_data)
            await self.fetch_device_data()
            logger.info("Authentication successful")
        except Exception as e:
            logger.error("Authentication error: %s", e)
            raise Exception("Failed to authenticate with Roborock API")

    async def fetch_device_data(self, device_number=0):
        """Fetch device data based on the device index in the home data."""
        try:
            product_model_map = {product.id: product.model for product in self.home_data.products}
            device_data_list = [
                DeviceData(device=device, model=product_model_map.get(device.product_id, "Unknown Model"), host=None)
                for device in self.home_data.devices
            ]
            self.device_data = device_data_list[device_number]
            logger.info("Device data fetched successfully")
        except KeyError as e:
            logger.error("Device data fetch error: %s", e)
            raise Exception("Device data is not available")

    async def initialize_mqtt(self):
        """Initialize the MQTT client and establish the connection if not already connected."""
        if self.mqtt_client is None:
            self.mqtt_client = RoborockMqttClientV1(
                user_data=self.user_data, device_info=self.device_data, queue_timeout=20
            )

        if not self.mqtt_client.is_connected():
            try:
                await self.mqtt_client.async_connect()
                logger.info("Connected to MQTT server")
            except Exception as e:
                logger.error("Failed to connect to MQTT: %s", e)
                raise Exception("Failed to connect to Roborock MQTT server")

    async def disconnect_mqtt(self):
        """Disconnect the MQTT client."""
        if self.mqtt_client and self.mqtt_client.is_connected():
            try:
                await self.mqtt_client.async_disconnect()
                logger.info("Disconnected from MQTT server")
            except Exception as e:
                logger.warning("Error disconnecting MQTT: %s", e)

    async def get_room_mappings(self):
        """Fetch room mappings, connecting to MQTT if necessary."""
        await self.initialize_mqtt()  # Ensure MQTT is connected
        try:
            mapping = await self.mqtt_client.send_command(RoborockCommand.GET_ROOM_MAPPING)
            logger.info("Room mappings fetched successfully")
            return mapping
        except Exception as e:
            logger.error("Failed to fetch room mappings: %s", e)
            raise Exception("Failed to retrieve room mappings from Roborock")
