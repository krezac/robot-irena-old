/*!
* \file RobbusNodeList.h
* \brief handling list of nodes on robbus networks
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*
*  Revision: 1.0
*  Date: 2009/10/30
*/

#ifndef ROBBUS_NODE_LIST_H
#define ROBBUS_NODE_LIST_H

#include <stdint.h>

#define ROBBUS_DEFAULT_NODE_LIST_CONFIG "/etc/robbus/nodes.conf"
#define ROBBUS_NODE_OVERHEAD_OFFSET 1

typedef struct node_desc {
	unsigned int	address;
	unsigned int	inDataOffset;
	unsigned int	inDataSize;
	unsigned int	outDataOffset;
	unsigned int	outDataSize; 
	char		name[20];
	struct node_desc*	next;
} RobbusNodeList_Descriptor_t;


int RobbusNodeList_PrintNode(RobbusNodeList_Descriptor_t *node);
int RobbusNodeList_PrintList(void);
int RobbusNodeList_Delete(void);
int RobbusNodeList_Create(const char *configFileName);
RobbusNodeList_Descriptor_t* RobbusNodeList_GetByAddress(uint8_t address);
RobbusNodeList_Descriptor_t* RobbusNodeList_GetByIndex(int index);
size_t RobbusNodeList_GetTotalInDataSize(void);
size_t RobbusNodeList_GetTotalOutDataSize(void);
int RobbusNodeList_GetNodeCount(void); 
#endif
