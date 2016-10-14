/*!
* \file robbus.c
* \brief Robbus command processing state machine
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2009/10/30
*/

#include <avr/io.h>
#include <avr/eeprom.h>
#include <avr/interrupt.h>

#include <string.h>

#include "robbus.h"

// packet start definitions
#define SERVICE_PACKET_HEAD 0x01
#define REGULAR_PACKET_HEAD 0x02
#define GROUP_PACKET_HEAD 0x03

#define SUBPACKET_ECHO 'e'
#define SUBPACKET_DESCRIPTION 'd'
#define SUBPACKET_CHANGE_ADDRESS 'a'
// message processing machine state
 enum RxStateEnum  {
	RX_STATE_READY = 0x01,

	// group stuff
	RX_STATE_WAIT_FOR_GROUP_ADDRESS,
	RX_STATE_WAIT_FOR_GROUP_MASK,

	// regular usage
	RX_STATE_WAIT_FOR_ADDRESS,
	RX_STATE_WAIT_FOR_LENGTH,
	RX_STATE_WAIT_FOR_DATA,
	RX_STATE_WAIT_FOR_CHECKSUM
};

enum TxStateEnum  {
	TX_STATE_READY = 0x10,
	TX_STATE_SEND_ADDRESS,
	TX_STATE_SEND_LENGTH,
	TX_STATE_SEND_DATA,
};

#define RX_STATE_MASK 0x0f
#define TX_STATE_MASK 0xf0

//#define changeRxState(newState) robbusState=(robbusState&TX_STATE_MASK)|newState
//#define changeTxState(newState) robbusState=(robbusState&RX_STATE_MASK)|newState

//#define getRxState() (robbusState&RX_STATE_MASK)
//#define getTxState() (robbusState&TX_STATE_MASK)

#define changeRxState(newState) rxState=newState
#define changeTxState(newState) txState=newState

#define getRxState() rxState
#define getTxState() txState

// packet special character prefix and shift
#define SPECIAL_CHAR_PREFIX 0x00
#define SPECIAL_CHAR_SHIFT 0x04

// max character being prefixed
#define SPECIAL_CHAR_MAX GROUP_PACKET_HEAD

// value added to the address while composing the reply	
#define ADDRESS_REPLY_MASK 0x80

// flags used during processing
#define RX_FLAG_SPECIAL_CHAR		0x01
#define RX_FLAG_SERVICE_PACKET 		0x02
#define RX_FLAG_GROUP_PACKET		0x04
#define TX_FLAG_SPECIAL_CHAR		0x10

#define getFlag(flag)   (robbusFlags&flag)
#define setFlag(flag)   (robbusFlags|=flag)
#define clearFlag(flag) (robbusFlags&=~flag)

// command handler function type definition and variable
static PtrFuncPtr_t commandHandler;

static volatile uint8_t txSpecial;
static volatile uint8_t rxState, txState;
//static volatile uint8_t robbusState;	//! state of the processing state machine (lower nibble rx, upper tx)
static volatile uint8_t robbusFlags;	//! various flags used during processing (see ROBBUS_FLAG_ defines)

static volatile uint8_t payloadLength;
static volatile uint8_t checkSum;
static volatile uint8_t deviceAddress;
static volatile uint8_t receivedAddress;


// data buffers
#define ROBBUS_MIN_BUFFER_SIZE 4
#define RX_SIZE (ROBBUS_INCOMMING_SIZE>ROBBUS_MIN_BUFFER_SIZE?ROBBUS_INCOMMING_SIZE:ROBBUS_MIN_BUFFER_SIZE)
#define TX_SIZE (ROBBUS_OUTGOING_SIZE)
#define USART_BUFFER_SIZE (RX_SIZE>TX_SIZE?RX_SIZE:TX_SIZE)
static uint8_t usartBuffer[USART_BUFFER_SIZE];

// working positions in the buffers
static uint8_t volatile usartBufferIndex;

// forward declarations
uint8_t doServiceCommand(void);

#define checkSumInit() checkSum = 0
#define checkSumAdd(data) checkSum += data;

/// return value 1 means switch to next state
static uint8_t sendWrapped(uint8_t c)
{
	if (c > SPECIAL_CHAR_MAX) {
		UDR = c;
	} else {
		if (getFlag(TX_FLAG_SPECIAL_CHAR)) {
			UDR = c + SPECIAL_CHAR_SHIFT;
			clearFlag(TX_FLAG_SPECIAL_CHAR);
		} else {
			UDR = SPECIAL_CHAR_PREFIX;
			setFlag(TX_FLAG_SPECIAL_CHAR);
			return 0;
		}
	}
	checkSumAdd(c);
	return 1;
}

