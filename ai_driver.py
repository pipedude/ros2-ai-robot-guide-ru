import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ackermann_msgs.msg import AckermannDriveStamped

class AIDriverNode(Node):
    def __init__(self):
        super().__init__('ai_driver_translator')
        
        # Подписчик на текстовые команды (Топик: /ai_command)
        self.subscription = self.create_subscription(
            String, '/ai_command', self.command_callback, 10)
            
        # Паблишер физических команд для шасси (Топик: /drive)
        self.publisher = self.create_publisher(
            AckermannDriveStamped, '/drive', 10)
            
        self.get_logger().info('Транслятор AI -> Ackermann запущен. Жду текстовых команд в топик /ai_command')

    def command_callback(self, msg):
        command = msg.data.lower()
        
        # Создаем пустое сообщение Ackermann
        drive_msg = AckermannDriveStamped()
        
        # Логика перевода текста в физику:
        # speed (м/с) - скорость
        # steering_angle (радианы) - угол поворота руля
        
        if command == 'вперед':
            drive_msg.drive.speed = 0.5
            drive_msg.drive.steering_angle = 0.0
        elif command == 'налево':
            drive_msg.drive.speed = 0.3
            drive_msg.drive.steering_angle = 0.5  # Примерно 28 градусов влево
        elif command == 'направо':
            drive_msg.drive.speed = 0.3
            drive_msg.drive.steering_angle = -0.5 # Примерно 28 градусов вправо
        elif command == 'назад':
            drive_msg.drive.speed = -0.3
            drive_msg.drive.steering_angle = 0.0
        elif command == 'стоп':
            drive_msg.drive.speed = 0.0
            drive_msg.drive.steering_angle = 0.0
        else:
            self.get_logger().warning(f'AI выдал неизвестную команду: {command}')
            return
            
        self.publisher.publish(drive_msg)
        self.get_logger().info(f'AI сказал "{command}". Едем: Скорость={drive_msg.drive.speed} м/с, Руль={drive_msg.drive.steering_angle} рад')

def main(args=None):
    rclpy.init(args=args)
    node = AIDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()