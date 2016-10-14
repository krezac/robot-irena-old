/*! \file i2c.c \brief I2C interface using AVR Two-Wire Interface (TWI) hardware. */
//*****************************************************************************
//
// File Name	: 'i2c.c'
// Title		: I2C interface using AVR Two-Wire Interface (TWI) hardware
// Author		: Pascal Stang - Copyright (C) 2002-2003
// Created		: 2002.06.25
// Revised		: 2003.03.02
// Version		: 0.9
// Target MCU	: Atmel AVR series
// Editor Tabs	: 4
//
// This code is distributed under the GNU Public License
//		which can be found at http://www.gnu.org/licenses/gpl.txt
//
//*****************************************************************************

#include <avr/io.h>
// OBSOLETE #include <avr/signal.h>
#include <avr/interrupt.h>

#include "robbus_config.h"
#include "i2c.h"

#define I2C_SEND_DATA_BUFFER_SIZE		0x05
#define I2C_RECEIVE_DATA_BUFFER_SIZE	0x05

// TWSR values (not bits)
// (taken from avr-libc twi.h - thank you Marek Michalkiewicz)
// Master
#define TW_START					0x08
#define TW_REP_START				0x10
// Master Transmitter
#define TW_MT_SLA_ACK				0x18
#define TW_MT_SLA_NACK				0x20
#define TW_MT_DATA_ACK				0x28
#define TW_MT_DATA_NACK				0x30
#define TW_MT_ARB_LOST				0x38
// Master Receiver
#define TW_MR_ARB_LOST				0x38
#define TW_MR_SLA_ACK				0x40
#define TW_MR_SLA_NACK				0x48
#define TW_MR_DATA_ACK				0x50
#define TW_MR_DATA_NACK				0x58
// Slave Transmitter
#define TW_ST_SLA_ACK				0xA8
#define TW_ST_ARB_LOST_SLA_ACK		0xB0
#define TW_ST_DATA_ACK				0xB8
#define TW_ST_DATA_NACK				0xC0
#define TW_ST_LAST_DATA				0xC8
// Slave Receiver
#define TW_SR_SLA_ACK				0x60
#define TW_SR_ARB_LOST_SLA_ACK		0x68
#define TW_SR_GCALL_ACK				0x70
#define TW_SR_ARB_LOST_GCALL_ACK	0x78
#define TW_SR_DATA_ACK				0x80
#define TW_SR_DATA_NACK				0x88
#define TW_SR_GCALL_DATA_ACK		0x90
#define TW_SR_GCALL_DATA_NACK		0x98
#define TW_SR_STOP					0xA0
// Misc
#define TW_NO_INFO					0xF8
#define TW_BUS_ERROR				0x00

// defines and constants
#define TWCR_CMD_MASK		0x0F
#define TWSR_STATUS_MASK	0xF8

// return values
#define I2C_OK				0x00
#define I2C_ERROR_NODEV		0x01

// types
typedef enum
{
	I2C_IDLE = 0, I2C_BUSY = 1,
	I2C_MASTER_TX = 2, I2C_MASTER_RX = 3,
	I2C_SLAVE_TX = 4, I2C_SLAVE_RX = 5
} eI2cStateType;



#define BV(x) (1<<x)

// Standard I2C bit rates are:
// 100KHz for slow speed
// 400KHz for high speed

//#define I2C_DEBUG

// I2C state and address variables
static volatile eI2cStateType I2cState;
static uint8_t I2cDeviceAddrRW;
// send/transmit buffer (outgoing data)
static uint8_t I2cSendData[I2C_SEND_DATA_BUFFER_SIZE];
static uint8_t I2cSendDataIndex;
static uint8_t I2cSendDataLength;
// receive buffer (incoming data)
static uint8_t I2cReceiveData[I2C_RECEIVE_DATA_BUFFER_SIZE];
static uint8_t I2cReceiveDataIndex;
static uint8_t I2cReceiveDataLength;

// forward declarations
//! Set the I2C transaction bitrate (in KHz)
void I2c_SetBitrate(uint16_t bitrateKHz);

// Low-level I2C transaction commands 
//! Send an I2C start condition in Master mode
void i2cSendStart(void);
//! Send an I2C stop condition in Master mode
void i2cSendStop(void);
//! Send an (address|R/W) combination or a data byte over I2C
void i2cSendByte(uint8_t data);
//! Receive a data byte over I2C  
// ackFlag = TRUE if recevied data should be ACK'ed
// ackFlag = FALSE if recevied data should be NACK'ed
void i2cReceiveByte(uint8_t ackFlag);




