from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class BalanceController:
    """
    A class to control the balance of the audio output.
    """
    def __init__(self):
        # Get the default speakers endpoint
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

    def set_balance(self, balance_str: str):
        """
        Set balance from string "L/T", where:
          - L is the left channel volume (0 ~ T)
          - T is the total scale (e.g., 100)
        e.g., "48/100" -> left channel at 48%, right channel at 52%
        """
        try:
            left_val, total = map(int, balance_str.split('/'))
        except ValueError:
            raise ValueError("Balance must be in the format 'L/T' where L and T are integers.")
        
        # clamp values and normalize
        left_val = max(0, min(left_val, total))
        right_val = total - left_val
        left_scalar = left_val / total
        right_scalar = right_val / total

        # apply per-channel volume
        self.volume.SetChannelVolumeLevelScalar(0, left_scalar, None)
        self.volume.SetChannelVolumeLevelScalar(1, right_scalar, None)

    def get_balance(self) -> str:
        """
        Return the current balance as a string "L/T".
        Query the current volume levels for both channels.
        """
        left_scalar = self.volume.GetChannelVolumeLevelScalar(0)
        right_scalar = self.volume.GetChannelVolumeLevelScalar(1)

        total_percent = left_scalar + right_scalar
        left_val = int(left_scalar * total_percent)
        total = int(total_percent * 100)
        return f"{left_val}/{total}"
    
if __name__ == "__main__":
    bc = BalanceController()
    print("Current balance:", bc.get_balance())    # e.g., "50/100"
    bc.set_balance("40/100")                       # Left 30%, Right 70%
    print("New balance:", bc.get_balance())