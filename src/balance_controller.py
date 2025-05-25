# src/balance_controller.py

import threading
import time
import math
import warnings
from dataclasses import dataclass
from ctypes import cast, POINTER
from typing import Optional
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


@dataclass
class RightLeftVolumeIntensity:
    """
    Represents independent left/right channel volume intensities as percentages.

    Attributes:
        left_percent:  Left channel intensity in the range [0, 100].
        right_percent: Right channel intensity in the range [0, 100].
    """
    left_percent: int
    right_percent: int

    def __post_init__(self) -> None:
        # Clamp to valid range
        object.__setattr__(self, 'left_percent',  max(0, min(100, self.left_percent)))
        object.__setattr__(self, 'right_percent', max(0, min(100, self.right_percent)))


class BalanceController:
    """
    Wraps Windows Core Audio endpoint volume control for per-channel (L/R) balance,
    plus an “8D” auto-panning mode that cycles balance in a sine wave pattern.
    """

    def __init__(self) -> None:
        """
        Initialize the COM interface to the default audio endpoint.
        """
        speakers = AudioUtilities.GetSpeakers()
        interface = speakers.Activate(
            IAudioEndpointVolume._iid_, 
            CLSCTX_ALL, 
            None
        )
        self._endpoint_volume = cast(interface, POINTER(IAudioEndpointVolume))

        # 8D mode state
        self._8d_thread: Optional[threading.Thread] = None
        self._8d_running = threading.Event()
        self._8d_max_percent: int = 100

    def set_balance(self, intensity: RightLeftVolumeIntensity) -> None:
        """
        Set left/right volume percentages immediately.

        Args:
            intensity: A RightLeftVolumeIntensity with values in [0, 100].
        """
        left_scalar = intensity.left_percent / 100.0
        right_scalar = intensity.right_percent / 100.0

        self._endpoint_volume.SetChannelVolumeLevelScalar(0, left_scalar, None)
        self._endpoint_volume.SetChannelVolumeLevelScalar(1, right_scalar, None)

    def get_balance(self) -> RightLeftVolumeIntensity:
        """
        Query the current left/right volume percentages.

        Returns:
            A RightLeftVolumeIntensity reflecting the current endpoint balance.
        """
        left_scalar = self._endpoint_volume.GetChannelVolumeLevelScalar(0)
        right_scalar = self._endpoint_volume.GetChannelVolumeLevelScalar(1)
        return RightLeftVolumeIntensity(
            left_percent=round(left_scalar * 100),
            right_percent=round(right_scalar * 100),
        )

    def _run_8d(self, rate_hz: float, depth_percent: int) -> None:
        """
        Internal loop for 8D auto-panning: sweeps L↔R in a sine wave.

        Args:
            rate_hz: Number of full L→R→L cycles per second.
            depth_percent: Peak-to-peak swing around center (0–100).
        """
        interval = 1.0 / (rate_hz * 50)  # 50 steps per cycle
        t = 0.0
        half_depth = depth_percent / 2.0

        while self._8d_running.is_set():
            # sine in [-1,1]
            v = math.sin(2 * math.pi * rate_hz * t)
            
            # map to [50-depth/2 ... 50+depth/2]
            raw_left = 50.0 + v * half_depth
            raw_right = 100.0 - raw_left

            # apply max cap
            left = raw_left * self._8d_max_percent / 100.0
            right = raw_right * self._8d_max_percent / 100.0

            # set balance
            self.set_balance(
                RightLeftVolumeIntensity(
                    left_percent=int(left),
                    right_percent=int(right)
                )
            )

            t += interval
            time.sleep(interval)

    def start_8d(self, rate_hz: float = 0.2, depth_percent: int = 80) -> None:
        """
        Enable 8D auto-panning in background.

        Args:
            rate_hz: Frequency of pan cycles (Hz).
            depth_percent: Total left↔right swing (0–100).
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
        """
        Disable 8D auto-panning, leaving the last balance in place.
        """
        self._8d_running.clear()
        if self._8d_thread:
            self._8d_thread.join(timeout=0.1)
            self._8d_thread = None

    def set_8d_max_percent(self, max_percent: int) -> None:
        """
        Adjust the upper cap for 8D intensity.

        Args:
            max_percent: New cap (0–100).
        """
        self._8d_max_percent = max(0, min(100, max_percent))

    def get_interface_name(self) -> str:
        """
        Return the friendly name of the default audio endpoint.

        Returns:
            e.g., "Speakers (Realtek High Definition Audio)" or "Unknown Device"
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)

            device = AudioUtilities.GetSpeakers()
            try:
                device_id = device.GetId()
            except Exception:
                return "Unknown Device"

            try:
                for dev in AudioUtilities.GetAllDevices():
                    if getattr(dev, "id", None) == device_id:
                        return dev.FriendlyName
            except Exception:
                pass

            return device_id