// functions
void I2c_Init(uint16_t bitrateKHz)
{
	// set pull-up resistors on I2C bus pins
	// TODO: should #ifdef these
	// PORTC |= (1<<PC4) | (1<<PC5);	// i2c SCL and SDA pull-ups

	// set i2c bit rate to 100KHz
	I2c_SetBitrate(bitrateKHz);
	// enable TWI (two-wire interface)
	TWCR |= (1<<TWEN);
	// set state
	I2cState = I2C_IDLE;
	// enable TWI interrupt and slave address ACK
	TWCR |= (1<<TWIE);
	TWCR |= (1<<TWEA);
	//outb(TWCR, (inb(TWCR)&TWCR_CMD_MASK)|BV(TWINT)|BV(TWEA));
}

void I2c_SetBitrate(uint16_t bitrateKHz)
{
	uint8_t bitrate_div;
	// set i2c bitrate
	// SCL freq = F_CPU/(16+2*TWBR))
	#ifdef TWPS0
		// for processors with additional bitrate division (mega128)
		// SCL freq = F_CPU/(16+2*TWBR*4^TWPS)
		// set TWPS to zero
		TWSR &= ~(1<<TWPS0);
		TWSR &= ~(1<<TWPS1);
	#endif
	// calculate bitrate division	
	bitrate_div = ((ROBBUS_CPU_FREQ/1000l)/bitrateKHz);
	if(bitrate_div >= 16)
		bitrate_div = (bitrate_div-16)/2;
	TWBR = bitrate_div;
}

inline void i2cSendStart(void)
{
	// send start condition
	TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT)|BV(TWSTA);
}

inline void i2cSendStop(void)
{
	// transmit stop condition
	// leave with TWEA on for slave receiving
	TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT)|BV(TWEA)|BV(TWSTO);
}

inline void i2cSendByte(uint8_t data)
{
	// save data to the TWDR
	TWDR = data;
	// begin send
	TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT);
}

inline void i2cReceiveByte(uint8_t ackFlag)
{
	// begin receive over i2c
	if( ackFlag )
	{
		// ackFlag = TRUE: ACK the recevied data
		TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT)|BV(TWEA);
	}
	else
	{
		// ackFlag = FALSE: NACK the recevied data
		TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT);
	}
}

void I2c_MasterSend(uint8_t deviceAddr, uint8_t length, uint8_t* data)
{
	uint8_t i;
	// wait for interface to be ready
	while(I2cState);
	// set state
	I2cState = I2C_MASTER_TX;
	// save data
	I2cDeviceAddrRW = (deviceAddr & 0xFE);	// RW cleared: write operation
	for(i=0; i<length; i++)
		I2cSendData[i] = *data++;
	I2cSendDataIndex = 0;
	I2cSendDataLength = length;
	// send start condition
	i2cSendStart();
}

void I2c_MasterReceive(uint8_t deviceAddr, uint8_t length, uint8_t* data)
{
	uint8_t i;
	// wait for interface to be ready
	while(I2cState);
	// set state
	I2cState = I2C_MASTER_RX;
	// save data
	I2cDeviceAddrRW = (deviceAddr|0x01);	// RW set: read operation
	I2cReceiveDataIndex = 0;
	I2cReceiveDataLength = length;
	// send start condition
	i2cSendStart();
	// wait for data
	while(I2cState);
	// return data
	for(i=0; i<length; i++)
		*data++ = I2cReceiveData[i];
}

