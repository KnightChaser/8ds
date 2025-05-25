# 8ds🎧

A simple and easy-to-use Windows GUI tool to control headset left/right balance and enjoy an “8D” auto-panning audio effect. Enjoy your favorite music sensationally with `8ds`!

![image](https://github.com/user-attachments/assets/846c84d0-cf16-405d-a1f7-003f795e3c00)

- **Manual Balance**: Two sliders to set left/right channel volume (0–100%).
- **8D Auto-Panning**: A toggleable mode that sweeps audio balance in a smooth sine wave.
- **8D Intensity Cap**: Slider to cap maximum 8D effect, preventing jarring 100% swings.
- **Single-File Executable**: Packaged with PyInstaller into `8ds.exe`.

## Download
Download the Windows `8ds` binary from [Releases](https://github.com/KnightChaser/8ds/releases).

## Build

1. Clone the repo and enter the directory:
```powershell
git clone https://github.com/KnightChaser/8ds.git
cd 8ds
```

2. Install dependencies (Suppose you create a Python virtual environment named `.venv`):
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
3. Build the EXE:
```powershell
.\build.ps1
```

4. Run:
```powershell
.\build\8ds.exe
```
(Alternatively, simply `python .\src\main_gui.py` for immediate execution without EXE packaging.)

## Usage

* `Interface` label shows the audio endpoint you are currently using.
* `Left / Right` sliders adjust channel volumes when 8D is **`off`**.
* `Enable 8D Audio` toggles auto-panning; sliders deactivate.
* `8D Max (%)` slider sets the peak balance swing when 8D is **`on`**.

## Contribution and license

This is open source. Feel free to explore, modify, or improve the source code.
Also, feel free to leave issues, add pull requests, or do something else in this repository!
