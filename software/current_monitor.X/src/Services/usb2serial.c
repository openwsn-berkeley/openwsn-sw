#include "./USB/usb.h"
#include "./USB/usb_function_cdc.h"
#include "usb_memory.h"

#include "HardwareProfile.h"
#include "./Services/usb2serial.h"

#include "GenericTypeDefs.h"
#include "Compiler.h"
#include "usb_config.h"
#include "USB/usb_device.h"
#include "USB/usb.h"
#include "USB/usb_function_generic.h"

#include "HardwareProfile.h"

char USB_Out_Buffer[CDC_DATA_OUT_EP_SIZE];
char RS232_Out_Data[CDC_DATA_IN_EP_SIZE];

unsigned char  NextUSBOut;
unsigned char    NextUSBOut;
//char RS232_In_Data;
unsigned char    LastRS232Out;  // Number of characters in the buffer
unsigned char    RS232cp;       // current position within the buffer
unsigned char RS232_Out_Data_Rdy = 0;
USB_HANDLE  lastTransmission;


#if defined(__18CXX)
    #define mDataRdyUSART() PIR1bits.RCIF
    #define mTxRdyUSART()   TXSTAbits.TRMT
#elif defined(__C30__) || defined(__C32__)
    #define mDataRdyUSART() UART2IsPressed()
    #define mTxRdyUSART()   U2STAbits.TRMT
#endif


void usb2serial_init() {
    	unsigned char i;
    InitializeUSART();

// 	 Initialize the arrays
	for (i=0; i<sizeof(USB_Out_Buffer); i++)
    {
		USB_Out_Buffer[i] = 0;
    }

	NextUSBOut = 0;
	LastRS232Out = 0;
}

void usb2serial_processIO() {

	if (RS232_Out_Data_Rdy == 0)  // only check for new USB buffer if the old RS232 buffer is
	{						  // empty.  This will cause additional USB packets to be NAK'd
		LastRS232Out = getsUSBUSART(RS232_Out_Data,64); //until the buffer is free.
		if(LastRS232Out > 0)
		{
			RS232_Out_Data_Rdy = 1;  // signal buffer full
			RS232cp = 0;  // Reset the current position
		}
	}

    //Check if one or more bytes are waiting in the physical UART transmit
    //queue.  If so, send it out the UART TX pin.
	if(RS232_Out_Data_Rdy && mTxRdyUSART())
	{
    	#if 0 && defined(USB_CDC_SUPPORT_HARDWARE_FLOW_CONTROL)
        	//Make sure the receiving UART device is ready to receive data before
        	//actually sending it.
        	if(UART_CTS == USB_CDC_CTS_ACTIVE_LEVEL)
        	{
        		putcUSART(RS232_Out_Data[RS232cp]);
        		++RS232cp;
        		if (RS232cp == LastRS232Out)
        			RS232_Out_Data_Rdy = 0;
    	    }
	    #else
	        //Hardware flow control not being used.  Just send the data.
    		putcUSART(RS232_Out_Data[RS232cp]);
    		++RS232cp;
    		if (RS232cp == LastRS232Out)
    			RS232_Out_Data_Rdy = 0;
	    #endif
	}

    //Check if we received a character over the physical UART, and we need
    //to buffer it up for eventual transmission to the USB host.
	if(mDataRdyUSART() && (NextUSBOut < (CDC_DATA_OUT_EP_SIZE - 1)))
	{
		USB_Out_Buffer[NextUSBOut] = getcUSART();
		++NextUSBOut;
		USB_Out_Buffer[NextUSBOut] = 0;
	}

	#if 0 && defined(USB_CDC_SUPPORT_HARDWARE_FLOW_CONTROL)
    	//Drive RTS pin, to let UART device attached know if it is allowed to
    	//send more data or not.  If the receive buffer is almost full, we
    	//deassert RTS.
    	if(NextUSBOut <= (CDC_DATA_OUT_EP_SIZE - 5u))
    	{
            UART_RTS = USB_CDC_RTS_ACTIVE_LEVEL;
        }
        else
        {
        	UART_RTS = (USB_CDC_RTS_ACTIVE_LEVEL ^ 1);
        }
    #endif

    //Check if any bytes are waiting in the queue to send to the USB host.
    //If any bytes are waiting, and the endpoint is available, prepare to
    //send the USB packet to the host.
	if((USBUSARTIsTxTrfReady()) && (NextUSBOut > 0))
	{
		putUSBUSART(&USB_Out_Buffer[0], NextUSBOut);
		NextUSBOut = 0;
	}

    CDCTxService();
}


