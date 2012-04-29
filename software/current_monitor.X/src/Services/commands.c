/* 
 * File:   commands.c
 * Author: nerd256
 *
 * Created on March 8, 2012, 6:50 PM
 */
#include <string.h>
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
#include "./Services/commands_xbee.h"
#include "./Services/commands_adc.h"
#include "./Services/commands_flash.h"
#include "Drivers/leds.h"

#if defined(__18CXX)
    #pragma udata
#endif
BOOL blinkStatusValid;
USB_HANDLE USBGenericOutHandle;
USB_HANDLE USBGenericInHandle;

typedef enum {
            PIC_RESET = 0x00,
            DEVICE_RESET = 0x01,

            FLASH_START_READ = 0x10,
            FLASH_CONTINUE_READ = 0x11,
            FLASH_STOP_READ = 0x12,
            FLASH_START_WRITE = 0x15,
            FLASH_CONTINUE_WRITE = 0x16,
            FLASH_STOP_WRITE = 0x17,

            XBEE_INFO = 0x20, // get information about # of configurations and current one
            XBEE_GET_CONFIG = 0x21, // dump a configuration
            XBEE_SAVE_CONFIG = 0x22, // provide a configuration
            XBEE_SET_CURRENT_CONFIG = 0x23, // start using a configuration
            XBEE_START_MONITOR = 0x24, // start monitoring events going through the UART
            XBEE_STOP_MONITOR = 0x25, //stop monitoring events going through the UART
            XBEE_CHECK_EVENT = 0x26, // check if monitor caught anything

            ADC_READ_IMMEDIATE = 0x30 // get one ADC reading
} command_code_t;

typedef struct {
    // sequence number
    UINT16 sequence_no;
    // length of packet
    UINT8 length;
    // number of segments
    UINT8 num_segments;
    // segment no.
    UINT8 segment_no;

    // first char is command code
    char payload[];
} packet_t;

#define MAX_PAYLOAD_PER_PACKET (USBGEN_EP_SIZE-sizeof(packet_t))

struct {
    unsigned recieving_partial:1;
    unsigned char segments_recieved;
    UINT16 current_seq_no;
} reciever_state;

#pragma udata udata2
char packet_buffer[256];
#pragma udata
char packet_buffer_len = 0;
char packet_send_len = 0;

void commands_init() {
    USBGenericOutHandle = 0;
    USBGenericInHandle = 0;
    reciever_state.recieving_partial = 0;
    reciever_state.current_seq_no = 0;
    reciever_state.segments_recieved = 0;

    commands_xbee_init();
    commands_flash_init();
}


void commands_packet_recieved() {
   // led_tog1();
    switch(((command_code_t *)packet_buffer)[0]) {
        case PIC_RESET:
            _reset();
            break;

        case DEVICE_RESET:
            break;

        case FLASH_START_READ:
            commands_FLASH_START_READ(); break;
        case FLASH_CONTINUE_READ:
            commands_FLASH_CONTINUE_READ(); break;
        case FLASH_STOP_READ:
            commands_FLASH_STOP_READ(); break;
        case FLASH_START_WRITE:
            commands_FLASH_START_WRITE(); break;
        case FLASH_CONTINUE_WRITE:
            commands_FLASH_CONTINUE_WRITE(); break;
        case FLASH_STOP_WRITE:
            commands_FLASH_STOP_WRITE(); break;

        case XBEE_INFO:  // get information about # of configurations and current one
            commands_XBEE_INFO(); break;
        case XBEE_GET_CONFIG: // dump a configuration
            commands_XBEE_GET_CONFIG(); break;
        case XBEE_SAVE_CONFIG: // provide a configuration
            commands_XBEE_SAVE_CONFIG(); break;
        case XBEE_SET_CURRENT_CONFIG: // start using a configuration
            commands_XBEE_SET_CURRENT_CONFIG(); break;
        case XBEE_START_MONITOR: // start monitoring events going through the UART
            commands_XBEE_START_MONITOR(); break;
        case XBEE_STOP_MONITOR: //stop monitoring events going through the UART
            commands_XBEE_STOP_MONITOR(); break;
        case XBEE_CHECK_EVENT:
            commands_XBEE_CHECK_EVENT(); break;

        case ADC_READ_IMMEDIATE:
            commands_ADC_READ_IMMEDIATE(); break;

        default: //unknown command
            break;
    }
}

