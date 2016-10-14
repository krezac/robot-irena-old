//----- Include Files ---------------------------------------------------------
#include <avr/io.h>	// include I/O definitions (port names, pin names, etc)
#include <avr/interrupt.h>

#define CPU_FREQ 16000000L
#define HOST_BAUDRATE 115200
#define BUS_BAUDRATE 115200

volatile uint8_t bytesToConsume = 0;

void Usart0_Init(void) {
}

static void init(void)
{
	Usart0_Init();
	// Initialize UART:
	// enable USART module and USART interrupts 
	//UCSRB = _BV(RXCIE) | _BV(UDRIE) | _BV(RXEN) | _BV(TXEN);
	UCSR0B = _BV(RXCIE) | _BV(RXEN) | _BV(TXEN);
	UCSR1B = _BV(RXCIE) | _BV(RXEN) | _BV(TXEN);

	// set baudrate
	uint16_t busBaudrate = ((CPU_FREQ+(BUS_BAUDRATE*8L))/(BUS_BAUDRATE*16L)-1);
	uint16_t hostBaudrate = ((CPU_FREQ+(HOST_BAUDRATE*8L))/(HOST_BAUDRATE*16L)-1);
	
	UBRR0L = hostBaudrate;
	#ifdef UBRR0H
	UBRR0H = hostBaudrate >> 8;
	#endif
	
	UBRR1L = busBaudrate;
	#ifdef UBRR1H
	UBRR1H = busBaudrate >> 8;
	#endif

	sei();
}

/// USART0 receive interrupt routine
ISR(USART0_RX_vect) {
		
	UDR1 = UDR0;
	bytesToConsume++;
}

/// USART1 receive interrupt routine
ISR(USART1_RX_vect) {
	uint8_t c = UDR1;
	if (bytesToConsume > 0) {
		bytesToConsume--;
	} else {
		UDR0 = c;
	}
}

//----- Begin Code ------------------------------------------------------------


int main(void)
{
	init();
	while(1) {
		asm volatile("wdr");
	}

	return 0;
}
