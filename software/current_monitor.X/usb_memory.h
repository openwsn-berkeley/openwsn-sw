#ifndef USB_MEMORY_H
#define USB_MEMORY_H


extern volatile FAR CDC_NOTICE cdc_notice;
extern volatile FAR unsigned char cdc_data_rx[CDC_DATA_OUT_EP_SIZE];
extern volatile FAR unsigned char cdc_data_tx[CDC_DATA_IN_EP_SIZE];
extern LINE_CODING line_coding;    // Buffer to store line coding information

#if defined(USB_CDC_SUPPORT_DSR_REPORTING)
    extern SERIAL_STATE_NOTIFICATION SerialStatePacket;
#endif

extern unsigned char OUTPacket[64];	//User application buffer for receiving and holding OUT packets sent from the host
extern unsigned char INPacket[64];		//User application buffer for sending IN packets to the host


#endif