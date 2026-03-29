import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class MockCamera(Node):
    def __init__(self):
        super().__init__('mock_camera')
        # Публикуем в топик, стандартный для цветных камер Orbbec
        self.publisher_ = self.create_publisher(Image, '/camera/color/image_raw', 10)
        
        # Таймер для 10 FPS (1 кадр каждые 0.1 сек)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.bridge = CvBridge()
        self.frame_count = 0
        
        self.get_logger().info('Виртуальная камера Orbbec запущена (10 FPS)...')

    def timer_callback(self):
        # 1. Генерируем "фейковый" кадр с помощью OpenCV (черный фон 640x480)
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # 2. Рисуем меняющийся текст, чтобы видеть, что видео идет
        text = f"Simulated Vision: Frame {self.frame_count}"
        cv2.putText(img, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        self.frame_count += 1

        # 3. Конвертируем OpenCV картинку (numpy array) в ROS 2 Image Message
        msg = self.bridge.cv2_to_imgmsg(img, encoding="bgr8")
        
        # 4. Публикуем в топик
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MockCamera()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()