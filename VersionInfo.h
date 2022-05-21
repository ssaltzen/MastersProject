// VersionInfo.h: interface for the VersionInfo class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_VERSIONINFO_H__F462493E_85D3_43A9_97FD_E338E4DFF8B4__INCLUDED_)
#define AFX_VERSIONINFO_H__F462493E_85D3_43A9_97FD_E338E4DFF8B4__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class VersionInfo  
{
public:
	char* getFileVersionString();
	unsigned long getFileVersionVals(unsigned long* ms, unsigned long* ls);
	unsigned long Create(char* file_name);
	VersionInfo();
	virtual ~VersionInfo();

private:
	char version_buff[25];
	void* fixed_file_info;
	unsigned char* version_info;
	unsigned long info_size;

};

#endif // !defined(AFX_VERSIONINFO_H__F462493E_85D3_43A9_97FD_E338E4DFF8B4__INCLUDED_)
