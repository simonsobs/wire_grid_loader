//
//This is the code for signal counting with PRU 200MHz clock
//
//program continues to count signals while variable 'on' is set to "*on == 0"
//
//PRU sends a packet of 100 counts data to Shared Memory and the memory
//holds three packets on its buffer
//
//the readout speed of the BeagleBone CPU is too slow to correctly read
//all the count data of PRU when a signal frequency is higher than 10kHz
//
//H.Nakata took over S.Adachi's code on 27.Jul.2020
//
#include <stdlib.h>

#define TEST_COUNT 0 // default: 0
#define TEST_TIMEPERIOD 1./2.e+3 // default: 0
unsigned int count_condition=0;
unsigned long int current_time; //use this only when TEST_COUNT == 0
unsigned long int previous_time;
#define COUNT_INTERVAL 75000
#define CLOCK_MAX 2147483647//this is pow(2,31)-1; default pow(2,32)-1
enum time_status {regular_time,overflow_time,counting};

// ***** Shared PRU addresses *****
// Address for shared variable 'on' to tell that the PRU is still sampling
#define ON_ADDRESS 0x00010000
// Address for shared variable 'clock_overflow' to count the overflows
#define OVERFLOW_ADDRESS 0x00010008

// Counter-specific addresses
// Address to where the packet identifier will be stored
#define ENCODER_READY_ADDRESS 0x00010010
// Address for Counter Packets to start being written to
#define ENCODER_ADDRESS 0x00010018
// Number of encoder data buffer
#define ENCODER_BUFFER_SIZE 3 // >=2, default:2

// Counter packet format data
// Counter header
#define ENCODER_HEADER 0x1EAF
// Size of edges to sample before sending packet
//#define ENCODER_COUNTER_SIZE 150
#define ENCODER_COUNTER_SIZE 100 // Because the refcount is added, the capacity of shared memory is in short if this is 150.
//#define ENCODER_COUNTER_SIZE 10 // Because the refcount is added, the capacity of shared memory is in short if this is 151.
// ~75% of the storable max counter value
#define MAX_COUNTER_VALUE 0x5FFFFFFF

// IEP (Industrial Ethernet Peripheral) Registers
// IEP base address
#define IEP 0x0002e000
// Register IEP Timer configuration
#define IEP_TMR_GLB_CFG ((volatile unsigned long int *)(IEP + 0x00))
// Register to check for clock overflows
#define IEP_TMR_GLB_STS ((volatile unsigned long int *)(IEP + 0x04))
// Register to configure compensation clock
#define IEP_TMR_COMPEN ((volatile unsigned long int *)(IEP + 0x08))
// Register for the IEP clock (32-bit, 200MHz)
#define IEP_TMR_CNT ((volatile unsigned long int *)(IEP + 0x0c))

// Structure to sample PRU input and determine edges
struct ECAP {
  // Previous sample of the input register __R31
  unsigned long int p_sample;
  // Time stamp of edge seen
  unsigned long int ts;
};

// Structure to store clock count of edges and
// the number of times the clock has overflowed
struct EncoderInfo {
  unsigned long int header;
  unsigned long int quad;
  unsigned long int clock[ENCODER_COUNTER_SIZE];
  unsigned long int clock_overflow[ENCODER_COUNTER_SIZE];
  unsigned long int count[ENCODER_COUNTER_SIZE];
  unsigned long int refcount[ENCODER_COUNTER_SIZE];
};

// Pointer to the 'on' variable
volatile unsigned long int* on = (volatile unsigned long int *) ON_ADDRESS;
// Pointer to the overflow variable
// Overflow variable is incremented everytime the clock overflows
volatile unsigned long int* clock_overflow = (volatile unsigned long int *) OVERFLOW_ADDRESS;

// Pointer to packet identifier and overflow variable
volatile unsigned long int* encoder_ready = (volatile unsigned long int *) ENCODER_READY_ADDRESS;
// Pointer to complete packet structure
volatile struct EncoderInfo* encoder_packets = (volatile struct EncoderInfo *) ENCODER_ADDRESS;

//  ***** LOCAL VARIABLES *****

// Variable to let PRU know that a quadrature sample
// is needed on rising edge
unsigned long int quad_needed;
// Variable to count number of edges seen
unsigned long int input_capture_count;
// Variable to count number of edges seen from reference point
unsigned long int input_reference_count;
// Variable used to write to two different blocks of memory allocated
// to an individual instantiation of counter struct
unsigned long int i;
// Variable used to write to entirety of counter struct
// One struct contains ENCODER_COUNTER_STRUCT edges
unsigned long int x;
// Variable for sampling input registers
unsigned long int edge_sample;
// Struct for storing captures
volatile struct ECAP ECAP;

// Registers to use for PRU input/output
// __R31 is input, __R30 is output
volatile register unsigned int __R31, __R30;

