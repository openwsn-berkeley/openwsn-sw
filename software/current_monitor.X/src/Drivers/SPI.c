

#include "Microchip/Include/Compiler.h"
#include "SPI.h"


/*
 *  RB4/RP7/SCK2 - SPI_SCK - out
 *  RB2/RP5/SDI2 - SPI_MISO - in
 *  RB3/RP6/SDO2 - SPI_MOSI - out
*/
void spi_init() {
    // default initialize to Fosc/4 = 12MHz
    SSP2CON1 = 0b00100000;

    //CKE = 1; // transmit on idle->active clock
    //SMP = 0; // sample on rising edge
    SSP2STAT = 0b01000000;

    // initialize port pins
    TRISBbits.TRISB4 = 0;
    TRISBbits.TRISB2 = 1;
    TRISBbits.TRISB3 = 0;

    RPOR7 = 10; // SCK
    RPINR21 = 5; // SDI
    RPOR6 = 9; // SDO
}

char spi_write(char byte) {
    SSP2CON1 &= ~(1<<7); // clear WCOL bit
    PIR3bits.SSP2IF = 0; // clear interrupt
    SSP2BUF = byte;
    while( !PIR3bits.SSP2IF );
    return SSP2BUF;
}
