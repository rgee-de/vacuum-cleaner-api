import logging

from roborock import RoborockCommand, RoomMapping, RoborockFanSpeedS7MaxV, RoborockMopModeS7, RoborockMopIntensityS7, \
    DeviceProp
from roborock.version_1_apis import RoborockLocalClientV1
from roborock.version_1_apis.roborock_client_v1 import RT

logger = logging.getLogger(__name__)


class RoboLocalClient(RoborockLocalClientV1):
    def on_connection_lost(self, exc: Exception | None) -> None:
        super().on_connection_lost(exc)
        self.validate_connection()
        logger.warning("Local connection lost: %s", exc)


    async def get_room_mapping(self) -> list[RoomMapping] | None:
        await self.check_connected()
        return await super().get_room_mapping()


    async def get_prop(self) -> DeviceProp:
        await self.check_connected()
        return await super().get_prop()


    async def send_command_custom(
            self,
            method: RoborockCommand | str,
            params: list | dict | int | None = None,
            return_type: type[RT] | None = None,
    ) -> RT:
        await self.check_connected()
        return await self.send_command(method, params, return_type)


    async def set_clean_mode_s7maxv(
            self,
            fan_speed: RoborockFanSpeedS7MaxV = RoborockFanSpeedS7MaxV.custom,
            mop_mode: RoborockMopModeS7 = RoborockMopModeS7.custom,
            mop_intensity: RoborockMopIntensityS7 = RoborockMopIntensityS7.custom
    ):
        await self.check_connected()
        try:
            await self.send_command_custom(
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


    async def check_connected(self):
        if not self.is_connected():
            logger.warning("Local client is not connected")
            await self.validate_connection()
            # raise Exception("Local client is not connected")
