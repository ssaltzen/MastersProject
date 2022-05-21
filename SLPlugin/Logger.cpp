/*!
*
* Copyright(c) 2016-2020 Precision Flight Controls, Inc. - All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
*
* \class Logger
* \brief thread safe class for logging to a file
*
*/

#include "Logger.hpp" 
#include <cstdio>
#include <vector>
#include <windows.h>
#include <sstream> 
#include <iomanip>

int Logger::iFrameCount;
bool Logger::debug_messages_enabled = false;

//create instance of global logger object
extern Logger gLog{ "C:\\PFC\\Minimum.txt" };

//////////////////////////// 
// CTOR 
//Logger::Logger() : m_debugTries(0) {
//
//}

Logger::Logger(const std::string & filename) : fname(filename), m_debugTries(0)
{
		m_logFile.open(fname, std::fstream::out);
		//TODO:  Write out file format and date
}

//////////////////////////// 
// DTOR 
Logger::~Logger() {
	if (m_logFile.is_open()) {
		m_logFile.close();
	}
}

//////////////////////////// 
//  OPEN
bool Logger::open(const std::string & fileName) {

	if (m_logFile.is_open())
		return true;
	else
	{
		m_logFile.open(fileName, std::fstream::out);
		return m_logFile.is_open();
	}

}

//////////////////////////// 
//  CLOSE
void Logger::close() {

	if (m_logFile.is_open()) {
		m_logFile.close();
	}
}

//////////////////////////// 
//  WRITE
void Logger::write(const std::string & msg) {

	something_was_logged_last_frame = true;

	std::lock_guard<std::mutex> lock(m_mutex);

	if (m_logFile.is_open()) {
		m_logFile << getTimeStamp().c_str() << " - " << msg.c_str() << "\n";
		m_logFile.flush();
	}
}

//////////////////////////// 
// DEBUG	MSG
void Logger::debugMsg(const char *fmt, ...)
{
	//#ifdef DEBUGGING_LOG
	if (debug_messages_enabled)
	{
		if (!m_logFile.is_open()) return;
		va_list args;
		va_start(args, fmt);
		writeDebugMsg(1024, fmt, args);
		va_end(args);
	}
	//#endif
}

void Logger::debugMsg(const std::string & msg)
{
	if (debug_messages_enabled) write(msg);
}


//////////////////////////// 
// WRITE with formatting
void Logger::writef(const char *fmt, ...)
{
	if (!m_logFile.is_open()) return;
	va_list args;
	va_start(args, fmt);
	writeDebugMsg(1024, fmt, args);
	va_end(args);
}


//////////////////////////// 
// WRITE	DEBUG	MSG
void Logger::writeDebugMsg(const int size, const char *fmt, va_list ap)
{

	std::vector<char> buf(size);
	char *cbufPtr = &buf[0];
	int needed = vsnprintf(cbufPtr, size, fmt, ap);

	//handle the vsnprintf  -1 return case on microsoft compilers
	if (needed < 0)
	{
		if (m_debugTries < 3)
		{
			//double the buffer size and try again
			++m_debugTries;
			writeDebugMsg(size * 2, fmt, ap);
			return;
		}
		else
		{
			m_debugTries = 0;
			return;
		}
	}

	//handle the case where the number of chars are actually returned
	//by vsnprintf
	if (needed > size)
	{
		buf.resize(needed + 1);
		needed = vsnprintf(&buf[0], needed, fmt, ap);
	}

	//we made it - log this message
	m_debugTries = 0;
	std::string msg(&buf[0]);
	write(msg);

}

//////////////////////////// 
//	GET		TIME	STAMP
std::string Logger::getTimeStamp()
{
	SYSTEMTIME st;
	GetSystemTime(&st);
	std::ostringstream ossMessage;

	ossMessage << std::setw(2) << std::setfill('0') << st.wHour << ":"
		<< std::setw(2) << std::setfill('0') << st.wMinute << ":"
		<< std::setw(2) << std::setfill('0') << st.wSecond << "."
		<< std::setw(3) << std::setfill('0') << st.wMilliseconds << " ["
		<< std::setw(7) << std::setfill('0') << iFrameCount << "]";

	return ossMessage.str();
}

void Logger::resetFrameCounter()
{
	iFrameCount = 0;
}


void Logger::incFrameCounter()
{
	iFrameCount++;
}

void Logger::newFrame()
{
	if (something_was_logged_last_frame)
	{
		write("-------------------------------------------------");
		something_was_logged_last_frame = false;
	}
}

void Logger::enable_verbose_logging()
{
	debug_messages_enabled = true;
}

void Logger::disable_verbose_logging()
{
	debug_messages_enabled = false;
}

bool Logger::get_verbose_logging_state()
{
	return debug_messages_enabled;
}