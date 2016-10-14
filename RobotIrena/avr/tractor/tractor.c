//----- Include Files ---------------------------------------------------------
#include <avr/io.h>	// include I/O definitions (port names, pin names, etc)
#include <avr/interrupt.h>

#include "adc.h"
#include "tick2.h"
#include "i2c.h"
#include "robbus.h"

#define INDEX_TIMESTAMP 0
#define INDEX_STATUS 1
#define INDEX_ODOMETRY 2
#define INDEX_SONAR_REAR 4
#define INDEX_VLOG 6
#define INDEX_VMOT 7
#define INDEX_AMOT 8

#define RELAY_PORT PORTD
#define RELAY_DDR  DDRD
#define RELAY_PIN  PD7

#define EMERGENCY_PORT PORTD
#define EMERGENCY_PINS PIND
#define START_PIN  PD5
#define EMERGENCY_PIN  PD6

#define MOTOR_RELAY_FLAG (1<<0)
#define REAR_SONAR_FLAG (1<<1)

// status
// odo (2 bytes)
// sonar (2 bytes)
// vlog
// vmot
// amot
static uint8_t outData[ROBBUS_OUTGOING_SIZE];
static volatile uint8_t g_watchDog;
static volatile uint8_t g_flags;
static volatile uint8_t g_ledTicks;
static uint8_t g_currentCenter = 128;
static volatile uint16_t g_odometry = 0;

ISR(INT0_vect) {
	if (PIND & (1<<PD3)) {
		g_odometry++;
	} else {
		g_odometry--;
	}
}

static uint8_t* messageHandler(uint8_t *inData) {
	PORTB ^= (1<<PB0);
	g_watchDog = inData[0];
	g_flags = inData[1];
	OCR1A = 247 + inData[2];
	OCR1B = 247 + inData[3];

	if ((g_watchDog > 0) && (g_flags & MOTOR_RELAY_FLAG)) {
		RELAY_PORT |= (1<<RELAY_PIN); // enable motors
	} else {
		RELAY_PORT &= ~(1<<RELAY_PIN); // disable motors
	}

	outData[INDEX_TIMESTAMP] = TimeTick2_Get();
	outData[INDEX_STATUS] = EMERGENCY_PINS;
	outData[INDEX_ODOMETRY] = (uint8_t)(g_odometry>>8);
	outData[INDEX_ODOMETRY+1] = (uint8_t)g_odometry;
	return outData;
}

void watchDogHandler(void) {
	if (g_watchDog > 0) {
		g_watchDog--;
	} else {	// emergency stop
		RELAY_PORT &= ~(1<<RELAY_PIN);
		OCR1A = 247 + 128;
		OCR1B=247 + 128;
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

uint8_t convertCurrent(uint16_t c) {
	if (c > g_currentCenter) {
		c = c - g_currentCenter;
	} else {
		c = g_currentCenter - c;
	}

	return (uint8_t)((c * 500) / 128);
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
	EMERGENCY_PORT |= (1<<START_PIN); // pull-up

	RELAY_DDR |= (1<<RELAY_PIN);

	// initialize timer
	TCNT1 = 0; // clean timer
	ICR1  = 5000; // main period (50Hz)
	TCCR1A = (1<<COM1A1) | (1<<COM1B1) | (1<<WGM11); // fast pwm
	TCCR1B = (1<<WGM13)  | (1<<WGM12)  | (1<<CS11) | (1<<CS10) ; // prescaler to 1:64
	OCR1A = 247 + 128;
	OCR1B=247 + 128;

	MCUCR |= (1<<ISC01) | (1<<ISC00); // int0 rising edge
	GICR |= (1<<INT0); 

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

	while(1) 
	{
		// make sonar fire
		buffer[0]=0x00; // cmd register
		buffer[1]=0x51; // range in cm
		if (g_flags & REAR_SONAR_FLAG) {
			buffer[0]=0x00; // cmd register
			buffer[1]=0x51; // range in cm
			I2c_MasterSend(0xE0, 2, buffer); // center
		}
		// wait for a while, measure in the meantime
		uint8_t i;
		outData[INDEX_VLOG] = convertVoltage(Adc_Get(0));
		outData[INDEX_VMOT] = convertVoltage(Adc_Get(1));
		outData[INDEX_AMOT] = convertCurrent(Adc_Get(2));
		asm volatile("wdr");

		// read rear sonar
		if (g_flags & REAR_SONAR_FLAG) {
			timerPause(100);
			buffer[0]=0x02; // range low byte
			I2c_MasterSend(0xE0, 1, buffer);
			I2c_MasterReceive(0xE0, 2, data);
			cli();
			outData[INDEX_SONAR_REAR] = data[0];
			outData[INDEX_SONAR_REAR+1] = data[1];
			sei();
		} else {
			cli();
			outData[INDEX_SONAR_REAR] = 0xff;
			outData[INDEX_SONAR_REAR+1] = 0xff;
			sei();
		}
		asm volatile("wdr");
	}

	return 0;
}
