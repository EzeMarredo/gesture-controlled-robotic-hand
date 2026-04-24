#! /home/jetson1/Desktop/Robotic_Hand_Project/gesture-controlled-robotic-hand/venv_yolo/bin/python3


import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import numpy as np
import math

"""
fingers = {
    "thumb": [1, 2, 3, 4],
    "index": [5, 6, 7, 8],
    "middle": [9, 10, 11, 12],
    "ring": [13, 14, 15, 16],
    "pinky": [17, 18, 19, 20]
}
"""

class AngleProcessor(Node):
    def __init__(self):
        super().__init__('angle_processor')
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'kpt_topico',
            self.listener_callback,
            10)
        self.subscription  # evitar advertencia de variable sin usar
        self.publisher_ = self.create_publisher(Float32MultiArray, 'angle_topico', 10)
        self.last_angle = [180.0, 180.0, 180.0, 180.0, 180.0]

    def listener_callback(self, msg):
        #self.get_logger().info(f'Recibido: "{msg.data}"')
        self.data = msg.data
        kpts = np.array(self.data).reshape((21, 2))  # Convertir a array de 21x2
        print(kpts)  # Imprimir los puntos clave como array
        
        if (kpts[0] != [0, 0]).any():  # Verificar si encuentra la muñeca para saber si está la mano en pantalla
            
            if(self.validate_kpt(kpts[2], kpts[3], kpts[4])):
                self.thumb_angle = self.angle_calc(kpts[2], kpts[3], kpts[4])
                self.get_logger().info(f'Ángulo del dedo pulgar: {self.thumb_angle:.2f} grados')
                if(math.isfinite(self.thumb_angle)):
                    self.last_angle[0] = self.thumb_angle

            if(self.validate_kpt(kpts[5], kpts[6], kpts[7])):
                self.index_angle = self.angle_calc(kpts[5], kpts[6], kpts[7])           
                self.get_logger().info(f'Ángulo del dedo índice: {self.index_angle:.2f} grados')            
                if(math.isfinite(self.index_angle)):
                    self.last_angle[1] = self.index_angle
            
            if(self.validate_kpt(kpts[9], kpts[10], kpts[11])):
                self.middle_angle = self.angle_calc(kpts[9], kpts[10], kpts[11])            
                self.get_logger().info(f'Ángulo del dedo medio: {self.middle_angle:.2f} grados')           
                if(math.isfinite(self.middle_angle)):
                    self.last_angle[2] = self.middle_angle
            
            if(self.validate_kpt(kpts[13], kpts[14], kpts[15])):
                self.ring_angle = self.angle_calc(kpts[13], kpts[14], kpts[15])         
                self.get_logger().info(f'Ángulo del dedo anular: {self.ring_angle:.2f} grados')         
                if(math.isfinite(self.ring_angle)):
                    self.last_angle[3] = self.ring_angle
            
            if(self.validate_kpt(kpts[17], kpts[18], kpts[19])):
                self.pinky_angle = self.angle_calc(kpts[17], kpts[18], kpts[19])            
                self.get_logger().info(f'Ángulo del dedo meñique: {self.pinky_angle:.2f} grados')           
                if(math.isfinite(self.pinky_angle)):
                    self.last_angle[4] = self.pinky_angle

            msg_pub = Float32MultiArray()
            msg_pub.data = [float(a) for a in self.last_angle]
            
            self.publisher_.publish(msg_pub)
            self.get_logger().info(f'Publicado: "{msg_pub.data}"')  

    # Función para calcular el ángulo entre tres puntos (a, b, c) con b como vértice
    def angle_calc(self, a, b, c):
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    def validate_kpt(self, point1, point2, point3):
        if (point1[0] == 0.0 and point1[1]== 0.0):
            return False
        
        if (point2[0] == 0.0 and point2[1]== 0.0):
            return False

        if (point3[0] == 0.0 and point3[1]== 0.0):
            return False

        return True

def main(args=None):
    rclpy.init(args=args)
    ang_proc = AngleProcessor()
    rclpy.spin(ang_proc)
    ang_proc.destroy_node()

    rclpy.shutdown()

if __name__ == '__main__':
    main()