//! initialize FSM
void Robbus_Init(PtrFuncPtr_t cmdHandler) {
	// Initialize UART:
	// enable USART module and USART interrupts 
	//UCSRB = _BV(RXCIE) | _BV(UDRIE) | _BV(RXEN) | _BV(TXEN);
	UCSRB = _BV(RXCIE) | _BV(TXCIE) | _BV(RXEN) | _BV(TXEN);

	// set baudrate
	uint16_t baudrate = ((ROBBUS_CPU_FREQ+(ROBBUS_BAUDRATE*8L))/(ROBBUS_BAUDRATE*16L)-1);
	UBRRL = baudrate;
	#ifdef UBRRH
	UBRRH = baudrate >> 8;
	#endif

	// initialize state machine
	changeRxState(RX_STATE_READY);
	changeTxState(TX_STATE_READY);

	robbusFlags = 0;

	// set initial device address
	deviceAddress = ROBBUS_INITIAL_ADDRESS;
	// read address from eeprom
	if (eeprom_read_byte((uint8_t*)ROBBUS_EEPROM_DATA_ADDRESS) == 'R') {
		deviceAddress = eeprom_read_byte((uint8_t*)(ROBBUS_EEPROM_DATA_ADDRESS+1)); 
	}

	// initialize buffer indices
	usartBufferIndex = 0;

	// register application command handler
	commandHandler = cmdHandler;
}


/// USART receive interrupt routine
ISR(USART_RXC_vect) {
	// read byte from USART register
	uint8_t data = UDR;

	// special characters handling
	if (data == SERVICE_PACKET_HEAD) {			// service packet
		robbusFlags = (robbusFlags & TX_STATE_MASK) | RX_FLAG_SERVICE_PACKET;	// set flag
		changeRxState(RX_STATE_WAIT_FOR_ADDRESS);	// and process as regular
		return;						// and leave processing
	} else if (data == GROUP_PACKET_HEAD) {			// group packet (will contain mask byte)
		robbusFlags = (robbusFlags & TX_STATE_MASK) | RX_FLAG_GROUP_PACKET;	// set flag
		changeRxState(RX_STATE_WAIT_FOR_GROUP_ADDRESS);	// and wait for composite address (address-mask)
		return;						// and leave processing
	} else if (data == REGULAR_PACKET_HEAD) {		// regular packet
		robbusFlags &= TX_STATE_MASK;			// clear flags
		changeRxState(RX_STATE_WAIT_FOR_ADDRESS);	// and wait for the address
		return;						// and leave processing
	} else if (data == SPECIAL_CHAR_PREFIX) {		// special character received, set flag, do not change state
		setFlag(RX_FLAG_SPECIAL_CHAR);			// only set flag
		return;						// and leave processing
	}

	if (getFlag(RX_FLAG_SPECIAL_CHAR)) {			// previous was special character
		clearFlag(RX_FLAG_SPECIAL_CHAR);		// clear the flag
		data -= SPECIAL_CHAR_SHIFT;			// and correct data byte value
	}

	switch (getRxState()) {
		// group sequence	
		case RX_STATE_WAIT_FOR_GROUP_ADDRESS:
			if (data & ADDRESS_REPLY_MASK) {
				changeRxState(RX_STATE_READY); // reply from someone (even me ;), ignore rest of packet
			} else {
				receivedAddress = data;
				checkSumInit();
				checkSumAdd(data);
				changeRxState(RX_STATE_WAIT_FOR_GROUP_MASK);
			}
			break;

		case RX_STATE_WAIT_FOR_GROUP_MASK:
			if ((data & receivedAddress) != (data & deviceAddress)) {
				changeRxState(RX_STATE_READY); // reply from someone, ignore rest of packet
			} else {
				receivedAddress = data;
				checkSumAdd(data);
				changeRxState(RX_STATE_WAIT_FOR_LENGTH);
			}
			break;
		
		// regulsr sequence	
		case RX_STATE_WAIT_FOR_ADDRESS:
			if (data & ADDRESS_REPLY_MASK || data != deviceAddress) {
				changeRxState(RX_STATE_READY); // reply from someone, or for another one ignore rest of packet
			} else {
				checkSumInit();
				checkSumAdd(data);
				changeRxState(RX_STATE_WAIT_FOR_LENGTH);
			}
			break;
		case RX_STATE_WAIT_FOR_LENGTH:
			checkSumAdd(data);
			payloadLength = data; // ommit the opcode
			usartBufferIndex = 0;
			changeRxState(RX_STATE_WAIT_FOR_DATA);
			break;

		case RX_STATE_WAIT_FOR_DATA:
			if (usartBufferIndex < USART_BUFFER_SIZE) {
				usartBuffer[usartBufferIndex] = data;
				checkSum += data;
				usartBufferIndex++;
			}
			
			if (usartBufferIndex == payloadLength) {
				changeRxState(RX_STATE_WAIT_FOR_CHECKSUM);
			}	
			break;

		case RX_STATE_WAIT_FOR_CHECKSUM:
			
			if (((uint8_t)(data + checkSum)) == 0) {
				// checksum ok, do action
				if (getFlag(RX_FLAG_SERVICE_PACKET)) {
					// process service packet
					if(!doServiceCommand()) {
						changeRxState(RX_STATE_READY);
						return;
					}
				} else {
					uint8_t i;
					// process regular packet
					uint8_t* replyData = commandHandler(usartBuffer);

					// copy user data to uart buffer
					for (i = 0; i < ROBBUS_OUTGOING_SIZE; i++)
						usartBuffer[i] = replyData[i];
					
					payloadLength = ROBBUS_OUTGOING_SIZE;
				}
				
				// if not group packet, send reply
				if (!(getFlag(RX_FLAG_GROUP_PACKET)))
				{
					// initialize checksum
					checkSumInit();

					// set tx machine state
					changeTxState(TX_STATE_SEND_ADDRESS);
					clearFlag(TX_FLAG_SPECIAL_CHAR);

					// and push first byte into usart register
					UDR = getFlag(RX_FLAG_SERVICE_PACKET) ? SERVICE_PACKET_HEAD : REGULAR_PACKET_HEAD;
				}
			}
			changeRxState(RX_STATE_READY);
			break;

		default:
			// should never happen ;-)
			changeRxState(RX_STATE_READY);
		break;
	}
}

