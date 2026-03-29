import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import ByteMultiArray, String, Float32
from example_interfaces.srv import AddTwoInts
import json

class AIBrain(Node):
    def __init__(self):
        super().__init__('ai_brain')
        
        # --- ПОДПИСКИ (Органы чувств) ---
        self.create_subscription(Image, '/camera/color/image_raw', self.image_cb, 10)
        self.create_subscription(ByteMultiArray, '/audio/mic_raw', self.audio_cb, 10)
        self.create_subscription(Float32, '/sensor/sonar_front', self.sonar_cb, 10)
        
        # --- ПАБЛИШЕРЫ (Действия) ---
        self.drive_pub = self.create_publisher(String, '/ai_command', 10)
        self.speaker_pub = self.create_publisher(ByteMultiArray, '/audio/speaker_raw', 10)
        
        # --- КЛИЕНТЫ СЕРВИСОВ ---
        self.head_client = self.create_client(AddTwoInts, 'set_head_position')
        
        # Состояние памяти робота
        self.latest_image = None
        self.front_distance = 999.0
        
        self.get_logger().info('🧠 AI Brain запущен и ждет данных...')

    def image_cb(self, msg):
        self.latest_image = "КАДР_В_ПАМЯТИ" # В реальности: cv_bridge перехват
        
    def sonar_cb(self, msg):
        self.front_distance = msg.data

    def audio_cb(self, msg):
        user_voice = bytes(msg.data).decode('utf-8')
        self.get_logger().info(f'🧠 Услышал голос: {user_voice}')
        self.process_ai_reasoning()

    def process_ai_reasoning(self):
        self.get_logger().info('🧠 Отправляю [Голос + Фото + Данные Сонара] в OpenAI Realtime API...')
        
        # --- ИМИТАЦИЯ ОТВЕТА ОТ OPENAI (LLM+VLM) ---
        # В реальности OpenAI Realtime API пришлет нам аудио-поток с голосом 
        # и JSON с вызовом функций (Function Calling) для моторов.
        
        if self.front_distance < 1.0:
            ai_thought = "Вижу препятствие близко. Нужно остановиться и сказать об этом."
            drive_cmd = "стоп"
            voice_reply = b"I stopped because there is an obstacle right in front of me!"
        else:
            ai_thought = "Путь свободен. Поверну голову посмотреть и поеду вперед."
            drive_cmd = "вперед"
            voice_reply = b"Moving forward and scanning the area."
            # Запрашиваем поворот головы (асинхронно)
            self.turn_head(45, 0)
            
        self.get_logger().info(f'🧠 Решение AI: {ai_thought}')
        
        # Говорим голосом
        speaker_msg = ByteMultiArray()
        speaker_msg.data = voice_reply
        self.speaker_pub.publish(speaker_msg)
        
        # Даем команду шасси
        drive_msg = String()
        drive_msg.data = drive_cmd
        self.drive_pub.publish(drive_msg)

    def turn_head(self, pan, tilt):
        if not self.head_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warning('Сервис головы недоступен!')
            return
            
        req = AddTwoInts.Request()
        req.a = pan
        req.b = tilt
        self.get_logger().info(f'🧠 Даю команду моторам головы: Pan={pan}, Tilt={tilt}')
        self.head_client.call_async(req) # Асинхронный вызов

def main(args=None):
    rclpy.init(args=args)
    node = AIBrain()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()