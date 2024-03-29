#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>
#include<time.h>
#include<prussdrv.h>
#include<pruss_intc_mapping.h>
#include<string.h>
#include<sys/time.h> // test
#include<sys/types.h>
#include<sys/socket.h>
#include<errno.h>
#include<arpa/inet.h>
#include<netinet/in.h>

//#define OPERATION_TIME 10 // OPERATION_TIME<0 : No limit
#define OPERATION_TIME -1 // OPERATION_TIME<0 : No limit

#define REFERENCE_COUNT_MAX 62000 // max num_counts of a grid cycle ignoring z-signal

//#define IP_ADDRESS "202.13.215.85" // tandem PC
//#define IP_ADDRESS "202.13.215.223" // wire grid PC at Kyoto
//#define IP_ADDRESS "192.168.0.2"// wire grid PC at Tokyo via local ethernet
#define IP_ADDRESS "133.11.6.73" // wiregridPC in Kusaka Lab. network

#define SAVETOBB 0 // 1:True(save file), 0:False(send data to PC)
#define isTCP 0 // 0:UDP, 1:TCP (Only when SAVETOBB is 0.)
#define SAVEVERBOSE 0
#define PORT 50007
#define PRUSS_INTC_CUSTOM { { PRU0_PRU1_INTERRUPT, PRU1_PRU0_INTERRUPT, PRU0_ARM_INTERRUPT, \
			      PRU1_ARM_INTERRUPT, ARM_PRU0_INTERRUPT, ARM_PRU1_INTERRUPT, 24, (char)-1 }, \
			    { {PRU0_PRU1_INTERRUPT,CHANNEL1}, {PRU1_PRU0_INTERRUPT,CHANNEL0}, \
			      {PRU0_ARM_INTERRUPT,CHANNEL2}, {PRU1_ARM_INTERRUPT,CHANNEL3}, \
			      {ARM_PRU0_INTERRUPT,CHANNEL0}, {ARM_PRU1_INTERRUPT,CHANNEL1}, \
			      {24,CHANNEL3}, {-1,-1} }, \
			    { {CHANNEL0,PRU0}, {CHANNEL1,PRU1}, {CHANNEL2, PRU_EVTOUT0}, \
			    {CHANNEL3,PRU_EVTOUT1}, {-1,-1} }, \
			    (PRU0_HOSTEN_MASK | PRU1_HOSTEN_MASK | PRU_EVTOUT0_HOSTEN_MASK | PRU_EVTOUT1_HOSTEN_MASK) \
			      }
#define ENCODER_COUNTER_SIZE 100
#define ENCODER_PACKETS_TO_SEND 1
#define IRIG_PACKETS_TO_SEND 3
#define ERROR_PACKETS_TO_SEND 1
#define TIMEOUT_PACKETS_TO_SEND 1
#define ON_OFFSET 0x0000
#define OVERFLOW_OFFSET 0x0008
#define ENCODER_READY_OFFSET 0x0010
#define ENCODER_OFFSET 0x0018
#define IRIG_READY_OFFSET 0x1850
#define IRIG_OFFSET 0x1858
#define ERROR_READY_OFFSET 0x2000
#define ERROR_OFFSET 0x2008
#define READOUT_BYTES 4
#define ENCODER_BUFFER_SIZE 2
#define ENCODER_TIMEOUT 10
#define IRIG_TIMEOUT 10
#define ENCODER_TIMEOUT_FLAG 1
#define IRIG_TIMEOUT_FLAG 2

#define PRU_CLOCKSPEED 200000000

volatile int32_t* init_prumem()
{
  volatile int32_t *p;
  prussdrv_map_prumem(PRUSS0_SHARED_DATARAM, (void**)&p);
  return p;
}

struct EncoderInfo {
  unsigned long int header;
  unsigned long int quad[ENCODER_COUNTER_SIZE];
  unsigned long int clock[ENCODER_COUNTER_SIZE];
  unsigned long int clock_overflow[ENCODER_COUNTER_SIZE];
  unsigned long int refcount[ENCODER_COUNTER_SIZE];
  unsigned long int error_signal[ENCODER_COUNTER_SIZE];
};

