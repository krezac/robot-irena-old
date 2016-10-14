/*!
* \file tick0.c
* \brief timestaping the packets from timer0
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2009/12/22
*/

#include <avr/io.h>
#include <avr/interrupt.h>

#include "tick0.h"

static volatile uint8_t g_timeTicks;
PtrTimeTick0Handler_t g_handler;

void TimeTick0_Init(PtrTimeTick0Handler_t handler) {
	g_handler = handler; // register handler (i.e. for watchdog)
	// initialize timer 0
	TCNT0 = 0;
	TCCR0 = (1<<CS02); // normal mode 1:256 prescaler
	TIMSK |= (1<<TOIE0); // enable interrupt
}

ISR(TIMER0_OVF_vect) {
 	g_timeTicks++;
	
	if (g_handler) {
		g_handler();
	}
}

uint8_t TimeTick0_Get(void) {
	return g_timeTicks;
}

