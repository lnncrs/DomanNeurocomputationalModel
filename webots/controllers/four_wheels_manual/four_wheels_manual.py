"""Controller multimodo do FourWheelRobot.

O modo automático reproduz o controller C de anti-colisão. Quando um
joystick está conectado, os botões selecionam controle manual, automático,
aprendizado (reservado) ou parada de emergência.
"""

from enum import Enum, auto
import json
import math
import sys

from controller import Robot


TIME_STEP = 64
MAX_SPEED = 10.0
TURN_LEFT_SPEED = 1.0
TURN_RIGHT_SPEED = -1.0
PROXIMITY_THRESHOLD = 950.0
AVOIDANCE_STEPS = 100
DPAD_AXIS_THRESHOLD = 16000
PASSIVE_REALISTIC_TORQUE = 0.03 # N·m por roda

DISTANCE_SENSOR_NAMES = ("ds_left", "ds_right")
PROXIMITY_SENSOR_NAMES = (
    "ds_left", "ds_right", "ps_front", "ps_back", "ps_left", "ps_right"
)
WHEEL_NAMES = ("wheel1", "wheel2", "wheel3", "wheel4")
PLANE_ANGLE_TOLERANCE_DEG = 2.0
MOTION_SPEED_THRESHOLD = 0.005

# Mapeamento observado no controle "Controller (Xbox One For Windows)"
# conectado via USB. O console continua imprimindo os índices para diagnóstico.
BUTTON_LB = 4
BUTTON_START = 0
BUTTON_A = 8
BUTTON_B = 9
BUTTON_X = 10
BUTTON_Y = 11

class ControlMode(Enum):
    AUTOMATIC = auto()
    MANUAL = auto()
    PASSIVE_FREE = auto()
    PASSIVE_REALISTIC = auto()
    LEARNING = auto()
    EMERGENCY_STOP = auto()


def parse_goal_argument(arguments: list[str]):
    """Lê x,y,z,largura,comprimento,altura,permanência de --goal."""
    prefix = "--goal="
    for argument in arguments:
        if argument.startswith(prefix):
            try:
                values = tuple(float(value) for value in argument[len(prefix):].split(","))
            except ValueError:
                print(f"Invalid goal parameters: {argument}")
                return None
            if len(values) == 7:
                return values
            print("--goal expects x,y,z,width,length,height,dwell_seconds")
    return None


class ExperimentMonitor:
    def __init__(self, goal) -> None:
        self.goal = goal
        self.previous_position = None
        self.previous_distance = None
        self.inside_since = None
        self.reached = False

    def update(self, time, position, accelerometer, gyro, motor_command):
        ax, ay, az = accelerometer
        gravity_magnitude = math.sqrt(ax * ax + ay * ay + az * az)
        tilt = (
            math.degrees(math.acos(min(1.0, abs(az) / gravity_magnitude)))
            if gravity_magnitude > 1e-9
            else 0.0
        )
        angular_speed = math.sqrt(sum(value * value for value in gyro))
        if angular_speed > 0.25:
            terrain = "INDETERMINADO"
        elif tilt <= PLANE_ANGLE_TOLERANCE_DEG:
            terrain = "PLANO"
        else:
            terrain = "INCLINADO"

        direction = "PARADO"
        goal_state = "NÃO CONFIGURADA"
        progress_speed = 0.0
        inside = False

        if self.goal is not None:
            goal_x, goal_y, goal_z, width, length, height, dwell = self.goal
            distance = math.hypot(position[0] - goal_x, position[1] - goal_y)
            if self.previous_distance is not None:
                elapsed = TIME_STEP / 1000.0
                progress_speed = (self.previous_distance - distance) / elapsed
                if progress_speed > MOTION_SPEED_THRESHOLD:
                    direction = "DESCENDO"
                elif progress_speed < -MOTION_SPEED_THRESHOLD:
                    direction = "SUBINDO"

            inside = (
                abs(position[0] - goal_x) <= width / 2
                and abs(position[1] - goal_y) <= length / 2
                and goal_z <= position[2] <= goal_z + height
            )
            if inside:
                if self.inside_since is None:
                    self.inside_since = time
                if time - self.inside_since >= dwell:
                    self.reached = True
                goal_state = "ALCANCADA" if self.reached else "DENTRO"
            else:
                self.inside_since = None
                goal_state = "ALCANCADA" if self.reached else "FORA"
            self.previous_distance = distance

        commanded = max(abs(motor_command[0]), abs(motor_command[1])) > 1e-6
        maraca = commanded and progress_speed > MOTION_SPEED_THRESHOLD and not self.reached
        self.previous_position = tuple(position)
        return {
            "terrain": terrain,
            "inclination": tilt,
            "longitudinalAcceleration": ax,
            "direction": direction,
            "goal": goal_state,
            "maraca": "ATIVA" if maraca else "INATIVA",
        }


