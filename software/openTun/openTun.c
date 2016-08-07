/*
 * Copyright (c) 2016, Michael Richardson <mcr@sandelman.ca>
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. The name of the author may not be used to endorse or promote
 *    products derived from this software without specific prior
 *    written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>

#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <termios.h>
#include <sys/ioctl.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <getopt.h>

//#include "opendefs.h"
const char *progname;

enum serframe_constants {
  SERFRAME_MOTE2PC_DATA   = 'D',
  SERFRAME_MOTE2PC_STATUS = 'S',
  SERFRAME_MOTE2PC_INFO   = 'I',
  SERFRAME_MOTE2PC_ERROR  = 'E',
  SERFRAME_MOTE2PC_CRITICAL='C',
  SERFRAME_MOTE2PC_REQUEST ='R',
  SERFRAME_MOTE2PC_SNIFFED_PACKET ='P',

  SERFRAME_PC2MOTE_SETDAGROOT= 'R',
  SERFRAME_PC2MOTE_DATA    ='D',
  SERFRAME_PC2MOTE_TRIGGERSERIALECHO = 'S',
  SERFRAME_PC2MOTE_COMMAND_GD        = 'G',

  SERFRAME_ACTION_YES      ='Y',
  SERFRAME_ACTION_NO       ='N',
  SERFRAME_ACTION_TOGGLE   ='T',
};

enum inputstate {
  START = 0,
  PROCESSING,
  ESCAPED,
  ENDFRAME
};

enum hdlc {
  HDLC_FLAG              = 0x7e,
  HDLC_FLAG_ESCAPED      = 0x5e,
  HDLC_ESCAPE            = 0x7d,
  HDLC_ESCAPE_ESCAPED    = 0x5d,
  HDLC_CRCINIT           = 0xffff,
  HDLC_CRCGOOD           = 0xf0b8,
};

unsigned short FCS16TAB[]={
  0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
  0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
  0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
  0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
  0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
  0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
  0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
  0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
  0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
  0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
  0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
  0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
  0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
  0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
  0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
  0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
  0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
  0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
  0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
  0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
  0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
  0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
  0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
  0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
  0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
  0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
  0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
  0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
  0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
  0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
  0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
  0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78,
};


/*
 * size of structure
 * 1+2+1+1+1+1 + 8 + 8 + 1+1+1+5 = 31
 *
 */
struct scheduleRow {
  unsigned char  row;
  unsigned short slotOffset;
  unsigned char  type;
  unsigned char  shared;
  unsigned char  channelOffset;
  unsigned char  neighbor_type;
  unsigned long long neighbor_bodyH;
  unsigned long long neighbor_bodyL;
  unsigned char  numRx;
  unsigned char  numTx;
  unsigned char  numTxACK;
  unsigned char  lastUsedAsn[5];
};

/*
 * size of structure
 * 1+1+1+1 + 1+1+8+8 + 2+1+1+1 + 1+1+5+1 = 35
 *
 */
struct neighborRow {
  unsigned char  row;
  unsigned char  used;
  unsigned char  parentPreference;
  unsigned char  stableNeighbor;
  unsigned char  switchStabilityCounter;
  unsigned char  addr_type;
  unsigned long long addr_bodyH;
  unsigned long long addr_bodyL;
  unsigned short DAGrank;
  char           rssi;
  unsigned char  numRx;
  unsigned char  numTx;
  unsigned char  numTxACK;
  unsigned char  numWraps;
  unsigned char  asn[5];
  unsigned char  joinPrio;
};



struct moteStatus {
  /* isSync */
  unsigned char isSync;

  /* IdManager */
  unsigned char isDAGroot;
  unsigned char myPANID_0;
  unsigned char myPANID_1;
  unsigned char my16bID_0;
  unsigned char my16bID_1;
  unsigned char my64bID_0;
  unsigned char my64bID_1;
  unsigned char my64bID_2;
  unsigned char my64bID_3;
  unsigned char my64bID_4;
  unsigned char my64bID_5;
  unsigned char my64bID_6;
  unsigned char my64bID_7;
  unsigned char myPrefix_0;
  unsigned char myPrefix_1;
  unsigned char myPrefix_2;
  unsigned char myPrefix_3;
  unsigned char myPrefix_4;
  unsigned char myPrefix_5;
  unsigned char myPrefix_6;
  unsigned char myPrefix_7;

