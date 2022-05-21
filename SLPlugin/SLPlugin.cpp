#include "PFC_Minimum.h"
#include "Xplane.h"
#include "Logger.hpp"
#include "VersionInfo.h"

#include "XPLMDisplay.h"
#include "XPLMGraphics.h"
#include <string.h>


#include "Network.h"
#include "iostream"

#if IBM
	#include <windows.h>
#endif
#if LIN
	#include <GL/gl.h>
#elif __GNUC__
	#include <OpenGL/gl.h>
#else
	#include <GL/gl.h>
#endif

#ifndef XPLM300
	#error This is made to be compiled againste the XPLM300 SDK
#endif

// *************************************************
// Example:  Dataref handle for indicated airspeed
// sim/flightmodel/position/indicated_airspeed
// Declare it here.  Assign in the Start.   Use it in Flightloop.
static XPLMDataRef XPL_Airspeed;
static XPLMDataRef XPL_Vz;
static XPLMDataRef XPL_Pitch;
static XPLMDataRef XPL_Roll;
static XPLMDataRef XPL_Yaw;
static XPLMDataRef XPL_Time;


static float prev_airspeed; // Save airspeed to compare between flightloops
// *************************************************


// *************************************************
// An opaque handle to the window 
static XPLMWindowID	g_window;

// Callbacks to register when create the window
void				draw_display_window(XPLMWindowID in_window_id, void * in_refcon);
int					dummy_mouse_handler(XPLMWindowID in_window_id, int x, int y, int is_down, void * in_refcon) { return 0; }
XPLMCursorStatus	dummy_cursor_status_handler(XPLMWindowID in_window_id, int x, int y, void * in_refcon) { return xplm_CursorDefault; }
int					dummy_wheel_handler(XPLMWindowID in_window_id, int x, int y, int wheel, int clicks, void * in_refcon) { return 0; }
void				dummy_key_handler(XPLMWindowID in_window_id, char key, XPLMKeyFlags flags, char virtual_key, void * in_refcon, int losing_focus) { }

// *************************************************



float FlightLoopCallback(float, float, int, void *);


