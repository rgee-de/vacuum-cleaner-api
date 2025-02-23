import logging
from roborock import (
    DeviceData,
    RoborockCommand,
    DeviceProp,
    RoborockFanSpeedS7MaxV,
    RoborockMopModeS7,
    RoborockMopIntensityS7
)
from roborock.version_1_apis import RoborockMqttClientV1
from roborock.web_api import RoborockApiClient

from app.config import USERNAME, PASSWORD, LOG_LEVEL

# Configure logging for RoborockInfo
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RoborockInfo:
    """
    Manages the Roborock device connection, MQTT client, and commands.
    """
    def __init__(self):
        self.api_client = RoborockApiClient(USERNAME)
        self.user_data = None
        self.home_data = None
        self.device_data = None
        self.mqtt_client = None
        self.room_mappings = None
        self.status = None

    async def initialize(self):
        """
        Authenticate and initialize RoborockInfo.
        """
        try:
            await self._authenticate()
            logger.info("RoborockInfo initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize RoborockInfo: %s", e)
            raise Exception("Failed to initialize RoborockInfo")

    async def _authenticate(self):
        """
        Authenticate with the Roborock API and fetch user data.
        """
        try:
            self.user_data = await self.api_client.pass_login(PASSWORD)
            await self.fetch_home_data()
            logger.info("Authentication successful.")
        except Exception as e:
            logger.error("Authentication error: %s", e)
            raise Exception("Failed to authenticate with Roborock API")

    async def fetch_home_data(self):
        """
        Fetch home data and room information from the API.
        """
        try:
            self.home_data = await self.api_client.get_home_data(self.user_data)
            await self.fetch_device_data()
            logger.info("Home data fetched successfully.")
        except Exception as e:
            logger.error("Error fetching home data: %s", e)
            raise Exception("Failed to fetch home data")

    async def fetch_device_data(self, device_number=0):
        """
        Fetch device data for a specific device in the user's home.
        """
        try:
            product_model_map = {product.id: product.model for product in self.home_data.products}
            device_data_list = [
                DeviceData(
                    device=device,
                    model=product_model_map.get(device.product_id, "Unknown Model"),
                    host=None
                )
                for device in self.home_data.devices
            ]
            self.device_data = device_data_list[device_number]
            logger.info("Device data fetched successfully.")
        except KeyError as e:
            logger.error("Device data fetch error: %s", e)
            raise Exception("Device data is not available")

    async def initialize_mqtt(self):
        """
        Initialize the MQTT client if it has not been created or is not connected.
        """
        if self.mqtt_client is None:
            self.mqtt_client = RoborockMqttClientV1(
                user_data=self.user_data,
                device_info=self.device_data,
                queue_timeout=20
            )
        if not self.mqtt_client.is_connected():
            try:
                await self.mqtt_client.async_connect()
                logger.info("Connected to MQTT server.")
            except Exception as e:
                logger.error("Failed to connect to MQTT: %s", e)
                raise Exception("Failed to connect to Roborock MQTT server")

    async def disconnect_mqtt(self):
        """
        Disconnect from the MQTT server if connected.
        """
        if self.mqtt_client and self.mqtt_client.is_connected():
            try:
                await self.mqtt_client.async_disconnect()
                logger.info("Disconnected from MQTT server.")
            except Exception as e:
                logger.warning("Error during MQTT disconnection: %s", e)

    async def fetch_room_mappings(self):
        """
        Fetch room mappings from the MQTT client if they are not already stored.
        """
        if not self.room_mappings:
            await self.initialize_mqtt()
            try:
                self.room_mappings = await self.mqtt_client.send_command(RoborockCommand.GET_ROOM_MAPPING)
                logger.info("Room mappings fetched successfully.")
            except Exception as e:
                logger.error("Failed to fetch room mappings: %s", e)
                raise Exception("Failed to retrieve room mappings from Roborock")

    async def get_rooms(self):
        """
        Get a list of rooms combined with segment IDs.
        """
        if not self.home_data:
            await self.fetch_home_data()
        if not self.room_mappings:
            await self.fetch_room_mappings()

        # Map room IDs to segment IDs
        room_mapping_dict = {
            iot_id: segment_id for segment_id, iot_id, _ in self.room_mappings
        }

        # Combine room names with segment IDs
        rooms_with_segments = [
            {"segment_id": room_mapping_dict.get(str(room.id)), "name": room.name}
            for room in self.home_data.rooms
            if str(room.id) in room_mapping_dict
        ]

        logger.info("Rooms with segment IDs: %s", rooms_with_segments)
        return rooms_with_segments

    async def get_device_prop(self) -> DeviceProp:
        """
        Retrieve device properties (e.g., status, battery level) via MQTT.
        """
        await self.initialize_mqtt()
        try:
            device_prop = await self.mqtt_client.get_prop()
            logger.info("Device prop fetched successfully.")
            return device_prop
        except Exception as e:
            logger.error("Failed to fetch device prop: %s", e)
            raise Exception("Failed to retrieve device prop from Roborock")

    async def set_clean_mode_s7maxv(
        self,
        fan_speed: RoborockFanSpeedS7MaxV = RoborockFanSpeedS7MaxV.custom,
        mop_mode: RoborockMopModeS7 = RoborockMopModeS7.custom,
        mop_intensity: RoborockMopIntensityS7 = RoborockMopIntensityS7.custom
    ):
        """
        Set clean mode (fan speed, mop mode, mop intensity) for S7MaxV via MQTT.
        """
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(
                RoborockCommand.SET_CLEAN_MOTOR_MODE,
                params=[{
                    "fan_power": fan_speed,
                    "mop_mode": mop_mode,
                    "water_box_mode": mop_intensity
                }]
            )
            logger.info("Clean mode set successfully.")
        except Exception as e:
            logger.error("Failed to set clean mode: %s", e)
            raise Exception("Failed to set clean mode on Roborock")

    async def clean_room(self, segment_ids: [int], repeat: int = 1):
        """
        Start cleaning specific room segments with optional repeat count.
        """
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(
                RoborockCommand.APP_SEGMENT_CLEAN,
                params=[{"segments": segment_ids, "repeat": repeat}]
            )
            logger.info("Room cleaning started successfully.")
        except Exception as e:
            logger.error("Failed to start room cleaning: %s", e)
            raise Exception("Failed to start clean room on Roborock")

    async def go_to(self, x: int, y: int):
        """
        Send the robot to specified coordinates (x, y).
        """
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.APP_GOTO_TARGET, params=[x, y])
            logger.info("Navigation to coordinates started successfully.")
        except Exception as e:
            logger.error("Failed to navigate to coordinates: %s", e)
            raise Exception("Failed to start go-to on Roborock")

    async def charge(self):
        """
        Send the robot back to its charging station.
        """
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.APP_CHARGE, params=[])
            logger.info("Robot sent to charging station successfully.")
        except Exception as e:
            logger.error("Failed to send robot to charging: %s", e)
            raise Exception("Failed to start go-to on Roborock")

    async def stop(self):
        """
        Stop the robot's current task (cleaning or navigation).
        """
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.APP_STOP)
            logger.info("Stopped the vacuum’s current task.")
        except Exception as e:
            logger.error("Failed to stop current task: %s", e)
            raise Exception("Failed to stop current task on Roborock")

    async def pause(self):
        """
        Pause the robot's current task (cleaning or navigation).
        """
        await self.initialize_mqtt()
        try:
            await self.mqtt_client.send_command(RoborockCommand.APP_PAUSE)
            logger.info("Paused the vacuum’s current task.")
        except Exception as e:
            logger.error("Failed to pause current task: %s", e)
            raise Exception("Failed to pause current task on Roborock")