  /* MyDagRank */
  unsigned short myDAGrank;

  /* OutputBuffer */
  unsigned short index_write;
  unsigned short index_read;

  /* Asn */
  unsigned char  asn[5];

  /* MacStats */
  unsigned char numSyncPkt;
  unsigned char numSyncAck;
  short         minCorrection;
  short         maxCorrection;
  unsigned char numDeSync;
  unsigned int  numTicsOn;
  unsigned int  numTicsTotal;

  /* ScheduleRow */
#define MAX_SCHEDULEROW 64
  struct scheduleRow  sched_rows[MAX_SCHEDULEROW];
  int        sched_rows_max;

  /* Backoff */
  unsigned char backoffExponent;
  unsigned char backoff;

  /* QueueRow */
#define QUEUE_ROW_COUNT 10
  struct creatorOwner {
    unsigned char creator;
    unsigned char owner;
  } queueRow[QUEUE_ROW_COUNT];

  /* NeighborsRow */
#define MAX_NEIGHBORS_ROW 64
  struct neighborRow neighbor_rows[MAX_NEIGHBORS_ROW];
  int neighbor_rows_max;

  /* kaPeriod */
  unsigned int kaPeriod;
};


unsigned int tooShort=0;
unsigned int verbose =0;
struct moteStatus stats;

char tput_init[]={0x1b,0x5b,0x21,0x70,0x1b,0x5b,0x3f,0x33,
                  0x3b,0x34,0x6c,0x1b,0x5b,0x34,0x6c,0x1b,0x3e};
char tput_clear[]={0x1b,0x5b,0x48,0x1b,0x5b,0x32,0x4a};
char tput_cup00[]={0x1b,0x5b,0x31,0x3b,0x31,0x48};

void screen_init(void)
{
  puts(tput_init);
}

void dump_screen(struct moteStatus *ms)
{
  int i;
  if(!verbose) {
    puts(tput_clear);
    puts(tput_cup00);
  }

  printf("DAG: %02d   DAGRANK: %03d  PANID: %02x%02x    SHORT: %02x%02x\n",
         ms->isDAGroot, ms->myDAGrank,
         ms->myPANID_0, ms->myPANID_1, ms->my16bID_0, ms->my16bID_1);

  printf("EUI64: %02x-%02x-%02x-%02x-%02x-%02x-%02x-%02x\n",
         ms->my64bID_0, ms->my64bID_1, ms->my64bID_2, ms->my64bID_3,
         ms->my64bID_4, ms->my64bID_5, ms->my64bID_6, ms->my64bID_7);

  printf("IPv6:  %02x%02x:%02x%02x:%02x%02x:%02x%02x\n",
         ms->myPrefix_0, ms->myPrefix_1, ms->myPrefix_2, ms->myPrefix_3,
         ms->myPrefix_4, ms->myPrefix_5, ms->myPrefix_6, ms->myPrefix_7);

  printf("\nASN:   %02x %02x %02x %02x %02x\n",
         ms->asn[0],         ms->asn[1],         ms->asn[2],
         ms->asn[3],         ms->asn[4]);

  printf("\nSched    Row: %03d\n", ms->sched_rows_max);
  printf(  "Neighbor Row: %03d\n", ms->neighbor_rows_max);

  printf("Schedule:    ASN               offset   sent/ack     Rx  neighbor body ------------------\n");
  for(i=0; i<ms->sched_rows_max; i++) {
    struct scheduleRow *sr = &ms->sched_rows[i];
    printf(" %02u lASN: %02x%02x%02x%02x%02x  CHAN: %03d/%05d Tx:%03d/%03d Rx: %03d %016lx%016lx\n",
           sr->row,
           sr->lastUsedAsn[0], sr->lastUsedAsn[1],
           sr->lastUsedAsn[2], sr->lastUsedAsn[3], sr->lastUsedAsn[4],
           sr->channelOffset, sr->slotOffset,
           sr->numTx, sr->numTxACK, sr->numRx,
           sr->neighbor_bodyH,
           sr->neighbor_bodyL);
  }
  printf("\nNeighbours:\n");
  for(i=0; i<ms->neighbor_rows_max; i++) {
    struct neighborRow *nr = &ms->neighbor_rows[i];
    printf(" %02u ASN: %02x%02x%02x%02x%02x  R:%05d %03d %03d Tx:%03d/%03d Rx: %03d %016lx%016lx\n",
           nr->row,
           nr->asn[0], nr->asn[1],
           nr->asn[2], nr->asn[3], nr->asn[4],
           nr->DAGrank, nr->addr_type, nr->stableNeighbor,
           nr->numTx, nr->numTxACK, nr->numRx,
           nr->addr_bodyH,
           nr->addr_bodyL);
  }

}

