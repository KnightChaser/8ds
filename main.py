from __future__ import annotations
from dataclasses import dataclass
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from typing import Optional


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


def parse_intensity(input_str: str) -> Optional[RightLeftVolumeIntensity]:
    """
    Parses a string of form "L/R" into a RightLeftVolumeIntensity.
    Both L and R are treated as 0-100 percentages.

    :param input_str: e.g. "40/8"
    :return: RightLeftVolumeIntensity or None if parsing fails
    """
    try:
        left_str, right_str = input_str.split("/")
        left_value = int(left_str)
        right_value = int(right_str)
        return RightLeftVolumeIntensity(left=left_value, right=right_value)
    except (ValueError, AttributeError):
        return None


def main() -> None:
    """
    REPL loop for adjusting balance.
    Displays previous → new balance on each valid input.
    Exits when the user presses Enter on a blank line.
    """
    controller = BalanceController()
    previous_intensity = controller.get_balance()
    print(f"Previous balance: {previous_intensity.left}/{previous_intensity.right}")

    while True:
        user_input = input("Input (L/R): ").strip()
        if not user_input:
            print("Exiting.")
            break

        new_intensity = parse_intensity(user_input)
        if new_intensity is None:
            print("  ↳ Invalid format; please use 'L/R' with integers (e.g. '40/8').")
            continue

        print(
            f"  ↳ Applying balance: "
            f"{previous_intensity.left}/{previous_intensity.right} → "
            f"{new_intensity.left}/{new_intensity.right}"
        )
        controller.set_balance(new_intensity)
        previous_intensity = new_intensity


if __name__ == "__main__":
    main()