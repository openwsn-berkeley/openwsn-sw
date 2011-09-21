#include "../drivers/gina.h"
#include "commands.h"

void dma_init(void) {
  DMA0DA = (int)(cmd_packet+4);                // Destination block address
  DMA0CTL = DMADT_5 + DMASRCINCR_3 + DMADSTINCR_3 + DMADSTBYTE + DMASRCBYTE; // Rpt, inc
  DMA0CTL |= DMAEN;                         // Enable DMA0

  cmd_packet[0] = AT_FRAME_TX;
  cmd_packet[2] = 0x00;
  cmd_packet[3] = 0x80;
}

void cmd_init(void) {
  dma_init();
  cmd_ledmode = CMD_LEDMODE_NONE;
  cmd_tickmode = CMD_TICK;
  cmd_mode = CMD_MODE_WAIT;
  cmd_mode_changed = 0;
  cmd_channel = 26;
  cmd_packet_new = 0;
}

int cmd_periph(char which, char enable) {
  int fail = 0;
  
  if (which & CMD_PERIPH_RADIO)
    if (at_test()) fail |= CMD_PERIPH_RADIO;
  if (which & CMD_PERIPH_XL)
    if (xl_test()) fail |= CMD_PERIPH_XL;
  if (which & CMD_PERIPH_IR)
    if (ir_test()) fail |= CMD_PERIPH_IR;
  if (which & CMD_PERIPH_PWM)
    if (pwm_test()) fail |= CMD_PERIPH_PWM;

  if (fail) cmd_mode = CMD_MODE_ERROR;
  else cmd_mode = CMD_MODE_SPIN;

  if (fail || !enable)
    return fail;

  if (which & CMD_PERIPH_RADIO)
    at_config();
  if (which & CMD_PERIPH_XL)
    xl_config();
  if (which & CMD_PERIPH_IR)
    ir_config();
  if (which & CMD_PERIPH_PWM)
    pwm_config();
  
  return 0;
}

void cmd_buildpkt(char *buf, int len) {
  DMA0SA = (int)(buf);                // Start block address
  DMA0SZ = len;                          // Block size
  DMA0CTL |= DMAREQ;                      // Trigger block transfer

  cmd_packet[1] = len+3;
  cmd_packet_new = 1;
}

void cmd_rf_recv(char onlyonce) {
  if (at_state != AT_STATE_RX_READY || cmd_channel != at_current_channel)
    at_rxmode(cmd_channel);
  
  AT_CLR_IRQ;          // read interrupt
  while (at_state != AT_STATE_RX_WAITING) cmd_wait();

  at_read(&bytes, &len);
  while(usb_send(bytes, *len + 5)) cmd_wait();

  bytes[*len+2] = '*';
  bytes[*len+3] = '*';
  bytes[*len+4] = '*';
  bytes[*len+1] = at_get_reg(RG_PHY_RSSI);          // read RSSI value
  
  at_state = AT_STATE_RX_READY;
  if (onlyonce) cmd_mode = CMD_MODE_WAIT;
}

void cmd_rf_send(char onlyonce) {
  if (at_state != AT_STATE_TX_READY || cmd_channel != at_current_channel)
    at_txmode(cmd_channel);
  
  while(at_send(cmd_packet, cmd_packet_rx, (int)cmd_packet[1])) cmd_wait();
  AT_TX_START;
  
  cmd_packet_new = 0;
  if (onlyonce) cmd_mode = CMD_MODE_WAIT;
}

void cmd_rf_recvsend(char onlyonce) {
  cmd_rf_recv(0);
  cmd_rf_send(onlyonce);
}

void cmd_rf_sendrecv(char onlyonce) {
  cmd_rf_send(0);
  cmd_rf_recv(onlyonce);
}

char cmd_parsepacket(char** buffer, char len, volatile char* state, char state_value) {
  char *buf = *buffer;
  
  char cmd = buf[0];
  char* pkt = buf + 1;
  char sum = 0;

  if (len) {
    cmd = CMD_RAW;
    pkt = buf;
    len = len-6;
    if (buf[2] == len) {
      for (int i = 0; i < len; i++) 
        sum += buf[i+3];
      sum = ~sum;
      if (sum == buf[len+3]) {
        cmd = buf[3];
        pkt = buf + 4;
      } 
    }
  } else
    len = usb_len; // XXX hack.

  switch(cmd) {
  case CMD_SETLEDS:
    LEDS_SET(pkt[0]); 
    break;
  case CMD_FLAGS:
    cmd_ledmode = pkt[0] & FLAGS_LEDMASK; 
    cmd_tickmode = pkt[0] & FLAGS_TICKMASK; 
    break;
  case CMD_PERIPH_TEST:
    cmd_mode_changed = 1;
    cmd_periph_which = pkt[0];
    cmd_mode = CMD_MODE_PERIPH_TEST; // cmd_peripherals(pkt[0]); 
    break;
  case CMD_PERIPH_ENABLE:
    cmd_mode_changed = 1;
    cmd_periph_which = pkt[0];
    cmd_mode = CMD_MODE_PERIPH_ENABLE; // cmd_peripherals(pkt[0]); 
    break;
  case CMD_RADIO:
    cmd_channel = pkt[0]; 
    break;
  case CMD_MODE:
    if (pkt[0] != cmd_mode)
      cmd_mode_changed = 1;
    cmd_mode = pkt[0]; 
    break;
  case CMD_SENDPKT:
    cmd_mode_changed = 1;
    cmd_mode = CMD_MODE_SEND;
  case CMD_BUILDPKT:
    cmd_buildpkt(&pkt[0], len);
    break;
  }
  
  *state = state_value;
  *buffer = pkt;
  return cmd;
}

#define ONCE 1
#define LOOP 0
void cmd_loop (void) {
  static int cmd_count = 0;

  if (cmd_mode != CMD_MODE_WAIT) {
    if (cmd_ledmode == CMD_LEDMODE_ROT) LEDS_ROT;
    if (cmd_ledmode == CMD_LEDMODE_CNT) LEDS_SET(cmd_count & 0xff);
    cmd_count++;
  }

  if (cmd_mode == CMD_MODE_SNIFF) cmd_rf_recv(LOOP);
  if (cmd_mode == CMD_MODE_RECV) cmd_rf_recv(ONCE);
  if (cmd_mode == CMD_MODE_BEACON) cmd_rf_send(LOOP);
  if (cmd_mode == CMD_MODE_SEND) cmd_rf_send(ONCE);
  if (cmd_mode == CMD_MODE_RELAY) cmd_rf_recvsend(LOOP);
  if (cmd_mode == CMD_MODE_RECVSEND) cmd_rf_recvsend(ONCE);
  if (cmd_mode == CMD_MODE_SENDRECV) cmd_rf_sendrecv(ONCE);
  if (cmd_mode == CMD_MODE_SPIN) spinonce(2000,75);
  if (cmd_mode == CMD_MODE_ERROR) erroronce(2000,300);
  if (cmd_mode == CMD_MODE_PERIPH_TEST) cmd_periph(cmd_periph_which, 0);
  if (cmd_mode == CMD_MODE_PERIPH_ENABLE) cmd_periph(cmd_periph_which, 1);
    
  cmd_mode_changed = 0;
}