void parse_idmanager(unsigned char inBuf[], unsigned int inLen)
{
  if(inLen < 21+4) {
    tooShort++;
    return;
  }

  stats.isDAGroot = inBuf[4];
  stats.myPANID_0 = inBuf[5];
  stats.myPANID_1 = inBuf[6];
  stats.my16bID_0 = inBuf[7];
  stats.my16bID_1 = inBuf[8];
  stats.my64bID_0 = inBuf[9];
  stats.my64bID_1 = inBuf[10];
  stats.my64bID_2 = inBuf[11];
  stats.my64bID_3 = inBuf[12];
  stats.my64bID_4 = inBuf[13];
  stats.my64bID_5 = inBuf[14];
  stats.my64bID_6 = inBuf[15];
  stats.my64bID_7 = inBuf[16];
  stats.myPrefix_0= inBuf[17];
  stats.myPrefix_1= inBuf[18];
  stats.myPrefix_2= inBuf[19];
  stats.myPrefix_3= inBuf[20];
  stats.myPrefix_4= inBuf[21];
  stats.myPrefix_5= inBuf[22];
  stats.myPrefix_6= inBuf[23];
  stats.myPrefix_7= inBuf[24];
}

void parse_macstats(unsigned char inBuf[], unsigned int inLen)
{
  if(inLen < 15+4) {
    tooShort++;
    return;
  }

  stats.numSyncPkt = inBuf[5];
  stats.numSyncAck = inBuf[6];
  stats.minCorrection = inBuf[7] + inBuf[8]<<8;
  stats.maxCorrection = inBuf[9] + inBuf[10]<<8;
  stats.numDeSync  = inBuf[11];
  stats.numTicsOn  = inBuf[12] + inBuf[13] << 8 + inBuf[14] << 16 + inBuf[15] << 24;
  stats.numTicsTotal=inBuf[16] + inBuf[17] << 8 + inBuf[18] << 16 + inBuf[19] << 24;
}

void parse_queueRow(unsigned char inBuf[], unsigned int inLen)
{
  unsigned int i;
  unsigned int queueCount = 4;

  if(inLen < (QUEUE_ROW_COUNT*2)+4) {
    tooShort++;
    return;
  }

  for(i=0; i < QUEUE_ROW_COUNT; i++) {
    stats.queueRow[i].creator = inBuf[queueCount++];
    stats.queueRow[i].owner   = inBuf[queueCount++];
  }
}

