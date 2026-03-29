import rclpy
from rclpy.node import Node
from std_msgs.msg import ByteMultiArray, String
import time

class AudioSystem(Node):
    def __init__(self):
        super().__init__('audio_system')
        
        # Микрофон (Публикует аудио-байты)
        self.mic_pub = self.create_publisher(ByteMultiArray, '/audio/mic_raw', 10)
        
        # Динамик (Слушает аудио-байты от AI и "воспроизводит" их)
        self.speaker_sub = self.create_subscription(
            ByteMultiArray, '/audio/speaker_raw', self.speaker_callback, 10)
            
        self.timer = self.create_timer(10.0, self.simulate_user_speech)
        self.get_logger().info('Аудиосистема (Микрофон + Динамик Adafruit) запущена.')

    def simulate_user_speech(self):
        # Имитируем, что пользователь что-то сказал (например, "Робот, что ты видишь?")
        msg = ByteMultiArray()
        # В реальности здесь будет массив байтов PCM 16-bit. 
        # Мы упакуем фейковую строку в байты для теста
        msg.data = b"VOICE_COMMAND: Look around and tell me what you see!"
        
        self.get_logger().info('🎙️ Человек сказал фразу в микрофон...')
        self.mic_pub.publish(msg)

    def speaker_callback(self, msg):
        # В реальности здесь байты отправляются на I2S Amp
        # Мы просто декодируем для теста
        text = bytes(msg.data).decode('utf-8', errors='ignore')
        self.get_logger().info(f'🔊 ДИНАМИК ВОСПРОИЗВОДИТ: {text}')

def main(args=None):
    rclpy.init(args=args)
    node = AudioSystem()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()