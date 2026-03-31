# Robotic Hand Control via Gesture Estimation (YOLO26-Pose + ROS 2)

This project develops a real-time control system for a **robotic hand**. It uses computer vision to detect human hand keypoints and translates those movements into servo motor angles using an ESP32 microcontroller.

## Overview

The project workflow is as follows:

1. **Capture and Detection:** A camera captures video, which is processed by an optimized **YOLO26-Pose** model.
2. **ROS 2 Processing:** A ROS 2 node converts the detected *keypoints* into position commands.
3. **Hardware Control:** Commands are sent via serial (UART) to an **ESP32**, which generates PWM signals to drive each finger’s servomotor.

## 📂 Project Structure

```text
.
├── ESP_servo_control/      # Microcontroller firmware
│   └── main/               # C++/Arduino code for servo control and UART
├── docs/                   # Metrics plots (mAP50, Loss) and documentation
├── ros2_ws/                # ROS 2 Jazzy workspace
│   └── src/
│       └── robotic_hand_ros/
│           ├── hand_nodes/ # Vision, logic, and serial communication nodes
│           ├── CMakeLists.txt
│           └── package.xml
└── scripts/                # Python utilities
```

## 🛠️ Technologies and Requirements

### Software

* **Operating System:** Ubuntu 24.04 LTS (Noble Numbat)
* **Middleware:** ROS 2 Jazzy Jalisco
* **AI/Vision:** Ultralytics YOLO26-Pose, OpenCV
* **Languages:** Python 3.12, C++

### Hardware

* **Microcontroller:** ESP32 (WROOM-32)
* **Actuators:** 5x Servomotors (MG90S or similar)
* **PC:** Setup with compatible GPU (used RTX 5060 Laptop)

## 📊 Training and Evaluation

The pose model was trained using custom datasets to ensure accuracy in specific hand gestures.

* Training metrics (mAP50 vs Epochs) can be found in the `docs/` folder.
* Scripts in `scripts/` automate comparison between different training runs, helping select the most stable model.

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/EzeMarredo/gesture-controlled-robotic-hand.git
cd gesture-controlled-robotic-hand
```

### 2. Set up the ROS 2 workspace

```bash
cd ros2_ws
colcon build --packages-select robotic_hand_ros
source install/setup.bash
```

### 3. Upload code to the ESP32

Open the contents of `ESP_servo_control/main` in Arduino IDE or PlatformIO and upload it to your board.

## 🖥️ Execution

To start the full system:

### Vision Node (Inference)

```bash
ros2 run robotic_hand_ros kpt_publisher.py
```
In other terminal run:
```bash
ros2 run robotic_hand_ros kpt_subscriber.py
```

### Serial Bridge (ESP32 Communication)

```bash
ros2 run robotic_hand_ros uart_communication_node.py
```
