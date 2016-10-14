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
	printf("Robbus data setting tool\n");
	printf("Usage: robbus_set [-h] [-c config] address data\n");
	printf("-h This help message\n");
	printf("-c Use given config file instead of default /etc/robbus/nodes.conf\n");
	printf("address decimal node address\n");
	printf("data data to set as hex string i.e. 45a35b\n");
}


int main (int argc, char **argv) {

	if (argc < 3) {
		printUsage();
		exit(1);
	}

	int i;

		int opt;
	char *configName = ROBBUS_DEFAULT_NODE_LIST_CONFIG;

	while ((opt=getopt(argc, argv, "hc:")) != -1) {
		switch (opt) {
			case 'c':
				configName = optarg;
				break;
			default:
				printUsage();
				exit(1);
		}
	}

	if (optind != argc-2) {
		printUsage();
		exit(1);
	}

	uint8_t address = atoi(argv[argc-2]);
	uint8_t dataSize = strlen(argv[argc-1])/2;
	uint8_t data[255];
	char tmp[3];
	tmp[2] = '\0';
	for (i = 0 ; i < dataSize; i++) {
		tmp[0] = argv[argc-1][2*i];
		tmp[1] = argv[argc-1][2*i+1];
		data[i] = strtol(tmp, 0, 16);
	}

	printf("Read %d byte(s) of data for address %d: ", dataSize, address);
	for (i = 0; i < dataSize; i++)
		printf("%02x", data[i]);
	printf("\n");

	RobbusNodeList_Create(configName);

	RobbusNodeList_Descriptor_t * node = RobbusNodeList_GetByAddress(address);
	if (!node) {
		printf("Address not on list\n");
		exit(1);
	}

	if (node->inDataSize != dataSize) {
		printf("Data size not valid (%d byte(s) needed\n", node->inDataSize);
		exit(1);
	}

	RobbusShm_Create(
		RobbusNodeList_GetTotalInDataSize(),
		RobbusNodeList_GetTotalOutDataSize(),
		10); // TODO: enter correct GPS size

	uint8_t *inData = malloc(RobbusNodeList_GetTotalInDataSize());

	RobbusShm_Read(ROBBUS_SHM_INPUT_DATA, inData, 0, 
		RobbusNodeList_GetTotalInDataSize());

	uint8_t *valid = inData + node->inDataOffset;
	*valid = 1;
	memcpy(inData + node->inDataOffset + ROBBUS_NODE_OVERHEAD_OFFSET, data, dataSize);

	RobbusShm_Write(ROBBUS_SHM_INPUT_DATA, inData, 0, 
		RobbusNodeList_GetTotalInDataSize());

	//RobbusShm_Delete();

	return 0;
}
