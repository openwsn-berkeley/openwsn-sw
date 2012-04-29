/* 
 * File:   xbee.c
 * Author: nerd256
 *
 * Created on March 20, 2012, 2:37 PM
 */
#include "GenericTypeDefs.h"


#include "./Services/usb2serial.h"
#include "./Services/commands.h"
#include "./Services/commands_xbee.h"
#include "HardwareProfile.h"
#include "xbee.h"


#define XB_START_DELIMITER 0x7E

volatile char xbee_api_buf[128];
volatile INT16 xbee_parse_pos;
volatile UINT16 xbee_payload_length;
volatile char xbee_parse_checksum;

void xbee_init() {

    xbee_reset_parser();
}

void xbee_reset_parser() {
    xbee_parse_pos = 0;
}

API_frame_t * xbee_parse(char ch) {
    if ( xbee_parse_pos == 0) {
        if ( ch == XB_START_DELIMITER ) // starting to get a frame
            xbee_parse_pos++;
        return NULL;
    }
    else { // we are getting a frame
        if (xbee_parse_pos <= 2 )
            xbee_api_buf[xbee_parse_pos -1] = ch;

        xbee_parse_pos++;
        if ( xbee_parse_pos == 3 ) { // we have the length now
            xbee_payload_length = xbee_api_buf[0]<<8 | xbee_api_buf[1];
            xbee_parse_checksum = 0;
        }
        else if ( xbee_parse_pos - 4 >= 128) {
            // overflow! ditch!
            xbee_parse_pos = 0;
            return NULL;
        }
        else if( xbee_parse_pos > 3 ) {
            xbee_parse_checksum += ch;
            xbee_api_buf[xbee_parse_pos - 4] = ch;
            
            if ( xbee_parse_pos == xbee_payload_length + 4 ) { // everything gotten
                xbee_parse_pos = 0; // regardless, we will start a new reception
                if ( xbee_parse_checksum == 0xFF ){
                    return (API_frame_t *)xbee_api_buf;
                } else {// checksum error, message discarded
                    return NULL;
                }
            }
        }
    }
}