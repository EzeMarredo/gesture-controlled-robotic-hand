#!/home/jetson1/Desktop/Robotic_Hand_Project/gesture-controlled-robotic-hand/venv_yolo/bin/python3


import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import cv2
import numpy as np
from ultralytics import YOLO
import time

class MiPublisher(Node):
    def __init__(self):
        super().__init__('kpt_publisher')
        self.publisher_ = self.create_publisher(Float32MultiArray, 'kpt_topico', 10)
        timer_period = 0.05  # segundos
        self.timer = self.create_timer(timer_period, self.timer_callback)

        #Para convertir el modelo .pt a .engine compatible con la Jetson
        #self.model = YOLO("/home/jetson1/Desktop/Robotic_Hand_Project/gesture-controlled-robotic-hand/ros2_ws/src/robotic_hand_ros/hand_nodes/models/best.pt")
        #self.model.export(format='engine', task='pose', half=True, imgsz=320)
        
        self.model = YOLO("/home/jetson1/Desktop/Robotic_Hand_Project/gesture-controlled-robotic-hand/ros2_ws/src/robotic_hand_ros/hand_nodes/models/bestFP16320px.engine" , task='pose')
        #self.model.to('cpu')
        self.cap = cv2.VideoCapture(0)
        #self.cap = cv2.VideoCapture("https://172.16.0.136:8080/video")
        self.SKELETON = [
        (0, 1), (1, 2), (2, 3), (3, 4),       # pulgar
        (0, 5), (5, 6), (6, 7), (7, 8),       # índice
        (0, 9), (9, 10), (10, 11), (11, 12),  # medio
        (0, 13), (13, 14), (14, 15), (15, 16), # anular
        (0, 17), (17, 18), (18, 19), (19, 20)  # meñique
        ]  
        self.kpts = np.zeros((21, 2))  # Inicializar con ceros

        # FPS calculation
        self.fps = 0.0
        self.prev_time = time.time()


    def timer_callback(self):
        ret, self.frame = self.cap.read()
        if not ret:
            return
        self.results = self.model(self.frame)
        self.box_result = self.results[0]

        for result in self.results:
            print(f"Boxes:  {result.boxes}")
            print(f"Keypoints:  {result.keypoints}")
            print(f"Keypoints xy:  {result.keypoints.xy if result.keypoints is not None else 'None'}")
            print(f"Conf:  {result.boxes.conf if result.boxes is not None else 'None'}")

            if result.keypoints is not None and len(result.keypoints.xy) > 0:
                self.confianza = result.boxes.conf[0].item()

               # if self.confianza > 0.9:  # Umbral de confianza
                self.kpts = result.keypoints.xy[0].cpu().numpy()

                msg = Float32MultiArray()
                msg.data = self.kpts.flatten().tolist() 
                self.publisher_.publish(msg)
                self.get_logger().info(f'Publicado: "{msg.data}"')  
                #self.get_logger().info(f'Confianza: {self.confianza:.2f}')

                for x, y in self.kpts:
                    cv2.circle(self.frame, (int(x), int(y)), 4, (0, 255, 0), -1)

                for a, b in self.SKELETON:
                    x1, y1 = self.kpts[a]
                    x2, y2 = self.kpts[b]
                    cv2.line(self.frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
        
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
    