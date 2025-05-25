# src/balance_controller.py

import threading
import time
import math
import warnings
from dataclasses import dataclass
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


@dataclass
class RightLeftVolumeIntensity:
    """
    Represents left and right channel volume intensity as a percentage.
    Values are clamped to the range [0, 100].
    """

    left: int
    right: int

    def __post_init__(self):
        object.__setattr__(self, "left", max(0, min(100, self.left)))
        object.__setattr__(self, "right", max(0, min(100, self.right)))


class BalanceController:
    def __init__(self):
        speakers = AudioUtilities.GetSpeakers()
        interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self._endpoint_volume = cast(interface, POINTER(IAudioEndpointVolume))

        # 8D mode state
        self._8d_thread = None
        self._8d_running = threading.Event()

    def set_balance(self, intensity: RightLeftVolumeIntensity) -> None:
        left_scalar = intensity.left / 100.0
        right_scalar = intensity.right / 100.0
        self._endpoint_volume.SetChannelVolumeLevelScalar(0, left_scalar, None)
        self._endpoint_volume.SetChannelVolumeLevelScalar(1, right_scalar, None)

    def get_balance(self) -> RightLeftVolumeIntensity:
        left_s = self._endpoint_volume.GetChannelVolumeLevelScalar(0)
        right_s = self._endpoint_volume.GetChannelVolumeLevelScalar(1)
        return RightLeftVolumeIntensity(
            left=round(left_s * 100), right=round(right_s * 100)
        )

    def _run_8d(self, rate_hz: float, depth_percent: int):
        """
        Internal loop: computes a sine wave at `rate_hz`, depth in percent,
        centered at 50/50, and updates until stopped.
        """
        interval = 1.0 / (rate_hz * 50)  # 50 samples per cycle
        t = 0.0
        while self._8d_running.is_set():
            # sine in [-1,1]
            v = math.sin(2 * math.pi * rate_hz * t)
            
            # map to [50-depth/2 ... 50+depth/2]
            half = depth_percent / 2.0
            left = 50 + v * half
            right = 100 - left
            self.set_balance(RightLeftVolumeIntensity(int(left), int(right)))
            t += interval
            time.sleep(interval)

    def start_8d(self, rate_hz: float = 0.2, depth_percent: int = 80) -> None:
        """
        Begin 8D auto-panning. rate_hz: how many full L->R->L cycles per second.
        depth_percent: total L+R swing (0-100).
        """
        if self._8d_running.is_set():
            return
        self._8d_running.set()
        self._8d_thread = threading.Thread(
            target=self._run_8d, 
            args=(rate_hz, depth_percent), 
            daemon=True
        )
        self._8d_thread.start()

    def stop_8d(self) -> None:
        """Stop 8D auto-panning and leave last balance in place."""
        self._8d_running.clear()
        if self._8d_thread:
            self._8d_thread.join(timeout=0.1)
            self._8d_thread = None

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
