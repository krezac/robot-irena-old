//----- Include Files ---------------------------------------------------------
#include <avr/io.h>	// include I/O definitions (port names, pin names, etc)
#include <avr/interrupt.h>

#include "tick0.h"
#include "robbus.h"
#include "swuart.h"
#include "i2c.h"
#include "nmea.h"

#define HEARTBEAT_LED_VALUE 0xff

static uint8_t outData[ROBBUS_OUTGOING_SIZE];
static volatile uint8_t g_beatCounter;

static uint8_t* messageHandler(uint8_t *inData) {
	PORTB ^= (1<<PB0);
	PORTB ^= (1<<PB1);
	g_beatCounter = HEARTBEAT_LED_VALUE;
	
	outData[0] = TimeTick0_Get();
	return outData;
}

void watchDogHandler(void) {
	// heart beat
	if (g_beatCounter > 0) {
		g_beatCounter--;
	} else {
		PORTB ^= (1<<PB0);
		PORTB ^= (1<<PB1);
		g_beatCounter = HEARTBEAT_LED_VALUE;
	}
}

static void charHandler(uint8_t c) {
	// TODO blikani
	if(Nmea_Add(c)) {
		PORTB &= ~(1<<PB2);
	} else {
		PORTB |= (1<<PB2);
	}
		
	PORTB ^= (1<<PB3);
}

static void init(void)
{
	TimeTick0_Init(watchDogHandler);
	SwUart_Init(charHandler);
	Robbus_Init(messageHandler);
	Nmea_Init(outData+3);
	I2c_Init(100);

	DDRB = 0xff;
	PORTB = 0xff;

	sei();
}

//----- Begin Code ------------------------------------------------------------


int main(void)
{
	init();

	uint8_t buffer[2];
	while(1) {
		asm volatile("wdr");
		buffer[0]=0x02; // azimuth low byte
		I2c_MasterSend(0xC0, 1, buffer);
		I2c_MasterReceive(0xC0, 2, buffer);
		cli();
		outData[1] = buffer[0];
		outData[2] = buffer[1];
	 	sei();	
	}

	return 0;
}
