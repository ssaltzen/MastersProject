#pragma once
/*!
*
* Copyright(c) 2016 Precision Flight Controls, Inc. - All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
*
* \class Logger
* \brief thread safe class for logging to a file
*
*/

#ifndef LOGGER_INCLUDE_H__ 
#define LOGGER_INCLUDE_H__ 

#include <fstream>
#include <cstdarg>
#include <mutex>

//Define DEBUGGING_LOG to enable "debugMsg()".  Handy for verbose debugging during development, then 
//undefine for production.

//#define DEBUGGING_LOG 

// declare global variable



class Logger {

public:
	
	Logger(const std::string & filename);

	virtual ~Logger();

	Logger() = delete;
		
	Logger& operator = (const Logger &L) {	return *this; }


	bool open(const std::string & fileName);
	bool isOpen() { return m_logFile.is_open(); }
	void close();


	void write(const std::string & msg);
	void writef(const char *fmt, ...);


	void debugMsg(const char *fmt, ...);
	void debugMsg(const std::string & msg);


	static void resetFrameCounter();
	static void incFrameCounter();
	
	void newFrame();

	static std::string getTimeStamp();

	static void enable_verbose_logging();
	static void disable_verbose_logging();
	static bool get_verbose_logging_state();


private:
	
	void writeDebugMsg(const int size, const char *fmt, va_list ap);


	const std::string fname;
	bool fileIsOpen = false;

	std::mutex m_mutex;

	std::fstream m_logFile;

	static int iFrameCount;

	bool something_was_logged_last_frame = false;
	static bool debug_messages_enabled;

	int m_debugTries;
};

#endif

extern Logger gLog;


