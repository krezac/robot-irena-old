/*!
* \file nmea.h
* \brief nmea parser
*
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2010/02/08
*/

#ifndef NMEA_H
#define NMEA_H

#include <avr/io.h>

#include "robbus_config.h"

#ifdef __cplusplus
extern "C" {
#endif

//! initialize
void Nmea_Init(uint8_t* target);

uint8_t Nmea_Add(uint8_t c);

#ifdef __cplusplus
}
#endif

#endif

