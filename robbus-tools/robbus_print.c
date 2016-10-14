/*!
* \file RobbusMaster.c
* \brief Robbus command processing state machine
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*
*  Revision: 1.0
*  Date: 2009/10/30
*/

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include "RobbusShm.h"
#include "RobbusNodeList.h"

void printUsage(void) {
	printf("Robbus data display tool\n");
	printf("Usage: robbus_print [-h] [-i iterations] [-c config]\n");
	printf("-h This help message\n");
	printf("-i Run only given number of iterations (default unlimited)\n");
	printf("-c Use given config file instead of default /etc/robbus/nodes.conf\n");
}


int main (int argc, char **argv) {

	int opt;
	char *configName = ROBBUS_DEFAULT_NODE_LIST_CONFIG;
	int iterations = -1;

	while ((opt=getopt(argc, argv, "hc:i:")) != -1) {
		switch (opt) {
			case 'c':
				configName = optarg;
				break;
			case 'i':
				iterations = atoi(optarg);
				break;
			default:
				printUsage();
				exit(1);
		}
	}
	


	RobbusNodeList_Create(configName);
	RobbusShm_Create(
		RobbusNodeList_GetTotalInDataSize(),
		RobbusNodeList_GetTotalOutDataSize(),
		10); // TODO: enter correct GPS size

	uint8_t *inData = malloc(RobbusNodeList_GetTotalInDataSize());
	uint8_t *outData = malloc(RobbusNodeList_GetTotalOutDataSize());

	while(iterations < 0 || (iterations-- > 0)) {
		int i;

		RobbusShm_Read(ROBBUS_SHM_INPUT_DATA, inData, 0, 
			RobbusNodeList_GetTotalInDataSize());
		RobbusShm_Read(ROBBUS_SHM_OUTPUT_DATA, outData, 0, 
			RobbusNodeList_GetTotalOutDataSize());

		printf("i: ");
		for (i = 0; i < RobbusNodeList_GetTotalInDataSize(); i++)
			printf("%02x", inData[i]);
		printf("  o: ");
		for (i = 0; i < RobbusNodeList_GetTotalOutDataSize(); i++)
			printf("%02x", outData[i]);
		printf("\n");

		struct timespec delay; /* used for wasting time. */
		delay.tv_sec = 0;
		delay.tv_nsec = 200000000L;
		nanosleep(&delay, NULL);
	}

	RobbusShm_Delete();

	return 0;
}
