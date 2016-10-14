/*!
* \file adc.c
* \brief analog to digital converter code
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2010/02/14
*/

#include <avr/io.h>
#include <avr/interrupt.h>

#include "tick0.h"

void Adc_Init(void) {
	ADMUX = (1<<REFS0) |	// AVCC as reference
		(1<< ADLAR);	// output value alignment

	ADCSRA = (1<<ADEN) |
		 (1<<ADPS2)|(1<<ADPS1); // 1:64 prescaler
}

uint8_t Adc_Get(uint8_t channel) {

	// set mux
	ADMUX = (1<<REFS0) |	// AVCC as reference
		(1<< ADLAR)|	// output value alignment
		(channel & 0x07);

	ADCSRA |= (1<<ADIF); // clear flag
	ADCSRA |= (1<<ADSC); // start conversion

	while (!(ADCSRA & (1<<ADIF))); // wait for confersion complete

	return ADCH;
}

