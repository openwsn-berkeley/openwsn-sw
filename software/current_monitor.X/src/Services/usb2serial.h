#ifndef USB2SERIAL_H
#define USB2SERIAL_H


void usb2serial_processIO();

void usb2serial_init();

void InitializeUSART(void);

unsigned char getcUSART ();

void putcUSART(char c);

void mySetLineCodingHandler(void);

unsigned char getcUSART();

void usb2serial_setCallbacks(  void (*usb2serial)(char), void (*serial2usb)(char));


#endif