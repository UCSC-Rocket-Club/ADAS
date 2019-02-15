/**
 * <rc/motor.h>
 *
 * @brief      Control our ADAS motor
 *
 * This code modifies the origional motor.c code for the robot
 * control library. Adapted for our purposes. Adapted to use the
 * MD10S motor driver board interface.
 *
 *
 * TODO: change the motor pin definitions to match the gpio pins we need
 *
 * @author     James Strawson
 * @date       1/31/2018
 *
 * @addtogroup Motor
 * @{
 */

#ifndef ADAS_MOTOR_H
#define ADAS_MOTOR_H

#ifdef __cplusplus
extern "C" {
#endif

#define ADAS_MOTOR_DEFAULT_PWM_FREQ	25000	///< 25kHz


// reverse on time in microseconds to stop motor on a dime
#define BACK_FORCE_TIME 50

/**
 * @brief      Initializes pins for motors and leaves motor in free spin state
 *
 *
 * This starts the motor drivers at RC_MOTOR_DEFAULT_PWM_FREQ. To use another
 * frequency initialize with rc_motor_init_freq instead.
 *
 * @return     0 on success, -1 on failure which is usually due to lack of user
 * permissions to access the gpio and pwm systems.
 */
int adas_motor_init(void);


/**
 * @brief      Just like adas_motor_init but allows the user to set the pwm
 * frequency
 *
 * adas_MOTOR_DEFAULT_PWM_FREQ is a good frequency to start at.
 *
 * The pwm is not set up yet but am leaving this here in case we get around to it
 *
 * @param[in]  pwm_frequency_hz  The pwm frequency in hz
 *
 * @return     0 on success, -1 on failure which is usually due to lack of user
 * permissions to access the gpio and pwm systems.
 */
int adas_motor_init_freq(int pwm_frequency_hz);


/**
 * @brief     Closes all file pointers to GPIO and PWM and puts motor in free spin state
 * systems.
 *
 * @return     0 on success, -1 on failure.
 */
int adas_motor_cleanup(void);


/**
 * @brief      Sets motor to a direction. Currently only spins at full speed
 * in a single direction. The duty is restricted to a value between -1.0 and 1.0 for now.
 * Speed and direction is encoded in a single double. Negative is clockwise and pos is counter clockwise
 *
 * @param[in]  duty  Duty cycle, -1.0 for full reverse, 1.0 for full forward
 *
 * @return     0 on success, -1 on failure
 */
int adas_motor_set(double duty);


/**
 * @brief      Puts motor into a zero-throttle state allowing it to spin
 * freely. Due to gear ratio of our motor this also locks it into place.
 * However if the motor is spinning the intertia carries it a bit. To stop
* motor on a dime call adas_motor_brake()
 *
 * This is accomplished by putting both motor terminals connected to the
 * h-bridge into a high-impedance state.
 *
 * @return     0 on success, -1 on failure
 */
int adas_motor_free_spin();


/**
 * @brief      Pulses the motor in the opposite direction to stop it on a dime.
 * The length of back pulse is defined in microseconds in BACK_FORCE_TIME at top.
 * Puts motor in free spin after pulse. Effectively locks motor.
 *
 * @param[in]  direction    The current direction and speed of the motor. Will stop this direction
 *
 * @return     0 on success, -1 on failure
 */
int adas_motor_brake();



#ifdef __cplusplus
}
#endif

#endif // adas_MOTOR_H

/** @} end group Motor */
