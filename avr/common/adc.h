/*!
* \file adc.h
* \brief analog to digital converter code
*
*  URL: http://robotika.cz/
*  
*  Revision: 1.0
*  Date: 2010/02/14
*/

#ifndef ADC_H
#define ADC_H

#include <avr/io.h>

#include "robbus_config.h"

#ifdef __cplusplus
extern "C" {
#endif

//! initialize adc
void Adc_Init(void);

//! get tick value
uint8_t Adc_Get(uint8_t channel);

#ifdef __cplusplus
}
#endif

#endif