struct IrigInfo {
  unsigned long int header;
  unsigned long int clock;
  unsigned long int clock_overflow;
  unsigned long int info[10];
  unsigned long int synch[10];
  unsigned long int synch_overflow[10];
};

struct ErrorInfo {
  unsigned long int header;
  unsigned long int err_code;
};

struct TimeoutInfo {
  unsigned long int header;
  unsigned long int type;
};

volatile unsigned long int *on;
volatile unsigned long int *clock_overflow;
volatile unsigned long int *encoder_ready;
volatile unsigned long int encoder_read;
volatile struct EncoderInfo *encoder_packets;
volatile unsigned long int *irig_ready;
volatile struct IrigInfo *irig_packets;
volatile unsigned long int *error_ready;
volatile struct ErrorInfo *error_packets;

volatile struct EncoderInfo encoder_to_send[ENCODER_PACKETS_TO_SEND];
volatile struct IrigInfo irig_to_send[IRIG_PACKETS_TO_SEND];
volatile struct ErrorInfo error_to_send[ERROR_PACKETS_TO_SEND];
volatile struct TimeoutInfo timeout_packet[TIMEOUT_PACKETS_TO_SEND];

unsigned long int offset;
unsigned long int encd_ind, irig_ind, err_ind;
clock_t curr_time, encd_time, irig_time, tmp1_time, tmp2_time;
int sockfd;
struct sockaddr_in servaddr;
int tos_write = 0b10100100;
int tos_read;
int tos_read_len = sizeof(tos_read);

int irig_secs, irig_mins, irig_hours, irig_day, irig_year;
unsigned long long irig_pruclock;

char ifilename0[] = "Encoder1.bin";
char ifilename1[] = "Encoder2.bin";
char ifilename2[] = "IRIG1.bin";
char ifilename3[] = "IRIG2.bin";

int de_irig(unsigned long int irig_signal, int base_shift){
  return (((irig_signal >> (0+base_shift)) & 1)
            + ((irig_signal >> (1+base_shift)) & 1) * 2
            + ((irig_signal >> (2+base_shift)) & 1) * 4
            + ((irig_signal >> (3+base_shift)) & 1) * 8
            + ((irig_signal >> (5+base_shift)) & 1) * 10
            + ((irig_signal >> (6+base_shift)) & 1) * 20
            + ((irig_signal >> (7+base_shift)) & 1) * 40
            + ((irig_signal >> (8+base_shift)) & 1) * 80);
};

double usec_timestamp(){
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return tv.tv_sec + tv.tv_usec * 1e-6;
}

int write_iamhere(FILE* file, double* usec_t1, double* usec_t2, unsigned long int position){
  *usec_t1 = usec_timestamp();
  if(*usec_t1 >= *usec_t2 + 0.300){
    fseek(file,0,0); // back to the first point of the file
    fprintf(file, "%lu\n", position); // write the position
    fflush(file); // write to the output file
    *usec_t2 = usec_timestamp(); //reset time but after writing process
  }
  return 0;
}