def read_pressed_buttons(joystick) -> set[int]:
    buttons: set[int] = set()
    button = joystick.getPressedButton()
    while button >= 0:
        buttons.add(button)
        button = joystick.getPressedButton()
    return buttons


def manual_dpad_drive(joystick) -> tuple[float, float]:
    # Mapeamento observado no controle Xbox/driver atual:
    # eixo 0: cima = -32767, baixo = +32768
    # eixo 1: esquerda = -32768, direita = +32767
    # O POV permanece em 0 mesmo solto e, portanto, não é utilizável.
    if joystick.getNumberOfAxes() < 2:
        return 0.0, 0.0

    vertical = joystick.getAxisValue(0)
    horizontal = joystick.getAxisValue(1)

    if vertical <= -DPAD_AXIS_THRESHOLD:
        throttle = 1.0
    elif vertical >= DPAD_AXIS_THRESHOLD:
        throttle = -1.0
    else:
        throttle = 0.0

    if horizontal >= DPAD_AXIS_THRESHOLD:
        steering = 1.0
    elif horizontal <= -DPAD_AXIS_THRESHOLD:
        steering = -1.0
    else:
        steering = 0.0

    left = throttle + steering
    right = throttle - steering

    # Preserva a proporção do comando ao saturar uma das laterais.
    largest = max(1.0, abs(left), abs(right))
    return left / largest * MAX_SPEED, right / largest * MAX_SPEED


def dpad_state(joystick) -> tuple[str, int, int]:
    if not joystick.isConnected() or joystick.getNumberOfAxes() < 2:
        return "NEUTRAL", 0, 0

    vertical = joystick.getAxisValue(0)
    horizontal = joystick.getAxisValue(1)
    directions = []
    if vertical <= -DPAD_AXIS_THRESHOLD:
        directions.append("UP")
    elif vertical >= DPAD_AXIS_THRESHOLD:
        directions.append("DOWN")
    if horizontal <= -DPAD_AXIS_THRESHOLD:
        directions.append("LEFT")
    elif horizontal >= DPAD_AXIS_THRESHOLD:
        directions.append("RIGHT")
    return "+".join(directions) or "NEUTRAL", vertical, horizontal


def send_control_state(robot, joystick, mode, pressed_buttons) -> None:
    direction, vertical, horizontal = dpad_state(joystick)
    message = {
        "type": "control_state",
        "mode": mode.name,
        "joystick": {
            "connected": joystick.isConnected(),
            "model": joystick.model if joystick.isConnected() else "",
            "buttons": sorted(pressed_buttons),
            "dpad": direction,
            "vertical": vertical,
            "horizontal": horizontal,
        },
    }
    robot.wwiSendText(json.dumps(message))


