/*!
* \file SerialApiLinux.cpp
* \brief implementation for Linux
*
* \author md -at- robotika.cz, jiri.isa -at- matfyz.cz
*
*  URL: http://robotika.cz/
*  
*  Revision: 1.2
*  Date: 2005/11/01
*/

//#define _POSIX_SOURCE 1 /* POSIX compliant source */

#include <termios.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
//#include <sys/stat.h>
//#include <string.h>

#include "SerialApi.h"

/* baudrate settings are defined in <asm/termbits.h>, which is
included by <termios.h> */
/* change this definition for the correct port */

//because we want to forbidd IUCLC (mapping to lower case) where it could happen and ignore the option otherwise (it is not defined by POSIX)
#ifndef IUCLC
#define IUCLC 0
#endif /*IUCLC*/

int m_handle;
struct termios m_oldtio, m_newtio;

int SerialApi_Init(const char *deviceName) {

	int a_baudRate = B115200;

	m_handle = open(deviceName, O_RDWR | O_NOCTTY );
	if(m_handle < 0)
	{
		perror("Serial port opening failed");
		return m_handle;
	}

	tcgetattr(m_handle,&m_oldtio); // save current serial port settings 
	tcgetattr(m_handle,&m_newtio); //and get the working copy 

	// speed,
	cfsetispeed(&m_newtio, a_baudRate);
	cfsetospeed(&m_newtio, a_baudRate);    
	
	m_newtio.c_cflag &= ~(CBAUD);	//clear bits used for char size
	m_newtio.c_cflag |= B115200;
    
	//char size
	m_newtio.c_cflag &= ~(CSIZE);	//clear bits used for char size
	m_newtio.c_cflag |= CS8;

	//no parity
	m_newtio.c_cflag &= ~(PARENB);	//clear parity enable
	m_newtio.c_iflag &= ~(INPCK);	//disable input parity checking
  
	 //one stop bit - default
	m_newtio.c_cflag &= ~(CSTOPB);	//clear parity enable

	//no sw flow control
	//FIXME removed to start functioning m_newtio.c_cflag &= ~(IXON | IXOFF | IXANY);

	//no hw flow control
	m_newtio.c_cflag &= ~(CRTSCTS); //this is not POSIX compliant! It might be omitted, if the device is already set to 'no hardware flow control"

	//raw output
	m_newtio.c_lflag = 0;		//no local flags
	m_newtio.c_oflag &= ~(OPOST);	//no output processing
	m_newtio.c_oflag &= ~(ONLCR);	//don't convert line feeds

	//no input processing
	m_newtio.c_iflag &= ~(INPCK | PARMRK | BRKINT | INLCR | ICRNL | IUCLC | IXANY);

	// ignore break conditions
	m_newtio.c_iflag |= IGNBRK;

	//enable input
	m_newtio.c_cflag |= CREAD;

	//
 	// * initialize all control characters
	// * default values can be found in /usr/include/termios.h, and are given
	// * in the comments, but we don't need them here
	//
    	m_newtio.c_cc[VINTR]    = 0;     // Ctrl-c //
    	m_newtio.c_cc[VQUIT]    = 0;     // Ctrl-\ //
    	m_newtio.c_cc[VERASE]   = 0;     // del //
    	m_newtio.c_cc[VKILL]    = 0;     // @ //
    	m_newtio.c_cc[VEOF]     = 4;     // Ctrl-d //
    	m_newtio.c_cc[VTIME]    = 1;     // inter-character timer (in 0.1s)//
    	m_newtio.c_cc[VMIN]     = 0;     // non-blocking read //
    	m_newtio.c_cc[VSWTC]    = 0;     // '\0' //
    	m_newtio.c_cc[VSTART]   = 0;     // Ctrl-q //
    	m_newtio.c_cc[VSTOP]    = 0;     // Ctrl-s //
    	m_newtio.c_cc[VSUSP]    = 0;     // Ctrl-z //
    	m_newtio.c_cc[VEOL]     = 0;     // '\0' //
    	m_newtio.c_cc[VREPRINT] = 0;     // Ctrl-r //
    	m_newtio.c_cc[VDISCARD] = 0;     // Ctrl-u //
    	m_newtio.c_cc[VWERASE]  = 0;     // Ctrl-w //
    	m_newtio.c_cc[VLNEXT]   = 0;     // Ctrl-v //
    	m_newtio.c_cc[VEOL2]    = 0;     // '\0' //

    	// now clean the modem line and activate the settings for the port
    	tcflush(m_handle, TCIFLUSH);
    	if(tcsetattr(m_handle, TCSANOW, &m_newtio) == -1)
   	{
      		perror("tcsetattr Error");
    	}

	return 0;
}

///////////////////////////////////////////////////////////
/*!
* Destructor
*/
int SerialApi_Close(void) {
	if(m_handle >= 0) {
		tcsetattr(m_handle,TCSANOW,&m_oldtio);
		close(m_handle);
		m_handle = -1;
	}

	return 0;
}

///////////////////////////////////////////////////////////
/*!
* \brief send single byte
*
* \param a_toSend byte to send
*/
int SerialApi_SendByte(uint8_t c) {
	return write(m_handle, &c, 1) == 1 ? 0 : -1;
}

int SerialApi_ReceiveByte(void) {
  uint8_t data;
  return read(m_handle, &data, 1) == 1 ? data : -1;
}

