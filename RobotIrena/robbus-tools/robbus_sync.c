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
#include <unistd.h>
#include <time.h>

#include "RobbusNodeList.h"
#include "RobbusShm.h"
#include "RobbusComm.h"

void printUsage(void) {
	printf("Robbus data synchronizing tool\n");
	printf("Usage: robbus_sync [-h] [-d device] [-i iterations] [-c config]\n");
	printf("-h This help message\n");
	printf("-d Sync given device instead of default /dev/robbus\n");
	printf("-i Run only given number of iterations (default unlimited)\n");
	printf("-c Use given config file instead of default /etc/robbus/nodes.conf\n");
}


int main (int argc, char **argv) {

	uint8_t i;
	int opt;
	char *deviceName = ROBBUS_DEFAULT_DEVICE;
	char *configName = ROBBUS_DEFAULT_NODE_LIST_CONFIG;
	int iterations = -1;

	while ((opt=getopt(argc, argv, "hd:c:i:")) != -1) {
		switch (opt) {
			case 'd':
				deviceName = optarg;
				break;
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
	
	printf("Syncing robbus device %s (config %s)\n", 
		deviceName, configName);		

	// read list of nodes
	RobbusNodeList_Create(configName);
	RobbusNodeList_PrintList();

	// create shared memory
	RobbusShm_Create(
		RobbusNodeList_GetTotalInDataSize(),
		RobbusNodeList_GetTotalOutDataSize(),
		10); // TODO: enter correct GPS size

	RobbusComm_Create(deviceName);

	// allocate buffers for local data copy
	void *inData = malloc(RobbusNodeList_GetTotalInDataSize());
	void *outData = malloc(RobbusNodeList_GetTotalOutDataSize());
	
	while(iterations < 0 || (iterations-- > 0)) {
		// create local copy of input data
		if (RobbusShm_Lock(ROBBUS_SHM_INPUT_DATA) != 0) {
			perror("Locking input data failed");
			continue;
		}
		void* sharedData = RobbusShm_GetPtr(ROBBUS_SHM_INPUT_DATA);
		memcpy(inData, sharedData, RobbusNodeList_GetTotalInDataSize());
		// erase valid flags in shared memory (are kept in local copy)
		for (i = 0; i < RobbusNodeList_GetNodeCount(); i++) {
			// fetch node descriptor
			RobbusNodeList_Descriptor_t * node = 
				RobbusNodeList_GetByIndex(i);
			uint8_t *inValid = ((uint8_t*)sharedData) + node->inDataOffset;
			*inValid = 0;
		}

		RobbusShm_Unlock(ROBBUS_SHM_INPUT_DATA);

		int atLeastOneSynced = 0;

		// communicate all nodes
		for (i = 0; i < RobbusNodeList_GetNodeCount(); i++) {
			// fetch node descriptor
			RobbusNodeList_Descriptor_t * node = 
				RobbusNodeList_GetByIndex(i);

			RobbusNodeList_PrintNode(node);
			
			uint8_t *inValid = ((uint8_t*)inData) + node->inDataOffset;
			if (*inValid) {
				void *inPayload = inData + node->inDataOffset + ROBBUS_NODE_OVERHEAD_OFFSET;
				void *outPayload = outData + node->outDataOffset + ROBBUS_NODE_OVERHEAD_OFFSET;
				uint8_t *outValid = ((uint8_t*)outData) + node->outDataOffset;
				*outValid = 0;

				if (RobbusComm_SendData(ROBBUS_TAG_REGULAR, node->address, 
					inPayload, node->inDataSize) == 0) {
					if (RobbusComm_ReceiveData(ROBBUS_TAG_REGULAR, node->address, 
						outPayload, node->outDataSize) == 0) {
						printf("Node synced\n");
						*outValid = 1;
						atLeastOneSynced = 1;
					} else {
						printf("Receive failed\n");
					}
				} else {
					printf("Send failed\n");
				}
			} else {
				printf("InData not valid\n");
			}
		}

		// and write back the output data into shared memory
		RobbusShm_Write(ROBBUS_SHM_OUTPUT_DATA, outData, 0, 
			RobbusNodeList_GetTotalOutDataSize());

		if (!atLeastOneSynced) {
			// wait for a while
			struct timespec delay; /* used for wasting time. */
			delay.tv_sec = 0;
			delay.tv_nsec = 100000000L;
			nanosleep(&delay, NULL);
		}
	}
	// free allocated local buffers
	free(inData);
	free(outData);

	// cleanup (will not be called ;)
	RobbusComm_Close();
	RobbusShm_Delete();
	RobbusNodeList_Delete();
	return 0;
}
