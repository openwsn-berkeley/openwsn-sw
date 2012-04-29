#ifndef CURRENT_ADC_H
#define CURRENT_ADC_H

#define CURRENT_READING_IN_PROGRESS 0xFFFF
#define CURRENT_READING_OVERFLOW 0xFFFE
#define CURRENT_READING_TIMEOUT 0xFFFD

extern volatile UINT16 current_reading_high;
extern volatile UINT16 current_reading_low;

void currentADC_init(void);
void ADC_interrupt(void) ;
void CCP2_interrupt(void);
void currentADC_trigger(void) ;




#endif