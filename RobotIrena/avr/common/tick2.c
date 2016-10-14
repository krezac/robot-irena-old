/*!
* \file tick2.c
* \brief timestaping the packets from timer2
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2009/12/22
*/

#include <avr/io.h>
#include <avr/interrupt.h>

#include "tick2.h"

static volatile uint8_t g_timeTicks;
PtrTimeTick2Handler_t g_handler;

void TimeTick2_Init(PtrTimeTick2Handler_t handler) {
	g_handler = handler; // register handler (i.e. for watchdog)
	// initialize timer 2
	TCNT2 = 0;
	TCCR2 = (1<<CS22) | (1<<CS21); // normal mode 1:256 prescaler
	TIMSK |= (1<<TOIE2); // enable interrupt
}

ISR(TIMER2_OVF_vect) {
 	g_timeTicks++;
	
	if (g_handler) {
		g_handler();
	}
}

uint8_t TimeTick2_Get(void) {
	return g_timeTicks;
}

