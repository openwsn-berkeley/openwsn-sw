
#ifndef XBEE_H
#define XBEE_H
#include "GenericTypeDefs.h"

extern char xbee_api_buf[128];
#define MAX_XBEE_API_PAYLOAD (sizeof(xbee_api_buf) - 4)

typedef struct {
    char code[2];
    char nBytes;
    char value[];
} AT_command_t;

typedef enum {
    AT_COMMAND = 0x08,
    AT_COMMAND_QUEUE = 0x09,
    TX_REQUEST = 0x10,
    TX_EXPLICIT_ADDRESSING = 0x11,
    REMOTE_AT_REQUEST = 0x17,
    CREATE_SOURCE_ROUTE = 0x21,

    AT_COMMAND_RESPONSE = 0x88,
    MODEM_STATUS = 0x8A,
    ZB_TRANSMIT_STATUS = 0x8B,
    ZB_RECEIVE_PACKET = 0x90,

    ZB_EXPLICIT_RX_INDICATOR = 0x91,
    ZB_IO_DATA_SAMPLE_INDICATOR = 0x92,
    ZB_SENSOR_READ_INDICATOR = 0x94,
    NODE_ID_INDICATOR = 0x95,

    REMOTE_COMMAND_RESPONSE = 0x97,
    OTA_FIRMWARE_UPDATE_STAUS = 0xA0,
    ROUTE_RECORD_INDICATOR = 0xA1,
    MANY_TO_ONE_ROUTE_REQUEST = 0xA3
} API_frame_type_t;

typedef struct {
    char frame_id;
    char code[2];
    char value[];
} AT_command_frame_t;

typedef struct {
    char frame_id;
    char addr64[8];
    char addr16[2];
    char radius;
    char options;
    char data[];
} TX_request_frame_t;

typedef struct {
    char frame_id;
    char addr64[8];
    char addr16[2];
    char options;
    char code[2];
    char value[];
} remote_AT_request_frame_t;

typedef struct {
    char frame_id;
    char addr64[8];
    char addr16[2];
    char options;
    char nAddresses;
    char addresses[][2];
} create_source_route_frame_t;

typedef struct {
    char frame_id;
    char code[2];
    char status;
    char value[];
} AT_command_response_frame_t;

typedef struct {
    char status;
} modem_status_frame_t;

typedef struct {
    char frame_id;
    char addr16[2];
    char retries_taken;
    char delivery_status;
    char discovery_status;
} transmit_status_frame_t;

typedef struct{
    char addr64[8];
    char addr16[2];
    char options;
    char data[];
} ZB_recieve_packet_frame_t;

typedef struct {
    API_frame_type_t frame_type;
    union {
        AT_command_frame_t at_command_frame;
        TX_request_frame_t tx_request_frame;
        remote_AT_request_frame_t remote_AT_request_frame;
        create_source_route_frame_t create_source_route_frame;
        AT_command_response_frame_t AT_command_response_frame;
        modem_status_frame_t modem_status_frame;
        transmit_status_frame_t transmit_status_frame;
        ZB_recieve_packet_frame_t ZB_recieve_packet_frame;
    } payload;
} API_frame_t;



void xbee_init();

void xbee_reset_parser();

extern UINT16 xbee_payload_length;

API_frame_t * xbee_parse(char ch);

#endif