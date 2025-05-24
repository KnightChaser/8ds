# src/balance_controller.py

from __future__ import annotations
from dataclasses import dataclass
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import warnings


@dataclass
class RightLeftVolumeIntensity:
    """
    Holds independent left/right channel intensity values in the 0-100 (percent) range.
    Values outside this range are clamped to [0, 100].
    """

    left: int
    right: int

    def __post_init__(self) -> None:
        # Ensure values are within 0–100
        object.__setattr__(self, "left", max(0, min(100, self.left)))
        object.__setattr__(self, "right", max(0, min(100, self.right)))


class BalanceController:
    """
    Controls system-wide left/right volume balance on Windows via pycaw.
    Channels: 0 = left, 1 = right. Values managed internally as scalars (0.0–1.0).
    """

    def __init__(self) -> None:
        """
        Initializes the Core Audio endpoint volume interface.
        Raises on COM activation failure.
        """
        speakers = AudioUtilities.GetSpeakers()
        interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self._endpoint_volume = cast(interface, POINTER(IAudioEndpointVolume))

    def set_balance(self, intensity: RightLeftVolumeIntensity) -> None:
        """
        Applies a new left/right balance.

        :param intensity: RightLeftVolumeIntensity with left/right in [0, 100]
        """
        left_scalar = intensity.left / 100.0
        right_scalar = intensity.right / 100.0

        self._endpoint_volume.SetChannelVolumeLevelScalar(0, left_scalar, None)
        self._endpoint_volume.SetChannelVolumeLevelScalar(1, right_scalar, None)

    def get_balance(self) -> RightLeftVolumeIntensity:
        """
        Retrieves the current left/right balance as percentages.

        :return: RightLeftVolumeIntensity with left/right in [0, 100]
        """
        left_scalar = self._endpoint_volume.GetChannelVolumeLevelScalar(0)
        right_scalar = self._endpoint_volume.GetChannelVolumeLevelScalar(1)
        return RightLeftVolumeIntensity(
            left=round(left_scalar * 100), right=round(right_scalar * 100)
        )

    def get_interface_name(self) -> str:
        """
        Returns the friendly name of the current default audio endpoint.
        If the name cannot be determined, returns "Unknown Device".

        :return: Friendly name of the default audio endpoint (e.g., "Speakers (Realtek High Definition Audio)")
        """
        with warnings.catch_warnings():
            # Suppress COM deprecation warnings
            warnings.simplefilter("ignore", UserWarning)

            # Get the default IMMDevice endpoint
            default_device = AudioUtilities.GetSpeakers()
            try:
                # Get the endpoint ID
                device_id = default_device.GetId()
            except Exception:
                return "Unknown Device"

            # Find matching AudioDevice wrapper for friendly name
            try:
                all_devices = AudioUtilities.GetAllDevices()
                for device in all_devices:
                    if hasattr(device, "id") and device.id == device_id:
                        # AudioDevice.FriendlyName property
                        return device.FriendlyName
            except Exception:
                pass

            # Fallback to returning the raw device ID
            return device_id
