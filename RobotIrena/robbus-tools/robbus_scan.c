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

#include "RobbusNodeList.h"
#include "RobbusShm.h"
#include "RobbusComm.h"

void printUsage(void) {
	printf("Robbus node scanner\n");
	printf("Usage: robbus_scan [-h] [-d device] [-l lower] [-u upper] [-c config]\n");
	printf("-h This help message\n");
	printf("-d Scan given device instead of default /dev/robbus\n");
	printf("-l Scan addresses from lower value (first scanned), default 4\n");
	printf("-u Scan addresses to upper value (last scanned), default 127\n");
	printf("-c Use given config file instead of default /etc/robbus/nodes.conf\n");
}

int main (int argc, char **argv) {

	int opt;
	char *deviceName = ROBBUS_DEFAULT_DEVICE;
	char *configName = ROBBUS_DEFAULT_NODE_LIST_CONFIG;
	uint8_t lowerLimit = 4;
	uint8_t upperLimit = 127;	

	while ((opt=getopt(argc, argv, "hd:c:l:u:")) != -1) {
		switch (opt) {
			case 'd':
				deviceName = optarg;
				break;
			case 'c':
				configName = optarg;
				break;
			case 'l':
				lowerLimit = atoi(optarg);
				break;
			case 'u': 
				upperLimit = atoi(optarg);
				break;
			default:
				printUsage();
				exit(1);
		}
	}

	uint8_t i;

	printf("Scanning robbus device %s for range <%d:%d> (config %s)\n", 
		deviceName, lowerLimit, upperLimit, configName);	
	// read list of nodes
	RobbusNodeList_Create(configName);

	uint8_t inData[] = {'d'}; // "describe" packet
	uint8_t outData[2];
	RobbusComm_Create(deviceName);
	
	printf("Scanning Robbus:\n");
	for (i = lowerLimit; i <= upperLimit; i++) {
		RobbusComm_SendData(1, i, inData, 1);
		int ret = RobbusComm_ReceiveData(1, i, outData, 2);

		if (ret == RBC_SUCCESS) {
			printf("Found node %d with indata %d and outdata %d\n", 
				i, outData[0], outData[1]);
		} else if (ret != RBC_TIMEOUT) {
			printf ("Incorrect reply from node %d (error code %d)\n", i, ret);
		}

	}
	RobbusComm_Close();

	RobbusNodeList_Delete();
	return 0;
}
