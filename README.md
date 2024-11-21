# MienMouse 🎯

MienMouse is a hands-free mouse control system that enables users to control their computer using facial gestures. Built with Python and powered by MediaPipe's facial landmark detection, it provides an intuitive and accessible way to interact with your computer.

## 🌟 Features

- **Intuitive Mouse Control**: Control cursor movement using head position
- **Natural Gestures**: 
  - Left Click: Open mouth
  - Right Click: Raise eyebrows
  - Double Click: Combine both gestures
  - Drag & Drop: Keep mouth open while moving
- **Smooth Tracking**: Advanced smoothing algorithms for precise cursor control
- **Real-time Feedback**: Visual indicators for gesture recognition
- **Customizable Settings**: Adjust sensitivity and response to your preferences

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Webcam
- Windows/Linux/MacOS

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/mienmouse.git
cd mienmouse
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```

## 🎮 Controls

| Action | Gesture |
|--------|---------|
| Move Cursor | Move head |
| Left Click | Open mouth |
| Right Click | Raise eyebrows |
| Double Click | Open mouth + raise eyebrows |
| Drag & Drop | Keep mouth open while moving |
| Recenter | Press 'R' |
| Toggle Precision | Press 'P' |
| Toggle Audio | Press 'A' |
| Toggle Tracking | Press 'T' |
| Hide Controls | Press 'H' |
| Exit | Press 'ESC' |

## ⚙️ Configuration

Adjust settings in `config.json` by copying `config.json.example` to `config.json`:
```json
{
    "webcam_index": 0,
    "smoothing": 0.5
}
```

## 🔧 Advanced Settings

Fine-tune the system by adjusting these parameters in `mouse_controller.py`:
- Movement sensitivity
- Gesture recognition thresholds
- Smoothing intensity
- Response time

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for facial landmark detection
- [OpenCV](https://opencv.org/) for image processing
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for mouse control

## 📞 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/mienmouse/issues).

---

<p align="center">
Made with ❤️ for accessibility
</p>