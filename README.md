# Rock Paper Scissors, Computer Vision

Play rock-paper-scissors against your computer using hand gestures detected via your webcam.

Built with [MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker) and OpenCV.

<video src="https://github.com/user-attachments/assets/30b120b7-548d-47cc-a065-d3acdcda3fed" controls></video>

## How It Works

The app uses MediaPipe's hand landmark detection to classify your hand into one of three gestures based on which fingers are extended:

- **Rock**: All fingers closed.
- **Scissors**: Index and middle fingers extended.
- **Paper**: All fingers extended.

A 3 second countdown gives you time to prepare, then the game reads your gesture and plays a random choice for the computer.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Download the hand landmarker model

Download `hand_landmarker.task` from [MediaPipe's model page](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models) and place it in the project root.

### 3. Run

```bash
python rock-paper-scissors-cv.py
```

## Controls

| Key    | Action     |
|--------|------------|
| `R`    | Play again |
| `Esc`  | Quit       |

## Requirements

- Python 3.9+
- A webcam
- Linux (uses V4L2 capture backend on macOS/Windows, you may need to remove the `cv2.CAP_V4L2` argument)