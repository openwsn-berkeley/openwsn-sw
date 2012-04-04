#ifndef COMMANDS_XBEE_H
#define COMMANDS_XBEE_H


void commands_xbee_init();

void commands_xbee_u2s_cb(char ch);
void commands_xbee_s2u_cb(char ch);

void commands_XBEE_INFO();  // get information about # of configurations and current one
void commands_XBEE_GET_CONFIG(); // dump a configuration
void commands_XBEE_SAVE_CONFIG(); // provide a configuration
void commands_XBEE_SET_CURRENT_CONFIG(); // start using a configuration
void commands_XBEE_START_MONITOR(); // start monitoring events going through the UART
void commands_XBEE_STOP_MONITOR(); //stop monitoring events going through the UART
void commands_XBEE_CHECK_EVENT(); // see if monitor caught anything


#endif