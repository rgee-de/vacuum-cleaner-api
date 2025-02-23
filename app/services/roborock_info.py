import logging

from roborock import DeviceData, RoborockCommand, DeviceProp, RoborockFanSpeedS7MaxV, RoborockMopModeS7, \
    RoborockMopIntensityS7
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
        self.room_mappings = None
        self.status = None

    async def initialize(self):
        """Authenticate and initialize RoborockInfo."""
        try:
            await self._authenticate()
            logger.info("RoborockInfo initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize RoborockInfo: %s", e)
            raise Exception("Failed to initialize RoborockInfo")

    async def _authenticate(self):
        """Authenticate with the API and fetch user data."""
        try:
            self.user_data = await self.api_client.pass_login(PASSWORD)
            await self.fetch_home_data()  # Initialize home data on authentication
            logger.info("Authentication successful")
        except Exception as e:
            logger.error("Authentication error: %s", e)
            raise Exception("Failed to authenticate with Roborock API")

    async def fetch_home_data(self):
        """Fetch home data and room information from the API."""
        try:
            self.home_data = await self.api_client.get_home_data(self.user_data)
            await self.fetch_device_data()
            logger.info("Home data fetched successfully")
        except Exception as e:
            logger.error("Error fetching home data: %s", e)
            raise Exception("Failed to fetch home data")

    async def fetch_device_data(self, device_number=0):
        """Fetch device data based on the selected device."""
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
        """Initialize the MQTT client only if not already connected."""
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
        """Disconnect from the MQTT server if connected."""
        if self.mqtt_client and self.mqtt_client.is_connected():
            try:
                await self.mqtt_client.async_disconnect()
                logger.info("Disconnected from MQTT server")
            except Exception as e:
                logger.warning("Error disconnecting MQTT: %s", e)

    async def fetch_room_mappings(self):
        """Fetch room mappings from MQTT if not already fetched."""
        if not self.room_mappings:
            await self.initialize_mqtt()
            try:
                self.room_mappings = await self.mqtt_client.send_command(RoborockCommand.GET_ROOM_MAPPING)
                logger.info("Room mappings fetched successfully")
            except Exception as e:
                logger.error("Failed to fetch room mappings: %s", e)
                raise Exception("Failed to retrieve room mappings from Roborock")

    async def get_rooms(self):
        """Fetch the latest room data and segment mappings, and return rooms with segment IDs."""
        # Ensure home_data and room_mappings are up-to-date
        if not self.home_data:
            await self.fetch_home_data()
        if not self.room_mappings:
            await self.fetch_room_mappings()

        # Create a dictionary to map room IDs to segment IDs
        room_mapping_dict = {iot_id: segment_id for segment_id, iot_id, _ in self.room_mappings}

        # Combine room names with segment IDs
        rooms_with_segments = [
            {"segment_id": room_mapping_dict.get(str(room.id)), "name": room.name}
            for room in self.home_data.rooms
            if str(room.id) in room_mapping_dict
        ]

        logger.info("Rooms with segment IDs: %s", rooms_with_segments)
        return rooms_with_segments

    async def get_device_prop(self) -> DeviceProp:
        """Fetch device prop from MQTT."""
        await self.initialize_mqtt()
        try:
            device_prop = await self.mqtt_client.get_prop()
            logger.info("Device prop fetched successfully")
            return device_prop
        except Exception as e:
            logger.error("Failed to fetch device prop: %s", e)
            raise Exception("Failed to retrieve device prop from Roborock")

    async def set_clean_mode_s7maxv(self, fan_speed: RoborockFanSpeedS7MaxV = RoborockFanSpeedS7MaxV.custom,
                                    mop_mode: RoborockMopModeS7 = RoborockMopModeS7.custom,
                                    mop_intensity: RoborockMopIntensityS7 = RoborockMopIntensityS7.custom):
        """Set clean mode for S7MaxV in MQTT."""
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.SET_CLEAN_MOTOR_MODE, params=[
                {"fan_power": fan_speed, "mop_mode": mop_mode, "water_box_mode": mop_intensity}])
            logger.info("Set clean mode successfully")
        except Exception as e:
            logger.error("Failed to set clean mode: %s", e)
            raise Exception("Failed to set clean mode on Roborock")

    async def clean_room(self, segment_ids: [int], repeat: int = 1):
        """Start clean room in MQTT."""
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.APP_SEGMENT_CLEAN,
                                                params=[{"segments": segment_ids, "repeat": repeat}])
            logger.info("Start clean room successfully")
        except Exception as e:
            logger.error("Failed to start clean room: %s", e)
            raise Exception("Failed to start clean room on Roborock")

    async def go_to(self, x: int, y: int):
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.APP_GOTO_TARGET, params=[x, y])
            logger.info("Start go to successfully")
        except Exception as e:
            logger.error("Failed to start go to: %s", e)
            raise Exception("Failed to start go to on Roborock")

    async def charge(self):
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.APP_CHARGE, params=[])
            logger.info("Start go to successfully")
        except Exception as e:
            logger.error("Failed to start go to: %s", e)
            raise Exception("Failed to start go to on Roborock")

    async def stop(self):
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.APP_STOP)
            logger.info("Stop the vacuum’s current task")
        except Exception as e:
            logger.error("Failed to stop current task: %s", e)
            raise Exception("Failed to stop current task on Roborock")

    async def pause(self):
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.APP_PAUSE)
            logger.info("Pause the vacuum’s current task")
        except Exception as e:
            logger.error("Failed to pause current task: %s", e)
            raise Exception("Failed to pause current task on Roborock")
