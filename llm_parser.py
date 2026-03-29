import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ackermann_msgs.msg import AckermannDriveStamped
from example_interfaces.srv import AddTwoInts
from pydantic import BaseModel, Field, ValidationError
from typing import Literal, Union, List

# --- ОПРЕДЕЛЯЕМ СХЕМУ (API НАШЕГО РОБОТА ДЛЯ LLM) ---

class DriveCommand(BaseModel):
    action: Literal["drive"]
    speed: float = Field(..., description="Скорость в м/с. От -0.5 (назад) до 0.5 (вперед)")
    steering: float = Field(..., description="Угол руля в радианах. От -0.5 (вправо) до 0.5 (влево)")

class HeadCommand(BaseModel):
    action: Literal["turn_head"]
    pan: int = Field(..., description="Поворот головы влево-вправо (градусы, от -90 до 90)")
    tilt: int = Field(..., description="Наклон головы вверх-вниз (градусы, от -90 до 90)")

class LlmResponse(BaseModel):
    thought: str = Field(..., description="Мысли агента вслух: почему он принял такое решение")
    commands: List[Union[DriveCommand, HeadCommand]] = Field(..., description="Список действий")

# --- ROS 2 УЗЕЛ ---

class LlmCommandParser(Node):
    def __init__(self):
        super().__init__('llm_parser')
        
        # Слушаем сырой JSON от LLM
        self.subscription = self.create_subscription(
            String, '/llm_raw_json', self.json_callback, 10)
            
        # Паблишер напрямую в Электронный Дифференциал (минуя текстовый транслятор)
        self.drive_pub = self.create_publisher(AckermannDriveStamped, '/drive', 10)
        
        # Клиент для управления головой
        self.head_client = self.create_client(AddTwoInts, 'set_head_position')
        
        self.get_logger().info('🤖 LLM JSON Парсер запущен. Жду структурированных команд...')

    def json_callback(self, msg):
        raw_json = msg.data
        
        try:
            # 1. Pydantic автоматически валидирует JSON! 
            # Если LLM ошиблась или погаллюцинировала, код выбросит ошибку, и робот не сойдет с ума.
            parsed_data = LlmResponse.model_validate_json(raw_json)
            
            self.get_logger().info(f'💡 Мысль AI: "{parsed_data.thought}"')
            
            # 2. Выполняем список команд по очереди
            for cmd in parsed_data.commands:
                if cmd.action == "drive":
                    self.execute_drive(cmd.speed, cmd.steering)
                elif cmd.action == "turn_head":
                    self.execute_head(cmd.pan, cmd.tilt)
                    
        except ValidationError as e:
            self.get_logger().error(f'❌ LLM прислала кривой JSON (Галлюцинация): {e}')

    def execute_drive(self, speed, steering):
        drive_msg = AckermannDriveStamped()
        drive_msg.drive.speed = speed
        drive_msg.drive.steering_angle = steering
        self.drive_pub.publish(drive_msg)
        self.get_logger().info(f'🚗 [ШАССИ] Отправлена команда: скорость {speed} м/с, руль {steering} рад')

    def execute_head(self, pan, tilt):
        if self.head_client.wait_for_service(timeout_sec=0.2):
            req = AddTwoInts.Request(a=pan, b=tilt)
            self.head_client.call_async(req)
            self.get_logger().info(f'👀 [ГОЛОВА] Отправлен запрос: Pan={pan}°, Tilt={tilt}°')
        else:
            self.get_logger().warning('⚠️ Сервис головы не в сети!')

def main(args=None):
    rclpy.init(args=args)
    node = LlmCommandParser()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()