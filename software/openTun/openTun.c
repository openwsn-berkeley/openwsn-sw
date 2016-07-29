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

const char *progname;

void read_from_serial(int motefd)
{
  unsigned inbuf[2];
  static int count;

  if(read(motefd, inbuf, 1) > 0) {
    printf("%02x ", inbuf[0]);
    count++;
    if((count & 0x0f) == 0) {
      printf("\n");
    }
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

int
main(int argc, char **argv)
{
  int maxfd;
  int ret;
  fd_set rset, wset;
  int motefd;

  if(argc != 2) {
    fprintf(stderr, "Usage: openTun /dev/ttyXXX\n");
    exit(2);
  }

  motefd = open(argv[1], O_RDWR|O_NDELAY);

  if(motefd < 0) {
    perror("open");
    exit(1);
  }
  setup_tty(motefd);

  progname = argv[0];

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
}
