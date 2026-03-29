import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class VLMAgentStub(Node):
    def __init__(self):
        super().__init__('vlm_agent')
        self.subscription = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.image_callback,
            10 # QoS (размер очереди)
        )
        self.bridge = CvBridge()
        self.latest_cv_image = None
        
        # Таймер, имитирующий обращение к OpenAI (например, раз в 3 секунды)
        self.timer = self.create_timer(3.0, self.process_vision_api)
        self.get_logger().info('AI Vision Агент запущен. Жду видеопоток...')

    def image_callback(self, msg):
        # Эта функция вызывается 10 раз в секунду. 
        # Мы НЕ делаем здесь тяжелых вычислений, просто обновляем кэш свежего кадра.
        self.latest_cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    def process_vision_api(self):
        # Эта функция вызывается раз в 3 секунды.
        if self.latest_cv_image is not None:
            height, width, channels = self.latest_cv_image.shape
            self.get_logger().info(
                f'>>> [API CALL] Беру свежий кадр размером {width}x{height} '
                f'и "отправляю" его в OpenAI GPT-4o Vision...'
            )
            # В будущем здесь будет код: 
            # 1. cv2.imencode('.jpg', self.latest_cv_image)
            # 2. base64.b64encode
            # 3. client.chat.completions.create(...)
        else:
            self.get_logger().warning('Кадров пока нет...')

def main(args=None):
    rclpy.init(args=args)
    node = VLMAgentStub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()