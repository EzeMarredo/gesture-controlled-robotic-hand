#! /home/eze/Desktop/PPS/Mano_Robótica/venv_yolo/bin/python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import cv2
import numpy as np
from ultralytics import YOLO


class MiPublisher(Node):
    def __init__(self):
        super().__init__('kpt_publisher')
        self.publisher_ = self.create_publisher(Float32MultiArray, 'kpt_topico', 10)
        timer_period = 0.05  # segundos
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.model = YOLO("/home/eze/ros2_ws/src/mi_publisher/mi_publisher/best.pt")
        #self.model.to('cpu')
        self.cap = cv2.VideoCapture(0)
        self.SKELETON = [
        (0, 1), (1, 2), (2, 3), (3, 4),       # pulgar
        (0, 5), (5, 6), (6, 7), (7, 8),       # índice
        (0, 9), (9, 10), (10, 11), (11, 12),  # medio
        (0, 13), (13, 14), (14, 15), (15, 16), # anular
        (0, 17), (17, 18), (18, 19), (19, 20)  # meñique
        ]  
        self.kpts = np.zeros((21, 2))  # Inicializar con ceros


    def timer_callback(self):
        ret, self.frame = self.cap.read()
        if not ret:
            return
        self.results = self.model(self.frame)
        self.box_result = self.results[0]
        for result in self.results:
            if result.keypoints is not None and len(result.keypoints.xy) > 0:
                self.confianza = result.boxes.conf[0].item()

                if self.confianza > 0.9:  # Umbral de confianza
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
    