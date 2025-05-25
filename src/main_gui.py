# src/main_gui.py

import tkinter as tk
from tkinter import ttk
import sv_ttk
from typing import Any

from balance_controller import BalanceController, RightLeftVolumeIntensity

class BalanceApp(ttk.Frame):
    """
    Tkinter GUI frame for manual L/R balance and 8D auto-panning controls.
    """

    def __init__(self, master: tk.Tk, controller: BalanceController) -> None:
        """
        Args:
            master: Root Tk window.
            controller: Backend BalanceController instance.
        """
        super().__init__(master, padding=20)
        self.controller = controller
        self.is_8d_enabled: bool = False

        # Initial state
        initial = self.controller.get_balance()
        interface_name = self.controller.get_interface_name()

        # Interface name display
        ttk.Label(self, text="Interface:").grid(column=0, row=0, sticky="w")
        self.interface_label = ttk.Label(self, text=interface_name)
        self.interface_label.grid(column=1, row=0, columnspan=2, sticky="w")

        # Left channel slider
        ttk.Label(self, text="Left (%)").grid(column=0, row=1, sticky="w")
        self.left_var = tk.IntVar(value=initial.left_percent)
        self.left_slider = ttk.Scale(
            self, from_=0, to=100, orient="horizontal",
            variable=self.left_var, command=self._on_manual_slide
        )
        self.left_slider.grid(column=1, row=1, sticky="ew")
        self.left_value_label = ttk.Label(self, text=str(initial.left_percent))
        self.left_value_label.grid(column=2, row=1, sticky="w")

        # Right channel slider
        ttk.Label(self, text="Right (%)").grid(column=0, row=2, sticky="w")
        self.right_var = tk.IntVar(value=initial.right_percent)
        self.right_slider = ttk.Scale(
            self, from_=0, to=100, orient="horizontal",
            variable=self.right_var, command=self._on_manual_slide
        )
        self.right_slider.grid(column=1, row=2, sticky="ew")
        self.right_value_label = ttk.Label(self, text=str(initial.right_percent))
        self.right_value_label.grid(column=2, row=2, sticky="w")

        # 8D toggle
        self.toggle_button = ttk.Button(
            self, text="Enable 8D Audio", command=self._toggle_8d_mode
        )
        self.toggle_button.grid(column=0, row=3, columnspan=2, sticky="ew", pady=(10, 0))

        self.mode_indicator = ttk.Label(self, text="8D OFF", foreground="red")
        self.mode_indicator.grid(column=2, row=3, sticky="w")

        # 8D max-cap slider
        ttk.Label(self, text="8D Max (%)").grid(column=0, row=4, sticky="w")
        self.max_var = tk.IntVar(value=100)
        self.max_slider = ttk.Scale(
            self, from_=0, to=100, orient="horizontal",
            variable=self.max_var, command=self._on_max_change
        )
        self.max_slider.grid(column=1, row=4, sticky="ew")
        self.max_value_label = ttk.Label(self, text="100")
        self.max_value_label.grid(column=2, row=4, sticky="w")
        self.max_slider.state(["disabled"])

        # Layout & title
        self.columnconfigure(1, weight=1)
        self.pack(fill="both", expand=True)
        master.title("8D Audio Balance Controller")

    def _on_manual_slide(self, _event: Any) -> None:
        """
        Handle manual slider movement when 8D is off.
        """
        if self.is_8d_enabled:
            return
        
        left = self.left_var.get()
        right = self.right_var.get()
        self.left_value_label.config(text=str(left))
        self.right_value_label.config(text=str(right))
        
        intensity = RightLeftVolumeIntensity(left_percent=left, right_percent=right)
        self.controller.set_balance(intensity)

    def _toggle_8d_mode(self) -> None:
        """
        Toggle 8D auto-panning on/off, update UI state.
        """
        if not self.is_8d_enabled:
            # Start 8D audio panning
            self.controller.start_8d(rate_hz=0.1, depth_percent=90)
            self.toggle_button.config(text="Disable 8D Audio")
            self.mode_indicator.config(text="8D ON", foreground="green")
            
            self.left_slider.state(["disabled"])
            self.right_slider.state(["disabled"])
            self.max_slider.state(["!disabled"])
        else:
            # Stop 8D audio panning
            self.controller.stop_8d()
            self.toggle_button.config(text="Enable 8D Audio")
            self.mode_indicator.config(text="8D OFF", foreground="red")
            
            self.left_slider.state(["!disabled"])
            self.right_slider.state(["!disabled"])
            self.max_slider.state(["disabled"])
            
        # Update max slider state
        self.is_8d_enabled = not self.is_8d_enabled

    def _on_max_change(self, _event: Any) -> None:
        """
        Handle changes to the 8D maximum intensity cap.
        """
        value = self.max_var.get()
        self.max_value_label.config(text=str(value))
        self.controller.set_8d_max_percent(value)


def main() -> None:
    """
    Launch the Tkinter GUI with Sun Valley theme.
    """
    root = tk.Tk()
    sv_ttk.set_theme("dark")

    controller = BalanceController()
    BalanceApp(root, controller)
    root.mainloop()


if __name__ == "__main__":
    main()
