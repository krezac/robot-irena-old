/*!
* \file RobbusShm.h
* \brief handling shared mamory
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*
*  Revision: 1.0
*  Date: 2009/10/30
*/

#ifndef ROBBUS_SHM_H
#define ROBBUS_SHM_H

#include <stdint.h>
#include <stdlib.h>

typedef enum {
	ROBBUS_SHM_INPUT_DATA = 0,
	ROBBUS_SHM_OUTPUT_DATA = 1,
	ROBBUS_SHM_GPS_DATA = 2
} RobbusShm_MemoryType_t;
int RobbusShm_Lock(RobbusShm_MemoryType_t memType);
int RobbusShm_Unlock(RobbusShm_MemoryType_t memType);
int RobbusShm_Create(size_t inDataSize, size_t outDataSize, size_t gpsDataSize);
int RobbusShm_Delete(void);
void* RobbusShm_GetPtr(RobbusShm_MemoryType_t memType); 
int RobbusShm_Read(RobbusShm_MemoryType_t memType, void* buffer, size_t offset, size_t size);
int RobbusShm_Write(RobbusShm_MemoryType_t memType, void* buffer, size_t offset, size_t size);

#endif