//! I2C (TWI) interrupt service routine
ISR(TWI_vect)
{
	// read status bits
	uint8_t status = TWSR & TWSR_STATUS_MASK;

	switch(status)
	{
	// Master General
	case TW_START:						// 0x08: Sent start condition
	case TW_REP_START:					// 0x10: Sent repeated start condition
		// send device address
		i2cSendByte(I2cDeviceAddrRW);
		break;
	
	// Master Transmitter & Receiver status codes
	case TW_MT_SLA_ACK:					// 0x18: Slave address acknowledged
	case TW_MT_DATA_ACK:				// 0x28: Data acknowledged
		if(I2cSendDataIndex < I2cSendDataLength)
		{
			// send data
			i2cSendByte( I2cSendData[I2cSendDataIndex++] );
		}
		else
		{
			// transmit stop condition, enable SLA ACK
			i2cSendStop();
			// set state
			I2cState = I2C_IDLE;
		}
		break;
	case TW_MR_DATA_NACK:				// 0x58: Data received, NACK reply issued
		// store final received data byte
		I2cReceiveData[I2cReceiveDataIndex++] = TWDR;
		// continue to transmit STOP condition
	case TW_MR_SLA_NACK:				// 0x48: Slave address not acknowledged
	case TW_MT_SLA_NACK:				// 0x20: Slave address not acknowledged
	case TW_MT_DATA_NACK:				// 0x30: Data not acknowledged
		// transmit stop condition, enable SLA ACK
		i2cSendStop();
		// set state
		I2cState = I2C_IDLE;
		break;
	case TW_MT_ARB_LOST:				// 0x38: Bus arbitration lost
	//case TW_MR_ARB_LOST:				// 0x38: Bus arbitration lost
		// release bus
		TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT);
		// set state
		I2cState = I2C_IDLE;
		// release bus and transmit start when bus is free
		//outb(TWCR, (inb(TWCR)&TWCR_CMD_MASK)|BV(TWINT)|BV(TWSTA));
		break;
	case TW_MR_DATA_ACK:				// 0x50: Data acknowledged
		// store received data byte
		I2cReceiveData[I2cReceiveDataIndex++] = TWDR;
		// fall-through to see if more bytes will be received
	case TW_MR_SLA_ACK:					// 0x40: Slave address acknowledged
		if(I2cReceiveDataIndex < (I2cReceiveDataLength-1))
			// data byte will be received, reply with ACK (more bytes in transfer)
			i2cReceiveByte(1);
		else
			// data byte will be received, reply with NACK (final byte in transfer)
			i2cReceiveByte(0);
		break;

	// Slave Receiver status codes
	case TW_SR_SLA_ACK:					// 0x60: own SLA+W has been received, ACK has been returned
	case TW_SR_ARB_LOST_SLA_ACK:		// 0x68: own SLA+W has been received, ACK has been returned
	case TW_SR_GCALL_ACK:				// 0x70:     GCA+W has been received, ACK has been returned
	case TW_SR_ARB_LOST_GCALL_ACK:		// 0x78:     GCA+W has been received, ACK has been returned
		// we are being addressed as slave for writing (data will be received from master)
		// set state
		I2cState = I2C_SLAVE_RX;
		// prepare buffer
		I2cReceiveDataIndex = 0;
		// receive data byte and return ACK
		TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT)|BV(TWEA);
		break;
	case TW_SR_DATA_ACK:				// 0x80: data byte has been received, ACK has been returned
	case TW_SR_GCALL_DATA_ACK:			// 0x90: data byte has been received, ACK has been returned
		// get previously received data byte
		I2cReceiveData[I2cReceiveDataIndex++] = TWDR;
		// check receive buffer status
		if(I2cReceiveDataIndex < I2C_RECEIVE_DATA_BUFFER_SIZE)
		{
			// receive data byte and return ACK
			i2cReceiveByte(1);
			//outb(TWCR, (inb(TWCR)&TWCR_CMD_MASK)|BV(TWINT)|BV(TWEA));
		}
		else
		{
			// receive data byte and return NACK
			i2cReceiveByte(0);
			//outb(TWCR, (inb(TWCR)&TWCR_CMD_MASK)|BV(TWINT));
		}
		break;
	case TW_SR_DATA_NACK:				// 0x88: data byte has been received, NACK has been returned
	case TW_SR_GCALL_DATA_NACK:			// 0x98: data byte has been received, NACK has been returned
		// receive data byte and return NACK
		i2cReceiveByte(0);
		//outb(TWCR, (inb(TWCR)&TWCR_CMD_MASK)|BV(TWINT));
		break;
	case TW_SR_STOP:					// 0xA0: STOP or REPEATED START has been received while addressed as slave
		// switch to SR mode with SLA ACK
		TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT)|BV(TWEA);
		// i2c receive is complete, call i2cSlaveReceive
		//if(i2cSlaveReceive) i2cSlaveReceive(I2cReceiveDataIndex, I2cReceiveData);
		// set state
		I2cState = I2C_IDLE;
		break;

	// Slave Transmitter
	case TW_ST_SLA_ACK:					// 0xA8: own SLA+R has been received, ACK has been returned
	case TW_ST_ARB_LOST_SLA_ACK:		// 0xB0:     GCA+R has been received, ACK has been returned
		// we are being addressed as slave for reading (data must be transmitted back to master)
		// set state
		I2cState = I2C_SLAVE_TX;
		// request data from application
		//if(i2cSlaveTransmit) I2cSendDataLength = i2cSlaveTransmit(I2C_SEND_DATA_BUFFER_SIZE, I2cSendData);
		// reset data index
		I2cSendDataIndex = 0;
		// fall-through to transmit first data byte
	case TW_ST_DATA_ACK:				// 0xB8: data byte has been transmitted, ACK has been received
		// transmit data byte
		TWDR = I2cSendData[I2cSendDataIndex++];
		if(I2cSendDataIndex < I2cSendDataLength)
			// expect ACK to data byte
			TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT)|BV(TWEA);
		else
			// expect NACK to data byte
			TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT);
		break;
	case TW_ST_DATA_NACK:				// 0xC0: data byte has been transmitted, NACK has been received
	case TW_ST_LAST_DATA:				// 0xC8:
		// all done
		// switch to open slave
		TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT)|BV(TWEA);
		// set state
		I2cState = I2C_IDLE;
		break;

	// Misc
	case TW_NO_INFO:					// 0xF8: No relevant state information
		// do nothing
		break;
	case TW_BUS_ERROR:					// 0x00: Bus error due to illegal start or stop condition
		// reset internal hardware and release bus
		TWCR = (TWCR&TWCR_CMD_MASK)|BV(TWINT)|BV(TWSTO)|BV(TWEA);
		// set state
		I2cState = I2C_IDLE;
		break;
	}
}

