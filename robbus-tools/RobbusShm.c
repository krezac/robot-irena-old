/*!
* \file RobbusShm.c
* \brief handling shared memory data block
*
* \author Kamil Rezac
*  URL: http://robotika.cz/
*
*  Revision: 1.0
*  Date: 2009/10/30
*/

#include <stdint.h>

#include <stdio.h> /* standard I/O routines. */
#include <sys/types.h> /* various type definitions. */
#include <sys/ipc.h> /* general SysV IPC structures */
#include <sys/shm.h> /* semaphore functions and structs. */
#include <sys/sem.h> /* shared memory functions and structs. */
#include <unistd.h> /* fork(), etc. */
#include <stdlib.h> /* rand(), etc. */
#include <string.h>
#define SEM_ID 250 /* ID for the semaphore. */

#include "RobbusShm.h"

union semun
{
	int val; /* value for SETVAL */
	struct semid_ds *buf; /* buffer for IPC_STAT & IPC_SET */
	unsigned short int *array;/* array for GETALL & SETALL */
	struct seminfo *__buf; /* buffer for IPC_INFO */
};


typedef struct {
	int key;
	int memHandle;
	void *memPtr;
	int semHandle;
} RobbusShmRecord_t;

#define MEMORY_TYPE_COUNT 3
#define MEMORY_INPUT_KEY ftok("/etc/robbus",'I')
#define MEMORY_OUTPUT_KEY ftok("/etc/robbus",'O')
#define MEMORY_GPS_KEY ftok("/etc/robbus",'G')

RobbusShmRecord_t g_memoryList[MEMORY_TYPE_COUNT];

/*
 * function: sem_lock. locks the semaphore, for exclusive access to a resource.
 * input: semaphore set ID.
 * output: none.
 */
int RobbusShm_Lock(RobbusShm_MemoryType_t memType) {
	/* structure for semaphore operations. */
	struct sembuf sem_op;
	/* wait on the semaphore, unless it's value is non-negative. */
	sem_op.sem_num = 0;
	sem_op.sem_op = -1;
	sem_op.sem_flg = 0;
	return semop(g_memoryList[memType].semHandle, &sem_op, 1);
}


/*
 * function: sem_unlock. un-locks the semaphore.
 * input: semaphore set ID.
 * output: none.
 */
int RobbusShm_Unlock(RobbusShm_MemoryType_t memType) {
	/* structure for semaphore operations. */
	struct sembuf sem_op;
	/* signal the semaphore - increase its value by one. */
	sem_op.sem_num = 0;
	sem_op.sem_op = 1; /* <-- Comment 3 */
	sem_op.sem_flg = 0;
	return semop(g_memoryList[memType].semHandle, &sem_op, 1);
}

int createMemoryType(RobbusShm_MemoryType_t index, int key, int size) {
	// TODO: implement node creation
	union semun sem_val; /* semaphore value, for semctl(). */

	g_memoryList[index].key = key;
	
	/* create a semaphore set with one semaphore */
	/* in it, with access only to the owner. */
	g_memoryList[index].semHandle = semget(key, 1, IPC_CREAT | 0600);
	if (g_memoryList[index].semHandle == -1) {
		perror("main: semget");
		return -1;
	}

	/* intialize the first (and single) semaphore in our set to '1'. */
	sem_val.val = 1;
	int rc = semctl(g_memoryList[index].semHandle, 0, SETVAL, sem_val);
	if (rc == -1) {
		perror("main: semctl");
		return -1;
	}

	/* allocate a shared memory segment with size of 2048 bytes. */
	printf("allocating %d bytes with key %d\n", size, key);
	g_memoryList[index].memHandle = shmget(key, size, IPC_CREAT | 0600);
	if (g_memoryList[index].memHandle == -1) {
		perror("main: shmget: ");
		return -1;
	}

	/* attach the shared memory segment to our process's address space. */
	g_memoryList[index].memPtr = shmat(g_memoryList[index].memHandle, NULL, 0);
	if (!g_memoryList[index].memPtr) { /* operation failed. */
		perror("main: shmat: ");
		return -1;
	}

	return 0;
}

int deleteMemoryType(RobbusShm_MemoryType_t index) {
	struct shmid_ds shm_desc;

	/* detach the shared memory segment from our process's address space. */
	if (shmdt(g_memoryList[index].memPtr) == -1) {
		perror("main: shmdt: ");
	}

	/* de-allocate the shared memory segment. */
	if (shmctl(g_memoryList[index].memHandle, IPC_RMID, &shm_desc) == -1) {
		perror("main: shmctl: ");
	}

	/* de-allocate semaphore. */
	if (semctl(g_memoryList[index].semHandle, 0, IPC_RMID, 0) == -1) {
		perror("main: shmctl: ");
	}


	return 0;
}

int RobbusShm_Create(size_t inDataSize, size_t outDataSize, size_t gpsDataSize) {
	// TODO return codes
	createMemoryType(ROBBUS_SHM_INPUT_DATA, MEMORY_INPUT_KEY, inDataSize);
	createMemoryType(ROBBUS_SHM_OUTPUT_DATA, MEMORY_OUTPUT_KEY, outDataSize);
	createMemoryType(ROBBUS_SHM_GPS_DATA, MEMORY_GPS_KEY, gpsDataSize);
	return 0;
}

int RobbusShm_Delete(void) {

	// TODO return codes
	deleteMemoryType(ROBBUS_SHM_INPUT_DATA);
	deleteMemoryType(ROBBUS_SHM_OUTPUT_DATA);
	deleteMemoryType(ROBBUS_SHM_GPS_DATA);
	return 0;
}

void* RobbusShm_GetPtr(RobbusShm_MemoryType_t memType) {
	return g_memoryList[memType].memPtr;
}

int RobbusShm_Read(RobbusShm_MemoryType_t memType, void* buffer, size_t offset, size_t size) {
	int ret = RobbusShm_Lock(memType);
	if (ret != 0) {
		printf ("E:%d\n", ret);
		perror("locking for read failed");
		return ret;
	}
	
	memcpy(buffer, g_memoryList[memType].memPtr + offset, size);
	RobbusShm_Unlock(memType);
	return 0;
}

int RobbusShm_Write(RobbusShm_MemoryType_t memType, void* buffer, size_t offset, size_t size) {
	int ret = RobbusShm_Lock(memType);
	if (ret != 0) {
		perror("locking for write failed");
		return ret;
	}
	memcpy(g_memoryList[memType].memPtr + offset, buffer, size);
	RobbusShm_Unlock(memType);
	return 0;
}