def send_telemetry(
    robot, proximity_sensors, wheels, accelerometer, gyro, gps, compass,
    experiment_state
) -> None:
    message = {
        "type": "telemetry",
        "time": robot.getTime(),
        "distance": {
            name: sensor.getValue()
            for name, sensor in proximity_sensors.items()
        },
        "motors": [wheel.getVelocity() for wheel in wheels],
        "accelerometer": list(accelerometer.getValues()),
        "gyro": list(gyro.getValues()),
        "gps": list(gps.getValues()),
        "compass": list(compass.getValues()),
        "experiment": experiment_state,
        "stopped": False,
    }
    robot.wwiSendText(json.dumps(message))


class CollisionAvoidance:
    def __init__(self, distance_sensors) -> None:
        self.distance_sensors = distance_sensors
        self.steps_remaining = 0

    def reset(self) -> None:
        self.steps_remaining = 0

    def step(self) -> tuple[float, float]:
        left_speed = MAX_SPEED
        right_speed = MAX_SPEED

        if self.steps_remaining > 0:
            self.steps_remaining -= 1
            left_speed = TURN_LEFT_SPEED
            right_speed = TURN_RIGHT_SPEED
        else:
            values = [sensor.getValue() for sensor in self.distance_sensors]
            if any(value < PROXIMITY_THRESHOLD for value in values):
                self.steps_remaining = AVOIDANCE_STEPS

        return left_speed, right_speed


def set_side_velocities(wheels, left: float, right: float) -> None:
    wheels[0].setVelocity(left)
    wheels[1].setVelocity(right)
    wheels[2].setVelocity(left)
    wheels[3].setVelocity(right)


def print_mode(mode: ControlMode) -> None:
    print(f"Control mode: {mode.name}")