void parse_scheduleRow(unsigned char inBuf[], unsigned int inLen)
{
  struct scheduleRow sr;

  if(inLen < (31+4)) {
    tooShort++;
    return;
  }

  sr.row        = inBuf[4];
  sr.slotOffset = inBuf[5] + inBuf[6] << 8;
  sr.type       = inBuf[7];
  sr.shared     = inBuf[8];
  sr.channelOffset = inBuf[9];
  sr.neighbor_type = inBuf[10];
  sr.neighbor_bodyH= (unsigned long long)inBuf[11] +
    (unsigned long long)inBuf[12] << 8 +
    (unsigned long long)inBuf[13] << 16 +
    (unsigned long long)inBuf[14] << 24 +
    (unsigned long long)inBuf[15] << 32 +
    (unsigned long long)inBuf[16] << 40 +
    (unsigned long long)inBuf[17] << 48 +
    (unsigned long long)inBuf[18] << 56;
  sr.neighbor_bodyL= (unsigned long long)inBuf[19] +
    (unsigned long long)inBuf[20] << 8 +
    (unsigned long long)inBuf[21] << 16 +
    (unsigned long long)inBuf[22] << 24 +
    (unsigned long long)inBuf[23] << 32 +
    (unsigned long long)inBuf[24] << 40 +
    (unsigned long long)inBuf[25] << 48 +
    (unsigned long long)inBuf[26] << 56;

  sr.numRx     = inBuf[27];
  sr.numTx     = inBuf[28];
  sr.numTxACK  = inBuf[29];

  sr.lastUsedAsn[0]  = inBuf[30];
  sr.lastUsedAsn[2]  = inBuf[31];
  sr.lastUsedAsn[1]  = inBuf[32];
  sr.lastUsedAsn[4]  = inBuf[33];
  sr.lastUsedAsn[3]  = inBuf[34];

  if(sr.row < MAX_SCHEDULEROW) {
    stats.sched_rows[sr.row] = sr;
    if(stats.sched_rows_max <= sr.row) {
      stats.sched_rows_max = sr.row;
    }
  }

};


void parse_neighborRow(unsigned char inBuf[], unsigned int inLen)
{
  struct neighborRow nr;

  if(inLen < (35+4)) {
    tooShort++;
    return;
  }

  nr.row        = inBuf[4];
  nr.used       = inBuf[5];
  nr.parentPreference = inBuf[6];
  nr.stableNeighbor= inBuf[7];
  nr.switchStabilityCounter = inBuf[8];
  nr.addr_type  = inBuf[9];

  nr.addr_bodyH = (unsigned long long)inBuf[10] +
    (unsigned long long)inBuf[11] << 8 +
    (unsigned long long)inBuf[12] << 16 +
    (unsigned long long)inBuf[13] << 24 +
    (unsigned long long)inBuf[14] << 32 +
    (unsigned long long)inBuf[15] << 40 +
    (unsigned long long)inBuf[16] << 48 +
    (unsigned long long)inBuf[17] << 56;

  nr.addr_bodyL = (unsigned long long)inBuf[18] +
    (unsigned long long)inBuf[19] << 8 +
    (unsigned long long)inBuf[20] << 16 +
    (unsigned long long)inBuf[21] << 24 +
    (unsigned long long)inBuf[22] << 32 +
    (unsigned long long)inBuf[23] << 40 +
    (unsigned long long)inBuf[24] << 48 +
    (unsigned long long)inBuf[25] << 56;

  nr.DAGrank = inBuf[26] + inBuf[27] << 8;
  nr.rssi    = inBuf[28];
  nr.numRx   = inBuf[29];
  nr.numTx   = inBuf[30];
  nr.numTxACK= inBuf[31];
  nr.numWraps= inBuf[32];
  nr.asn[0]  = inBuf[33];
  nr.asn[2]  = inBuf[34];
  nr.asn[1]  = inBuf[35];
  nr.asn[4]  = inBuf[36];
  nr.asn[3]  = inBuf[37];
  nr.joinPrio= inBuf[38];

  if(nr.row < MAX_NEIGHBORS_ROW) {
    stats.neighbor_rows[nr.row] = nr;
    if(stats.neighbor_rows_max <= nr.row) {
      stats.neighbor_rows_max = nr.row;
    }
  }
};


