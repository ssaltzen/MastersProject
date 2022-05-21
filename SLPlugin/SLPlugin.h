#pragma once


// UPDATE_TIME is a return value from the flightloop that tells X-Plane when
// to call the flightloop again.  Positive values are seconds (float).   Negative values are 
// flightloop counts (use -1 to call every flightloop).   Zero means don't call the flightloop.
//#define UPDATE_TIME 0.1f	// update interval in seconds
#define UPDATE_TIME -1	// update interval in flightloops

//Standard library stuff
#include <cstdio> 
#include <cstring>
#include <sstream>
#include <iomanip>
#include <cmath>