void commands_processIO() {
    packet_t * packet = NULL;
    char do_pack_recieved = 0;
    char num_segments;
    char i;
    //If the host sends a packet of data to the endpoint 1 OUT buffer, the hardware of the SIE will
    //automatically receive it and store the data at the memory location pointed to when we called
    //USBGenRead().  Additionally, the endpoint handle (in this case USBGenericOutHandle) will indicate
    //that the endpoint is no longer busy.  At this point, it is safe for this firmware to begin reading
    //from the endpoint buffer, and processing the data.  In this example, we have implemented a few very
    //simple commands.  For example, if the host sends a packet of data to the endpoint 1 OUT buffer, with the
    //first byte = 0x80, this is being used as a command to indicate that the firmware should "Toggle LED(s)".
    if(!USBHandleBusy(USBGenericOutHandle))		//Check if the endpoint has received any data from the host.
    {
        // 64-byte packet is in OUTPacket
        packet = (packet_t *)OUTPacket;
        // filter bad packets
        if ( packet->num_segments != 0 && packet->num_segments < 8 && packet->segment_no < packet->num_segments &&
                (packet->num_segments*(MAX_PAYLOAD_PER_PACKET) >= packet->length)){
            // don't clobber a newer packet
            if ( !reciever_state.recieving_partial || packet->sequence_no > reciever_state.current_seq_no || packet->sequence_no == 0 ) {
                // already have full packet
                if ( packet->num_segments == 1 ) {
                    memcpy(packet_buffer,packet->payload,packet->length);
                    do_pack_recieved = 1;
                } else { // restart reception
                    reciever_state.recieving_partial = 1;
                    reciever_state.segments_recieved = 1<<(packet->segment_no);
                    reciever_state.current_seq_no = packet->sequence_no;

                    if ( packet->segment_no < packet->num_segments - 1 ){
                        memcpy(packet_buffer + MAX_PAYLOAD_PER_PACKET * packet->segment_no,packet->payload,MAX_PAYLOAD_PER_PACKET );
                    } else {
                       // never going to start a transmission w/ the last packet
                    }
                }
            } else if ( reciever_state.recieving_partial && reciever_state.current_seq_no == packet->sequence_no ) {
                reciever_state.segments_recieved |= 1<<(packet->segment_no);
                if ( packet->segment_no == packet->num_segments - 1 )
                    memcpy(packet_buffer + MAX_PAYLOAD_PER_PACKET * packet->segment_no,packet->payload, (packet->length-1) % MAX_PAYLOAD_PER_PACKET + 1);
                else
                    memcpy(packet_buffer + MAX_PAYLOAD_PER_PACKET * packet->segment_no,packet->payload, MAX_PAYLOAD_PER_PACKET);
                
                if ( (UINT16)(reciever_state.segments_recieved) + 1 == (1<<packet->num_segments)) {
                    do_pack_recieved = 1;
                    reciever_state.recieving_partial = 0;
                }
            }
        }

        if ( do_pack_recieved ) {
            packet_buffer_len = packet->length;
            packet_send_len = 0;
            commands_packet_recieved();
            // now send the response
            num_segments = (packet_send_len - 1) / (MAX_PAYLOAD_PER_PACKET) + 1;
            if ( packet_send_len <= MAX_PAYLOAD_PER_PACKET ) num_segments = 1;
            packet->num_segments = num_segments;
            packet->length = packet_send_len;
            for ( i = 0; i < num_segments; i++ ) {
                packet->segment_no = i;
                if ( i == num_segments - 1 )
                    memcpy(packet->payload,packet_buffer + MAX_PAYLOAD_PER_PACKET * i,(packet_send_len - 1) % MAX_PAYLOAD_PER_PACKET + 1);
                else
                    memcpy(packet->payload,packet_buffer + MAX_PAYLOAD_PER_PACKET * i,MAX_PAYLOAD_PER_PACKET);

                while(USBHandleBusy(USBGenericInHandle));
                USBGenericInHandle = USBGenWrite(USBGEN_EP_NUM,(BYTE *)packet,USBGEN_EP_SIZE);
            }
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