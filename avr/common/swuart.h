/*!
* \file swuart.h
* \brief software usart receiver
*
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2010/02/05
*/

#ifndef SWUART_H
#define SWUART_H

#include <avr/io.h>

#include "robbus_config.h"

#ifdef __cplusplus
extern "C" {
#endif

// handler type
typedef void (*PtrSwUartHandler_t)(uint8_t);

//! initialize ticker
void SwUart_Init(PtrSwUartHandler_t handler);

#ifdef __cplusplus
}
#endif

#endif

