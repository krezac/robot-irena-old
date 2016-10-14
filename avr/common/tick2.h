/*!
* \file tick2.h
* \brief timestaping the data packets from timer2
*
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2009/12/22
*/

#ifndef TICK2_H
#define TICK2_H

#include <avr/io.h>

#include "robbus_config.h"

#ifdef __cplusplus
extern "C" {
#endif

// handler type
typedef void (*PtrTimeTick2Handler_t)(void);

//! initialize ticker
void TimeTick2_Init(PtrTimeTick2Handler_t handler);

//! get tick value
uint8_t TimeTick2_Get(void);

#ifdef __cplusplus
}
#endif

#endif

