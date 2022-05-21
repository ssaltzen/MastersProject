// VersionInfo.cpp: implementation of the VersionInfo class.
//
//////////////////////////////////////////////////////////////////////
#include "VersionInfo.h"

#include <Windows.h>
#include <stdio.h>

#if 0
struct VS_FIXEDFILEINFO
{ 
  DWORD dwSignature; 
  DWORD dwStrucVersion; 
  DWORD dwFileVersionMS; 
  DWORD dwFileVersionLS; 
  DWORD dwProductVersionMS; 
  DWORD dwProductVersionLS; 
  DWORD dwFileFlagsMask; 
  DWORD dwFileFlags; 
  DWORD dwFileOS; 
  DWORD dwFileType; 
  DWORD dwFileSubtype; 
  DWORD dwFileDateMS; 
  DWORD dwFileDateLS; 
}FixedFileInfo; 
#endif

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

VersionInfo::VersionInfo()
{
	version_info = NULL;
	fixed_file_info = NULL;

}

VersionInfo::~VersionInfo()
{

	if (NULL != version_info)
		delete [] version_info;
}

unsigned long VersionInfo::Create(char *file_name)
{
	info_size = GetFileVersionInfoSize(file_name, 0);
	if (0 == info_size)
		return 1;

	version_info = new unsigned char[info_size + 1];
	if (NULL == version_info)
		return 2;

	if (0 == GetFileVersionInfo(file_name, 0, info_size, (void*)version_info))
	{
		unsigned long dwError = GetLastError();
		return 3;
	}

	return 0;

}

char* VersionInfo::getFileVersionString()
{
	char* rtn = NULL;
	unsigned int file_info_len;

	BOOL res = VerQueryValue(version_info, 
              TEXT("\\"),
              &fixed_file_info,
              &file_info_len);


	if (TRUE == res)
	{
		VS_FIXEDFILEINFO* file_info = (VS_FIXEDFILEINFO*)fixed_file_info;

		sprintf(version_buff, "%d.%d.%d.%d",
			HIWORD(file_info->dwFileVersionMS),
			LOWORD(file_info->dwFileVersionMS),
			HIWORD(file_info->dwFileVersionLS),
			LOWORD(file_info->dwFileVersionLS)
			);
		rtn = (char*)&version_buff;
	}

	return rtn;
}

unsigned long VersionInfo::getFileVersionVals(unsigned long* ms, unsigned long* ls)
{
	unsigned int file_info_len;

	BOOL res = VerQueryValue(version_info, 
              TEXT("\\"),
              &fixed_file_info,
              &file_info_len);


	if (TRUE == res)
	{
		VS_FIXEDFILEINFO* file_info = (VS_FIXEDFILEINFO*)fixed_file_info;

		*ms = file_info->dwFileVersionMS;
		*ls = file_info->dwFileVersionLS;
		return 0;
	}

	return 1;
}
