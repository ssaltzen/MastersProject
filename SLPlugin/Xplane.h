#pragma once

// Xplane Defines for version support
#define XPLM303 
#define XPLM302 
#define XPLM301 
#define XPLM300
#define XPLM210
#define XPLM200 

// Datarefs for failure modes:
#define XPLANE_ALWAYS_WORKING	0
#define XPLANE_MTBF_FAIL		1
#define XPLANE_EXACT_TIME_FAIL	2
#define XPLANE_AIRSPEED_FAIL	3
#define XPLANE_ALTITUDE_FAIL	4
#define XPLANE_CNTL_F_FAIL		5
#define XPLANE_INOP				6

// Xplane libraries
#include <XPLMPlugin.h>
#include <XPLMDataAccess.h>
#include <XPLMMenus.h>
#include <XPLMProcessing.h>
#include <XPLMUtilities.h>
#include <XPLMPlanes.h>


