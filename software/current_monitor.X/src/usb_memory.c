
#include "USB/usb.h"
#include "USB/usb_function_cdc.h"
#include "HardwareProfile.h"
#include "usb_memory.h"

#if defined(__18CXX)
    #if defined(__18F14K50) || defined(__18F13K50) || defined(__18LF14K50) || defined(__18LF13K50) 
        #pragma udata usbram2
    #elif defined(__18F2455) || defined(__18F2550) || defined(__18F4455) || defined(__18F4550)\
        || defined(__18F2458) || defined(__18F2453) || defined(__18F4558) || defined(__18F4553)
        #pragma udata USB_VARIABLES_1=0x500
    #elif defined(__18F4450) || defined(__18F2450)
        #pragma udata USB_VARIABLES=0x480
    #else
        #pragma udata usb_cdc
    #endif
#endif

volatile FAR CDC_NOTICE cdc_notice;
volatile FAR unsigned char cdc_data_rx[CDC_DATA_OUT_EP_SIZE];
volatile FAR unsigned char cdc_data_tx[CDC_DATA_IN_EP_SIZE];
LINE_CODING line_coding;    // Buffer to store line coding information

#if defined(USB_CDC_SUPPORT_DSR_REPORTING)
    SERIAL_STATE_NOTIFICATION SerialStatePacket;
#endif

#if defined(__18CXX)
    #if defined(__18F14K50) || defined(__18F13K50) || defined(__18LF14K50) || defined(__18LF13K50)
        #pragma udata usbram2
    #elif defined(__18F2455) || defined(__18F2550) || defined(__18F4455) || defined(__18F4550)\
        || defined(__18F2458) || defined(__18F2453) || defined(__18F4558) || defined(__18F4553)
        #pragma udata USB_VARIABLES_2=0x600
    #elif defined(__18F4450) || defined(__18F2450)
        #pragma udata USB_VARIABLES=0x480
    #else
        #pragma udata usb_custom
#endif

unsigned char OUTPacket[64];	//User application buffer for receiving and holding OUT packets sent from the host
unsigned char INPacket[64];		//User application buffer for sending IN packets to the host

#if defined(__18CXX)
#pragma udata
#endif