void parse_status(unsigned char inBuf[], unsigned int inLen)
{
  if(inLen < 4) return;
  unsigned int moteId = inBuf[1] + inBuf[2]<<8;
  unsigned int statusElem = inBuf[3];

  if(verbose) printf("moteId %04x status: %u --:", moteId, statusElem);
  switch(statusElem) {
  case 0:
    dump_screen(&stats);
    break;

  case 1:
    parse_idmanager(inBuf, inLen);
    break;

  case 2:
    stats.myDAGrank = inBuf[4];
    break;

  case 3:
    if(inLen >= 8) {
      stats.index_read = inBuf[4] + inBuf[5]<<8;
      stats.index_write= inBuf[6] + inBuf[7]<<8;
    }
    break;

  case 4:
    if(inLen >= 5 + 4) {
      stats.asn[0]  = inBuf[4];
      stats.asn[2]  = inBuf[5];
      stats.asn[1]  = inBuf[6];
      stats.asn[4]  = inBuf[7];
      stats.asn[3]  = inBuf[8];
    }
    break;

  case 5:
    parse_macstats(inBuf, inLen);
    break;

  case 6:
    if(verbose) printf("ScheduleRow\n");
    parse_scheduleRow(inBuf, inLen);
    break;

  case 7:
    if(inLen >= 6) {
      stats.backoffExponent = inBuf[4];
      stats.backoff =         inBuf[5];
    }
    break;

  case 8:
    if(verbose) printf("QueueRow\n");
    break;

  case 9:
    if(verbose) printf("NeighborsRow\n");
    break;

  case 10:
    /* kaPeriod */
    if(inLen >= 8) {
      stats.kaPeriod = inBuf[4] + inBuf[5] << 8 + inBuf[6] << 16 + inBuf[7] << 24;
    }
    break;

  default:
    printf("unknown\n");
    break;
  }

}

void process_input(unsigned char inBuf[], unsigned int inLen)
{
  int i;
  switch(inBuf[0]) {
  case SERFRAME_MOTE2PC_DATA:
    if(verbose) {
      printf("mote2pc data(%u)\n  ", inLen);

      for(i=1; i<inLen; i++) {
        printf("%02x ", inBuf[i]);
      }
      printf("\n");
    }
    break;

  case SERFRAME_MOTE2PC_STATUS:
    if(verbose) printf("mote2pc status(%u) \n  ", inLen);
    parse_status(inBuf, inLen);
    break;

  case SERFRAME_MOTE2PC_INFO:
    if(verbose) printf("mote2pc info\n");
    break;

  case SERFRAME_MOTE2PC_ERROR:
    if(verbose) printf("mote2pc error\n");
    break;

  case SERFRAME_MOTE2PC_CRITICAL:
    if(verbose) printf("mote2pc critical\n");
    break;

  case SERFRAME_MOTE2PC_REQUEST:
    if(verbose) {
      printf("mote2pc request(%u)\n  ", inLen);
      for(i=1; i<inLen; i++) {
        printf("%02x ", inBuf[i]);
      }
      printf("\n");
    }
    break;

  case SERFRAME_MOTE2PC_SNIFFED_PACKET:
    if(verbose) printf("mote2pc sniffed\n");
    break;
#if 0
  case SERFRAME_PC2MOTE_SETDAGROOT:
    printf("pc2mote setdagroot\n");
    break;
  case SERFRAME_PC2MOTE_DATA:
    printf("pc2mote data\n");
    break;
  case SERFRAME_PC2MOTE_TRIGGERSERIALECHO:
    printf("pc2mote triggerserialecho\n");
    break;
  case SERFRAME_PC2MOTE_COMMAND_GD:
    printf("pc2mote GD\n");
    break;
#endif
  case SERFRAME_ACTION_YES:
    if(verbose) printf("action yes\n");
    break;
  case SERFRAME_ACTION_NO:
    if(verbose) printf("action no\n");
    break;
  case SERFRAME_ACTION_TOGGLE:
    if(verbose) printf("action toggle\n");
    break;
  default:
    printf("invalid comment: %02x\n", inBuf[0]);
    break;
  }
}

