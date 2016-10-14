/*!
* \file SerialCommLinux.cpp
* \brief implementation for Linux
*
* \author md -at- robotika.cz, jiri.isa -at- matfyz.cz
*
*  URL: http://robotika.cz/
*  
*  Revision: 1.2
*  Date: 2005/11/01
*/

//#define _POSIX_SOURCE 1 /* POSIX compliant source */

#include <termios.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
//#include <sys/stat.h>
//#include <string.h>

#include "RobbusComm.h"
#include "SerialApi.h"

/* baudrate settings are defined in <asm/termbits.h>, which is
included by <termios.h> */
/* change this definition for the correct port */

//because we want to forbidd IUCLC (mapping to lower case) where it could happen and ignore the option otherwise (it is not defined by POSIX)
#ifndef IUCLC
#define IUCLC 0
#endif /*IUCLC*/

int RobbusComm_Create(const char *deviceName) {

	return SerialApi_Init(deviceName);
}

///////////////////////////////////////////////////////////
/*!
* Destructor
*/
int RobbusComm_Close(void) {
	return SerialApi_Close();
}

///////////////////////////////////////////////////////////
/*!
* \brief send single byte
*
* \param a_toSend byte to send
*/
int RobbusComm_SendByte(uint8_t c, uint8_t *checkSum)
{
	SerialApi_SendByte(c);
	SerialApi_ReceiveByte(); // TODO: consume sent byte

	if (checkSum != NULL)
		*checkSum += c;

	return RBC_SUCCESS;
}

int RobbusComm_SendByteWrapped(uint8_t c, uint8_t *checkSum)
{
	if (c < 4) {
		RobbusComm_SendByte(0, NULL);
		RobbusComm_SendByte(c+4, NULL);
	} else {
		RobbusComm_SendByte(c, NULL);
	}
	
	if (checkSum != NULL)
		*checkSum += c;

	return RBC_SUCCESS;
}

int RobbusComm_ReceiveByte(void)
{
  return SerialApi_ReceiveByte();
 
}

int RobbusComm_ReceiveByteWrapped(void) {
	int c = RobbusComm_ReceiveByte();
	if (c < 0) return c;
	if (c >= 4) return c;

	c = RobbusComm_ReceiveByte();
	if (c < 0) return c;
	return c - 4;
}

int RobbusComm_SendData(uint8_t tag, uint8_t address, const uint8_t* data, uint8_t size) {
	uint8_t i, checkSum = 0;
	
	//printf("Sending %d byte(s) to node %d with tag %d: ", size, address, tag);
	//for (i = 0; i < size; i++)
	//	printf("%02x", data[i]);
	//printf("\n");

	// TODO: flush serial buffer
	RobbusComm_SendByte(tag, NULL);
	RobbusComm_SendByte(address, &checkSum);
	RobbusComm_SendByteWrapped(size, &checkSum);
	
	// data
	for (i = 0; i < size; i++) {
		RobbusComm_SendByteWrapped(data[i], &checkSum);
	}
	RobbusComm_SendByteWrapped((~checkSum)+1, NULL);

	return RBC_SUCCESS;
}


int RobbusComm_ReceiveData(uint8_t tag, uint8_t address, uint8_t* data, uint8_t size) {
	int c;
	uint8_t i, packetSize, checkSum = 0;

	// tag
	c = RobbusComm_ReceiveByte();	
	if (c < 0) return c;
	if (c != tag) {
		// printf("Got tag %d instead of %d\n", c, tag);
		return RBC_TAG;
	}
	
	// address TODO: manage group
	c = RobbusComm_ReceiveByte();	
	if (c < 0) return c;
	if (((c&0x80) == 0) || ((c^0x80) != address)) return RBC_ADDRESS;
	checkSum += (uint8_t)c;
	
	// length
	c = RobbusComm_ReceiveByteWrapped();	
	if (c < 0) return c;
	packetSize = (uint8_t)c;
	checkSum += packetSize;

	for (i = 0; i < packetSize; i++) {
		c = RobbusComm_ReceiveByteWrapped();	
		if (c < 0) return c;
		data[i] = (uint8_t)c;
		checkSum += (uint8_t)c;
	}
	
	// checksum
	c = RobbusComm_ReceiveByteWrapped();	
	if (c < 0) return c;
	checkSum += (uint8_t)c;

	if (checkSum != 0) return RBC_CHECKSUM;
	
	//printf("Received %d byte(s) from node %d with tag %d: ", size, address, tag);
	//for (c = 0; c < size; c++)
	//	printf("%02x", data[c]);
	//printf("\n");
	
return RBC_SUCCESS;

}
