#! /home/jetson1/Desktop/Robotic_Hand_Project/gesture-controlled-robotic-hand/venv_yolo/bin/python3

import sys
# Forzar que se use el protobuf del venv antes que el de ROS
sys.path.insert(0, '/home/jetson1/.local/lib/python3.10/site-packages')
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import cv2
import numpy as np
import mediapipe as mp
import time

class MiPublisher(Node):
    def __init__(self):
        super().__init__('kpt_publisher')
        self.publisher_ = self.create_publisher(Float32MultiArray, 'kpt_topico', 10)
        timer_period = 0.05  # segundos
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not access the camera.")
            return
        
        print(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils        
        
        self.kpts = np.zeros((21, 2))  # Inicializar con ceros

        # FPS calculation
        self.fps = 0.0
        self.prev_time = time.time()

    def timer_callback(self):
        ret, self.frame = self.cap.read()
        if not ret:
            return
        
        rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        h, w , _ = self.frame.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.kpts = np.array([(lm.x * w, lm.y * h) for lm in hand_landmarks.landmark], dtype=np.float32)
                self.mp_draw.draw_landmarks(self.frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            msg = Float32MultiArray()
            msg.data = self.kpts.flatten().tolist() 
            self.publisher_.publish(msg)
            self.get_logger().info(f'Publicado: "{msg.data}"')  
            #self.get_logger().info(f'Confianza: {self.confianza:.2f}')

        # Display FPS
        curr_time = time.time()
        self.fps = 1.0 / (curr_time - self.prev_time)
        self.prev_time = curr_time
        fps_text = f"FPS: {self.fps:.2f}"
        cv2.putText(self.frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)    
        


        cv2.imshow("Hand Pose", self.frame)
        cv2.waitKey(1)

    def destroy_node(self):
        super().destroy_node()
        self.cap.release()
        cv2.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    mi_publisher = MiPublisher()
    rclpy.spin(mi_publisher)
    mi_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    