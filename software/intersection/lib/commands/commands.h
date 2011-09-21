#ifndef __COMMANDS_H
#define __COMMANDS_H

#define CMD_RESERVED      0
#define CMD_RAW           1
#define CMD_SETLEDS       2

#define CMD_FLAGS         3
#  define FLAGS_LEDMASK   0x03
#    define CMD_LEDMODE_NONE    0x00
#    define CMD_LEDMODE_CNT     0x01
#    define CMD_LEDMODE_ROT     0x02
#    define CMD_LEDMODE_DISP    0x03
#  define FLAGS_TICKMASK  0x04
#    define CMD_TICK            0x00
#    define CMD_NOTICK          0x04
  char cmd_ledmode;
  char cmd_tickmode;

#define CMD_PERIPH_TEST   4
#define CMD_PERIPH_ENABLE 5
#  define CMD_PERIPH_RADIO  0x01
#  define CMD_PERIPH_PWM    0x02
#  define CMD_PERIPH_GYRO   0x04
#  define CMD_PERIPH_XL     0x08
#  define CMD_PERIPH_USB    0x10
#  define CMD_PERIPH_IR     0x20
  char cmd_periph_which;

#define CMD_MODE          6
#  define CMD_MODE_WAIT       1
#  define CMD_MODE_SPIN       2
#  define CMD_MODE_ERROR      3
#  define CMD_MODE_RECV       4
#  define CMD_MODE_SNIFF      5
#  define CMD_MODE_SEND       6
#  define CMD_MODE_BEACON     7
#  define CMD_MODE_RECVSEND   8
#  define CMD_MODE_RELAY      9
#  define CMD_MODE_SENDRECV   12
#  define CMD_MODE_PERIPH_TEST    10
#  define CMD_MODE_PERIPH_ENABLE  11
#  define CMD_MODE_IMU_LOOP       20
  char cmd_mode;
  char cmd_mode_changed;

#define CMD_RADIO         7
  char cmd_channel;

#define CMD_BUILDPKT      8
#define CMD_SENDPKT       9
  char cmd_packet[AT_MAX_PACKET_LEN + 4];
  char cmd_packet_rx[AT_MAX_PACKET_LEN + 4];
  char cmd_packet_new;

#define CMD_SETCONTROLS   20
  
#define cmd_wait() {if (cmd_mode_changed) return;}
  
void dma_init(void);
void cmd_init(void);
int cmd_periph(char which, char enable);

void cmd_buildpkt(char *buf, int len);
void cmd_rf_recv(char onlyonce);
void cmd_rf_send(char onlyonce);
void cmd_rf_recvsend(char onlyonce);

char cmd_parsepacket(char** buf, char len, volatile char* state, char state_value);
void cmd_loop (void);

#endif