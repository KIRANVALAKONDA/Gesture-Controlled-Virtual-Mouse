# Gesture-Controlled Virtual Mouse with Voice Assistant
A comprehensive gesture-controlled virtual mouse system that allows users to control their computer using hand gestures detected via webcam, combined with a voice assistant named Proton for additional functionality.

## Features

### Gesture Control
- **Mouse Movement**: Use V-gesture to move the cursor
- **Left Click**: MID gesture while V-gesture is active
- **Right Click**: INDEX gesture while V-gesture is active
- **Double Click**: TWO_FINGER_CLOSED gesture while V-gesture is active
- **Drag**: FIST gesture to hold and drag
- **Scroll Vertical**: PINCH_MINOR gesture (minor hand) - pinch up/down to scroll
- **Scroll Horizontal**: PINCH_MINOR gesture (minor hand) - pinch left/right to scroll
- **Volume Control**: PINCH_MAJOR gesture (major hand) - pinch up/down to adjust volume
- **Brightness Control**: PINCH_MAJOR gesture (major hand) - pinch left/right to adjust brightness

### Voice Assistant (Proton)
- Voice-activated commands for system control
- File navigation and management
- Web search and location lookup
- System information (date, time)
- Launch/stop gesture recognition
- Copy/paste operations
- Wake up/sleep functionality

## Requirements

- Python 3.7+
- Webcam
- Windows OS (for some system controls)
- Internet connection (for voice recognition and web features)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gesture-controlled-virtual-mouse.git
cd gesture-controlled-virtual-mouse
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/Proton.py
```

## Usage

### Starting the System
Run `python src/Proton.py` to start the voice assistant and web interface.

### Gesture Control
1. Say "Proton launch gesture recognition" to start gesture control
2. Position your hand in front of the webcam
3. Use the gestures listed above to control the mouse
4. Say "Proton stop gesture recognition" to stop

### Voice Commands
- **Wake/Sleep**: "Proton wake up" / "Proton bye"
- **Basic Info**: "Proton date", "Proton time"
- **Web Search**: "Proton search [query]"
- **Location**: "Proton location" (then speak the place)
- **File Navigation**: "Proton list" (lists root directory), "Proton open [number]", "Proton back"
- **System Control**: "Proton copy", "Proton paste"
- **Exit**: "Proton exit"

## Supported Gestures

| Gesture | Action |
|---------|--------|
| V_GEST | Move cursor |
| FIST | Drag (hold left click) |
| MID (with V_GEST) | Left click |
| INDEX (with V_GEST) | Right click |
| TWO_FINGER_CLOSED (with V_GEST) | Double click |
| PINCH_MINOR | Scroll (vertical/horizontal) |
| PINCH_MAJOR | Volume/Brightness control |

## Dependencies

- opencv-python
- mediapipe
- pyautogui
- pyttsx3
- speechrecognition
- eel
- screen-brightness-control
- pycaw
- pynput
- wikipedia
- comtypes

## Troubleshooting

- Ensure your webcam is properly connected and not used by other applications
- Adjust lighting for better hand detection
- Speak clearly for voice commands
- Check microphone permissions for voice input

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