/******************************************************************************
 * Function:        void InitializeUSART(void)
 *
 * PreCondition:    None
 *
 * Input:           None
 *
 * Output:          None
 *
 * Side Effects:    None
 *
 * Overview:        This routine initializes the UART to 19200
 *
 * Note:
 *
 *****************************************************************************/
void InitializeUSART(void)
{
    #if defined(__18CXX)
	    unsigned char c;
        #if defined(__18F14K50)
    	    //ANSELHbits.ANS11 = 0;	// Make RB5 digital so USART can use pin for Rx
            ANSELH = 0;
            #ifndef BAUDCON
                #define BAUDCON BAUDCTL
            #endif
        #endif
        UART_TRISRx=1;				// RX
        UART_TRISTx=0;				// TX
        TXSTA = 0x24;       	// TX enable BRGH=1
        RCSTA = 0x90;       	// Single Character RX
        SPBRG = 0x71;
        SPBRGH = 0x02;      	// 0x0271 for 48MHz -> 19200 baud
        BAUDCON = 0x08;     	// BRG16 = 1
        c = RCREG;				// read
    #endif

    #if defined(__C30__)
        #if defined( __PIC24FJ256GB110__ ) || defined( PIC24FJ256GB210_PIM )
            // PPS - Configure U2RX - put on pin 49 (RP10)
            RPINR19bits.U2RXR = 10;

            // PPS - Configure U2TX - put on pin 50 (RP17)
            RPOR8bits.RP17R = 5;
        #elif defined(__PIC24FJ64GB004__)
            // PPS - Configure U2RX - put on RC3/pin 36 (RP19)
            RPINR19bits.U2RXR = 19;

            // PPS - Configure U2TX - put on RC9/pin 5 (RP25)
            RPOR12bits.RP25R = 5;
        #elif defined(__PIC24FJ64GB502__)
            // PPS - Configure U2RX - put on RB7 (RP7)
            RPINR19bits.U2RXR = 7;

            // PPS - Configure U2TX - put on RB8 (RP8)
            RPOR4bits.RP8R = 5;
        #elif defined(__PIC24FJ256DA210__)
            // PPS - Configure U2RX - put on RD0 pin 72 (RP11)
            // Make sure jumper JP12 is in 2-4 position if using the
            // PIC24FJ256DA210 Development Board (microchipDIRECT.com DM240312).
            // Also make sure JP16 and JP17 are in the 1-2 position on this board.
            RPINR19bits.U2RXR = 11; //Assign U2RX to RD0/RP11 pin.

            // PPS - Configure U2TX - put on RF3/pin 51 (RP16)
            RPOR8bits.RP16R = 5;

            TRISFbits.TRISF3 = 0;
        #elif defined(__dsPIC33EP512MU810__) || defined (__PIC24EP512GU810__)
            // The dsPIC33EP512MU810 features Peripheral Pin
            // select. The following statements map UART2 to
            // device pins which would connect to the the
            // RX232 transciever on the Explorer 16 board.

             RPINR19 = 0;
             RPINR19 = 0x64;
             RPOR9bits.RP101R = 0x3;

        #else
            #error Verify that any required PPS is done here.
        #endif

        UART2Init();
    #endif

    #if defined(__C32__)
        UART2Init();
    #endif

}//end InitializeUSART

/******************************************************************************
 * Function:        void putcUSART(char c)
 *
 * PreCondition:    None
 *
 * Input:           char c - character to print to the UART
 *
 * Output:          None
 *
 * Side Effects:    None
 *
 * Overview:        Print the input character to the UART
 *
 * Note:
 *
 *****************************************************************************/
