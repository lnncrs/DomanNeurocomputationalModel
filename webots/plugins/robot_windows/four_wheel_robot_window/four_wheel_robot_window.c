#include <webots/accelerometer.h>
#include <webots/compass.h>
#include <webots/distance_sensor.h>
#include <webots/gps.h>
#include <webots/gyro.h>
#include <webots/motor.h>
#include <webots/plugins/robot_window/robot_wwi.h>
#include <webots/robot.h>

#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#define DISTANCE_SENSOR_COUNT 6
#define MOTOR_COUNT 4
#define TELEMETRY_PERIOD_MS 100

static const char *distance_sensor_names[DISTANCE_SENSOR_COUNT] = {
    "ds_left", "ds_right", "ps_front", "ps_back", "ps_left", "ps_right"};
static const char *motor_names[MOTOR_COUNT] = {"wheel1", "wheel2", "wheel3", "wheel4"};

static WbDeviceTag distance_sensors[DISTANCE_SENSOR_COUNT];
static WbDeviceTag motors[MOTOR_COUNT];
static WbDeviceTag accelerometer;
static WbDeviceTag gyro;
static WbDeviceTag gps;
static WbDeviceTag compass;
static bool stop_motors = false;
static int elapsed_ms = 0;

static double finite_or_zero(double value)
{
  return isfinite(value) ? value : 0.0;
}

static void enable_devices()
{
  const int sampling_period = (int)wb_robot_get_basic_time_step();

  for (int i = 0; i < DISTANCE_SENSOR_COUNT; ++i)
  {
    distance_sensors[i] = wb_robot_get_device(distance_sensor_names[i]);
    if (distance_sensors[i])
      wb_distance_sensor_enable(distance_sensors[i], sampling_period);
  }

  for (int i = 0; i < MOTOR_COUNT; ++i)
    motors[i] = wb_robot_get_device(motor_names[i]);

  accelerometer = wb_robot_get_device("accelerometer");
  gyro = wb_robot_get_device("gyro");
  gps = wb_robot_get_device("gps");
  compass = wb_robot_get_device("compass");

  if (accelerometer)
    wb_accelerometer_enable(accelerometer, sampling_period);
  if (gyro)
    wb_gyro_enable(gyro, sampling_period);
  if (gps)
    wb_gps_enable(gps, sampling_period);
  if (compass)
    wb_compass_enable(compass, sampling_period);
}

void wb_robot_window_init()
{
  enable_devices();
}

static void receive_commands()
{
  const char *message;
  while ((message = wb_robot_wwi_receive_text()))
  {
    if (strcmp(message, "stop motors") == 0)
      stop_motors = true;
    else if (strcmp(message, "release motors") == 0)
      stop_motors = false;
    else
      fprintf(stderr, "Unknown robot window message: '%s'\n", message);
  }
}

static void apply_motor_override()
{
  if (!stop_motors)
    return;

  for (int i = 0; i < MOTOR_COUNT; ++i)
  {
    if (motors[i])
      wb_motor_set_velocity(motors[i], 0.0);
  }
}

static void send_telemetry()
{
  double distance[DISTANCE_SENSOR_COUNT] = {0};
  double velocity[MOTOR_COUNT] = {0};
  double acceleration[3] = {0};
  double angular_velocity[3] = {0};
  double position[3] = {0};
  double north[3] = {0};

  for (int i = 0; i < DISTANCE_SENSOR_COUNT; ++i)
  {
    if (distance_sensors[i])
      distance[i] = finite_or_zero(wb_distance_sensor_get_value(distance_sensors[i]));
  }
  for (int i = 0; i < MOTOR_COUNT; ++i)
  {
    if (motors[i])
      velocity[i] = finite_or_zero(wb_motor_get_velocity(motors[i]));
  }

  const double *values;
  if (accelerometer && (values = wb_accelerometer_get_values(accelerometer)))
  {
    for (int i = 0; i < 3; ++i)
      acceleration[i] = finite_or_zero(values[i]);
  }
  if (gyro && (values = wb_gyro_get_values(gyro)))
  {
    for (int i = 0; i < 3; ++i)
      angular_velocity[i] = finite_or_zero(values[i]);
  }
  if (gps && (values = wb_gps_get_values(gps)))
  {
    for (int i = 0; i < 3; ++i)
      position[i] = finite_or_zero(values[i]);
  }
  if (compass && (values = wb_compass_get_values(compass)))
  {
    for (int i = 0; i < 3; ++i)
      north[i] = finite_or_zero(values[i]);
  }

  char message[2048];
  snprintf(
      message, sizeof(message),
      "{\"type\":\"telemetry\",\"time\":%.3f,\"stopped\":%s,"
      "\"distance\":{\"ds_left\":%.6g,\"ds_right\":%.6g,\"ps_front\":%.6g,"
      "\"ps_back\":%.6g,\"ps_left\":%.6g,\"ps_right\":%.6g},"
      "\"motors\":[%.6g,%.6g,%.6g,%.6g],"
      "\"accelerometer\":[%.6g,%.6g,%.6g],\"gyro\":[%.6g,%.6g,%.6g],"
      "\"gps\":[%.6g,%.6g,%.6g],\"compass\":[%.6g,%.6g,%.6g]}",
      wb_robot_get_time(), stop_motors ? "true" : "false",
      distance[0], distance[1], distance[2], distance[3], distance[4], distance[5],
      velocity[0], velocity[1], velocity[2], velocity[3],
      acceleration[0], acceleration[1], acceleration[2],
      angular_velocity[0], angular_velocity[1], angular_velocity[2],
      position[0], position[1], position[2], north[0], north[1], north[2]);
  wb_robot_wwi_send_text(message);
}

void wb_robot_window_step(int time_step)
{
  receive_commands();
  apply_motor_override();

  elapsed_ms += time_step;
  if (elapsed_ms >= TELEMETRY_PERIOD_MS)
  {
    elapsed_ms = 0;
    send_telemetry();
  }
}

void wb_robot_window_cleanup()
{
}
