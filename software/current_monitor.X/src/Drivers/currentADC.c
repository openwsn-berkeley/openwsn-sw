
#include "GenericTypeDefs.h"
#include "Compiler.h"
#include "HardwareProfile.h"
#include "currentADC.h"

volatile UINT16 current_reading_high;
volatile UINT16 current_reading_low;

// AN0/C1INA/RP0 : Integrating capacitor ( doesn't use ADC module )
// AN2 : 470Ohm sense resistor

// Peripherals used:
//  ADC
//  TIMER3 + CCP2

void ADC_interrupt() {
    current_reading_high = ADRESH<<8 | ADRESL;
    PIR1bits.ADIF = 0;
    PIE1bits.ADIE = 0;
}

void CCP2_interrupt() {
    current_reading_low = CCPR2H<<8 | CCPR2L;
    PIR2bits.CCP2IF = 0;
    PIE2bits.CCP2IE = 0;
}

void currentADC_trigger() {
    // drain low-power cap
    TRISAbits.TRISA0 = OUTPUT_PIN;

    current_reading_high = current_reading_low = CURRENT_READING_IN_PROGRESS;

    // start high-power conversion
    PIR1bits.ADIF = 0;
    PIE1bits.ADIE = 1;
    ADCON0bits.GO = 1; // start conversion on AN0

    // start low-power conversion
    PIR2bits.CCP2IF = 0;
    PIE2bits.CCP2IE = 1;
    TMR3H = 0x00;
    TMR3L = 0x00;
    if (PORTAbits.RA0) { // could not pull down the cap in time
        current_reading_low = CURRENT_READING_OVERFLOW;
        PIE2bits.CCP2IE = 0;
    }
    TRISAbits.TRISA0 = INPUT_PIN;
}

void currentADC_init() {
    ANCON0 = 0b11111011;
    ANCON1 = 0b00011111;

    ADCON0 = (0<<2) | 1; // turn on module, channel 0
    ADCON1 = 0b11000110; // no acquisition time, do calibration, right-justified
    ADCON0bits.GO = 1;// start conversion
    while(ADCON0bits.GO);
    ADCON1bits.ADCAL = 0; // turn off calibration
    ADCON0 = (2<<2) | 1; // turn on module, channel 2

    // turn on interrupts for ADC
    PIR1bits.ADIF = 0;
    IPR1bits.ADIP = 0;

    // set up low-power conversion
    TRISAbits.TRISA0 = INPUT_PIN;
    LATAbits.LATA0 = 0;

    T3CON = 3; // power on clck=Fosc/4= 16MHz
    TCLKCON = 2; // both CCP1 and CCP2 use timer 3 & timer 4;

    PPSCONbits.IOLOCK = 0; // Unlock PPS registers
    RPINR8 = 0; // Input capture 2 assigned to RP0

    CCP2CON = 0b00000101; // capture mode rising edge
    IPR2bits.CCP2IP = 0;

    current_reading_high = current_reading_low = CURRENT_READING_IN_PROGRESS;
}