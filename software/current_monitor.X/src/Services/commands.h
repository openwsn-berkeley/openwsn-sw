#ifndef COMMANDS_H
#define COMMANDS_H


extern char packet_buffer[256];
extern char packet_buffer_len;
extern char packet_send_len;

void commands_init(void);

void commands_initEP(void);

void commands_packet_recieved(void);
void commands_processIO(void);






#endif