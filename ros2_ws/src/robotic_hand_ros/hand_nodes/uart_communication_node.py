#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import serial
import time



class SerialCommunication(Node):
    def __init__(self):
        super().__init__('angle_processor')
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'angle_topico',
            self.listener_callback,
            10)
        self.subscription  # evitar advertencia de variable sin usar

        # Puerto serial y velocidad de baudios
        self.com = serial.Serial("/dev/ttyACM0", 115200, write_timeout=0.1)
        time.sleep(2)  # Esperar a que se establezca la conexión serial


    def listener_callback(self, msg):
        angles = msg.data
        
        if len(angles) == 5:
            # Convertir a string sin corchetes ni espacios
            data_str = "{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(
                angles[0], angles[1], angles[2],
                angles[3], angles[4]
            )

            self.get_logger().info(f'Enviando: {data_str.strip()}')

            self.com.write(data_str.encode('utf-8'))
        else:
            self.get_logger().warn("Se esperaban 5 ángulos")


def main(args=None):
    rclpy.init(args=args)
    serial_com = SerialCommunication()
    rclpy.spin(serial_com)
    serial_com.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()