/*********************************************************
*  Plugin Start - Required
*********************************************************/
PLUGIN_API int XPluginStart(
	char *		outName,
	char *		outSig,
	char *		outDesc)
{
	bool success = true;

	//Get and log full filepath and name
	wchar_t path[MAX_PATH];
	HMODULE hm = NULL;

	if (GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
		(LPCSTR)&XPluginStart, &hm) == 0)
	{
		int ret = GetLastError();
		gLog.writef("GetModuleHandle failed, error = %d\n", ret);
		return false;
	}

	if (GetModuleFileNameW(hm, path, sizeof(path)) == 0)
	{
		int ret = GetLastError();
		gLog.writef("GetModuleFileName failed, error = %d\n", ret);
		return false;
	}

	std::wstring ws(path);
	std::string spath(ws.begin(), ws.end());
	gLog.writef("PFC Minimum Log File: %s ", spath.c_str());

	//Get and log version info
	VersionInfo version;
	static char version_buff[MAX_PATH + 200];
	static char file_path[MAX_PATH];

	if (0 == version.Create(const_cast<char *>(spath.c_str())))
	{
		sprintf_s(version_buff, "Version %s (%s at %s)",
			version.getFileVersionString(),
			__DATE__,
			__TIME__);
	}
	else
	{
		sprintf_s(version_buff, "Version (%s at %s)",
			__DATE__,
			__TIME__);
	}

	gLog.write(version_buff);
	gLog.write("-----------------------------------------------------------------");


	// Set Plugin Info that is displayed in X-Plane's plugin admin window
	//-------------------
	strcpy(outName, "Siena and Lukas MSP");
	strcpy(outSig, "PFC.Min");
	strcpy(outDesc, version_buff);
	
	// Log message in X-Plane 11/log.txt file
	XPLMDebugString("PFC Minimum:  Entered XPluginStart\n");

	// Log beginning of XPluginStart processing
	gLog.write("Entered XPluginStart");



	// *************************************************
	// TODO:  Start up code here
	// If anything fails here, set success = false
	// *************************************************
	


	
	// *************************************************
	// Example:  Get a handle to a X-Plane dataref. Do this once at startup.
	XPL_Airspeed = XPLMFindDataRef("sim/flightmodel/position/indicated_airspeed");

	XPL_Vz = XPLMFindDataRef("sim/flightmodel/position/vh_ind"); //The velocity in local OGL coordinates

	XPL_Pitch = XPLMFindDataRef("sim/flightmodel/position/theta");// The pitch relative to the plane normal to the Y axis in degrees - OpenGL coordinates - other option is 
																  //sim/flightmodel/position/true_theta  The pitch of the aircraft relative to the earth precisely below the aircraft
	
	XPL_Roll = XPLMFindDataRef("sim/flightmodel/position/phi");// TThe roll of the aircraft in degrees - OpenGL coordinates
																//sim / flightmodel / position / true_phi	float	n	degrees	The roll of the aircraft relative to the earth precisely below the aircraft
	
	XPL_Yaw = XPLMFindDataRef("sim/flightmodel/position/beta");//The heading relative to the flown path (yaw)

	XPL_Time = XPLMFindDataRef("sim/time/total_flight_time_sec"); //Time since flight was last interupted 

	if (NULL == XPL_Airspeed)
	{
		gLog.write("Airspeed dataref not found");
		success = false;
	}
	else
	{
		gLog.write("Airspeed dataref found!");
	}
	//  End of example
	// *************************************************


	XPLMCreateWindow_t params;
	params.structSize = sizeof(params);
	params.visible = 1;
	params.drawWindowFunc = draw_display_window;
	// Note on "dummy" handlers:
	// Even if we don't want to handle these events, we have to register a "do-nothing" callback for them
	params.handleMouseClickFunc = dummy_mouse_handler;
	params.handleRightClickFunc = dummy_mouse_handler;
	params.handleMouseWheelFunc = dummy_wheel_handler;
	params.handleKeyFunc = dummy_key_handler;
	params.handleCursorFunc = dummy_cursor_status_handler;
	params.refcon = NULL;
	params.layer = xplm_WindowLayerFloatingWindows;
	// Opt-in to styling our window like an X-Plane 11 native window
	// If you're on XPLM300, not XPLM301, swap this enum for the literal value 1.
	params.decorateAsFloatingWindow = xplm_WindowDecorationRoundRectangle;

	// Set the window's initial bounds
	// Note that we're not guaranteed that the main monitor's lower left is at (0, 0)...
	int left, bottom, right, top;
	XPLMGetScreenBoundsGlobal(&left, &top, &right, &bottom);
	params.left = left + 50;
	params.bottom = bottom + 150;
	params.right = params.left + 200;
	params.top = params.bottom + 200;

	g_window = XPLMCreateWindowEx(&params);

	// Position the window as a "free" floating window, which the user can drag around
	XPLMSetWindowPositioningMode(g_window, xplm_WindowPositionFree, -1);
	// Limit resizing our window: maintain a minimum width/height of 100 boxels and a max width/height of 300 boxels
	XPLMSetWindowResizingLimits(g_window, 200, 200, 300, 300);
	XPLMSetWindowTitle(g_window, "Current Values");


	// Register flightloop callback if successful
	if (success && (g_window != NULL))
	{
		XPLMRegisterFlightLoopCallback(FlightLoopCallback, -1, NULL);
		gLog.write("START() Success");
		return 1; // signal success
	}
	else
	{
		gLog.write("START() Failed");
		return 0; // signal failure -- plugin will be ignored
	}

}



/*********************************************************
*  Plugin Stop - Required
*  Clean up stuff on X-Plane exit
*********************************************************/

PLUGIN_API void    XPluginStop(void)
{
	gLog.write("Entering XPluginStop");

	std::string message = Logger::getTimeStamp() + "PFC_Minimum: Enter XPluginStop\n";
	XPLMDebugString(message.c_str());

	XPLMDestroyWindow(g_window);
	g_window = NULL;

	XPLMUnregisterFlightLoopCallback(FlightLoopCallback, NULL);

	gLog.write("Exit XPluginStop");
	gLog.close();

	message = Logger::getTimeStamp() + "PFC_Minimum: Logfile close\n";
	XPLMDebugString(message.c_str());

	XPLMDebugString("Exit XPluginStop\n ");
}



