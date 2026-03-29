import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped
import math

class ElectronicDifferential(Node):
    def __init__(self):
        super().__init__('electronic_differential')
        
        # Подписываемся на команды от AI (или навигации)
        self.subscription = self.create_subscription(
            AckermannDriveStamped, '/drive', self.drive_callback, 10)
            
        # Габариты твоего шасси Wheeltec (примерные в метрах, потом замеришь рулеткой)
        self.wheelbase = 0.25  # L: расстояние между передней и задней осью
        self.track_width = 0.15 # W: расстояние между левым и правым задним колесом
        
        self.get_logger().info('Электронный дифференциал запущен. Жду команды /drive...')

    def drive_callback(self, msg):
        v = msg.drive.speed
        delta = msg.drive.steering_angle
        
        # Если едем прямо или стоим (угол поворота близок к нулю)
        if abs(delta) < 0.01:
            v_left = v
            v_right = v
        else:
            # Радиус поворота центра задней оси
            R = self.wheelbase / math.tan(delta)
            
            # Рассчитываем скорости для каждого колеса
            v_left = v * (1 - self.track_width / (2 * R))
            v_right = v * (1 + self.track_width / (2 * R))
            
        # В будущем этот узел будет отправлять v_left, v_right и delta
        # по Serial или I2C в Raspberry Pi Pico 2. 
        # А пока просто красиво логируем:
        
        if v == 0:
            status = "СТОИМ"
        elif delta > 0.01:
            status = f"ПОВОРОТ НАЛЕВО (Внутреннее колесо медленнее)"
        elif delta < -0.01:
            status = f"ПОВОРОТ НАПРАВО (Внутреннее колесо медленнее)"
        else:
            status = "ЕДЕМ ПРЯМО"

        self.get_logger().info(
            f'\n--- {status} ---\n'
            f'Целевая: Скорость={v:.2f} м/с, Руль={delta:.2f} рад\n'
            f'Мотор ЛЕВЫЙ:  {v_left:.2f} м/с\n'
            f'Мотор ПРАВЫЙ: {v_right:.2f} м/с\n'
            f'Серво РУЛЬ:   {delta:.2f} рад'
        )

def main(args=None):
    rclpy.init(args=args)
    node = ElectronicDifferential()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()