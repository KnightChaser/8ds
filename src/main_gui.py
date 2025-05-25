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
        self._8d_on = False         # Is 8D mode enabled?

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
            command=self.on_slide,
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
            command=self.on_slide,
        )
        self.right_scale.grid(column=1, row=2, sticky="ew")
        self.right_value_label = ttk.Label(
            self, 
            text=str(self.previous_intensity.right)
        )
        self.right_value_label.grid(column=2, row=2, sticky="w")

        # 8D Toggle and max-cap slider
        self.toggle_button = ttk.Button(
            self, text="Enable 8D Audio", 
            command=self.toggle_8d_mode
        )
        self.toggle_button.grid(
            column=0, 
            row=3, 
            columnspan=2, 
            sticky="ew", 
            pady=(10, 0)
        )

        self.mode_indicator = ttk.Label(self, text="8D Audio OFF", foreground="red")
        self.mode_indicator.grid(column=2, row=3, sticky="w")
        
        # Max-cap slider for 8D audio mode (only active when 8D is enabled)
        ttk.Label(self, text="Maximum sound intensity").grid(column=0, row=4, sticky="w")
        self.max_percent_var = tk.IntVar(value=90)
        self.max_percent_scale = ttk.Scale(
            self,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.max_percent_var,
            command=self.on_max_percent_change,
        )
        self.max_percent_scale.grid(column=1, row=4, sticky="ew")
        self.max_percent_value_label = ttk.Label(self, text="100")
        self.max_percent_value_label.grid(column=2, row=4, sticky="w")
        self.max_percent_scale.state(["disabled"])  # Initially disabled

        # Layout and pack...
        self.columnconfigure(1, weight=1)
        self.pack(fill="both", expand=True)
        master.title("8ds: Audio balance controller")

    def on_slide(self, _event: str) -> None:
        """
        Called when either slider moves: updates labels and applies balance.
        """
        left = self.left_var.get()
        right = self.right_var.get()

        # Update live labels
        self.left_value_label.config(text=str(left))
        self.right_value_label.config(text=str(right))

        # Apply to controller
        intensity = RightLeftVolumeIntensity(left=left, right=right)
        self.controller.set_balance(intensity)

    def toggle_8d_mode(self):
        if not self._8d_on:
            # Turn 8D on
            self.controller.start_8d(rate_hz=0.1, depth_percent=90)
            self.toggle_button.config(text="Disable 8D Audio")
            self.mode_indicator.config(text="8D Audio ON", foreground="green")
            
            # Disable manual sliders and enable max-cap slider
            self.left_scale.state(["disabled"])
            self.right_scale.state(["disabled"])
            self.max_percent_scale.state(["!disabled"])
            self._8d_on = True
        else:
            # Turn 8D off
            self.controller.stop_8d()
            self.toggle_button.config(text="Enable 8D Audio")
            self.mode_indicator.config(text="8D Audio OFF", foreground="red")
            
            # Re-enable sliders and disable max-cap slider
            self.left_scale.state(["!disabled"])
            self.right_scale.state(["!disabled"])
            self.max_percent_scale.state(["disabled"])
            self._8d_on = False
            
    def on_max_percent_change(self, _event: str) -> None:
        """
        Called when the max-cap slider changes: updates label and controller.
        """
        max_percent = self.max_percent_var.get()
        self.max_percent_value_label.config(text=str(max_percent))
        self.controller.set_8d_max_percent(max_percent)

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