int main(void) {
  // No edges counted to start
  input_capture_count   = 0; // total captured edge counts
  input_reference_count = 0; // total captured edge counts from reference point

  // Clears Overflow Flags
  *IEP_TMR_GLB_STS = 1;
  // Enables IEP counter to increment by 1 every cycle
  *IEP_TMR_GLB_CFG = 0x11;
  // Disables compensation clock
  *IEP_TMR_COMPEN = 0;

  // Packet address is 0 when no counter packets are ready to be sent,
  // Otherwise, it's 1, 2,.. 1+ENCODER_BUFFER_SIZE depending on which packet is ready
  *encoder_ready = 0;

  // Previous sample
  ECAP.p_sample = 0;
  // Current time
  ECAP.ts = *IEP_TMR_CNT;

  // Previous time
  previous_time = *IEP_TMR_CNT;
  //current_time = *IEP_TMR_CNT;

  //time status
  enum time_status tstts;
  tstts = counting;

  // Reset the overflow variable when code starts
  *clock_overflow = 0;

  // Maintain two packets simultaneously, alternating between them
  // Write headers for packets
  // there are two stored-packet locations
  encoder_packets[0].header = ENCODER_HEADER;
  encoder_packets[1].header = ENCODER_HEADER;

  // IRIG controls *on variable (If it is taking IRIG data, *on is 1. If not, *on is 0.)
  // Once the IRIG code has sampled for a given time, it will set *on to 1
  while(*on == 0){
    // Alternate between packet locations in memory
    i = 0;
    while(i < ENCODER_BUFFER_SIZE){ // loop over two packet locations
      // Loop until packet is filled
      quad_needed = 1; // if quadrature value (ENC_Q_SIG) is stored, this becomes False.
      x = 0;
      while(x < ENCODER_COUNTER_SIZE){
        // Record new counter value if changed
        // ( [R31(inputs)] &(AND) [0b10000000000(1<<10)]) : bit of R31[10] 
        // R31[10] : P8_28, encoder_signal (ENC_P_SIG)
        // p_sample : previous R31[10]
        // R31[10] ^(XOR) [p_sample]  : If R31[10] is different from previous one, this is True.

	//Stores new time stamp
	ECAP.ts = *IEP_TMR_CNT;//IEP timer counts
	
	// Check for the clock overflow register and reset it by writing a 1
	if ((*IEP_TMR_GLB_STS & 1) == 1) {
	  *clock_overflow += 1;
	  *IEP_TMR_GLB_STS = 1;
	}
	
	if(previous_time + COUNT_INTERVAL < ECAP.ts){
	  tstts = regular_time;
	}else{
	  if(CLOCK_MAX < previous_time + COUNT_INTERVAL){
	    if(previous_time + COUNT_INTERVAL < ECAP.ts + CLOCK_MAX)
	      tstts = overflow_time;
	  }	
	}
	  
	switch(tstts){
	case regular_time:
	case overflow_time:
	  // Store time stamp
	  encoder_packets[i].clock[x] = ECAP.ts;
	  // Store overflows
	  encoder_packets[i].clock_overflow[x] = (*clock_overflow);
	  //*clock_overflow + ((*IEP_TMR_GLB_STS & 1))); // clock_overflow is calculated in IRIG_Detection.c (clock_overflow). This is shared in the OVERFLOW_ADDRESS
	  // *clock_overflow); // clock_overflow is calculated in this script (clock_overflow). This is shared in the OVERFLOW_ADDRESS
	  // Store number of edges detected
	  encoder_packets[i].count[x]    = input_capture_count;
	  encoder_packets[i].refcount[x] = input_reference_count;
	  // Reset the edge counter if exceeding its max allowed value
	  if(input_capture_count == MAX_COUNTER_VALUE) {
	    input_capture_count = 0;
	  }
	  x += 1; // increment filled data in a packet

	  previous_time = ECAP.ts;

	  tstts = counting;
	  break;

	default:
	  break;
	}

	if(!TEST_COUNT){
	  //Store timing sample
	  edge_sample = (__R31 & (1 << 10)); //R31[10]
	  count_condition = edge_sample ^ ECAP.p_sample;
	}else{
	  current_time    = *IEP_TMR_CNT;
	  count_condition = ((float)(current_time - previous_time)/201.e+6) > TEST_TIMEPERIOD;
	  if(count_condition) previous_time = current_time;
	}
	
        if (count_condition) { 
	  // Stores current sample as previous sample
          ECAP.p_sample = edge_sample;
          // Increments number of edges that have been detected
          input_capture_count += 1;

	  if( (((__R31 & (1 << 9)) >> 9) & 0x1 ) == 1 ){
            input_reference_count  = 0;
          }else{
            input_reference_count += 1;
          }

          // Store the quadrature value
          if(quad_needed == 1) { // how to recognize the signal edge is rising???
            // Store quad sample
            // Get R31[8], P8_27, encoder_quadrature_signal (ENC_Q_SIG)
            // Usually, this is caused in the first count and p_sample=0 and current signal(R31) is 1 --> rising edge
            encoder_packets[i].quad = ((__R31 & (1 << 8)) >> 8) & 0x1; 
            quad_needed = 0; // No need to store quadrature value anymore
          }
	}
	       
      }
      // Sets packet identifier variable to 1, 2,..,1+ENCODER_BUFFER_SIZE and to notify ARM a packet is ready
      *encoder_ready = (i + 1); // encoder_ready(next packet address)=i+1

      i += 1; // 0->1->2->..->1+ENCODER_BUFFER_SIZE(no storing data)->0->...
    } // End of while(i<ENCODER_BUFFER_SIZE)
  } // End of while(*on==0)
  // Reset PRU input
  __R31 = 0x28;
  // Stop PRU data taking
  __halt();
}
