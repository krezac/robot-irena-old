//----- Include Files ---------------------------------------------------------
#include <avr/io.h>	// include I/O definitions (port names, pin names, etc)
#include <avr/interrupt.h>

#include "adc.h"
#include "tick2.h"
#include "i2c.h"
#include "robbus.h"

#define INDEX_TIMESTAMP 0
#define INDEX_STATUS 1
#define INDEX_SONAR_LEFT 2
#define INDEX_SONAR_CENTER 4
#define INDEX_SONAR_RIGHT 6
#define INDEX_VSER 8

#define LIDAR_MOTOR_DDR DDRD
#define LIDAR_MOTOR_PORT PORTD
#define LIDAR_MOTOR_PIN PD6

#define RELAY_PORT PORTD
#define RELAY_DDR  DDRD
#define RELAY_PIN PD7

#define SERVO_RELAY_FLAG (1<<0)
#define LEFT_SONAR_FLAG (1<<1)
#define CENTER_SONAR_FLAG (1<<2)
#define RIGHT_SONAR_FLAG (1<<3)
#define LIDAR_MOTOR_FLAG (1<<4)

// timestamp
// status
// left sonar (2 bytes)
// right sonar (2 bytes)
static uint8_t outData[ROBBUS_OUTGOING_SIZE];
static volatile uint8_t g_watchDog;
static volatile uint8_t g_flags;
static volatile uint8_t g_ledTicks;

static uint8_t* messageHandler(uint8_t *inData) {
	PORTB ^= (1<<PB0);
	g_watchDog = inData[0];
	g_flags = inData[1];
	OCR1A = 247 + inData[2];
	OCR1B = 247 + inData[3];

	if ((g_watchDog > 0) && (g_flags & SERVO_RELAY_FLAG)) {
		RELAY_PORT |= (1<<RELAY_PIN); // enable motors
	} else {
		RELAY_PORT &= ~(1<<RELAY_PIN); // disable motors
	}

	outData[INDEX_TIMESTAMP] = TimeTick2_Get();

	if ((g_watchDog > 0) && (g_flags & LIDAR_MOTOR_FLAG))
		LIDAR_MOTOR_PORT |= (1<<LIDAR_MOTOR_PIN);
	else
		LIDAR_MOTOR_PORT &= ~(1<<LIDAR_MOTOR_PIN);

	return outData;
}

void watchDogHandler(void) {
	if (g_watchDog > 0) {
		g_watchDog--;
	} else {	// emergency stop
		RELAY_PORT &= ~(1<<RELAY_PIN);
		OCR1A = 247 + 128;
		OCR1B=247 + 128;
		LIDAR_MOTOR_PORT &= ~(1<<LIDAR_MOTOR_PIN);
	}

	if (g_ledTicks > 0) {
		g_ledTicks--;
	} else {
		PORTB ^= (1<<PB0);
		g_ledTicks = 0xff;
	}
		
}

uint8_t convertVoltage(uint16_t v) {
	return (uint8_t)((56 * v) / 100);
}

static void init(void)
{
	// initialize timestamping
	TimeTick2_Init(watchDogHandler);

	// initialize library units
	Robbus_Init(messageHandler);
	I2c_Init(100);

	Adc_Init();


	DDRB |=  (1<<PB0) | (1<<PB1) | (1<<PB2); // OC1A and OC!B as outputs

	RELAY_DDR |= (1<<RELAY_PIN);

	// initialize timer
	TCNT1 = 0; // clean timer
	ICR1  = 5000; // main period (50Hz)
	TCCR1A = (1<<COM1A1) | (1<<COM1B1) | (1<<WGM11); // fast pwm
	TCCR1B = (1<<WGM13)  | (1<<WGM12)  | (1<<CS11) | (1<<CS10) ; // prescaler to 1:64
	OCR1A = 247 + 128;
	OCR1B=247 + 128;

	// enable output for lidar motor
	LIDAR_MOTOR_DDR |= (1<<LIDAR_MOTOR_PIN);	

	// enable interrupts	
	sei();
}

void timerPause(uint8_t param) {
	volatile uint8_t i,j,k;
	for (i = 0; i < 255; i++)
		for (j = 0; j < 255; j++)
			for (k = 0; k < 2; k++);
}

//----- Begin Code ------------------------------------------------------------


int main(void)
{
	init();
	uint8_t buffer[2];
	uint8_t data[2];
	while(1) {
		// make all sonars fire
		buffer[0]=0x00; // cmd register
		buffer[1]=0x51; // range in cm
		if (g_flags & CENTER_SONAR_FLAG) {
			I2c_MasterSend(0xE0, 2, buffer); // center
		}

		if (g_flags & LEFT_SONAR_FLAG) {
			I2c_MasterSend(0xE2, 2, buffer); // left
		}

		if (g_flags & RIGHT_SONAR_FLAG) {
			I2c_MasterSend(0xE4, 2, buffer); // right
		}

		// wait for a while
		timerPause(100);

		// and read them
		buffer[0]=0x02; // range low byte

		// left
		if (g_flags & LEFT_SONAR_FLAG) {
			I2c_MasterSend(0xE2, 1, buffer);
			I2c_MasterReceive(0xE2, 2, data);
			cli();
			outData[INDEX_SONAR_LEFT] = data[0];
			outData[INDEX_SONAR_LEFT+1] = data[1];
			sei();
		} else {
			cli();
			outData[INDEX_SONAR_LEFT] = 0xff;
			outData[INDEX_SONAR_LEFT+1] = 0xff;
			sei();
		}

		// center
		if (g_flags & CENTER_SONAR_FLAG) {
			I2c_MasterSend(0xE0, 1, buffer);
			I2c_MasterReceive(0xE0, 2, data);
			cli();
			outData[INDEX_SONAR_CENTER] = data[0];
			outData[INDEX_SONAR_CENTER+1] = data[1];
			sei();
		} else {
			cli();
			outData[INDEX_SONAR_CENTER] = 0xff;
			outData[INDEX_SONAR_CENTER+1] = 0xff;
			sei();
		}

		// right
		if (g_flags & RIGHT_SONAR_FLAG) {
			I2c_MasterSend(0xE4, 1, buffer);
			I2c_MasterReceive(0xE4, 2, data);
			cli();
			outData[INDEX_SONAR_RIGHT] = data[0];
			outData[INDEX_SONAR_RIGHT+1] = data[1];
			sei();
		} else {
			cli();
			outData[INDEX_SONAR_RIGHT] = 0xff;
			outData[INDEX_SONAR_RIGHT+1] = 0xff;
			sei();
		}
		
		// voltage
		outData[INDEX_VSER] = convertVoltage(Adc_Get(0));
		
		// nothing to do in main loop
		asm volatile("wdr");
	}

	return 0;
}
