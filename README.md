# Blind Vision – Object Detection with Voice Assistance

A Python desktop application that detects objects in real time using a webcam and gives voice feedback in **English** and **Tamil**. This project is designed to assist visually impaired users by identifying nearby objects and announcing them through audio.

## Features

* Real-time object detection using webcam
* YOLOv8-based object detection
* TensorFlow MobileNetV2 classification support
* English voice output using `pyttsx3`
* Tamil voice output using `gTTS`
* Simple Tkinter GUI
* Live camera preview
* Displays detected object names and confidence
* Voice alerts for detected objects

## Tech Stack

* Python 3.10
* OpenCV
* Ultralytics YOLOv8
* TensorFlow
* NumPy
* Pillow
* Tkinter
* pyttsx3
* gTTS
* pygame

## Installation

```cmd
py -3.10 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install opencv-python==4.8.0.74 numpy==1.24.3 Pillow==10.0.0 pyttsx3==2.90 gTTS==2.3.2 tensorflow==2.13.0 ultralytics pygame
```

## Run the Project

```cmd
python main.py
```

## Recommended requirements.txt

```txt
opencv-python==4.8.0.74
numpy==1.24.3
Pillow==10.0.0
pyttsx3==2.90
gTTS==2.3.2
tensorflow==2.13.0
ultralytics
pygame
```

## How It Works

1. Webcam captures live video frames.
2. YOLOv8 detects objects from each frame.
3. TensorFlow MobileNetV2 supports object classification.
4. Detected objects are displayed in the GUI.
5. The application speaks detected object names using voice output.
6. English audio works offline using `pyttsx3`.
7. Tamil audio uses `gTTS`, so internet is required.

## Common Errors and Fixes

### No module named `cv2`

```cmd
python -m pip install opencv-python
```

### No module named `ultralytics`

```cmd
python -m pip install ultralytics
```

### No module named `tensorflow`

```cmd
python -m pip install tensorflow==2.13.0
```

### Tamil audio not playing

```cmd
python -m pip install pygame gTTS
```

Tamil audio requires internet because `gTTS` uses Google Text-to-Speech.

## Python Version

Recommended:

```txt
Python 3.10
```

Python 3.10 is recommended because TensorFlow, OpenCV, YOLOv8, and other required packages work properly with it.

## Applications

* Assistive technology for visually impaired users
* Real-time object recognition
* Voice-based navigation support
* Academic mini project or major project
* Computer vision learning project

## Future Enhancements

* Add distance estimation for detected objects
* Add obstacle danger-level warning
* Add GPS-based outdoor navigation
* Add offline Tamil text-to-speech support
* Improve detection speed using lightweight models
* Convert the application into an executable file
* Add support for more Indian languages

## Author

**Vinu J**
M.Sc. Computer Science
Python Developer / Software Developer Fresher

## License

This project is created for academic and learning purposes.
