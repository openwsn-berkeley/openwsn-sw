#include "./Services/usb2serial.h"
#include "./Services/commands.h"
#include "./Services/commands_xbee.h"

#include "./Drivers/xbee.h"

#define AT_CMD_BUFFER_LEN 52
char at_cmd_buffer[AT_CMD_BUFFER_LEN];
char at_cmd_buffer_pos;
char at_commands_queued;
char overflow;

void commands_xbee_init() {

    at_cmd_buffer_pos = 0;
}

void commands_xbee_u2s_cb(char ch) {
    API_frame_t * frame = xbee_parse(ch);
    if ( frame && frame->frame_type == AT_COMMAND) {
        if( at_cmd_buffer_pos < AT_CMD_BUFFER_LEN - xbee_payload_length - 2 ) {
            AT_command_frame_t * data = &(frame->payload.at_command_frame);
            at_cmd_buffer[at_cmd_buffer_pos] = data->code[0];
            at_cmd_buffer[at_cmd_buffer_pos + 1] = data->code[1];
            at_cmd_buffer[at_cmd_buffer_pos + 2] = xbee_payload_length - offsetof(API_frame_t,payload.at_command_frame.value);
            memcpy(at_cmd_buffer + at_cmd_buffer_pos + 3,data->value,at_cmd_buffer[at_cmd_buffer_pos + 2]);
            at_cmd_buffer_pos += 3 + at_cmd_buffer[at_cmd_buffer_pos + 2];
            at_commands_queued++;
        } else {
            overflow ++;
        }
    }
}

void commands_xbee_s2u_cb(char ch) {
}

// The commands
// packet buffer contains packet, first byte is ignored (command code)
void commands_XBEE_INFO(){   // get information about # of configurations and current one

}

void commands_XBEE_GET_CONFIG(){  // dump a configuration

}
void commands_XBEE_SAVE_CONFIG(){ // provide a configuration

}
void commands_XBEE_SET_CURRENT_CONFIG(){// start using a configuration

}

void commands_XBEE_START_MONITOR(){ // start monitoring events going through the UART
    xbee_reset_parser();
    at_commands_queued = 0;
    at_cmd_buffer_pos = 0;
    overflow = 0;
    usb2serial_setCallbacks(&commands_xbee_u2s_cb,&commands_xbee_s2u_cb);
}
void commands_XBEE_STOP_MONITOR(){ //stop monitoring events going through the UART
    usb2serial_setCallbacks(NULL,NULL);
    xbee_reset_parser();
}
void commands_XBEE_CHECK_EVENT() { // see if monitor caught anything
    packet_buffer[0] = at_commands_queued;
    packet_buffer[1] = overflow;
    memcpy(packet_buffer + 2,at_cmd_buffer,at_cmd_buffer_pos);
    packet_send_len = 2 + at_cmd_buffer_pos;

    at_cmd_buffer_pos = 0;
    at_commands_queued = 0;
    overflow = 0;
}

