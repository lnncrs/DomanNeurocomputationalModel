from src.control import MotorActionMapper
from src.neural import MotorAction


def test_motor_mapper_groups_front_and_rear_axles():
    mapper = MotorActionMapper(speed=3.0)
    assert mapper.map(MotorAction.FRONT_CLOCKWISE).as_tuple() == (3.0, 3.0, 0.0, 0.0)
    assert mapper.map(MotorAction.FRONT_COUNTERCLOCKWISE).as_tuple() == (-3.0, -3.0, 0.0, 0.0)
    assert mapper.map(MotorAction.REAR_CLOCKWISE).as_tuple() == (0.0, 0.0, 3.0, 3.0)
    assert mapper.map(MotorAction.REAR_COUNTERCLOCKWISE).as_tuple() == (0.0, 0.0, -3.0, -3.0)


def test_physical_rotation_signs_can_be_calibrated_without_changing_network():
    mapper = MotorActionMapper(
        speed=2.0,
        front_clockwise_sign=-1.0,
        rear_clockwise_sign=1.0,
    )
    assert mapper.map(MotorAction.FRONT_CLOCKWISE).as_tuple() == (-2.0, -2.0, 0.0, 0.0)
    assert mapper.map(MotorAction.REAR_CLOCKWISE).as_tuple() == (0.0, 0.0, 2.0, 2.0)
