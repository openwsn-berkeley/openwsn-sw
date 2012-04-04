#include "GenericTypeDefs.h"
#include "Compiler.h"
#include "HardwareProfile.h"
#include "rtc.h"

volatile UINT32 current_time_s;

void T1_interrupt() {
    current_time_s += 2;
    PIR1bits.TMR1IF = 0;
}

void rtc_init() {
    // turn on Timer1
    T1CON = 0b10001011; // enable crystal oscillator, 32.768KHz, 2s period

    current_time_s = 0;

    PIE1bits.TMR1IE = 1; // enable interrupts
}

void rtc_set_time(UINT32 time) {
    TMR1H = 0;
    TMR1L = 0;
    current_time_s = time;
}