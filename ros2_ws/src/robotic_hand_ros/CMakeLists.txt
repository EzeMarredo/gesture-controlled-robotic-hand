cmake_minimum_required(VERSION 3.10)
project(robotic_hand)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Dependencias

find_package(ament_cmake_python REQUIRED)

find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)

install (
  PROGRAMS
  hand_nodes/kpt_publisher.py
  hand_nodes/uart_communication_node.py
  hand_nodes/kpt_subscriber.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()