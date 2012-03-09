/* 
 * File:   commands.c
 * Author: nerd256
 *
 * Created on March 8, 2012, 6:50 PM
 */
#include "./USB/usb.h"
#include "./USB/usb_function_cdc.h"
#include "usb_memory.h"

#include "HardwareProfile.h"
#include "GenericTypeDefs.h"
#include "Compiler.h"
#include "usb_config.h"
#include "USB/usb_device.h"
#include "USB/usb.h"
#include "USB/usb_function_generic.h"

#include "HardwareProfile.h"

#include "./Services/usb2serial.h"
#include "./Services/commands.h"

#if defined(__18CXX)
    #pragma udata
#endif
BOOL blinkStatusValid;
USB_HANDLE USBGenericOutHandle;
USB_HANDLE USBGenericInHandle;

typedef enum {
            PIC_RESET = 0x00,
            DEVICE_RESET = 0x01,

            FLASH_READ = 0x10,
            FLASH_WRITE = 0x12,
            FLASH_ERASE = 0x13,

            XBEE_INFO = 0x20, // get information about # of configurations and current one
            XBEE_GET_CONFIG = 0x21, // dump a configuration
            XBEE_SAVE_CONFIG = 0x22, // provide a configuration
            XBEE_SET_CURRENT_CONFIG = 0x23, // start using a configuration
            XBEE_START_MONITOR = 0x24, // start monitoring events going through the UART
            XBEE_STOP_MONITOR = 0x25 //stop monitoring events going through the UART
} command_code_t;

typedef struct {
    // command code
    command_code_t code : 8;
    // length of packet
    UINT16 length;
    // number of segments
    UINT8 num_segments;
    // segment no.
    UINT8 segment_no;

    char payload[];
} packet_t;

char packet_buffer[256];

void commands_init() {
    	USBGenericOutHandle = 0;
	USBGenericInHandle = 0;
}

void commands_processIO() {

        //If the host sends a packet of data to the endpoint 1 OUT buffer, the hardware of the SIE will
    //automatically receive it and store the data at the memory location pointed to when we called
    //USBGenRead().  Additionally, the endpoint handle (in this case USBGenericOutHandle) will indicate
    //that the endpoint is no longer busy.  At this point, it is safe for this firmware to begin reading
    //from the endpoint buffer, and processing the data.  In this example, we have implemented a few very
    //simple commands.  For example, if the host sends a packet of data to the endpoint 1 OUT buffer, with the
    //first byte = 0x80, this is being used as a command to indicate that the firmware should "Toggle LED(s)".
    if(!USBHandleBusy(USBGenericOutHandle))		//Check if the endpoint has received any data from the host.
    {
        switch(OUTPacket[0])					//Data arrived, check what kind of command might be in the packet of data.
        {
            case 0x80:  //Toggle LED(s) command from PC application.
		        blinkStatusValid = FALSE;		//Disable the regular LED blink pattern indicating USB state, PC application is controlling the LEDs.
                if(mGetLED_1() == mGetLED_2())
                {
                    mLED_1_Toggle();
                    mLED_2_Toggle();
                }
                else
                {
                    mLED_1_On();
                    mLED_2_On();
                }
                break;
            case 0x81:  //Get push button state command from PC application.
                INPacket[0] = 0x81;				//Echo back to the host PC the command we are fulfilling in the first byte.  In this case, the Get Pushbutton State command.
				if(sw2 == 1)					//pushbutton not pressed, pull up resistor on circuit board is pulling the PORT pin high
				{
					INPacket[1] = 0x01;
				}
				else							//sw2 must be == 0, pushbutton is pressed and overpowering the pull up resistor
				{
					INPacket[1] = 0x00;
				}
				//Now check to make sure no previous attempts to send data to the host are still pending.  If any attemps are still
				//pending, we do not want to write to the endpoint 1 IN buffer again, until the previous transaction is complete.
				//Otherwise the unsent data waiting in the buffer will get overwritten and will result in unexpected behavior.
                if(!USBHandleBusy(USBGenericInHandle))
	            {
		            //The endpoint was not "busy", therefore it is safe to write to the buffer and arm the endpoint.
	                //The USBGenWrite() function call "arms" the endpoint (and makes the handle indicate the endpoint is busy).
	                //Once armed, the data will be automatically sent to the host (in hardware by the SIE) the next time the
	                //host polls the endpoint.  Once the data is successfully sent, the handle (in this case USBGenericInHandle)
	                //will indicate the the endpoint is no longer busy.
					USBGenericInHandle = USBGenWrite(USBGEN_EP_NUM,(BYTE*)&INPacket,USBGEN_EP_SIZE);
                }
                break;
        }

        //Re-arm the OUT endpoint for the next packet:
	    //The USBGenRead() function call "arms" the endpoint (and makes it "busy").  If the endpoint is armed, the SIE will
	    //automatically accept data from the host, if the host tries to send a packet of data to the endpoint.  Once a data
	    //packet addressed to this endpoint is received from the host, the endpoint will no longer be busy, and the application
	    //can read the data which will be sitting in the buffer.
        USBGenericOutHandle = USBGenRead(USBGEN_EP_NUM,(BYTE*)&OUTPacket,USBGEN_EP_SIZE);
    }
    
}

void commands_initEP() {
    USBEnableEndpoint(USBGEN_EP_NUM,USB_OUT_ENABLED|USB_IN_ENABLED|USB_HANDSHAKE_ENABLED|USB_DISALLOW_SETUP);
    USBGenericOutHandle = USBGenRead(USBGEN_EP_NUM,(BYTE*)&OUTPacket,USBGEN_EP_SIZE);
}