def main() -> None:
    robot = Robot()

    proximity_sensors = {
        name: robot.getDevice(name) for name in PROXIMITY_SENSOR_NAMES
    }
    for sensor in proximity_sensors.values():
        sensor.enable(TIME_STEP)
    distance_sensors = [proximity_sensors[name] for name in DISTANCE_SENSOR_NAMES]

    accelerometer = robot.getDevice("accelerometer")
    gyro = robot.getDevice("gyro")
    gps = robot.getDevice("gps")
    compass = robot.getDevice("compass")
    for sensor in (accelerometer, gyro, gps, compass):
        sensor.enable(TIME_STEP)

    wheels = [robot.getDevice(name) for name in WHEEL_NAMES]
    wheel_max_torques = [wheel.getMaxTorque() for wheel in wheels]
    for wheel in wheels:
        wheel.setPosition(float("inf"))
        wheel.setVelocity(0.0)

    joystick = robot.getJoystick()
    joystick.enable(TIME_STEP)

    collision_avoidance = CollisionAvoidance(distance_sensors)
    experiment_monitor = ExperimentMonitor(parse_goal_argument(sys.argv[1:]))
    if "--passive-free" in sys.argv[1:] or "--passive" in sys.argv[1:]:
        mode = ControlMode.PASSIVE_FREE
    elif "--passive-realistic" in sys.argv[1:]:
        mode = ControlMode.PASSIVE_REALISTIC
    elif "--manual" in sys.argv[1:]:
        mode = ControlMode.MANUAL
    else:
        mode = ControlMode.AUTOMATIC
    previous_buttons: set[int] = set()
    joystick_was_connected = False
    axis_centers: list[float] = []
    print_mode(mode)

    while robot.step(TIME_STEP) != -1:
        connected = joystick.isConnected()
        current_buttons = read_pressed_buttons(joystick) if connected else set()
        newly_pressed = current_buttons - previous_buttons

        if connected and not joystick_was_connected:
            axis_centers = [
                joystick.getAxisValue(axis)
                for axis in range(joystick.getNumberOfAxes())
            ]
            print(
                f"Joystick connected: {joystick.model} "
                f"({joystick.getNumberOfAxes()} axes, "
                f"{joystick.getNumberOfPovs()} POVs)"
            )
            print(f"Joystick axis centers: {axis_centers}")
        elif not connected and joystick_was_connected:
            print("Joystick disconnected")
            axis_centers = []

        if newly_pressed:
            print(f"Joystick buttons pressed: {sorted(newly_pressed)}")
            axis_values = [
                joystick.getAxisValue(axis)
                for axis in range(joystick.getNumberOfAxes())
            ]
            print(f"Joystick axes: {axis_values}")
            pov_values = [
                joystick.getPovValue(pov)
                for pov in range(joystick.getNumberOfPovs())
            ]
            print(f"Joystick POVs: {pov_values}")

        previous_mode = mode

        # X tem prioridade e trava a parada. START é a única liberação.
        if BUTTON_X in newly_pressed:
            mode = ControlMode.EMERGENCY_STOP
        elif mode == ControlMode.EMERGENCY_STOP:
            if BUTTON_START in newly_pressed:
                mode = ControlMode.AUTOMATIC
        elif BUTTON_A in newly_pressed:
            passive_cycle = {
                ControlMode.AUTOMATIC: ControlMode.PASSIVE_FREE,
                ControlMode.PASSIVE_FREE: ControlMode.PASSIVE_REALISTIC,
                ControlMode.PASSIVE_REALISTIC: ControlMode.AUTOMATIC,
            }
            mode = passive_cycle.get(mode, ControlMode.AUTOMATIC)
        elif BUTTON_B in newly_pressed:
            mode = ControlMode.MANUAL
        elif BUTTON_Y in newly_pressed:
            mode = ControlMode.LEARNING

        if mode != previous_mode:
            print_mode(mode)
            if mode == ControlMode.AUTOMATIC:
                collision_avoidance.reset()
            elif mode == ControlMode.MANUAL:
                print("Use the D-pad to drive; releasing it stops the robot.")
            elif mode == ControlMode.PASSIVE_FREE:
                print("Motor torque disabled; wheels are completely free.")
            elif mode == ControlMode.PASSIVE_REALISTIC:
                print(
                    "Limited motor resistance enabled: "
                    f"{PASSIVE_REALISTIC_TORQUE:.3f} N.m per wheel."
                )
            if mode == ControlMode.LEARNING:
                print("Learning mode is reserved and keeps the motors stopped.")

        for wheel, max_torque in zip(wheels, wheel_max_torques):
            if mode == ControlMode.PASSIVE_FREE:
                available_torque = 0.0
            elif mode == ControlMode.PASSIVE_REALISTIC:
                available_torque = min(PASSIVE_REALISTIC_TORQUE, max_torque)
            else:
                available_torque = max_torque
            wheel.setAvailableTorque(available_torque)

        if mode == ControlMode.EMERGENCY_STOP:
            left_speed, right_speed = 0.0, 0.0
        elif mode == ControlMode.AUTOMATIC:
            left_speed, right_speed = collision_avoidance.step()
        elif mode == ControlMode.MANUAL:
            if connected:
                left_speed, right_speed = manual_dpad_drive(joystick)
            else:
                left_speed, right_speed = 0.0, 0.0
        elif mode in (
            ControlMode.PASSIVE_FREE,
            ControlMode.PASSIVE_REALISTIC,
        ):
            left_speed, right_speed = 0.0, 0.0
        else:  # ControlMode.LEARNING
            left_speed, right_speed = 0.0, 0.0

        set_side_velocities(wheels, left_speed, right_speed)
        experiment_state = experiment_monitor.update(
            robot.getTime(),
            gps.getValues(),
            accelerometer.getValues(),
            gyro.getValues(),
            (left_speed, right_speed),
        )
        send_telemetry(
            robot,
            proximity_sensors,
            wheels,
            accelerometer,
            gyro,
            gps,
            compass,
            experiment_state,
        )
        send_control_state(robot, joystick, mode, current_buttons)
        previous_buttons = current_buttons
        joystick_was_connected = connected


if __name__ == "__main__":
    main()
