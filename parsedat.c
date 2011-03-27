#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

/* 22 byte entries 
   little endian
   4 byte Unix timestamp
   2 byte 16 bit val
*/

int getwordLE(FILE *fptr, uint32_t *word) {
  int tmp = 0;
  int buf = 0;
  int i;
  for (i=0; i<4; i++) {
    buf = getc(fptr);
    if (buf == EOF) return -1;
    tmp |= buf << (i*8);
  }
  *word = tmp;
  return 0;
}

int gethalfLE(FILE *fptr, uint16_t *word) {
  int tmp = 0;
  int buf = 0;
  int i;
  for (i=0; i<2; i++) {
    buf = getc(fptr);
    if (buf == EOF) return -1;
    tmp |= buf << (i*8);
  }
  *word = tmp;
  return 0;
}

float cvt(uint32_t word) {
  float v = 0.0;
  uint32_t *bits = (uint32_t *) &v;
  *bits = word;
  return v;
}

int main (int argc, char *argv[]) {
  FILE *datfile = stdin;
  FILE *ofile = stdout;
  uint16_t val16;
  uint32_t vals[4];
  int status = 0;
  int entries = 0;
  time_t timestamp = 0;
  struct tm *ts;
  char timestr[80];
  int tlen;
  if (argc >= 2) {
    if ((datfile = fopen(argv[1], "r")) == 0) {
      printf("error opening input file %s\n",argv[1]);
      exit(1);
    }
  }
  if (argc == 3) {
    if ((ofile = fopen(argv[2],"w")) == 0) {
      printf("error opening output file %s\n",argv[2]);
      exit(1);
    }
  }
  if (ofile != stdout) {
    printf("Parsing %s to %s\n",argv[1],argv[2]);
  }
  while (status == 0) {
    entries++;
    status |= getwordLE(datfile, (uint32_t *) &timestamp);
    status |= gethalfLE(datfile, &val16);
    status |= getwordLE(datfile, vals+0);
    status |= getwordLE(datfile, vals+1);
    status |= getwordLE(datfile, vals+2);
    status |= getwordLE(datfile, vals+3);
    ts = localtime(&timestamp);
    tlen = strftime(timestr,80,"%Y-%m-%d %T", ts);
    //    printf("%s,\t%04X,\t%08X,\t%08X,\t%08X,\t%08X\n",timestr, val16, 
    //    	   vals[0],vals[1],vals[2],vals[3]);
    fprintf(ofile,"%u,\t%s,\t%04X,\t%.2f,\t%.2f,\t%.2f,\t%.2f\n",
	    (uint32_t) timestamp, timestr, val16, 
	    cvt(vals[0]),cvt(vals[1]),cvt(vals[2]),cvt(vals[3]));
  }
  if (ofile != stdout) {
    printf("%d entries\n",entries);
  }
  fclose(datfile);
  fclose(ofile);
  return 0;
}
