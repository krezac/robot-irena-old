/*!
* \file RobbusComm.h
* \brief handling serial comm
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*
*  Revision: 1.0
*  Date: 2009/10/30
*/

#ifndef ROBBUS_COMM_H
#define ROBBUS_COMM_H

#include <stdint.h>
#include <stdlib.h>

#define ROBBUS_DEFAULT_DEVICE "/dev/robbus"
#define ROBBUS_TAG_SERVICE 1
#define ROBBUS_TAG_REGULAR 2
#define ROBBUS_TAG_GROUP 3

// error codes
#define RBC_SUCCESS 0
#define RBC_TIMEOUT -1
#define RBC_TAG -2
#define RBC_ADDRESS -3
#define RBC_LENGTH -4
#define RBC_CHECKSUM -5
#define RBC_HANDLE -6

int RobbusComm_Create(const char *deviceName);
int RobbusComm_Close(void);
int RobbusComm_SendData(uint8_t tag, uint8_t address, const uint8_t* data, uint8_t size);
int RobbusComm_ReceiveData(uint8_t tag, uint8_t address, uint8_t* data, uint8_t size);
#endif
