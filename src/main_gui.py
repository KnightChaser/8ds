# src/main_gui.py

import tkinter as tk
from tkinter import ttk
import sv_ttk

from balance_controller import BalanceController, RightLeftVolumeIntensity


class BalanceApp(ttk.Frame):
    """
    GUI for adjusting left/right audio balance.
    """

    def __init__(self, master: tk.Tk, controller: BalanceController) -> None:
        super().__init__(master, padding=20)
        self.controller = controller

        # Initialize previous intensity and interface name
        self.previous_intensity = self.controller.get_balance()
        interface_name = self.controller.get_interface_name()

        # Interface label
        ttk.Label(self, text="Interface:").grid(column=0, row=0, sticky="w")
        self.interface_label = ttk.Label(self, text=interface_name)
        self.interface_label.grid(column=1, row=0, columnspan=2, sticky="w")

        # Left slider and label
        ttk.Label(self, text="Left channel").grid(column=0, row=1, sticky="w")
        self.left_var = tk.IntVar(value=self.previous_intensity.left)
        self.left_scale = ttk.Scale(
            self,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.left_var,
            command=self.on_slide
        )
        self.left_scale.grid(column=1, row=1, sticky="ew")
        self.left_value_label = ttk.Label(self, text=str(self.previous_intensity.left))
        self.left_value_label.grid(column=2, row=1, sticky="w")

        # Right slider and label
        ttk.Label(self, text="Right channel").grid(column=0, row=2, sticky="w")
        self.right_var = tk.IntVar(value=self.previous_intensity.right)
        self.right_scale = ttk.Scale(
            self,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.right_var,
            command=self.on_slide
        )
        self.right_scale.grid(column=1, row=2, sticky="ew")
        self.right_value_label = ttk.Label(self, text=str(self.previous_intensity.right))
        self.right_value_label.grid(column=2, row=2, sticky="w")

        # Layout configuration
        self.columnconfigure(1, weight=1)
        self.pack(fill="both", expand=True)
        master.title("Audio Balance Controller")

    def on_slide(self, _event: str) -> None:
        """
        Called when either slider moves: updates labels and applies balance.
        """
        left = self.left_var.get()
        right = self.right_var.get()

        # Update live labels
        self.left_value_label.config(text=f"{str(left)} %")
        self.right_value_label.config(text=f"{str(right)} %")

        # Apply to controller
        intensity = RightLeftVolumeIntensity(left=left, right=right)
        self.controller.set_balance(intensity)


def main() -> None:
    """
    Initializes theme, controller, and runs the Tkinter mainloop.
    """
    root = tk.Tk()

    # Apply Sun Valley theme using sv_ttk
    sv_ttk.set_theme("dark")

    controller = BalanceController()
    app = BalanceApp(root, controller)
    root.mainloop()


if __name__ == "__main__":
    main()
