/*!
* \file tick0.h
* \brief timestaping the data packets ftom timer0
*
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2010/02/05
*/

#ifndef TICK0_H
#define TICK0_H

#include <avr/io.h>

#include "robbus_config.h"

#ifdef __cplusplus
extern "C" {
#endif

// handler type
typedef void (*PtrTimeTick0Handler_t)(void);

//! initialize ticker
void TimeTick0_Init(PtrTimeTick0Handler_t handler);

//! get tick value
uint8_t TimeTick0_Get(void);

#ifdef __cplusplus
}
#endif

#endif
