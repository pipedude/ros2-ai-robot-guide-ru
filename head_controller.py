import rclpy
from rclpy.node import Node
# Импортируем стандартный тип сервиса (Запрос: a, b. Ответ: sum)
from example_interfaces.srv import AddTwoInts
import time

class HeadControllerService(Node):
    def __init__(self):
        super().__init__('head_controller')
        
        # Создаем Service Server
        # Аргументы: Тип сервиса, Имя сервиса, Функция-обработчик
        self.srv = self.create_service(AddTwoInts, 'set_head_position', self.move_head_callback)
        
        # Текущие углы (робот смотрит прямо)
        self.current_pan = 0
        self.current_tilt = 0
        
        self.get_logger().info('Контроллер Pan-Tilt головы запущен. Жду команд (Сервисов)...')

    def move_head_callback(self, request, response):
        # Эта функция вызывается, когда кто-то "звонит" в этот сервис
        target_pan = request.a
        target_tilt = request.b
        
        self.get_logger().info(f'Получена команда: повернуть голову на Pan={target_pan}°, Tilt={target_tilt}°')
        
        # Имитируем физическое время работы сервоприводов LSC-16 (1 секунда)
        self.get_logger().info('Моторы жжжжжж...')
        time.sleep(1.0) 
        
        # Обновляем текущие координаты
        self.current_pan = target_pan
        self.current_tilt = target_tilt
        
        # Формируем ответ клиенту. 
        # В AddTwoInts ответ хранится в поле "sum". Мы запишем туда 1 (успех)
        response.sum = 1 
        self.get_logger().info('Движение завершено. Отправляю ответ.')
        
        return response

def main(args=None):
    rclpy.init(args=args)
    head_controller = HeadControllerService()
    
    try:
        rclpy.spin(head_controller)
    except KeyboardInterrupt:
        pass
    finally:
        head_controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()