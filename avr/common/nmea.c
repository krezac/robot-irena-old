/*!
* \file RobbusMaster.c
* \brief Robbus command processing state machine
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*
*  Revision: 1.0
*  Date: 2009/10/30
*/

#include <stdio.h>
#include <string.h>

#define NMEA_BUFFER_LENGTH 80
uint8_t g_nmeaBuffer[NMEA_BUFFER_LENGTH+1]; // for final '\0'
uint8_t g_bufferPos;
uint8_t *g_targetBuffer;

void Nmea_Init(uint8_t *target) {
	g_targetBuffer = target;
	g_bufferPos = 0;
	g_nmeaBuffer[NMEA_BUFFER_LENGTH] = '\0';
}

uint8_t byteToNumber(uint8_t c) {
	if (c >= '0' && c <= '9')
		return c - '0';
	else if (c >= 'a' && c <= 'f')
		return c - 'a' + 10;
	else if (c >= 'A' && c <= 'F')
		return c - 'A' + 10;
	else 
		return 0;		
}

void write32(uint8_t *buf, int32_t value) {
	int8_t i;
	for (i = 3; i >= 0; i--) { 
		
		*(buf+i) = value & 0x000000ff;
		value = value >> 8;
	}
}

uint8_t Nmea_ValidateChecksum(void) {
	uint8_t i = 1;
	uint8_t sum = 0;

	while (i < g_bufferPos && g_nmeaBuffer[i] != '*') {
		sum ^= g_nmeaBuffer[i++];
	}
	
	if (i != (g_bufferPos - 3)) {
		return 0;	// no checksum found
	}

	uint8_t check = byteToNumber(g_nmeaBuffer[g_bufferPos-2]);
	check <<= 4;
	check += byteToNumber(g_nmeaBuffer[g_bufferPos-1]);
	return check == sum;
}

uint8_t Nmea_FindIndex(uint8_t startPos, uint8_t index) {

	while(startPos < g_bufferPos) {
		if (index == 0) {
			return startPos;
		}

		if (g_nmeaBuffer[startPos] == ',') {
			index--;
		}
		startPos++;
	}

	return g_bufferPos;
}

uint32_t Nmea_ReadNumber(uint8_t pos) {
	uint32_t value = 0;
	
	while(pos < g_bufferPos && g_nmeaBuffer[pos] != ',') {
		if (g_nmeaBuffer[pos] != '.') {
			value = 10*value + byteToNumber(g_nmeaBuffer[pos]);
		}
		pos++;
	}

	return value;
}

uint8_t Nmea_Parse(void) {
	if (g_bufferPos == 0) {
		return 0;	// empty buffer
	}

	if (g_nmeaBuffer[0] != '$') {
		return 0;	// wrong start byte
	}

	if (!Nmea_ValidateChecksum()) {
		return 0;
	}

	char *ptr = (char*)g_nmeaBuffer + 3;
	if (strncmp(ptr, "GGA", 3) == 0) {
		uint8_t valid = Nmea_ReadNumber(Nmea_FindIndex(0, 6)) == 1;
		uint32_t value;

		// read latitude
		if (valid) {
			 value = Nmea_ReadNumber(Nmea_FindIndex(0, 2));
			if (g_nmeaBuffer[Nmea_FindIndex(0, 3)] == 'S') {
				value += 0x80000000;
			}
		} else {
			value = 0x7fffffff;
		}

		write32(g_targetBuffer, value);

		// read longitude
		if (valid) {
			 value = Nmea_ReadNumber(Nmea_FindIndex(0, 4));
			if (g_nmeaBuffer[Nmea_FindIndex(0, 5)] == 'W') {
				value += 0x80000000;
			}
		} else {
			value = 0x7fffffff;
		}
		
		write32(g_targetBuffer + 4, value);
		
		// read dop
		if (valid) {	
			value = Nmea_ReadNumber(Nmea_FindIndex(0, 8));
		} else {
			value = 255;
		}
		if (value > 255) {
			value = 255;
		}

		g_targetBuffer[8] = (uint8_t) value;

		return valid;
	}

	return 0;
}

/**
 * @return 1 when message parsed
 */
uint8_t Nmea_Add(uint8_t c) {
	if (c == '\r' || c == '\n') {
		g_nmeaBuffer[g_bufferPos] = '\0';
		if (g_bufferPos == 0) {
			return 0;
		}
		uint8_t ret = Nmea_Parse();
		g_bufferPos = 0;
		return ret;
		
	}
	if (g_bufferPos >= NMEA_BUFFER_LENGTH) {
		// max length oveflow
		g_bufferPos = 0;
		return 0;
	} else {
		g_nmeaBuffer[g_bufferPos++] = c;
	}

	return 0;
}

