#include <webots/compass.h>
#include <webots/distance_sensor.h>
#include <webots/gps.h>
#include <webots/gyro.h>
#include <webots/motor.h>
#include <webots/robot.h>

#define TIME_STEP 64
#define MAX_SPEED 4.0
#define TURN_SPEED 2.5
#define PROXIMITY_THRESHOLD 200.0

int main(int argc, char **argv) {
  wb_robot_init();

  WbDeviceTag left_motor = wb_robot_get_device("left_motor");
  WbDeviceTag right_motor = wb_robot_get_device("right_motor");
  wb_motor_set_position(left_motor, INFINITY);
  wb_motor_set_position(right_motor, INFINITY);
  wb_motor_set_velocity(left_motor, 0.0);
  wb_motor_set_velocity(right_motor, 0.0);

  WbDeviceTag ps_front = wb_robot_get_device("ps_front");
  WbDeviceTag ps_back = wb_robot_get_device("ps_back");
  WbDeviceTag ps_left = wb_robot_get_device("ps_left");
  WbDeviceTag ps_right = wb_robot_get_device("ps_right");
  wb_distance_sensor_enable(ps_front, TIME_STEP);
  wb_distance_sensor_enable(ps_back, TIME_STEP);
  wb_distance_sensor_enable(ps_left, TIME_STEP);
  wb_distance_sensor_enable(ps_right, TIME_STEP);

  WbDeviceTag gyro = wb_robot_get_device("gyro");
  WbDeviceTag gps = wb_robot_get_device("gps");
  WbDeviceTag compass = wb_robot_get_device("compass");
  wb_gyro_enable(gyro, TIME_STEP);
  wb_gps_enable(gps, TIME_STEP);
  wb_compass_enable(compass, TIME_STEP);

  while (wb_robot_step(TIME_STEP) != -1) {
    const double front = wb_distance_sensor_get_value(ps_front);
    const double back = wb_distance_sensor_get_value(ps_back);
    const double left = wb_distance_sensor_get_value(ps_left);
    const double right = wb_distance_sensor_get_value(ps_right);

    double left_speed = MAX_SPEED;
    double right_speed = MAX_SPEED;

    if (front > PROXIMITY_THRESHOLD || right > PROXIMITY_THRESHOLD) {
      left_speed = -TURN_SPEED;
      right_speed = TURN_SPEED;
    } else if (left > PROXIMITY_THRESHOLD) {
      left_speed = TURN_SPEED;
      right_speed = -TURN_SPEED;
    } else if (back > PROXIMITY_THRESHOLD) {
      left_speed = MAX_SPEED;
      right_speed = MAX_SPEED;
    }

    wb_motor_set_velocity(left_motor, left_speed);
    wb_motor_set_velocity(right_motor, right_speed);
  }

  wb_robot_cleanup();
  return 0;
}
