"""Controller multimodo do FourWheelRobot.

O modo automático reproduz o controller C de anti-colisão. Quando um
joystick está conectado, os botões selecionam controle manual, automático,
aprendizado (reservado) ou parada de emergência.
"""

from enum import Enum, auto
import json
import sys

from controller import Robot


TIME_STEP = 64
MAX_SPEED = 10.0
TURN_LEFT_SPEED = 1.0
TURN_RIGHT_SPEED = -1.0
PROXIMITY_THRESHOLD = 950.0
AVOIDANCE_STEPS = 100
DPAD_AXIS_THRESHOLD = 16000

DISTANCE_SENSOR_NAMES = ("ds_left", "ds_right")
WHEEL_NAMES = ("wheel1", "wheel2", "wheel3", "wheel4")

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
    LEARNING = auto()
    EMERGENCY_STOP = auto()


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
    mode = (
        ControlMode.MANUAL
        if "--manual" in sys.argv[1:]
        else ControlMode.AUTOMATIC
    )
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
                print("Use the D-pad to drive; releasing it stops the robot.")
            if mode == ControlMode.LEARNING:
                print("Learning mode is reserved and keeps the motors stopped.")

        if mode == ControlMode.EMERGENCY_STOP:
            left_speed, right_speed = 0.0, 0.0
        elif mode == ControlMode.AUTOMATIC:
            left_speed, right_speed = collision_avoidance.step()
        elif mode == ControlMode.MANUAL:
            if connected:
                left_speed, right_speed = manual_dpad_drive(joystick)
            else:
                left_speed, right_speed = 0.0, 0.0
        else:  # ControlMode.LEARNING
            left_speed, right_speed = 0.0, 0.0

        set_side_velocities(wheels, left_speed, right_speed)
        send_control_state(robot, joystick, mode, current_buttons)
        previous_buttons = current_buttons
        joystick_was_connected = connected


if __name__ == "__main__":
    main()