void process_byte(unsigned char byte)
{
  static enum inputstate currentstate;
  static int  inPos;
  static char inBuf[2048];

  switch(currentstate) {
  case START:
    switch(byte) {
    case HDLC_FLAG:
      inPos = 0;
      currentstate = PROCESSING;
      break;

#if 0
    default:
      /* eat byte, continue */
      break;
#endif
    }
    break;

  case PROCESSING:
    switch(byte) {
    case HDLC_FLAG:
      /* end of packet */
      currentstate = ENDFRAME;
      break;

    case HDLC_ESCAPE:
      currentstate = ESCAPED;
      break;

    default:
      inBuf[inPos++] = byte;
      break;
    }
    break;

  case ESCAPED:
    switch(byte) {
    case HDLC_FLAG_ESCAPED:
      inBuf[inPos++] = HDLC_FLAG;
      break;

    case HDLC_ESCAPE_ESCAPED:
      inBuf[inPos++] = HDLC_ESCAPE;
      break;

      /* should not happen, unless bytes get lost */
    case HDLC_FLAG:
      currentstate = ENDFRAME;

    default:
      inBuf[inPos++] = byte;
      break;
    }
    currentstate = PROCESSING;
    break;

  case ENDFRAME:
    break;
  }

  if(currentstate == ENDFRAME) {
    unsigned int i;
    unsigned short crc = HDLC_CRCINIT;

    /* checkout the CRC, and if it is okay, pass frame upwards */
    for(i=0; i < inPos; i++) {
      unsigned char b = inBuf[i];
      crc = (crc>>8)^FCS16TAB[((crc^(b)) & 0xff)];
    }
    if(crc == HDLC_CRCGOOD) {
      /* good crc! */
      inPos -= 2;
      process_input(inBuf, inPos);
    } else {
      fprintf(stderr, "bad CRC: %02x vs %02x len=%u\n", crc,
              HDLC_CRCGOOD, inPos);
    }

    currentstate = START;
  }
}

void read_from_serial(int motefd)
{
  unsigned char inbuf[2];
  static int count;

  if(read(motefd, inbuf, 1) > 0) {
    process_byte(inbuf[0]);
  }
}

void setup_tty(int fd)
{
  struct termios tty;
  speed_t speed = B115200;
  int i;

  if(tcflush(fd, TCIOFLUSH) == -1) {
    perror("tcflush");
    exit(10);
  }

  if(tcgetattr(fd, &tty) == -1) {
    perror("tcgetattr");
    exit(10);
  }

  cfmakeraw(&tty);

  /* Nonblocking read. */
  tty.c_cc[VTIME] = 0;
  tty.c_cc[VMIN] = 0;
  tty.c_cflag &= ~CRTSCTS;
  tty.c_iflag &= ~IXON;
  tty.c_cflag &= ~HUPCL;
  tty.c_cflag &= ~CLOCAL;

  cfsetispeed(&tty, speed);
  cfsetospeed(&tty, speed);

  if(tcsetattr(fd, TCSAFLUSH, &tty) == -1) {
    perror("tcsetattr");
    exit(10);
  }
}

void usage(void)
{
  fprintf(stderr, "openTun [--verbose] device\n");
  exit(10);
}

static struct option const longopts[] =
{
    { "help",      0, 0, '?'},
    { "verbose",   1, 0, 'v'},
};

int
main(int argc, char **argv)
{
  int maxfd;
  int ret;
  fd_set rset, wset;
  int motefd;
  int c;
  char *serialPort = "/dev/ttyAMA0";


  while((c = getopt_long(argc, argv, "", longopts, NULL)) != -1) {
    switch(c) {
    case '?':
    default:
      usage();
    }
  }

  if(optind < argc) {
    serialPort = argv[optind];
  }

  motefd = open(serialPort, O_RDWR|O_NDELAY);

  if(motefd < 0) {
    perror("open");
    exit(1);
  }
  setup_tty(motefd);

  progname = argv[0];

  stats.sched_rows_max = -1;
  stats.neighbor_rows_max = -1;
  screen_init();

  while(1) {
    maxfd = 0;
    FD_ZERO(&rset);
    FD_ZERO(&wset);

    FD_SET(motefd, &rset);	/* Read from tty ASAP! */
    if(motefd > maxfd) maxfd = motefd;

    ret = select(maxfd + 1, &rset, &wset, NULL, NULL);
    if(ret == -1 && errno != EINTR) {
      perror("select");
    } else if(ret > 0) {

      if(FD_ISSET(motefd, &rset)) {
        read_from_serial(motefd);
      }
    }
  }

  exit(0);
}

