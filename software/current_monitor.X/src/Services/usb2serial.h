#ifndef USB2SERIAL_H
#define USB2SERIAL_H


void usb2serial_processIO(void);

void usb2serial_init(void);

void InitializeUSART(void);

unsigned char getcUSART (void);

void putcUSART(char c);

void mySetLineCodingHandler(void);

unsigned char getcUSART(void);

void usb2serial_setCallbacks(  void (*usb2serial)(char), void (*serial2usb)(char));


#endif