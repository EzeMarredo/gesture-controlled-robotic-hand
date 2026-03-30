#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import numpy as np

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

    def listener_callback(self, msg):
        #self.get_logger().info(f'Recibido: "{msg.data}"')
        self.data = msg.data
        kpts = np.array(self.data).reshape((21, 2))  # Convertir a array de 21x2
        print(kpts)  # Imprimir los puntos clave como array
        
        if (kpts[0] != [0, 0]).any():  # Verificar si encuentra la muñeca para saber si está la mano en pantalla
            
            self.thumb_angle = self.angle_calc(kpts[2], kpts[3], kpts[4])
            self.get_logger().info(f'Ángulo del dedo pulgar: {self.thumb_angle:.2f} grados')

            self.index_angle = self.angle_calc(kpts[5], kpts[6], kpts[7])
            self.get_logger().info(f'Ángulo del dedo índice: {self.index_angle:.2f} grados')

            self.middle_angle = self.angle_calc(kpts[9], kpts[10], kpts[11])
            self.get_logger().info(f'Ángulo del dedo medio: {self.middle_angle:.2f} grados')

            self.ring_angle = self.angle_calc(kpts[13], kpts[14], kpts[15])
            self.get_logger().info(f'Ángulo del dedo anular: {self.ring_angle:.2f} grados')

            self.pinky_angle = self.angle_calc(kpts[17], kpts[18], kpts[19])
            self.get_logger().info(f'Ángulo del dedo meñique: {self.pinky_angle:.2f} grados')

        msg_pub = Float32MultiArray()
        msg_pub.data = [self.thumb_angle, self.index_angle, self.middle_angle, self.ring_angle, self.pinky_angle]  
        self.publisher_.publish(msg_pub)
        self.get_logger().info(f'Publicado: "{msg_pub.data}"')  

    # Función para calcular el ángulo entre tres puntos (a, b, c) con b como vértice
    def angle_calc(self, a, b, c):
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)


def main(args=None):
    rclpy.init(args=args)
    ang_proc = AngleProcessor()
    rclpy.spin(ang_proc)
    ang_proc.destroy_node()

    rclpy.shutdown()

if __name__ == '__main__':
    main()