/*********************************************************
*  Plugin Disabled - Required
*********************************************************/

PLUGIN_API void XPluginDisable(void)
{
	std::string message = gLog.getTimeStamp() + "PFC_Minimum: XPluginDisabled\n";
	XPLMDebugString(message.c_str());
}


/*********************************************************
*  Plugin Enabled - Required
*********************************************************/

PLUGIN_API int XPluginEnable(void)
{
	XPLMDebugString("PFC_Minimum: Entered XPluginEnable\n");
	return 1;
}



/*********************************************************
*  Plugin Receive Message - Required
*********************************************************/

PLUGIN_API void XPluginReceiveMessage(
	XPLMPluginID    inFromWho,
	long            inMessage,
	void *          inParam)
{
	switch (inMessage)
	{
	case XPLM_MSG_AIRPORT_LOADED:
		gLog.write("Airport Loaded Message");
		break;

	case (XPLM_MSG_SCENERY_LOADED):
		gLog.write("Scenary Loaded Message");
		break;

	case (XPLM_MSG_PLANE_LOADED):
		gLog.write("Aircraft Loaded Message");
		break;

	case (XPLM_MSG_WILL_WRITE_PREFS):
		gLog.write("Write Prefs Message");
		break;

	case(XPLM_MSG_PLANE_CRASHED):
		gLog.write("Plane Crash Message");
		break;

	default:
		break;
	}
}

/*********************************************************
* Window Draw
*********************************************************/

void	draw_display_window(XPLMWindowID in_window_id, void * in_refcon)
{
	// Mandatory: We *must* set the OpenGL state before drawing
	// (we can't make any assumptions about it)
	XPLMSetGraphicsState(
		0 /* no fog */,
		0 /* 0 texture units */,
		0 /* no lighting */,
		0 /* no alpha testing */,
		1 /* do alpha blend */,
		1 /* do depth testing */,
		0 /* no depth writing */
	);

	int l, t, r, b;
	XPLMGetWindowGeometry(in_window_id, &l, &t, &r, &b);

	float col_white[] = { 1.0, 1.0, 1.0 }; // red, green, blue

	XPLMDrawString(col_white, l + 10, t - 20, "Some Test text", NULL, xplmFont_Proportional);
}




/*********************************************************
*  FlightLoopCallback
*********************************************************/

float FlightLoopCallback(float inElapsedSinceLastCall, float inElapsedTimeSinceLastFlightLoop, int inCounter, void *inRefcon)
{
	// Update frame counter via Logger static function
	Logger::incFrameCounter();

	// This will draw a dividing line between flightloops IF anything was logged during the last flightloop
	gLog.newFrame();



	//******************************************
	// TODO:   Flight loop code here
	//******************************************




	//******************************************
	// Example:  Let's log the airspeed each flightloop
	float airspeed = XPLMGetDataf(XPL_Airspeed);

	float Vz = XPLMGetDataf(XPL_Vz);
	std::string VzStr = std::to_string(Vz);

	float pitch = XPLMGetDataf(XPL_Pitch);
	std::string pitchStr = std::to_string(pitch);

	float roll = XPLMGetDataf(XPL_Roll);
	std::string rollStr = std::to_string(roll);

	float yaw = XPLMGetDataf(XPL_Yaw);
	std::string yawStr = std::to_string(yaw);

	float time = XPLMGetDataf(XPL_Time);
	std::string timeStr = std::to_string(time);

	// Only log airspeed if it changed since last flight loop
	if (airspeed != prev_airspeed)
	{
		//gLog.writef("Airspeed (Indicated) = %f Knots", airspeed);

		prev_airspeed = airspeed; // Save for next flightloop

	}
	// End of example
	//*******************************************

	std::string IP = "127.0.0.1";
	int PORT = 8888;

	try
	{
		WSASession Session;
		UDPSocket Socket;
		std::string data = VzStr + ' ' + pitchStr + ' ' + rollStr + ' ' + yawStr + ' ' + timeStr;
		gLog.write("WSA SESSION SET UP");
		Socket.SendTo(IP, PORT, data.c_str(), data.size());
		gLog.write("sent");
	}
	catch (std::exception &ex)
	{
		std::cout << ex.what();
		gLog.write("WSA Failed");
	}

	

	return UPDATE_TIME;
}


