/*!
* \file swuart.c
* \brief software USART receiver
*
* uses Timer2
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2010/02/05
*/

#include <avr/io.h>
#include <avr/interrupt.h>

#include "swuart.h"

// UART receive pin defines
// This pin must correspond to the
// External Interrupt 0 (INT0) pin for your processor
#define UARTSW_RX_PORT			PORTD	///< UART Receive Port
#define UARTSW_RX_DDR			DDRD	///< UART Receive DDR
#define UARTSW_RX_PORTIN		PIND	///< UART Receive Port Input
#define UARTSW_RX_PIN			PD3	///< UART Receive Pin

// calculate division factor for requested baud rate, and set it
//UartswBaudRateDiv = (u08)(((F_CPU/256L)+(baudrate/2L))/(baudrate*1L));
#define BAUDRATE_DIV (uint8_t)(((ROBBUS_CPU_FREQ/64)+(ROBBUS_SWUART_BAUDRATE/2L))/(ROBBUS_SWUART_BAUDRATE*1L))

static PtrSwUartHandler_t g_handler;

// uartsw receive status and data variables
static volatile uint8_t UartswRxData;
static volatile uint8_t UartswRxBitNum;

static volatile uint8_t first = 1;

// TODO detect start and stop bit

void SwUart_Init(PtrSwUartHandler_t handler) {

	g_handler = handler;
	// initialize ports
	UARTSW_RX_DDR &= ~(1<<UARTSW_RX_PIN);
	UARTSW_RX_PORT &= ~(1<<UARTSW_RX_PIN);

	 // initialize timer 2
        TCNT2 = 0;
        TCCR2 = (1<<CS22); // normal mode 1:64 prescaler

	//PORTD |= (1<< PD2);
	// setup the receiver
	// OC2 interrupt disabled
	TIMSK &= ~(1<<OCIE2);
	// INT0 trigger on rising/falling edge
	MCUCR = (1<<ISC11);	// non-invert: falling edge
	// enable INT0 interrupt
	GICR |= (1<<INT1);
}

ISR(INT1_vect) {
	// this must be is a start bit
		
	// disable INT1 interrupt
	GICR &= ~(1<<INT1);
	// schedule data bit sampling 1.5 bit periods from now
	OCR2 = TCNT2 + BAUDRATE_DIV + BAUDRATE_DIV/2;
	// clear OC0 interrupt flag
	TIFR = (1<<OCF2);
	// enable OC0 interrupt
	TIMSK |= (1<<OCIE2);
	// reset bit counter
	UartswRxBitNum = 0;
	// reset data
	UartswRxData = 0;
}

ISR(TIMER2_COMP_vect) {
	// start bit has already been received
	// we're in the data bits
	
	// shift data byte to make room for new bit
	UartswRxData = UartswRxData>>1;

	// sample the data line
	if( (UARTSW_RX_PORTIN & (1<<UARTSW_RX_PIN)) ) // non-inverting
	{
		// serial line is marking
		// record '1' bit
		UartswRxData |= 0x80;
	}

	// increment bit counter
	UartswRxBitNum++;
	// schedule next bit sample
	OCR2 += BAUDRATE_DIV;

	// check if we have a full byte
	if(UartswRxBitNum >= 8)
	{
		// call handler
		g_handler(UartswRxData);
		// disable OC0 interrupt
		TIMSK &= ~(1<<OCIE2);
		// clear INT1 interrupt flag
		GIFR = (1<<INTF1);
		// enable INT interrupt
		GICR |= (1<<INT1);
	}
}

