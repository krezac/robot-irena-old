/*!
* \file SerialApi.h
* \brief generic serial port interface
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*
*  Revision: 1.0
*  Date: 2009/10/30
*/

#ifndef SERIAL_API_H
#define SERIAL_API_H

#include <stdint.h>
#include <stdlib.h>

int SerialApi_Init(const char *deviceName);
int SerialApi_Close(void);
int SerialApi_SendByte(uint8_t c);
int SerialApi_ReceiveByte(void);

#endif
