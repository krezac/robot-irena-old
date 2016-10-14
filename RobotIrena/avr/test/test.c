//----- Include Files ---------------------------------------------------------
#include <avr/io.h>	// include I/O definitions (port names, pin names, etc)
#include <avr/interrupt.h>

#include "tick2.h"
#include "robbus.h"

#define HEARTBEAT_LED_VALUE 0xff

static uint8_t outData[ROBBUS_OUTGOING_SIZE];
static volatile uint8_t g_watchDog;
static volatile uint8_t g_beatCounter;

static uint8_t* messageHandler(uint8_t *inData) {
	PORTB ^= (1<<PB0);
	g_beatCounter = HEARTBEAT_LED_VALUE;
	
	outData[0] = TimeTick2_Get();
	outData[1] = PINC;
	g_watchDog = 0xff;// reset watchdog
	return outData;
}

void watchDogHandler(void) {
	// heart beat
	if (g_beatCounter > 0) {
		g_beatCounter--;
	} else {
		PORTB ^= (1<<PB0);
		g_beatCounter = HEARTBEAT_LED_VALUE;
	}

	if (g_watchDog > 0) {
		g_watchDog--;
	} else {	// emergency stop
	}
}

static void init(void)
{
	TimeTick2_Init(watchDogHandler);
	// initialize library units
	Robbus_Init(messageHandler);

	DDRB = 0xff;
	PORTB = 0xff;
	PORTC = 0xff;

	sei();
}

//----- Begin Code ------------------------------------------------------------


int main(void)
{
	init();

	while(1) 
	{
		// nothing to do in main loop
		asm volatile("wdr");
	}

	return 0;
}
