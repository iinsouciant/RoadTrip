# SpotifyRecommendation

Drag and drop pins in order to plan out your next road trip route in a quick and efficient manner!

Use UV to initialize the project with a virtual environment: https://docs.astral.sh/uv/

---
macOS and Linux install

`wget -qO- https://astral.sh/uv/install.sh | sh`

Windows

`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex`

---


Initialize the project using `uv init` within the directory for the repository. Run the project using `uv run main.py` in the same directory.

## Dependencies
Dependencies and Python version are also listed in the `pyproject.toml` file.
- [pywinstyles](https://pypi.org/project/pywinstyles/)
- [pillow](https://pypi.org/project/pillow/) - Image processing stuff
- [customtkinter](https://pypi.org/project/customtkinter/) - a modification of tkinter for QoL things