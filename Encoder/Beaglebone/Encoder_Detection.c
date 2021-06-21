//
//This is a modified script of Encoder_Detection.c and seems to be easy to read.
//
#include<stdlib.h>

#define TEST_COUNT 0
#define PACK_INTERVAL 100000
#define CLOCK_MAX 4294967295
unsigned int count_condition = 0;
unsigned long int previous_time;
int packing_status_flag = 0;
int direction_status_flag = 0;
int error_flag = 1; // 1:normal 0:irregular
enum TIME_STATUS {regular_time, overflow_time, counting};

//***** Shared PRU addresses *****
#define ON_ADDRESS 0x00010000
#define OVERFLOW_ADDRESS 0x00010008
#define ENCODER_READY_ADDRESS 0x00010010
#define ENCODER_ADDRESS 0x00010018
#define ENCODER_BUFFER_SIZE 2
#define ENCODER_HEADER 0x1EAF
#define ENCODER_COUNTER_SIZE 100
#define MAX_COUNTER_VALUE 0x5FFFFFFF
#define IEP 0x0002e000
#define IEP_TMR_GLB_CFG ((volatile unsigned long int *)(IEP + 0x00))
#define IEP_TMR_GLB_STS ((volatile unsigned long int *)(IEP + 0x04))
#define IEP_TMR_COMPEN ((volatile unsigned long int *)(IEP + 0x08))
#define IEP_TMR_CNT ((volatile unsigned long int *)(IEP + 0x0c))

struct ECAP {
  unsigned long int p_sample;
  unsigned long int ts;
};

struct EncoderInfo {
  unsigned long int header;
  unsigned long int quad[ENCODER_COUNTER_SIZE];
  unsigned long int clock[ENCODER_COUNTER_SIZE];
  unsigned long int clock_overflow[ENCODER_COUNTER_SIZE];
  //unsigned long int count[ENCODER_COUNTER_SIZE];
  unsigned long int refcount[ENCODER_COUNTER_SIZE];
  unsigned long int error_signal[ENCODER_COUNTER_SIZE];
};

volatile unsigned long int *on = (volatile unsigned long int *) ON_ADDRESS;
volatile unsigned long int *clock_overflow = (volatile unsigned long int *) OVERFLOW_ADDRESS;
volatile unsigned long int *encoder_ready = (volatile unsigned long int *) ENCODER_READY_ADDRESS;
volatile struct EncoderInfo *encoder_packets = (volatile struct EncoderInfo *) ENCODER_ADDRESS;

//unsigned long int input_capture_count = 0;
unsigned long int input_reference_count = 0;
unsigned long int i;
unsigned long int j;
unsigned long int edge_sample;
volatile struct ECAP ECAP;

volatile register unsigned int __R31, __R30;

int main(void){
  *IEP_TMR_GLB_STS = 1;
  *IEP_TMR_GLB_CFG = 0x11;
  *IEP_TMR_COMPEN = 0;

  *encoder_ready = 0;

  //ECAP.p_sample = 0;
  ECAP.p_sample = ((__R31 & (1 << 10)) >> 10); // initial count signal
  ECAP.ts = *IEP_TMR_CNT;

  previous_time = (unsigned long long int)*IEP_TMR_CNT;

  enum TIME_STATUS tstts;
  tstts = counting;

  *clock_overflow = 0;

  encoder_packets[0].header = ENCODER_HEADER;
  encoder_packets[1].header = ENCODER_HEADER;

  while(*on == 0){
    i = 0;
    while(i < ENCODER_BUFFER_SIZE){
      j = 0;
      while(j < ENCODER_COUNTER_SIZE){

        if((*IEP_TMR_GLB_STS & 1) == 1){
          *clock_overflow +=1;
          *IEP_TMR_GLB_STS = 1;
          packing_status_flag = 1;
        }

        ECAP.ts = *IEP_TMR_CNT;

        if(packing_status_flag){
          if(PACK_INTERVAL <= (unsigned long long int)ECAP.ts + CLOCK_MAX - (unsigned long long int)previous_time){
            tstts = overflow_time;
            packing_status_flag = 0;
          }
        }else{
          if((unsigned long long int)previous_time + PACK_INTERVAL <= (unsigned long long int)ECAP.ts){
            tstts = regular_time;
          }
        }

        switch(tstts){
          case regular_time:
          case overflow_time:

            encoder_packets[i].clock[j] = ECAP.ts;
            encoder_packets[i].clock_overflow[j] = (*clock_overflow);
            //encoder_packets[i].count[j] = input_capture_count;
            encoder_packets[i].refcount[j] = input_reference_count;
            encoder_packets[i].quad[j] = direction_status_flag;
            encoder_packets[i].error_signal[j] = error_flag;

            previous_time = ECAP.ts;
            tstts = counting;
            j += 1;
            break;

          default:
            break;
        }

        error_flag = ((__R31 & (1 << 7)) >> 7);
        edge_sample = ((__R31 & (1 << 10)) >> 10);
        count_condition = edge_sample ^ ECAP.p_sample;

        if( (((__R31 & (1 << 9)) >> 9) & 0x1) == 1){
          input_reference_count = 0;
        }

        if(count_condition){
          /*if(input_capture_count == MAX_COUNTER_VALUE){
            input_capture_count = 0;
            }*/

          if(edge_sample == 1){
            if( ((__R31 & (1 << 8)) >> 8) == 0 ){
              direction_status_flag = 0;
              //input_capture_count += 1;
              input_reference_count += 1;
            }else{
              direction_status_flag = 1;
              //input_capture_count -= 1;
              input_reference_count -= 1;
            }
          }else{
            if( ((__R31 & (1 << 8)) >> 8) == 0){
              direction_status_flag = 1;
              //input_capture_count -= 1;
              input_reference_count -= 1;
            }else{
              direction_status_flag = 0;
              //input_capture_count += 1;
              input_reference_count += 1;
            }
          }
          ECAP.p_sample = edge_sample;
        }

      }
      *encoder_ready = (i + 1);
      i += 1;
    }
  }
  __R31 = 0x28;
  __halt();
}
