import asyncio
import logging

from roborock import HomeDataProduct, DeviceData, UserData, NetworkInfo, HomeDataDevice, HomeData
from roborock.version_1_apis import RoborockMqttClientV1
from roborock.web_api import RoborockApiClient

from app.model.room_summary import RoomSummary
from app.services.local_client import RoboLocalClient

logger = logging.getLogger(__name__)


class ClientConnection:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

        self.web_api: RoborockApiClient = None
        self.user_data: UserData = None
        self.home_data: HomeData = None
        self.device: HomeDataDevice = None
        self.product_info: dict[str, HomeDataProduct] = None
        self.device_data: DeviceData = None
        self.mqtt_client: RoborockMqttClientV1 = None
        self.network_info: NetworkInfo = None
        self.local_client: RoboLocalClient = None


    async def initialize(self) -> None:
        logger.info("Starting Roborock connection initialization.")
        try:
            await self._authenticate()
            await self._fetch_device_data()
            await self._connect_mqtt_client()
            await self._fetch_network_info()
            self._create_local_client()
            logger.info("Roborock connection initialized.")
        except Exception as e:
            logger.error("Roborock connection initialization failed: %s", e)
            raise


    async def _authenticate(self) -> None:
        try:
            self.web_api = RoborockApiClient(self.username)
            self.user_data = await self.web_api.pass_login(self.password)
        except Exception:
            logger.exception("Authentication failed.")
            raise


    async def _fetch_device_data(self) -> None:
        try:
            self.home_data = await self.web_api.get_home_data_v2(self.user_data)
            logger.info("Home data retrieved: %s", self.home_data)

            self.device = self.home_data.devices[0]
            logger.info("First device: %s", self.device)

            self.product_info: dict[str, HomeDataProduct] = {
                product.id: product for product in self.home_data.products
            }
            logger.info("Product info: %s", self.product_info)

            if self.device.product_id not in self.product_info:
                raise ValueError(f"Product info for {self.device.product_id} not found.")
            self.device_data = DeviceData(self.device, self.product_info[self.device.product_id].model)

        except IndexError:
            logger.error("No devices found in home data.")
            raise
        except Exception as e:
            logger.exception("Failed to fetch device data: %s", e)
            raise


    async def _connect_mqtt_client(self) -> None:
        try:
            self.mqtt_client = RoborockMqttClientV1(self.user_data, self.device_data)
            logger.info("MQTT client connected")
        except Exception as e:
            logger.exception("Failed to to connect MQTT client: %s", e)
            raise


    async def _fetch_network_info(self) -> None:
        try:
            self.network_info = await self.mqtt_client.get_networking()
            logger.info("Network info retrieved: %s", self.network_info)
        except Exception as e:
            logger.exception("Failed to to fetch network info: %s", e)
            raise


    def _create_local_client(self) -> None:
        try:
            local_device_data = DeviceData(self.device, self.product_info[self.device.product_id].model,
                                           self.network_info.ip)
            logger.info("Local device data created: %s", local_device_data)
            self.local_client = RoboLocalClient(local_device_data)
            logger.info("Local client created")

            asyncio.create_task(self._connect_local())

        except Exception as e:
            logger.exception("Failed to create local client: %s", e)
            raise


    async def _connect_local(self):
        await self.local_client.async_connect()
        logger.info("Local client connected → %r", self.local_client.is_connected())


    async def get_rooms(self) -> list[RoomSummary]:
        if not self.home_data or not self.home_data.rooms:
            raise RuntimeError("Home data or rooms not initialized.")

        rooms = self.home_data.rooms
        try:
            room_mapping = await self.local_client.get_room_mapping()
        except Exception as e:
            logger.exception("Failed to fetch room mapping.")
            raise

        segment_by_id = {
            int(rm.iot_id): rm.segment_id
            for rm in room_mapping
            if rm.iot_id.isdigit()
        }

        combined = []
        for room in rooms:
            segment_id = segment_by_id.get(room.id)
            if segment_id is not None:
                combined.append(RoomSummary(name=room.name, id=room.id, segment_id=segment_id))

        return combined