/// USART transmit data register empty interrupt routine
//ISR(USART_UDRE_vect) {
ISR(USART_TXC_vect) {
	switch(getTxState()) {
		case TX_STATE_READY:	// falback, someone canceled transmitting, so do not continue
			return;	
		case TX_STATE_SEND_ADDRESS:
			sendWrapped(deviceAddress | ADDRESS_REPLY_MASK); // no need to check the special characters
			changeTxState(TX_STATE_SEND_LENGTH);
			break;
		case TX_STATE_SEND_LENGTH:
			if (sendWrapped(payloadLength))
			{
				usartBufferIndex = 0;
				changeTxState(TX_STATE_SEND_DATA);
			}
			break;
		case TX_STATE_SEND_DATA:
			if (usartBufferIndex < payloadLength) {
				if (sendWrapped(usartBuffer[usartBufferIndex]))
					usartBufferIndex++;
			} else { // checksum
				if (sendWrapped(-checkSum))
					changeTxState(TX_STATE_READY);
			}
			break;
		default:
			UDR = 'e';
			changeTxState(TX_STATE_READY);
	}
}

uint8_t doServiceCommand(void) {
	uint8_t newAddress;
	switch (usartBuffer[0])
	{
		case SUBPACKET_DESCRIPTION:
			usartBuffer[0] = ROBBUS_INCOMMING_SIZE;
			usartBuffer[1] = ROBBUS_OUTGOING_SIZE;
			payloadLength = 2;
			return 1;
		case SUBPACKET_ECHO:
			return 1;
		case SUBPACKET_CHANGE_ADDRESS:
			newAddress = usartBuffer[1];
			if (usartBuffer[2] != deviceAddress || usartBuffer[3] != (deviceAddress ^ newAddress))
				return 0;
			eeprom_write_byte((uint8_t*)(ROBBUS_EEPROM_DATA_ADDRESS+0), 'R'); 
			eeprom_write_byte((uint8_t*)(ROBBUS_EEPROM_DATA_ADDRESS+1), newAddress); 
			//deviceAddress = newAddress;	
			payloadLength = 2;
			return 1;
		default:
			return 0;
	}
}

