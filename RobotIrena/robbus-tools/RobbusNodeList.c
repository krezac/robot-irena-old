/*!
* \file RobbusNodeList.c
* \brief handling list of nodes on robbus networks
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

#include "RobbusNodeList.h"

static RobbusNodeList_Descriptor_t *g_nodeList = NULL;
static int g_nodeCount = 0;
static RobbusNodeList_Descriptor_t **g_nodeArray;

int RobbusNodeList_PrintNode(RobbusNodeList_Descriptor_t *node) {
	printf("Node %02x: in: %d (offset: %d) out: %d (offset: %d) name: %s\n",
	node->address,node->inDataSize, node->inDataOffset, 
	node->outDataSize, node->outDataOffset, node->name);

	return 0;
}

int RobbusNodeList_PrintList(void) {
	RobbusNodeList_Descriptor_t * node = g_nodeList;
	while (node != NULL) {
		RobbusNodeList_PrintNode(node);
		node = node->next;
	}
	return 0;
}

int RobbusNodeList_Delete(void) {
	RobbusNodeList_Descriptor_t *node = g_nodeList;
	while (g_nodeList != NULL) {
		node = g_nodeList;
		g_nodeList = g_nodeList->next;
		free(node);
	}
	free(g_nodeArray);
	return 0;
}	

int RobbusNodeList_Create(const char *configFileName) {
	FILE* f;
	char line[255];
	int i;
	RobbusNodeList_Descriptor_t *node, *lastNode = g_nodeList;

	printf("Reading config file %s\n", configFileName);
	f = fopen(configFileName, "r");
	
	if (f == NULL) {
		perror("Unable to open config file");
		return 1;
	}

	g_nodeCount = 0;

	while(fgets(line, 255, f) != NULL) {
		if (strlen(line) < 4 || line [0] == '#')
			continue;

		node = malloc(sizeof(RobbusNodeList_Descriptor_t));
		node->next = NULL;
		if(sscanf(line, "%d:%d:%d:%s", 
			&node->address, &node->inDataSize, 
			&node->outDataSize, node->name) < 4) {
			perror("Line parsing failed");
			free(node);
			continue;
		}

		// add to list
		if (g_nodeList == NULL) {
			node->inDataOffset = 0;
			node->outDataOffset = 0;
			g_nodeList = node;
		} else {
			node->inDataOffset = 
				lastNode->inDataOffset + lastNode->inDataSize + ROBBUS_NODE_OVERHEAD_OFFSET;
			node->outDataOffset = 
				lastNode->outDataOffset + lastNode->outDataSize + ROBBUS_NODE_OVERHEAD_OFFSET;
			lastNode->next = node;
		}
		lastNode = node;

		g_nodeCount++;
	}

	fclose(f);

	// construct array of pointers
	g_nodeArray = malloc(g_nodeCount * sizeof(RobbusNodeList_Descriptor_t*));
	node = g_nodeList;
	i = 0;
	while (node != NULL) {
		g_nodeArray[i++] = node;
		node = node->next;
	}

	return 0;
}

RobbusNodeList_Descriptor_t* RobbusNodeList_GetList(void) {
	return g_nodeList;
}

RobbusNodeList_Descriptor_t* RobbusNodeList_GetByAddress(uint8_t address) {

	RobbusNodeList_Descriptor_t* node = g_nodeList;
	while (node != NULL) {
		if (node->address == address) {
			return node;
		} else {
			node = node->next;
		} 
	}
	return NULL;
}

RobbusNodeList_Descriptor_t* RobbusNodeList_GetByIndex(int index) {
	return g_nodeArray[index];
}


RobbusNodeList_Descriptor_t* RobbusNodeList_GetLastNode(void) {
	if (g_nodeList == NULL) {
		return NULL;
	}

	RobbusNodeList_Descriptor_t *node = g_nodeList;
	while(node->next != NULL) {
		node = node-> next;
	}
	return node;
}


size_t RobbusNodeList_GetTotalInDataSize(void) {
	RobbusNodeList_Descriptor_t *node = RobbusNodeList_GetLastNode();
	if (node == NULL) {
		return 0;
	}

	return node->inDataOffset + node->inDataSize + ROBBUS_NODE_OVERHEAD_OFFSET;
}

size_t RobbusNodeList_GetTotalOutDataSize(void) {
	RobbusNodeList_Descriptor_t *node = RobbusNodeList_GetLastNode();
	if (node == NULL) {
		return 0;
	}

	return node->outDataOffset + node->outDataSize + ROBBUS_NODE_OVERHEAD_OFFSET;
}

int RobbusNodeList_GetNodeCount(void) {
	return g_nodeCount;
}