// *********************************
// ************* MAIN **************
// *********************************
int main(int argc, char **argv)
{
  system("./pinconfig");

  prussdrv_init();

  if(prussdrv_open(PRU_EVTOUT_1) == -1){
    printf("prussdrv_open() failed\n");
  }

  tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_CUSTOM;
  prussdrv_pruintc_init(&pruss_intc_initdata);

  on = (volatile unsigned long int *)(init_prumem() + (ON_OFFSET / READOUT_BYTES));
  clock_overflow = (volatile unsigned long int *)(init_prumem() + (OVERFLOW_OFFSET / READOUT_BYTES));
  encoder_ready = (volatile unsigned long int *)(init_prumem() + (ENCODER_READY_OFFSET / READOUT_BYTES));
  encoder_packets = (volatile struct EncoderInfo *)(init_prumem() + (ENCODER_OFFSET / READOUT_BYTES));
  irig_ready = (volatile unsigned long int *)(init_prumem() + (IRIG_READY_OFFSET / READOUT_BYTES));
  irig_packets = (volatile struct IrigInfo *)(init_prumem() + (IRIG_OFFSET / READOUT_BYTES));
  error_ready = (volatile unsigned long int *)(init_prumem() + (ERROR_READY_OFFSET / READOUT_BYTES));
  error_packets = (volatile struct ErrorInfo *)(init_prumem() + (ERROR_OFFSET / READOUT_BYTES));

  char n = 0;
  for( n = 0; n < ENCODER_BUFFER_SIZE; n++){
    memset((struct EncoderInfo *) &encoder_packets[n], 0, sizeof(*encoder_packets));
  }
  memset((struct IrigInfo *) &irig_packets[0], 0, sizeof(*irig_packets));
  memset((struct IrigInfo *) &irig_packets[1], 0, sizeof(*irig_packets));
  memset((struct ErrorInfo *) &error_packets[0], 0, sizeof(*error_packets));

  *encoder_ready = 0;
  *irig_ready = 0;
  *error_ready = 0;
  encoder_read = 0;

  printf("Initializing PRU1\n");
  if(prussdrv_load_datafile(1, ifilename1) < 0){
      fprintf(stderr, "Error loading %s\n", ifilename1);
      exit(-1);
  }

  if(prussdrv_exec_program(1, ifilename0) < 0){
    fprintf(stderr, "Error loading %s\n", ifilename0);
    exit(-1);
  }

  printf("Initializing PRU0\n");
  if(prussdrv_load_datafile(0, ifilename3) < 0){
      fprintf(stderr, "Error loading %s\n", ifilename3);
      exit(-1);
  }

  if(prussdrv_exec_program(0, ifilename2) < 0){
    fprintf(stderr, "Error loading %s\n", ifilename2);
    exit(-1);
  }

  const char *socket_type = (isTCP) ? "TCP" : "UDP";
  FILE *outfile;
  FILE *irigout;
  FILE *encoder_position;
  FILE *measurement_time; //test
  time_t measurement_start, measurement_stop;
  unsigned long position;
  if(!SAVETOBB){

    if(isTCP){
      if( (sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0){
	        perror("TCP socket creation failed");
	        exit(EXIT_FAILURE);
      }
    }else{
      if( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0){
	        perror("UDP socket creation failed");
	        exit(EXIT_FAILURE);
      }
    }
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(PORT);
    if( inet_pton(AF_INET, IP_ADDRESS, &(servaddr.sin_addr.s_addr)) < 1){
      perror("server address could not be converted to binary form");
      exit(EXIT_FAILURE);
    }
    setsockopt(sockfd, IPPROTO_IP, IP_TOS, &tos_write, sizeof(tos_write));
    getsockopt(sockfd, IPPROTO_IP, IP_TOS, &tos_read, &tos_read_len);
    printf("IP %s TOS byte set to 0x%X\n", socket_type, tos_read);
    printf("   Precedence = 0x%X\n", (tos_read >> 5) & 0x7);
    printf("   TOS = 0x%X\n", (tos_read >> 1) & 0xF);
    if(isTCP){
      if( (connect(sockfd, (struct sockaddr *) &servaddr, sizeof(servaddr))) < 0){
	        perror("socket TCP connection failed");
	        exit(EXIT_FAILURE);
      }
    }
  }else{
    outfile = fopen(argv[1], "w");
    fprintf(outfile, "#TIME ERROR DIRECTION TIMERCOUNT REFERENCE\n");
    irigout = fopen("irig_output_tmp.dat", "w");
    fprintf(irigout, "#PRU sec min hour day year\n");
  }
  const int operation_time = argc>2 ? atoi(argv[2]) : (int)(OPERATION_TIME) ;
  printf("operation_time = %d\n", operation_time);
  // Measurement time file
  time(&measurement_start); //test
  measurement_time = fopen("timer.txt","w");
  fprintf(measurement_time, "Start at %ld\n", measurement_start);
  // Current position file
  encoder_position = fopen("iamhere.txt", "w");

  timeout_packet->header = 0x1234;
  encd_ind = 0;
  irig_ind = 0;
  curr_time = clock();
  int i, j = 0;
  unsigned long long int timer_count;
  double usec_t1, usec_t2 = usec_timestamp();

  printf("Initializing DAQ\n");
  printf("Notice that the Encoder Count Max is set to %d!\n", REFERENCE_COUNT_MAX);
  //printf("Ignoring IRIG timeout error\n");//please check comment out about irig below

  while( *on != 1 ){

    curr_time = clock();

    if( *encoder_ready > 0 && *encoder_ready != encoder_read ){
      if( encoder_read < ENCODER_BUFFER_SIZE ) encoder_read += 1;
      else                                     encoder_read = 1;
      offset = encoder_read - 1;
      encoder_to_send[encd_ind] = encoder_packets[offset];
      encd_ind += 1;
      encd_time = curr_time; // Update the last time the encoder data was recorded
    }
    if( *irig_ready != 0 ){
      offset = *irig_ready - 1;
      irig_to_send[irig_ind] = irig_packets[offset];
      irig_ind += 1;
      *irig_ready = 0;
      irig_time = curr_time; // Update the last time the IRIG data was recorded
      //printf("IRIG header = %d / irig_ind = %d\n", irig_packets[offset].header, irig_ind);
    }
    if( *error_ready != 0 ){
      offset = *error_ready - 1;
      error_to_send[err_ind] = error_packets[offset];
      err_ind += 1;
      *error_ready = 0;
    }

    if(!SAVETOBB){ // Send data to PC via ethernet

      if( encd_ind == ENCODER_PACKETS_TO_SEND ) {

	      if( sendto(sockfd, (struct EncoderInfo *) encoder_to_send, sizeof(encoder_to_send), MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr)) < 0){
	          fprintf(stderr, "Error sending encoder data [errorno=%d: %s]\n", errno, strerror(errno));
	          fprintf(stderr, "    Sending data size = %d (size of 0 = %d)\n", sizeof(encoder_to_send), sizeof(0));
	      }

        // write iamhere at the end of encoder_to_send
        //position = (encoder_to_send[ENCODER_PACKETS_TO_SEND-1].refcount[ENCODER_COUNTER_SIZE-1]+REFERENCE_COUNT_MAX)%REFERENCE_COUNT_MAX;
        //write_iamhere(encoder_position, &usec_t1, &usec_t2, position);

        // check measurement_stop
        time(&measurement_stop); //test
        if(measurement_stop - measurement_start > OPERATION_TIME && OPERATION_TIME>0 ){
          fprintf(measurement_time, "Stop at %ld\n", measurement_stop);
          exit(0);
        }
        // reseet encd_ind
	      encd_ind = 0;
      }

      if( irig_ind == IRIG_PACKETS_TO_SEND ){
	      //printf("%lu: sending IRIG packets\n", curr_time);
	      if( sendto(sockfd, (struct IRIGInfo *) irig_to_send, sizeof(irig_to_send), MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr)) < 0 ){
	        fprintf(stderr, "Error sending IRIG data\n");
	      }
	      irig_ind = 0;
      }

      if( err_ind == ERROR_PACKETS_TO_SEND ){
	      printf("%lu: sending error packets\n", curr_time);
	      if( sendto(sockfd, (struct ErrorInfo *) error_to_send, sizeof(error_to_send), MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr)) < 0 ){
	        fprintf(stderr, "Error sending error data\n");
	      }
	      err_ind = 0;
      }

      // Sending encoder timeout packet
      if(((double)(curr_time - encd_time))/CLOCKS_PER_SEC > ENCODER_TIMEOUT){
	      printf("%lu: sending encodet timeout packet\n", curr_time);
	      timeout_packet->type = ENCODER_TIMEOUT_FLAG;
	      if( sendto(sockfd, (struct TimeoutInfo *) &timeout_packet, sizeof(*timeout_packet), MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr)) < 0 ){
	        fprintf(stderr, "Error sending encoder timeout packet\n");
	      }
	      encd_time = curr_time; // Reset the last time the encoder was monitored
      }

      // Sending IRIG timeout packet
      if(((double)(curr_time - irig_time))/CLOCKS_PER_SEC > IRIG_TIMEOUT){
	      printf("%lu: sending IRIG timeout packet\n", curr_time);
	      timeout_packet->type = IRIG_TIMEOUT_FLAG;
	      if( sendto(sockfd, (struct TimeoutInfo *) &timeout_packet, sizeof(*timeout_packet), MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr)) < 0 ){
	        fprintf(stderr, "Error sending IRIG timeout packet\n");
	      }
	      irig_time = curr_time; // Reset the last time the IRIG was monitored
      }

    }else{ // Save data to a output file in BB

      // write encoder data
      if( encd_ind == ENCODER_PACKETS_TO_SEND ){
        if( SAVEVERBOSE == 1 ) tmp1_time = clock();
        for( i = 0; i < ENCODER_PACKETS_TO_SEND; i++ ){
          for( j = 0; j < ENCODER_COUNTER_SIZE; j++ ){
            timer_count = (unsigned long long int)encoder_to_send[i].clock[j] + ( (unsigned long long int)(encoder_to_send[i].clock_overflow[j]) << (4*8) );
            position = (encoder_to_send[i].refcount[j]+REFERENCE_COUNT_MAX)%REFERENCE_COUNT_MAX;
            fprintf(outfile, "%ld %lu %lu %llu %lu\n", time(NULL), 1-encoder_to_send[i].error_signal[j], encoder_to_send[i].quad[j], timer_count, position);
          }
        }
        // write iamhere at the end of encoder_to_send
        write_iamhere(encoder_position, &usec_t1, &usec_t2, position);
        // check measurement_stop
        time(&measurement_stop); //test
        if(measurement_stop - measurement_start > OPERATION_TIME && OPERATION_TIME>0 ){
          fprintf(measurement_time, "Stop at %ld\n", measurement_stop);
          exit(0);
        }
        if( SAVEVERBOSE == 1 ){
          tmp2_time = clock();
          printf("CPU time: %f usec (CLOCKS_PER_SEC = %d)\n", 1.e+6*(float)(tmp2_time - tmp1_time)/(float)CLOCKS_PER_SEC, CLOCKS_PER_SEC );
        }
        // reseet encd_ind
        encd_ind = 0;
      }

      // write IRIG data
      if( irig_ind == IRIG_PACKETS_TO_SEND ){
        for(i = 0; i < IRIG_PACKETS_TO_SEND; i++){
          irig_secs = de_irig(irig_to_send[i].info[0], 1);
          irig_mins = de_irig(irig_to_send[i].info[1], 0);
          irig_hours = de_irig(irig_to_send[i].info[2], 0);
          irig_day = de_irig(irig_to_send[i].info[3], 0) \
                     + de_irig(irig_to_send[i].info[4], 0) * 100;
          irig_year = de_irig(irig_to_send[i].info[5], 0);
          irig_pruclock = (unsigned long long int)irig_to_send[i].clock + ( (unsigned long long int\
)(irig_to_send[i].clock_overflow) << (4*8) );
          fprintf(irigout, "%llu %d %d %d %d %d\n", irig_pruclock, irig_secs, irig_mins, irig_hours, irig_day, irig_year);
          //printf("%llu %d %d %d %d %d\n", irig_pruclock, irig_secs, irig_mins, irig_hours, irig_day, irig_year);
          fflush(irigout); // write to the output file
        };
        // reset irig_ind
        irig_ind = 0;
      }

      // write error (TODO: implementation)
      if(err_ind == ERROR_PACKETS_TO_SEND ){
        // reset err_ind
        err_ind = 0;
      }

      // Check encoder timeout
      if(((double)(curr_time - encd_time))/CLOCKS_PER_SEC > ENCODER_TIMEOUT){
        printf("%lu: encoder timeout\n", curr_time);
        encd_time = curr_time; // Reset the last time the encoder was monitored
      }

      // Check IRIG timeout
      if(((double)(curr_time - irig_time))/CLOCKS_PER_SEC > IRIG_TIMEOUT){
        printf("%lu: IRIG timeout\n", curr_time);
        irig_time = curr_time; // Reset the last time the IRIG was monitored
      }

    } // end of saving

  } // end of while loop

  if( !SAVETOBB ){
    close(sockfd);
  }else{
    fclose(outfile);
    fclose(irigout);
  }
  fclose(encoder_position);
  fclose(measurement_time);//test

  if(*on == 1){
    prussdrv_pru_wait_event(PRU_EVTOUT_1);
    printf("ALL done\n");
    prussdrv_pru_disable(1);
    prussdrv_pru_disable(0);
    prussdrv_exit();
  }

  return 0;

}
