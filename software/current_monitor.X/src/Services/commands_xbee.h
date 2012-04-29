#ifndef COMMANDS_XBEE_H
#define COMMANDS_XBEE_H


void commands_xbee_init(void);

void commands_xbee_u2s_cb(char ch);
void commands_xbee_s2u_cb(char ch);

void commands_XBEE_INFO(void);  // get information about # of configurations and current one
void commands_XBEE_GET_CONFIG(void); // dump a configuration
void commands_XBEE_SAVE_CONFIG(void); // provide a configuration
void commands_XBEE_SET_CURRENT_CONFIG(void); // start using a configuration
void commands_XBEE_START_MONITOR(void); // start monitoring events going through the UART
void commands_XBEE_STOP_MONITOR(void); //stop monitoring events going through the UART
void commands_XBEE_CHECK_EVENT(void); // see if monitor caught anything


#endif