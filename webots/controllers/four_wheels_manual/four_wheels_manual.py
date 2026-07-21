"""Controller multimodo do FourWheelRobot.

O modo automático reproduz o controller C de anti-colisão. Quando um
joystick está conectado, os botões selecionam controle manual, automático,
aprendizado (reservado) ou parada de emergência.
"""

from enum import Enum, auto

from controller import Robot


TIME_STEP = 64
MAX_SPEED = 10.0
TURN_LEFT_SPEED = 1.0
TURN_RIGHT_SPEED = -1.0
PROXIMITY_THRESHOLD = 950.0
AVOIDANCE_STEPS = 100
JOYSTICK_DEAD_ZONE = 0.12
JOYSTICK_AXIS_MAX = 32767.0

DISTANCE_SENSOR_NAMES = ("ds_left", "ds_right")
WHEEL_NAMES = ("wheel1", "wheel2", "wheel3", "wheel4")

# Mapeamento observado no controle "Controller (Xbox One For Windows)"
# conectado via USB. O console continua imprimindo os índices para diagnóstico.
BUTTON_LB = 4
BUTTON_RB = 5
BUTTON_START = 0
BUTTON_A = 8
BUTTON_B = 9
BUTTON_X = 10
BUTTON_Y = 11

# Mapeamento observado no driver atual:
# - D-pad vertical/horizontal: eixos 0/1
# - analógico esquerdo: eixos 2/3
AXIS_DPAD_Y = 0
AXIS_DPAD_X = 1
AXIS_LEFT_X = 2
AXIS_LEFT_Y = 3


class ControlMode(Enum):
    AUTOMATIC = auto()
    MANUAL = auto()
    LEARNING = auto()
    EMERGENCY_STOP = auto()


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def normalize_axis(raw_value: float, center: float = 0.0) -> float:
    delta = raw_value - center
    available_range = (
        JOYSTICK_AXIS_MAX - center if delta >= 0 else center + 32768.0
    )
    if available_range <= 0:
        return 0.0

    value = clamp(delta / available_range, -1.0, 1.0)
    magnitude = abs(value)
    if magnitude <= JOYSTICK_DEAD_ZONE:
        return 0.0

    scaled = (magnitude - JOYSTICK_DEAD_ZONE) / (1.0 - JOYSTICK_DEAD_ZONE)
    return scaled if value > 0 else -scaled


def read_pressed_buttons(joystick) -> set[int]:
    buttons: set[int] = set()
    button = joystick.getPressedButton()
    while button >= 0:
        buttons.add(button)
        button = joystick.getPressedButton()
    return buttons


def manual_arcade_drive(
    joystick, axis_centers: list[float] | None = None
) -> tuple[float, float]:
    axis_centers = axis_centers or []

    def center_for(axis: int) -> float:
        return axis_centers[axis] if axis < len(axis_centers) else 0.0

    if joystick.getNumberOfAxes() <= max(AXIS_LEFT_X, AXIS_LEFT_Y):
        steering = 0.0
        throttle = 0.0
    else:
        steering = normalize_axis(
            joystick.getAxisValue(AXIS_LEFT_X), center_for(AXIS_LEFT_X)
        )
        throttle = -normalize_axis(
            joystick.getAxisValue(AXIS_LEFT_Y), center_for(AXIS_LEFT_Y)
        )

    # Neste driver, o D-pad também aparece nos eixos 0/1. Ele assume o comando
    # quando o analógico esquerdo estiver neutro.
    if (
        steering == 0.0
        and throttle == 0.0
        and joystick.getNumberOfAxes() > max(AXIS_DPAD_X, AXIS_DPAD_Y)
    ):
        steering = normalize_axis(
            joystick.getAxisValue(AXIS_DPAD_X), center_for(AXIS_DPAD_X)
        )
        throttle = -normalize_axis(
            joystick.getAxisValue(AXIS_DPAD_Y), center_for(AXIS_DPAD_Y)
        )

    # Alguns drivers expõem o D-pad somente como POV; essa leitura permanece
    # como fallback quando nenhum dos eixos anteriores estiver ativo.
    if steering == 0.0 and throttle == 0.0 and joystick.getNumberOfPovs() > 0:
        pov = joystick.getPovValue(0)
        pov_commands = {
            0: (1.0, 0.0),
            45: (1.0, 1.0),
            90: (0.0, 1.0),
            135: (-1.0, 1.0),
            180: (-1.0, 0.0),
            225: (-1.0, -1.0),
            270: (0.0, -1.0),
            315: (1.0, -1.0),
        }
        throttle, steering = pov_commands.get(pov, (0.0, 0.0))

    left = throttle + steering
    right = throttle - steering

    # Preserva a proporção do comando ao saturar uma das laterais.
    largest = max(1.0, abs(left), abs(right))
    return left / largest * MAX_SPEED, right / largest * MAX_SPEED


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

    distance_sensors = [robot.getDevice(name) for name in DISTANCE_SENSOR_NAMES]
    for sensor in distance_sensors:
        sensor.enable(TIME_STEP)

    wheels = [robot.getDevice(name) for name in WHEEL_NAMES]
    for wheel in wheels:
        wheel.setPosition(float("inf"))
        wheel.setVelocity(0.0)

    joystick = robot.getJoystick()
    joystick.enable(TIME_STEP)

    collision_avoidance = CollisionAvoidance(distance_sensors)
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

        # Y tem prioridade e trava a parada. START é a única liberação.
        if BUTTON_Y in newly_pressed:
            mode = ControlMode.EMERGENCY_STOP
        elif mode == ControlMode.EMERGENCY_STOP:
            if BUTTON_START in newly_pressed:
                mode = ControlMode.AUTOMATIC
        elif BUTTON_A in newly_pressed:
            mode = ControlMode.AUTOMATIC
        elif BUTTON_B in newly_pressed:
            mode = ControlMode.MANUAL
        elif BUTTON_X in newly_pressed:
            mode = ControlMode.LEARNING

        if mode != previous_mode:
            print_mode(mode)
            if mode == ControlMode.AUTOMATIC:
                collision_avoidance.reset()
            elif mode == ControlMode.MANUAL:
                print("Hold RB and use the left stick or D-pad to drive.")
            if mode == ControlMode.LEARNING:
                print("Learning mode is reserved and keeps the motors stopped.")

        if mode == ControlMode.EMERGENCY_STOP:
            left_speed, right_speed = 0.0, 0.0
        elif mode == ControlMode.AUTOMATIC:
            left_speed, right_speed = collision_avoidance.step()
        elif mode == ControlMode.MANUAL:
            if connected and BUTTON_RB in current_buttons:
                left_speed, right_speed = manual_arcade_drive(
                    joystick, axis_centers
                )
            else:
                # Deadman switch: sem RB ou sem conexão, o robô permanece parado.
                left_speed, right_speed = 0.0, 0.0
        else:  # ControlMode.LEARNING
            left_speed, right_speed = 0.0, 0.0

        set_side_velocities(wheels, left_speed, right_speed)
        previous_buttons = current_buttons
        joystick_was_connected = connected


if __name__ == "__main__":
    main()