void putcUSART(char c)
{
    #if defined(__18CXX)
	    TXREG = c;
    #else
        UART2PutChar(c);
    #endif
}


/******************************************************************************
 * Function:        void mySetLineCodingHandler(void)
 *
 * PreCondition:    USB_CDC_SET_LINE_CODING_HANDLER is defined
 *
 * Input:           None
 *
 * Output:          None
 *
 * Side Effects:    None
 *
 * Overview:        This function gets called when a SetLineCoding command
 *                  is sent on the bus.  This function will evaluate the request
 *                  and determine if the application should update the baudrate
 *                  or not.
 *
 * Note:
 *
 *****************************************************************************/
#if defined(USB_CDC_SET_LINE_CODING_HANDLER)
void mySetLineCodingHandler(void)
{
    //If the request is not in a valid range
    if(cdc_notice.GetLineCoding.dwDTERate.Val > 115200)
    {
        //NOTE: There are two ways that an unsupported baud rate could be
        //handled.  The first is just to ignore the request and don't change
        //the values.  That is what is currently implemented in this function.
        //The second possible method is to stall the STATUS stage of the request.
        //STALLing the STATUS stage will cause an exception to be thrown in the
        //requesting application.  Some programs, like HyperTerminal, handle the
        //exception properly and give a pop-up box indicating that the request
        //settings are not valid.  Any application that does not handle the
        //exception correctly will likely crash when this requiest fails.  For
        //the sake of example the code required to STALL the status stage of the
        //request is provided below.  It has been left out so that this demo
        //does not cause applications without the required exception handling
        //to crash.
        //---------------------------------------
        //USBStallEndpoint(0,1);
    }
    else
    {
        //Update the baudrate info in the CDC driver
        CDCSetBaudRate(cdc_notice.GetLineCoding.dwDTERate.Val);

        //Update the baudrate of the UART
        #if defined(__18CXX)
        {
            DWORD_VAL dwBaud;
            dwBaud.Val = (DWORD)(GetSystemClock()/4)/line_coding.dwDTERate.Val-1;
            SPBRG = dwBaud.v[0];
            SPBRGH = dwBaud.v[1];
        }
        #elif defined(__C30__)
        {
            DWORD_VAL dwBaud;
            #if defined(__dsPIC33EP512MU810__) || defined (__PIC24EP512GU810__)
            dwBaud.Val = ((GetPeripheralClock()/(unsigned long)(16 * line_coding.dwDTERate.Val)))- 1;
            #else
            dwBaud.Val = (((GetPeripheralClock()/2)+(BRG_DIV2/2*line_coding.dwDTERate.Val))/BRG_DIV2/line_coding.dwDTERate.Val-1);
            #endif
            U2BRG = dwBaud.Val;
        }
        #elif defined(__C32__)
        {
            U2BRG = ((GetPeripheralClock()+(BRG_DIV2/2*line_coding.dwDTERate.Val))/BRG_DIV2/line_coding.dwDTERate.Val-1);
            //U2MODE = 0;
            U2MODEbits.BRGH = BRGH2;
            //U2STA = 0;
        }
        #endif
    }
}
#endif

/******************************************************************************
 * Function:        void putcUSART(char c)
 *
 * PreCondition:    None
 *
 * Input:           None
 *
 * Output:          unsigned char c - character to received on the UART
 *
 * Side Effects:    None
 *
 * Overview:        Print the input character to the UART
 *
 * Note:
 *
 *****************************************************************************/
unsigned char getcUSART ()
{
	char  c;

    #if defined(__18CXX)

	if ( RCSTAbits.OERR)  // in case of overrun error
	{                    // we should never see an overrun error, but if we do,
		RCSTAbits.CREN = 0;  // reset the port
		c = RCREG;
		RCSTAbits.CREN = 1;  // and keep going.
	}
	else
		c = RCREG;
// not necessary.  EUSART auto clears the flag when RCREG is cleared
//	PIR1bits.RCIF = 0;    // clear Flag

    #endif

    #if defined(__C30__) || defined(__C32__)
        c = UART2GetChar();
    #endif

	return c;
}
