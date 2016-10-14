//----- Include Files ---------------------------------------------------------
#include <avr/io.h>	// include I/O definitions (port names, pin names, etc)
#include <avr/interrupt.h>

#define CPU_FREQ 16000000L
#define HOST_BAUDRATE 115200
#define BUS_BAUDRATE 115200

#define BRIDGE_PING_BYTE 'R'
#define BRIDGE_START_BYTE 0x02

#define HOST_RX_BUFFER_SIZE 1024
#define HOST_TX_BUFFER_SIZE 1024

#define HOST_RX_READY 0
#define HOST_RX_WAIT_FOR_TYPE 1
#define HOST_RX_WAIT_FOR_SIZE_H 3
#define HOST_RX_WAIT_FOR_SIZE_L 4
#define HOST_RX_WAIT_FOR_DATA 5
#define HOST_RX_WAIT_FOR_CHECKSUM 6
#define HOST_RX_PROCESSING 7


#define BUS_RX_CONSUMING 0
#define BUS_RX_PROCESSING 1

#define BUS_TX_READY 0
#define BUS_TX_SENDING_ADDRESS 1
#define BUS_TX_SENDING_LENGTH 2
#define BUS_TX_SENDING_DATA 3
#define BUS_TX_SENDING_CHECKSUM 4


uint8_t hostRxBuffer[HOST_RX_BUFFER_SIZE];
uint8_t hostTxBuffer[HOST_TX_BUFFER_SIZE];

volatile uint8_t hostRxState = HOST_RX_READY;
volatile uint8_t hostRxPacketType = 0;
volatile uint16_t hostRxPacketSize = 0;

volatile uint16_t hostRxBytesReceived;

volatile uint8_t busRxState = BUS_RX_PROCESSING;

volatile uint8_t busTxState = BUS_TX_READY;
volatile uint8_t busTxPosition;

static void init(void)
{
	// Initialize UART:
	// enable USART module and USART interrupts 
	//UCSRB = _BV(RXCIE) | _BV(UDRIE) | _BV(RXEN) | _BV(TXEN);
	UCSR0B = _BV(RXCIE) | _BV(TXCIE) | _BV(RXEN) | _BV(TXEN);
	UCSR1B = _BV(RXCIE) | _BV(TXCIE) | _BV(RXEN) | _BV(TXEN);

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

void busSendNext(void) {
}

void busReceiveNext(uint8_t c) {
}

/// USART0 receive interrupt routine (receive from host)
ISR(USART0_RX_vect) {
	uint8_t c = UDR0;

	switch (hostRxState) {
		case HOST_RX_READY:
			if (c == BRIDGE_PING_BYTE) {
				UDR0 = BRIDGE_PING_BYTE; // ping
			} else if (c == BRIDGE_START_BYTE) { // start
				hostRxState = HOST_RX_WAIT_FOR_TYPE;
			}
			break;
		case HOST_RX_WAIT_FOR_TYPE:
			hostRxPacketType = c;
			hostRxState = HOST_RX_WAIT_FOR_SIZE_H;
			break;
		case HOST_RX_WAIT_FOR_SIZE_H:
			hostRxPacketSize = c;
			hostRxState = HOST_RX_WAIT_FOR_SIZE_L;
			break;
		case HOST_RX_WAIT_FOR_SIZE_L:
			hostRxPacketSize = (hostRxPacketSize << 8) + c;
			hostRxState = HOST_RX_WAIT_FOR_DATA;
			hostRxBytesReceived = 0;
			break;
		case HOST_RX_WAIT_FOR_DATA:
			hostRxBuffer[hostRxBytesReceived++] = c;
			if (hostRxBytesReceived == hostRxPacketSize) {
				hostRxState = HOST_RX_WAIT_FOR_CHECKSUM;
			}
			break;
		case HOST_RX_WAIT_FOR_CHECKSUM:
			// TODO
			hostRxState = HOST_RX_PROCESSING;
			break;
		default: // includes HOST_RX_PROCESSING, also acts as fallback
			if (c == BRIDGE_PING_BYTE) { // "reset" any time
				UDR0 = BRIDGE_PING_BYTE;
				hostRxState = HOST_RX_READY;
				busSendNext();
			}
			break;
	}
		
	UCSR1B &= ~_BV(RXEN); // disable receive
	UDR1 = UDR0;
}

/// USART0 transmit data register empty interrupt routine (send to host)
//ISR(USART0_UDRE_vect) {
ISR(USART0_TX_vect) {
}

/// USART1 receive interrupt routine (receive form bus)
ISR(USART1_RX_vect) {
	uint8_t c = UDR1;
	if (busRxState == BUS_RX_CONSUMING) {
		busRxState = BUS_RX_PROCESSING;
	} else {
		busReceiveNext(c);
	}
}

/// USART1 transmit data register empty interrupt routine (send to bus)
//ISR(USART1_UDRE_vect) {
ISR(USART1_TX_vect) {
	UCSR1B |= _BV(RXEN); // byte sent, reenable receive
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
