#ifndef LEDS_H
#define LEDS_H


#define leds_init() { TRISAbits.TRISA6 = OUTPUT_PIN; TRISCbits.TRISC2 = OUTPUT_PIN;  }

#define led1(X) LATAbits.LATA6 = (X)
#define led2(X) LATCbits.LATC2 = (X)

#define led_tog1() LATA ^= (1<<6)
#define led_tog2() LATC ^= (1<<2)



#endif