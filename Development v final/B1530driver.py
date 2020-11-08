# -*-coding:Latin-1 -*
#------------------------------------------------------------------------------
# Name:        B1530driver
# Purpose:     v 0.1
#
# Author:      AV242852
#
# Created:     23/09/2014
# Copyright:   (c) AV242852 2014
# Licence:     <your licence>
#------------------------------------------------------------------------------
"""
module to use the B1530A functions implemented in an agilent C++ dll.
"""

###############################################################################
#                                Modules import                               #
###############################################################################

import ctypes as ct     # ctypes allows to call functions in dlls libraries and
                        # has extensive facilities to create, access and
                        # manipulate simple and complicated C data types in
                        # Python.

from ctypes import byref# byref function pass parameters by reference lyke
                        # pointers in C

import sys              # Exit from Python. used to interrupt the program

import inspect
import ErrorModule
####################################################################################














################################################################
wgfmu_link = r'C:\Windows\System32\wgfmu.dll' # lien vers la dll du B1530 
                                              # (faire bien attention qu'elle
                                              # se trouve a cet emplacement)

####################################################################################




################################################################









                                              
###############################################################################
#                                Library import                               #
###############################################################################

try: # tries to load B1530 dll
    B1530 = ct.WinDLL(wgfmu_link)
except: # if the dll is not loadable error occurs and program is stopped
    print "error occurs with wgfmu.dll"
    #sys.exit()

###############################################################################
#                              Variables creation                             #
###############################################################################

INT = ct.c_int # creates an integer C variable

DOUBLE = ct.c_double # creates a double floating C variable

CHAR = ct.create_string_buffer # creates a string pointer C variable

###############################################################################
#                               B1530A constants                              #
###############################################################################

# Dictionaries for B1530 parameters.

_warningLevel = {'off' : 1000,
                 'severe' : 1001,
                 'normal' : 1002,
                 'information' : 1003}
                 
_operationMode = {'dc' : 2000,
                  'fastiv' : 2001,
                  'pg' : 2002,
                  'smu' : 2003}
                  
_forceVoltageRange = {'auto' : 3000,
                      '3V' : 3001,
                      '5V' : 3002,
                      '10Vn' : 3003,
                      '10Vp' : 3004}
                      
_measureMode = {'voltage' : 4000,
                'current' : 4001}
                
_measureVoltageRange = {'5V' : 5001,
                        '10V' : 5002}
                        
_measureCurrentRange = {'1uA' : 6001,
                        '10uA' : 6002,
                        '100uA' : 6003,
                        '1mA' : 6004,
                        '10mA' : 6005}
                        
_measureEnabled = {'disable' : 7000,
                   'enable' : 7001}
                   
_triggerOutMode = {'disable' : 8000,
                   'execution' : 8001,
                   'sequence' : 8002,
                   'pattern' : 8003,
                   'event' : 8004}
                   
_triggerOutPolarity = {'positive' : 8100,
                       'negative' : 8101}
                       
_axis = {'time' : 9000,
         'voltage' : 9001}
         
_measureEvent = {'notCompleted' : 11000,
                 'completed' : 11001}
                 
_measureEventData = {'averaged' : 12000,
                     'raw' : 12001}
        
_returnSelfCalTest = {0 : 'Self-test passed or self-calibration passed',
                      1 : 'Self-test failed or self-calibration failed'}
                      
_status = {10000 : 'All sequences are completed and all data is ready to read',
           10001 : 'All sequences are just completed',
           10002 : 'Sequencer is running',
           10003 : 'Sequencer is aborted and all data is ready to read',
           10004 : 'Sequencer is just aborted',
           10005 : 'Illegal state',
           10006 : 'Idle state'}
           
_errorCode = {0 : 'No Error.',
              -1 : 'Invalid parameter value was found. It will be out of the range. Set the effective parameter value.',
              -2 : 'Invalid string value was found. It will be empty or illegal (pointer). Set the effective string value.',
              -3 : 'Context error was found between relative functions. Set the effective parameter value.',
              -4 : 'Specified function is not supported by this channel. Set the channel id properly.',
              -5 : 'IO library error was found.',
              -6 : 'Firmware error was found.',
              -7 : 'WGFMU instrument library error was found.',
              -8 : 'Unidentified error was found.',
              -9 : 'Specified channel id is not available for WGFMU. Set the channel id properly',
              -10 : 'Unexpected pattern name was specified. Specify the effective pattern name. Or create a new pattern.',
              -11 : 'Unexpected event name was specified. Specify the effective event name.',
              -12 : 'Duplicate pattern name was specified. Specify the unique pattern name',
              -13 : 'Sequencer must be run to execute the specified function. Run the sequencer',
              -14 : 'Measurement is in progress. Read the result data after the measurement is completed',
              -15 : 'Measurement result data was deleted by the setup change. The result data must be read before changing the waveform setup or the measurement setup'}


###############################################################################
#                               B1530A functions                              #
###############################################################################

def abort():
    """
    This function stops the sequencer of all WGFMU channels. After this
    command, the channels keep the output voltage when this command is
    executed.

    Parameters
    ----------
    None 
        
    Returns
    -------
    error : integer
        Error status 
    """
    error = B1530.WGFMU_abort()
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def abortChannel(chanId):
    """
    This function stops the sequencer of the specified channel. After this
    command, the channel keeps the output voltage when this command is
    executed.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
        
    Returns
    -------
    error : integer
        Error status
    """
    error = B1530.WGFMU_abortChannel(INT(chanId))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def addSequence(chanId, pattern, count):
    """
    This function specifies a sequence by using pattern and count, and connects
    it to the last point of the sequence data set to the specified channel.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    pattern : string
        Name of waveform pattern.
    count : numeric
        Repeat count of the waveform pattern. 1 to 1,099,511,627,776. If the
        specified value is out of this range, the sequence is not added. If the
        value is not integer, the value is rounded to the nearest integer. For
        example, if the value is 7.2, the value is rounded to 7.
        
    Returns
    -------
    error : integer
        Error status

    See Also
    --------
    createPattern, createMergedPattern, createMultipliedPattern,
    createOffsetPattern

    Notes
    -----
    Waveform pattern specified by pattern must be created before this function
    is executed.
    
    If a channel repeats a sequence output, no delay time occurs between the
    repeats. If a channel outputs sequences in series, 50 ns delay time occurs
    between the sequences. In the delay time, the channel outputs the last
    voltage of the last vector for the beginning 10 ns and the start voltage of
    the next vector for the rest 40 ns.
    """
    pattern_c = CHAR(pattern, len(pattern))
    error = B1530.WGFMU_addSequence(INT(chanId), pattern_c, DOUBLE(count))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def addSequences(chanId, pattern, count, size):
    """
    This function specifies sequences by using pattern and count, and connects
    them to the last point of the sequence data set to the specified channel in
    the array element order.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    pattern : string array
        Name of waveform pattern. Array elements must be corresponding to the
        count array elements together in the element order.
    count : numeric array
        Repeat count of the waveform pattern. Array elements must be
        corresponding to the pattern array elements together in the element
        order. The value must be 1 to 1,099,511,627,776. If the specified value
        is out of this range, the sequences are not added. If the value is not
        integer, the value is value is 7.2, the value is rounded to 7.
    size : integer
        Array size. Number of array elements for both pattern and count.
        
    Returns
    -------
    error : integer
        Error status

    See Also
    --------
    createPattern, createMergedPattern, createMultipliedPattern,
    createOffsetPattern

    Notes
    -----
    Waveform pattern specified by pattern must be created before this function
    is executed.
    
    If a channel repeats a sequence output, no delay time occurs between the
    repeats. If a channel outputs sequences in series, 50 ns delay time occurs
    between the sequences. In the delay time, the channel outputs the last
    voltage of the last vector for the beginning 10 ns and the start voltage of
    the next vector for the rest 40 ns.
    """
    pattern_c = (ct.c_char_p * len(pattern))()
    pattern_c[:]=pattern[:]
    count_c = (DOUBLE * size)()
    count_c[:] = count[:]
    error = B1530.WGFMU_addSequences(INT(chanId), byref(pattern_c),
                                     byref(count_c), INT(size))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def addVector(pattern, dTime, voltage):
    """
    This function specifies a scalar data by using dTime and voltage, and
    connects it to the last point of the specified waveform pattern. This adds
    a vector to the pattern.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to add a vector.
    dTime : numeric
        Incremental time value, in second. 10 ns to 10995.11627775 seconds, in
        10 ns resolution. If the specified value is out of this range, the
        vector is not added. If the value is not multiple number of 10 ns, the
        value is rounded to the nearest multiple number. For example, if the
        value is 72 ns, the value is rounded to 70 ns.
    voltage : numeric
        Output voltage, in V.
        
    Returns
    -------
    error : integer
        Error status

    See Also
    --------
    createPattern, createMergedPattern, createMultipliedPattern,
    createOffsetPattern

    Notes
    -----
    Waveform pattern specified by pattern must be created before this function
    is executed.
    """
    pattern_c = CHAR(pattern, len(pattern))
    error = B1530.WGFMU_addVector(pattern_c, DOUBLE(dTime), DOUBLE(voltage))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def addVectors(pattern, dTime, voltage, size):
    """
    This function specifies multiple scalar data by using dTime and voltage,
    and connects them to the last point of the specified waveform pattern in
    the array element order. This adds vectors to the pattern.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to add a vector.
    dTime : numeric array
        Incremental time value, in second. Array elements must be corresponding
        to the voltage array elements together in the element order. The value
        must be 10 ns to 10995.11627775 seconds, in 10 ns resolution. If the
        specified value is out of this range, the vector is not added. If the
        value is not multiple number of 10 ns, the value is rounded to the
        nearest multiple number. For example, if the value is 72 ns, the value
        is rounded to 70 ns.
    voltage : numeric array
        Output voltage, in V. Array elements must be corresponding to the dTime
        array elements together in the element order.
    size : integer
        Array size. Number of array elements for both dTime and voltage.
        
    Returns
    -------
    error : integer
        Error status

    See Also
    --------
    createPattern, createMergedPattern, createMultipliedPattern,
    createOffsetPattern

    Notes
    -----
    Waveform pattern specified by pattern must be created before this function
    is executed.
    """
    pattern_c = CHAR(pattern, len(pattern))
    dTime_c = (DOUBLE * size)()
    dTime_c[:] = dTime[:]
    voltage_c = (DOUBLE * size)()
    voltage_c[:] = voltage[:]
    error = B1530.WGFMU_addVectors(pattern_c, byref(dTime_c), byref(voltage_c),
                                   INT(size))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def clear():
    """
    This function clears the instrument library's software setup information
    such as all pattern and sequence information, error, error summary,
    warning, warning summary, warning level, warning level for the
    treatWarningsAsErrors function. This function does not change the hardware
    status.

    Parameters
    ----------
    None
        
    Returns
    -------
    error : integer
        Error status
    """
    error = B1530.WGFMU_clear()
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def closeLogFile():
    """
    This function closes the log file opened by the openLogFile function.

    Parameters
    ----------
    None
        
    Returns
    -------
    error : integer
        Error status
    """
    error = B1530.WGFMU_closeLogFile()
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def closeSession():
    """
    This function closes the session (communication with B1500A) opened by the
    openSession function.

    Parameters
    ----------
    None
        
    Returns
    -------
    error : integer
        Error status
    """
    error = B1530.WGFMU_closeSession()
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error
    
def connect(chanId):
    """
    This function enables the specified WGFMU channel and the RSU connected to
    the WGFMU.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
        
    Returns
    -------
    error : integer
        Error status
    """
    error = B1530.WGFMU_connect(INT(chanId))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def createMergedPattern(pattern, pattern1, pattern2, direction):
    """
    This function creates a waveform pattern by copying the waveform specified
    by pattern1 and adding the waveform specified by pattern2.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to create. Name must be unique. However, the
        same value as pattern1 or pattern2 is allowed.
    pattern1 : string
        Name of waveform pattern to be copied. Same value as pattern or
        pattern2 is allowed.
    pattern2 : string
        Name of waveform pattern to be added. Same value as pattern or pattern1
        is allowed.
    direction : integer
        Direction to add waveform pattern.
        
    Returns
    -------
    error : integer
        Error status

    See Also
    --------
    createPattern, createMultipliedPattern, createOffsetPattern

    Notes
    -----
    Waveform patterns specified by pattern1 and pattern2 must be created before
    this function is executed.
    
    Event settings by this function with direction=WGFMU_AXIS_VOLTAGE
        +---------------------------------------------------------------------+
        | The pattern2 event settings delete and overwrite the pattern1 event |
        | settings of the same event type in the same time frame. For example,|
        | the pattern2 measurement event settings delete and overwrite the    |
        | pattern1 measurement event settings in the same time frame, but do  |
        | not delete the pattern1 range change event settings and the pattern1|
        | trigger output event settings.                                      |
        +---------------------------------------------------------------------+
    """
    pattern_c = CHAR(pattern, len(pattern))
    pattern1_c = CHAR(pattern1, len(pattern1))
    pattern2_c = CHAR(pattern2, len(pattern2))
    error = B1530.WGFMU_createMergedPattern(pattern_c, pattern1_c, pattern2_c,
                                            INT(direction))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def createMultipliedPattern(pattern, pattern1, factorT, factorV):
    """
    This function creates a waveform pattern by copying the waveform specified
    by pattern1 and multiplying the waveform by the specified factor for each
    direction, time and voltage.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to be created. Name must be unique. However,
        the same value as pattern1 is allowed.
    pattern1 : string
        Name of waveform pattern to be copied. Same value as pattern is
        allowed.
    factorT : numeric
        Multiplier factor in the time direction. Non zero value. Event
        attributes are changed by factorT.
    factorV : numeric
        Multiplier factor in the voltage direction. Non zero value. Event
        attributes are changed by factorV.
        
    Returns
    -------
    error : integer
        Error status

    See Also
    --------
    createPattern, createMergedPattern, createOffsetPattern

    Notes
    -----
    Waveform pattern specified by pattern1 must be created before this function
    is executed.
    
    Measurement event attributes changed by factorT
        Event attributes time, interval, and avgTime are multiplied by factorT.
        The measPts attribute is not changed.
        
    Range change event attributes changed by factorT
        Event attribute time is multiplied by factorT. The rngIndex attribute
        is not changed.
        
    Trigger output event attributes changed by factorT
        Event attributes time and duration are multiplied by factorT.
        
    For the negative factorT
        If factorT < 0, this function creates a new pattern by calculating the
        line symmetry of the copied pattern and multiplying it by \|factorT\|.
        Then the axis of symmetry is the voltage axis placed on the center of
        the copied pattern. The time value newTime of the measurement event for
        the new pattern is calculated by the following formula.
            +-----------------------------------------------------------------+
            |newTime = pattern1 period - time - interval*(measPts-1) - avgTime|
            +-----------------------------------------------------------------+
        For example, if time=100 ns, measPts=4, interval=50 ns, avgTime=30 ns,
        and pattern1 period=500 ns, the inverted time value newTime is 220 ns.
        
        By the line symmetry, the first point of a pattern will become the last
        point of the new pattern. Also, the averaging end of a measurement
        point will become the averaging start of the point on the new pattern.
        So the measurement start time of the new pattern will be the inversion
        of the averaging end of the last measurement point. The start time of
        each measurement point will be automatically adjusted.
    """
    pattern_c = CHAR(pattern, len(pattern))
    pattern1_c = CHAR(pattern1, len(pattern1))
    error = B1530.WGFMU_createMultipliedPattern(pattern_c, pattern1_c,
                                                DOUBLE(factorT),
                                                DOUBLE(factorV))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def createOffsetPattern(pattern, pattern1, offsetT, offsetV):
    """
    This function creates a waveform pattern by copying the waveform specified
    by pattern1 and adding the specified offset for each direction; time and
    voltage.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to be created. Name must be unique. However,
        the same value as pattern1 is allowed.
    pattern1 : string
        Name of waveform pattern to be copied. Same value as pattern is
        allowed.
    offsetT : numeric
        Offset value in the time direction, in second. Event attribute time is
        changed by offsetT. The value will be time + offsetT.
    offsetV : numeric
        Offset value in the voltage direction, in V. Event attributes are not
        changed by offsetV.
        
    Returns
    -------
    error : integer
        Error status

    See Also
    --------
    createPattern, createMergedPattern, createMultipliedPattern

    Notes
    -----
    Waveform pattern specified by pattern1 must be created before this function
    is executed.
    
    For the positive offsetT, the copied pattern will be shifted to the
    positive direction, and a vector with the initial voltage will be inserted
    at the beginning of the pattern.
    
    For the negative offsetT, the copied pattern will be shifted to the
    negative direction. Then the vectors before offsetT will be deleted and the
    time offsetT will become the time origin. At the end of the pattern, no
    vector is added.
    """
    pattern_c = CHAR(pattern, len(pattern))
    pattern1_c = CHAR(pattern1, len(pattern1))
    error = B1530.WGFMU_createOffsetPattern(pattern_c, pattern1_c, 
                                            DOUBLE(offsetT), DOUBLE(offsetV))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def createPattern(pattern, initV):
    """
    This function creates a waveform pattern.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern. Name must be unique.
    initV : numeric
        Voltage value for the start point of the pattern, in V. This value is
        voltage for the time origin (0 s) of the pattern.
        
    Returns
    -------
    error : integer
        Error status
    """
    pattern_c = CHAR(pattern, len(pattern))
    error = B1530.WGFMU_createPattern(pattern_c, DOUBLE(initV))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def dcforceVoltage(chanId, voltage):
    """
    This function starts DC voltage output immediately by using the specified
    channel.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    voltage : numeric
        Voltage value, in V.
        
    Returns
    -------
    error : integer
        Error status

    Notes
    -----
    Error occurs if the specified channel is not in the DC mode. The operation
    mode is set by the setOperationMode function.
    
    The dcforceVoltage, dcmeasureAveragedValue, and dcmeasureValue functions
    apply the setup of the following function to the channel.
        | setOperationMode
        | setForceVoltageRange
        | setMeasureCurrentRange
        | setMeasureVoltageRange
        | setMeasureMode
    """
    error = B1530.WGFMU_dcforceVoltage(INT(chanId), DOUBLE(voltage))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def dcmeasureAveragedValue(chanId, points, interval):
    """
    This function starts a sampling measurement immediately by using the
    specified channel and returns the averaged measurement voltage or current.
    The measurement mode is set by the setMeasureMode function.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    points : integer
        Number of sampling points (1 to 65535).
    interval : integer
        Sampling interval (1 to 65535). The channel sets the sampling interval
        given by the following formula.
            +-------------------------------------+
            | sampling interval = interval * 5 ns |
            +-------------------------------------+
    Return
    -------
    error : integer
        Error status
    value : numeric
        The measured value, in V or A.

    Notes
    -----
    Error occurs if the specified channel is not in the DC mode. The operation
    mode is set by the setOperationMode function.
    """
    value_c = DOUBLE()
    error = B1530.WGFMU_dcmeasureAveragedValue(INT(chanId), INT(points),
                                             INT(interval), byref(value_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, value_c.value)

def dcmeasureValue(chanId):
    """
    This function starts a voltage or current measurement immediately by using
    the specified channel and returns the measurement value.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
 
    Returns
    -------
    error : integer
        Error status
    value : numeric
        The measured value, in V or A.

    Notes
    -----
    Error occurs if the specified channel is not in the DC mode. The operation
    mode is set by the setOperationMode function.
    """
    value_c = DOUBLE()
    error = B1530.WGFMU_dcmeasureValue(INT(chanId), byref(value_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, value_c.value)

def disconnect(chanId):
    """
    This function disables the specified WGFMU channel and the RSU.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
        
    Returns
    -------
    error : integer
        Error status
    """
    error = B1530.WGFMU_disconnect(INT(chanId))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def doSelfCalibration():
    """
    This function performs the self-calibration for the mainframe and all
    modules.

    Parameters
    ----------
    None
    
    Returns
    -------
    error : integer
        Error status
    result : integer
        Self-calibration result. The following response will be returned. If
        multiple failures are detected, the returned value will be sum of
        responses. For example, if failures are detected in the slot 2 and 3
        modules, :math:`6*(2^1+2^2)` is returned.
            +---------------------------------------------------------------+
            | :math:`0` : mainframe and all modules passed self-calibration |
            +---------------------------------------------------------------+
            | :math:`2^{N-1}` : Slot N module failed self-calibration       |
            +---------------------------------------------------------------+
            | :math:`2^{10} (1024)` : Mainframe failed self-calibration     |
            +---------------------------------------------------------------+
    detail : string
        Self-calibration result detail string.
    size : integer
        Number of characters to read the self-calibration result detail string.
        If the specified size value is greater than or equal to the length of
        the detail string, all of the detail string is stored in detail. And it
        returns the length of the detail string. If the specified size value is
        less than the length of the detail string, a part of the detail string
        is stored in detail and a warning occurs. Then the number of characters
        stored in detail is size.
    """
    result_c = INT()
    size_c = INT(256)
    detail_c = CHAR(size_c.value+1)
    error = B1530.WGFMU_doSelfCalibration(byref(result_c), detail_c,
                                        byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, result_c.value, detail_c.value, size_c.value)

def doSelfTest():
    """
    This function performs the self-test for the mainframe and all modules.

    Parameters
    ----------
    None
        
    Returns
    -------
    error : integer
        Error status
    result : integer
        Self-calibration result. The following response will be returned. If
        multiple failures are detected, the returned value will be sum of
        responses. For example, if failures are detected in the slot 2 and 3
        modules, :math:`3*(2^1+2^2)` is returned.
            +--------------------------------------------------------+
            | :math:`0` : mainframe and all modules passed self-test |
            +--------------------------------------------------------+
            | :math:`2^{N-1}` : Slot N module failed self-test       |
            +--------------------------------------------------------+
            | :math:`2^{10} (1024)` : Mainframe failed self-test     |
            +--------------------------------------------------------+
    detail : string
        Self-test result detail string.
    size : integer
        Number of characters to read the self-test result detail string. If the
        specified size value is greater than or equal to the length of the
        detail string, all of the detail string is stored in detail. And it
        returns the length of the detail string. If the specified size value is
        less than the length of the detail string, a part of the detail string
        is stored in detail and a warning occurs. Then the number of characters
        stored in detail is size.
    """
    result_c = INT()
    size_c = INT(256)
    detail_c = CHAR(size_c.value+1)
    error = B1530.WGFMU_doSelfTest(byref(result_c), detail_c, byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, result_c.value, detail_c.value, size_c.value)

def execute():
    """
    This function runs the sequencer of all enabled WGFMU channels in the Fast
    IV mode or the PG mode. The channels start the predefined operation. If
    there are channels in the run status, this function stops the sequencers
    and runs the sequencer of all enabled WGFMU channels. After the execution,
    the channels keep the last output voltage.

    Parameters
    ----------
    None
        
    Returns
    -------
    error : integer
        Error status

    Notes
    -----
    This function applies the setup of the following function to the channel.
        | setOperationMode
        | setForceVoltageRange
        | setMeasureCurrentRange
        | setMeasureVoltageRange
        | setMeasureMode
    """
    error = B1530.WGFMU_execute()
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def exportAscii(fileName):
    """
    This function creates a setup summary report and saves it as a csv (comma
    separated values) file. The summary report contains the pattern data, event
    data, and sequence data for the channels configured by the instrument
    library. The file can be read by using a spreadsheet software. This is
    effective for quick debugging.

    Parameters
    ----------
    result : string
        Name of the summary report file. The file extension will be csv if you
        do not specify it.
        
    Returns
    -------
    error : integer
        Error status

    Notes
    -----
    If the specified file does not exist, this function creates new file. If
    the specified file exists, this function overwrites the file. Error occurs
    if an invalid path is specified, a file is not created, or a setup summary
    is not written.
    """
    fileName_c = CHAR(fileName, len(fileName))
    error = B1530.WGFMU_exportAscii(fileName_c)
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def getChannelIds():
    """
    This function reads the channel id of the WGFMU channels installed in the
    B1500A connected to this session. To know the number of WGFMU channels,
    execute the getChannelIdSize function.

    Parameters
    ----------
    None
        
    Returns
    -------
    error : integer
        Error status
    result : integer
        Return the channel id array.
    size : integer
        Number of WGFMU channel id to read.
    """
    size_c = INT(1)
    B1530.WGFMU_getChannelIdSize(byref(size_c))
    result_c = (INT *size_c.value)()
    error = B1530.WGFMU_getChannelIds(byref(result_c), byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, result_c[:], size_c.value)

def getChannelIdSize():
    """
    This function returns the number of WGFMU channels installed in the B1500A
    connected to this session.

    Parameters
    ----------
    None

    Returns
    -------
    error : integer
        Error status
    size : integer
        Number of WGFMU channels.
    """
    size_c = INT()
    error = B1530.WGFMU_getChannelIdSize(byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, size_c.value)

def getChannelStatus(chanId):
    """
    This function returns the status of the specified channel in the Fast IV
    mode or the PG mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
        
    Returns
    -------
    error : integer
        Error status
    status : integer
        Status.
    elapsT : numeric
        Estimated elapsed time, in second.
    totalT : numeric
        Estimated total time until all sequences are completed, in second.
    """
    status_c = INT()
    elapsT_c = DOUBLE()
    totalT_c = DOUBLE()
    error = B1530.WGFMU_getChannelStatus(INT(chanId), byref(status_c),
                                         byref(elapsT_c), byref(totalT_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, status_c.value, elapsT_c.value, totalT_c.value)

def getCompletedMeasureEventSize(chanId):
    """
    This function returns the number of completed measurement events and the
    total number of measurement events set to the specified channel.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
        
    Returns
    -------
    error : integer
        Error status
    complete : integer
        Number of the measurement events which have been already completed.
    total : integer
        Total number of the measurement events.
    """
    complete_c = INT()
    total_c = INT()
    error = B1530.WGFMU_getCompletedMeasureEventSize(INT(chanId),
                                                     byref(complete_c),
                                                     byref(total_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, complete_c.value, total_c.value)

def getError():
    """
    This function reads one error string. To know the length of the next error
    string, execute the getErrorSize function. The error string is cleared by
    the clear function.

    Parameters
    ----------
    None
    
    Returns
    -------
    error : integer
        Error status
    result : string
        Error string.
    size : integer
        Number of characters to read the error string.
    """
    size_c = INT(1)
    B1530.WGFMU_getErrorSize(byref(size_c))
    result_c = CHAR(size_c.value+1)
    error = B1530.WGFMU_getError(result_c, byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, result_c.value, size_c.value)

def getErrorSize():
    """
    This function returns the length of the next error
    string.

    Parameters
    ----------
    None

    Returns
    -------
    error : integer
        Error status
    size : integer
        Length of the next error string.
    """
    size_c = INT()
    error = B1530.WGFMU_getErrorSize(byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, size_c.value)

def getErrorSummary():
    """
    This function reads the error summary string which contains all errors. To
    know the length of the error summary string, execute the
    getErrorSummarySize function. The error summary string is cleared by the
    clear function.

    Parameters
    ----------
    None
        
    Returns
    -------
    error : integer
        Error status
    result : string
        Error summary string.
    size : integer
        Number of characters to read the error summary string.
    """
    size_c = INT(1)
    B1530.WGFMU_getErrorSummarySize(byref(size_c))
    result_c = CHAR(size_c.value+1)
    error = B1530.WGFMU_getErrorSummary(result_c, byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, result_c.value, size_c.value)

def getErrorSummarySize():
    """
    This function returns the length of the error summary string which contains
    all errors.

    Parameters
    ----------
        
    Returns
    -------
    error : integer
        Error status
    size : integer
        Length of the error summary string.
    """
    size_c = INT()
    error = B1530.WGFMU_getErrorSummarySize(byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, size_c.value)

def getForceDelay(chanId):
    """
    This function returns the device delay time of the specified source channel
    in the Fast IV mode or the PG mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
        
    Returns
    -------
    error : integer
        Error status
    delay : numeric
        Device delay time, in second. delay must be -50 ns to 50 ns, in 625 ps
        resolution. If the value is not multiple number of 625 ps, the value is
        rounded to the nearest multiple number. For example, if the value is
        1.5 ns, the value is rounded to 1.25 ns.
    """
    delay_c = DOUBLE()
    error = B1530.WGFMU_getForceDelay(INT(chanId), byref(delay_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, delay_c.value)

def getForceValue(chanId, index):
    """
    This function specifies a channel and an index of sequence data, and
    returns the corresponding setup data (time and voltage).

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    index : integer
        Index of the sequence data to read setup. index must be 0 to the total
        number of setup data -1. Error occurs if the value is out of this
        range.
        
    Returns
    -------
    error : integer
        Error status
    time : numeric
        Time data, in second.
    voltage : numeric
        Voltage data, in V.
    """
    time_c = DOUBLE()
    voltage_c = DOUBLE()
    error = B1530.WGFMU_getForceValue(INT(chanId), DOUBLE(index),
                                      byref(time_c), byref(voltage_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, time_c.value, voltage_c.value)

def getForceValues(chanId, index, length):
    """
    This function specifies a channel and a range of sequence data, and returns
    the corresponding setup data (time and voltage). To know the total number
    of setup data, execute the getForceValueSize function.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    index : integer
        First index of the sequence data to read setup. index must be 0 to the
        total number of setup data-1. Error occurs if the value is out of this
        range.
    length : integer
        Number of setup data to read. Length must be 1 to the total number of
        setup data-index. If length is greater than this value, all of the
        returned data is stored in time and voltage and a warning occurs. Error
        occurs if length is less than 1.

    Returns
    -------
    error : integer
        Error status
    length : integer
        Number of data returned.
    time : numeric
        Time data, in second.
    voltage : numeric
        Voltage data, in V.
    """
    length_c = INT(length)
    time_c = (DOUBLE * length)()
    voltage_c = (DOUBLE * length)()
    error = B1530.WGFMU_getForceValues(INT(chanId), DOUBLE(index),
                                      byref(length_c), byref(time_c),
                                      byref(voltage_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, length_c.value, time_c[:], voltage_c[:])

def getForceValueSize(chanId):
    """
    This function returns the total number of setup data (time and voltage)
    defined in the source output sequence set to the specified channel.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
        
    Returns
    -------
    error : integer
        Error status
    size : numeric
        Total number of setup data.
    """
    size_c = DOUBLE()
    error = B1530.WGFMU_getForceValueSize(INT(chanId), byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, size_c.value)

def getForceVoltageRange(chanId):
    """
    This function returns the voltage output range set to the specified
    channel. The value is set by the setForceVoltageRange function. The setting
    is applied to the channel by the update, updateChannel, execute, or the
    functions of the DC measurement group.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
        
    Returns
    -------
    error : integer
        Error status
    vRange : integer
        Voltage output range.
    """
    vRange_c = INT()
    error = B1530.WGFMU_getForceVoltageRange(INT(chanId), byref(vRange_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, vRange_c.value)

def getInterpolatedForceValue(chanId, time):
    """
    This function specifies a channel and a time value (time), and returns the
    voltage value (voltage) applied by the specified WGFMU channel at the
    specified time. The returned value may be the value given by the
    interpolation.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    time : numeric
        Time to read the voltage output value, in second. time must be 0 to the
        length of the waveform set to the specified channel. Error occurs if
        the value is out of this range.
        
    Returns
    -------
    error : integer
        Error status
    voltage : numeric
        Voltage output value, in V.
    """
    voltage_c = DOUBLE()
    error = B1530.WGFMU_getInterpolatedForceValue(INT(chanId), DOUBLE(time),
                                                 byref(voltage_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, voltage_c.value)

def getMeasureCurrentRange(chanId):
    """
    This function returns the current measurement range set to the specified
    channel. The value is set by the setMeasureCurrentRange function. The
    setting is applied to the channel by the update, updateChannel, execute,
    or the functions of the DC measurement group. The setting is not effective
    for the voltage measurement mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status
    iRange : integer
        Current measurement range.
    """
    iRange_c = INT()
    error = B1530.WGFMU_getMeasureCurrentRange(INT(chanId), byref(iRange_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, iRange_c.value)

def getMeasureDelay(chanId):
    """
    This function returns the device delay time of the specified measurement
    channel in the Fast IV mode or the PG mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
        
    Returns
    -------
    error : integer
        Error status
    delay : numeric
        Device delay time, in second. delay must be -50 ns to 50 ns, in 625 ps
        resolution. If the value is not multiple number of 625 ps, the value is
        rounded to the nearest multiple number. For example, if the value is
        1.5 ns, the value is rounded to 1.25 ns.
    """
    delay_c = DOUBLE()
    error = B1530.WGFMU_getMeasureDelay(INT(chanId), byref(delay_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, delay_c.value)

def getMeasureEvent(chanId, measId):
    """
    This function specifies a channel and an index of measurement event, and
    returns the corresponding setup (pattern, event, cycle, loop, count, index,
    and length).

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    measId : integer
        Index of the measurement event to read setup. measId must be 0 to the
        total number of measurement events-1. Error occurs if the value is out
        of this range.

    Returns
    -------
    error : integer
        Error status
    pattern : string
        Waveform pattern name.
    event : string
        Event name.
    cycle : integer
        Usage count. This parameter means how many times the pattern is used in
        the sequence of the specified channel.
    loop : numeric
        Loop count. This parameter means how many times the pattern is looped
        in the sequence of the specified channel.
    count : integer
        Event count. This parameter means how many times the event is used in
        the pattern.
    index : integer
        First data index assigned to the specified measurement event.
    length : integer
        Number of sampling points for the specified measurement event.
    """
    pattern_c = CHAR(512)
    event_c = CHAR(512)
    cycle_c = INT()
    loop_c = DOUBLE()
    count_c = INT()
    index_c = INT()
    length_c = INT()
    error = B1530.WGFMU_getMeasureEvent(INT(chanId), INT(measId), pattern_c,
                                       event_c, byref(cycle_c), byref(loop_c),
                                       byref(count_c), byref(index_c),
                                       byref(length_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, pattern_c.value, event_c.value, cycle_c.value, loop_c.value,
            count_c.value, index_c.value, length_c.value)

def getMeasureEventAttribute(chanId, measId):
    """
    This function specifies a channel and a measurement event index, and
    returns the corresponding measurement event attribute (time, points,
    interval, average, and rdata) which have been set by the setMeasureEvent
    function.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    measId : integer
        Measurement event index. For instance, the index can be read by 
        isMeasureEventCompleted.

    Returns
    -------
    error : integer
        Error status
    time : numeric
        Measurement start time in the pattern, in second.
    point : integer
        Number of sampling points.
    interval : numeric
        Sampling interval, in second.
    average : numeric
        Averaging time, in second.
    rdata : integer
        rdata value of setMeasureEvent.
    """
    time_c = DOUBLE()
    points_c = INT()
    interval_c = DOUBLE()
    average_c = DOUBLE()
    rdata_c = INT()
    error = B1530.WGFMU_getMeasureEventAttribute(INT(chanId), INT(measId),
                                                byref(time_c), byref(points_c),
                                                byref(interval_c),
                                                byref(average_c),
                                                byref(rdata_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, time_c.value, points_c.value, interval_c.value,
            average_c.value, rdata_c.value)

def getMeasureEvents(chanId, measId, eventsNo):
    """
    This function specifies a channel and a range of measurement events, and
    returns the corresponding setup (pattern, event, cycle, loop, count, index,
    and length). To know the total number of events, execute the
    getMeasureEventSize function.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    measId : integer
        First index of the measurement events to read setup. Integer. measId
        must be 0 to the total number of measurement events -1. Error occurs if
        the value is out of this range.
    eventsNo : integer
        Number of measurement events to read setup. eventsNo must be 1 to the
        (total number of measurement events - measId). If eventsNo is greater
        than this value, all of the returned data is stored in pattern, event,
        cycle, loop, count, index, and length and a warning occurs. Error
        occurs if eventsNo is less than 1.

    Returns
    -------
    error : integer
        Error status
    eventsNo : integer
        Number of events returned.
    pattern : string array
        Waveform pattern name.
    event : string array
        Event name.
    cycle : integer array
        Usage count. This parameter means how many times the pattern is used in
        the sequence of the specified channel.
    loop : numeric array
        Loop count. This parameter means how many times the pattern is looped
        in the sequence of the specified channel.
    count : integer array
        Event count. This parameter means how many times the event is used in
        the pattern.
    index : integer array
        First data index assigned to the specified measurement event.
    length : integer array
        Number of sampling points for the specified measurement event.
    """
    eventsNo_c = INT(eventsNo)
    pattern_c = [ct.create_string_buffer(512) for i in range(eventsNo)]
    pattern_c_p = (ct.c_char_p * eventsNo)(*map(ct.addressof, pattern_c))
    event_c = [ct.create_string_buffer(512) for i in range(eventsNo)]
    event_c_p = (ct.c_char_p * eventsNo)(*map(ct.addressof, event_c))
    cycle_c = (INT * eventsNo)(0)
    loop_c = (DOUBLE * eventsNo)(0.)
    count_c = (INT * eventsNo)(0)
    index_c = (INT * eventsNo)(0)
    length_c = (INT * eventsNo)(0)
    error = B1530.WGFMU_getMeasureEvents(INT(chanId), INT(measId),
                                         byref(eventsNo_c), pattern_c_p,
                                         event_c_p, byref(cycle_c),
                                         byref(loop_c), byref(count_c),
                                         byref(index_c), byref(length_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    pattern = [s.value for s in pattern_c]
    event = [s.value for s in event_c]
    return (error, eventsNo_c.value, pattern[:], event[:], cycle_c[:],
            loop_c[:], count_c[:], index_c[:], length_c[:])

def getMeasureEventSize(chanId):
    """
    This function returns the total number of measurement events defined in the
    source output and measurement sequence set to the specified channel.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status
    size : integer
        Total number of measurement events.
    """
    size_c = INT()
    error = B1530.WGFMU_getMeasureEventSize(INT(chanId), byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, size_c.value)
 
def getMeasureMode(chanId):
    """
    This function returns the measurement mode set to the specified channel.
    The value is set by the setMeasureMode function. The setting is applied to
    the channel by the update, updateChannel, execute, or the functions of the
    DC measurement group.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status
    mode : integer
        Measurement mode of the specified channel.
    """
    mode_c = INT()
    error = B1530.WGFMU_getMeasureMode(INT(chanId), byref(mode_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, mode_c.value)
 
def getMeasureTime(chanId, index):
    """
    This function specifies a channel and an index of measurement point, and
    returns the measurement start time for the point. For the averaging
    measurement which takes multiple data for one point measurement, the
    returned value will be (start time + stop time)/2.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    index : integer
        Index of the measurement point to read the measurement start time.
        index must be 0 to the (total number of measurement points - 1). Error
        occurs if the value is out of this range.

    Returns
    -------
    error : integer
        Error status
    time : numeric
        Measurement start time, in second.
    """
    time_c = DOUBLE()
    error = B1530.WGFMU_getMeasureTime(INT(chanId), INT(index), byref(time_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, time_c.value)

def getMeasureTimes(chanId, index, length):
    """
    This function specifies a channel and a range of measurement points, and
    returns the measurement start time for the points. For the averaging
    measurement which takes multiple data for one point measurement, the
    returned value will be (start time + stop time)/2. To know the total number
    of measurement points, execute the getMeasureTimeSize function.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    index : integer
        Index of the measurement point to read the measurement start time.
        index must be 0 to the (total number of measurement points - 1). Error
        occurs if the value is out of this range.
    length : integer
        Number of measurement points to read the measurement start time. length
        must be 1 to the total number of measurement points - index. If length
        is greater than this value, all of the returned data is stored in time
        and a warning occurs. Error occurs if length is less than 1.

    Returns
    -------
    error : integer
        Error status
    time : numeric array
        Measurement start time, in second.
    """
    length_c = INT(length)
    time_c = (DOUBLE * length)()
    error = B1530.WGFMU_getMeasureTimes(INT(chanId), INT(index),
                                        byref(length_c), byref(time_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, time_c[:])

def getMeasureTimeSize(chanId):
    """
    This function returns the total number of measurement points defined in the
    source output and measurement sequence set to the specified channel.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status
    size : integer
        Total number of measurement points.
    """
    size_c = INT()
    error = B1530.WGFMU_getMeasureTimeSize(INT(chanId), byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, size_c.value)

def getMeasureValue(chanId, index):
    """
    This function specifies a channel and an index of measurement point, and
    returns the measurement data (time and value) for the point. For the
    averaging measurement which takes multiple data for one point measurement,
    the returned value is the value given by averaging the multiple measured
    values.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    index : integer
        Index of the measurement point to read the measured value. index must
        be 0 to the total number of measurement points -1. Error occurs if the
        value is out of this range.

    Returns
    -------
    error : integer
        Error status
    time : numeric
        Measurement start time, in second.
    value : numeric
        Measured value, in V or A.
    """
    value_c = DOUBLE()
    time_c = DOUBLE()
    error = B1530.WGFMU_getMeasureValue(INT(chanId), INT(index), byref(time_c),
                                        byref(value_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, time_c.value, value_c.value)

def getMeasureValues(chanId, index, length):
    """
    This function specifies a channel and a range of measurement points, and
    returns the measurement data (time and value) for the points. For the
    averaging measurement which takes multiple data for one point measurement,
    the returned value is the value given by averaging the multiple measured
    values.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    index : integer
        First index of the measurement points to read the measured value. index
        must be 0 to the total number of measurement points -1. Error occurs if
        the value is out of this range.
    length : integer
        Number of measurement points to read the measured value. length must be
        1 to the total number of measurement points - index. If length is
        greater than this value, all of the returned data is stored in time and
        voltage and a warning occurs. Error occurs if length is less than 1.

    Returns
    -------
    error : integer
        Error status
    time : numeric array
        Measurement start time, in second.
    value : numeric array
        Measured value, in V or A.
    """
    length_c = INT(length)
    value_c = (DOUBLE * length)()
    time_c = (DOUBLE * length)()
    error = B1530.WGFMU_getMeasureValues(INT(chanId), INT(index),
                                         byref(length_c), byref(time_c),
                                         byref(value_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, time_c[:], value_c[:])

def getMeasureValueSize(chanId):
    """
    This function returns the number of completed measurement points and the
    total number of measurement points set to the specified channel.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status
    complete : integer
        Number of the measurement events which have been already completed.
    total : integer
        Total number of the measurement events.
    """
    complete_c = INT()
    total_c = INT()
    error = B1530.WGFMU_getMeasureValueSize(INT(chanId), byref(complete_c),
                                            byref(total_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, complete_c.value, total_c.value)

def getMeasureVoltageRange(chanId):
    """
    This function returns the voltage measurement range set to the specified
    channel. The value is set by the setMeasureVoltageRange function. The
    setting is applied to the channel by the update, updateChannel, execute, or
    the functions of the DC measurement group. The setting is not effective for
    the current measurement mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status
    vRange : integer
        Voltage measurement range.
    """
    vRange_c = INT()
    error = B1530.WGFMU_getMeasureVoltageRange(INT(chanId), byref(vRange_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, vRange_c.value)

def getOperationMode(chanId):
    """
    This function returns the operation mode set to the specified channel. The
    value is set by the setOperationMode function. The setting is applied to
    the channel by the update, updateChannel, execute, or the functions of the
    DC measurement group.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status
    mode : integer
        Operation mode.
    """
    mode_c = INT()
    error = B1530.WGFMU_getOperationMode(INT(chanId), byref(mode_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, mode_c.value)

def getPatternForceValue(pattern, index):
    """
    This function specifies a pattern and an index of scalar, and returns the
    corresponding scalar data (time and voltage).

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to read the scalar data.
    index : integer
        Index of the scalar to read data. index must be 0 to the total number 
        of scalar -1. Error occurs if the value is out of this range.

    Returns
    -------
    error : integer
        Error status
    time : numeric
        Time value of the scalar, in second.
    voltage : numeric
        Voltage value of the scalar, in V.
    """
    pattern_c = CHAR(pattern, len(pattern))
    voltage_c = DOUBLE()
    time_c = DOUBLE()
    error = B1530.WGFMU_getPatternForceValue(pattern_c, INT(index),
                                             byref(time_c), byref(voltage_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, time_c.value, voltage_c.value)

def getPatternForceValues(pattern, index, length):
    """
    This function specifies a pattern and a range of scalar, and returns the
    corresponding scalar data (time and voltage). To know the total number of
    scalar, execute the getPatternForceValueSize function.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to read the scalar data.
    index : integer
        First index of the scalar to read data. index must be 0 to the total
        number of scalar -1. Error occurs if the value is out of this range.
    length : integer
        Number of scalar to read. length must be 1 to the total number of
        scalar - index. If length is greater than this value, all of the
        returned data is stored in time and voltage and a warning occurs. Error
        occurs if length is less than 1.

    Returns
    -------
    error : integer
        Error status
    length : integer
        Number of scalar returned.
    time : numeric array
        Time value of the scalar, in second.
    voltage : numeric array
        Voltage value of the scalar, in V.
    """
    pattern_c = CHAR(pattern, len(pattern))
    length_c = INT(length)
    voltage_c = (DOUBLE * length)()
    time_c = (DOUBLE * length)()
    error = B1530.WGFMU_getPatternForceValues(pattern_c, INT(index),
                                              byref(length_c), byref(time_c),
                                              byref(voltage_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, length_c.value, time_c[:], voltage_c[:])

def getPatternForceValueSize(pattern):
    """
    This function returns the total number of scalar defined in the specified
    waveform pattern.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to read the scalar data.

    Returns
    -------
    error : integer
        Error status
    size : integer
        Total number of scalar.
    """
    pattern_c = CHAR(pattern, len(pattern))
    size_c = INT()
    error = B1530.WGFMU_getPatternForceValueSize(pattern_c, byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, size_c.value)

def getPatternInterpolatedForceValue(pattern, time):
    """
    This function specifies a pattern and a time value (time), and returns the
    voltage output value (voltage) of the specified pattern at the specified
    time. The returned value may be the value given by the interpolation.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to read the scalar data.
    time : numeric
        Time to read the voltage output value, in second. time must be 0 to the
        length of the waveform specified by pattern. Error occurs if the value
        is out of this range.

    Returns
    -------
    error : integer
        Error status
    voltage : numeric
        Voltage output value, in V.
    """
    pattern_c = CHAR(pattern, len(pattern))
    voltage_c = DOUBLE()
    error = B1530.WGFMU_getPatternInterpolatedForceValue(pattern_c,
                                                         DOUBLE(time),
                                                         byref(voltage_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, voltage_c.value)

def getPatternMeasureTime(pattern, index):
    """
    This function specifies a pattern and an index of measurement point, and
    returns the measurement start time for the point. For the averaging
    measurement which takes multiple data for one point measurement, the
    returned value will be (start time + stop time)/2.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to read the measurement start time.
    index : integer
        Index of the measurement point to read the measurement start time.
        index must be 0 to the total number of measurement points -1. Error
        occurs if the value is out of this range.

    Returns
    -------
    error : integer
        Error status
    time : numeric
        Measurement start time, in second.
    """
    pattern_c = CHAR(pattern, len(pattern))
    time_c = DOUBLE()
    error = B1530.WGFMU_getPatternMeasureTime(pattern_c, INT(index),
                                              byref(time_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, time_c.value)

def getPatternMeasureTimes(pattern, index, length):
    """
    This function specifies a pattern and a range of measurement points, and
    returns the measurement start time for the points. For the averaging
    measurement which takes multiple data for one point measurement, the
    returned value will be (start time + stop time)/2. To know the total number
    of measurement points, execute the getPatternMeasureTimeSize function.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to read the measurement start time.
    index : integer
        First index of the measurement points to read the measurement start
        time. Integer. index must be 0 to the total number of measurement
        points -1. Error occurs if the value is out of this range.
    length : integer
        Number of measurement points to read the measurement start time. length
        must be 1 to the total number of measurement points - index. If length
        is greater than this value, all of the returned data is stored in time
        and a warning occurs. Error occurs is length is less than 1.

    Returns
    -------
    error : integer
        Error status
    length : integer
        Number of measurement points.
    time : numeric array
        Measurement start time, in second.
    """
    pattern_c = CHAR(pattern, len(pattern))
    length_c = INT(length)
    time_c = (DOUBLE * length)()
    error = B1530.WGFMU_getPatternMeasureTimes(pattern_c, INT(index),
                                               byref(length_c), byref(time_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, length_c.value, time_c[:])

def getPatternMeasureTimeSize(pattern):
    """
    This function returns the total number of measurement points in the
    specified waveform pattern.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to read the measurement start time.

    Returns
    -------
    error : integer
        Error status
    size : integer
        Total number of measurement points.
    """
    pattern_c = CHAR(pattern, len(pattern))
    size_c = INT()
    error = B1530.WGFMU_getPatternMeasureTimeSize(pattern_c, byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, size_c.value)

def getStatus():
    """
    This function reads the status of the WGFMU channels in the Fast IV mode or
    the PG mode. The returned values are the maximum of the values presented by
    all active channels.

    Parameters
    ----------
    None

    Returns
    -------
    error : integer
        Error status
    status : integer
        Status.
    elapsT : numeric
        Estimated elapsed time, in second.
    totalT : numeric
        Estimated total time until all sequences are completed, in second.
    """
    status_c = INT()
    elapsT_c = DOUBLE()
    totalT_c = DOUBLE()
    error = B1530.WGFMU_getStatus(byref(status_c), byref(elapsT_c),
                                  byref(totalT_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, status_c.value, elapsT_c.value, totalT_c.value)

def getTriggerOutMode(chanId):
    """
    This function returns the trigger output mode of the specified channel.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status
    mode : integer
        Trigger output mode.
    polarity : integer
        Trigger polarity.
    """
    mode_c = INT()
    polarity_c = INT()
    error = B1530.WGFMU_getTriggerOutMode(INT(chanId), byref(mode_c),
                                          byref(polarity_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, mode_c.value, polarity_c.value)

def getWarningLevel():
    """
    This function reads the warning level setting. The warning level affects to
    the getWarningSummary, getWarningSummarySize, and openLogFile functions.

    Parameters
    ----------
    None

    Returns
    -------
    error : integer
        Error status
    level : integer
        Warning level setting.
    """
    level_c = INT()
    error = B1530.WGFMU_getWarningLevel(byref(level_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, level_c.value)

def getWarningSummary():
    """
    This function reads the warning summary string which contains all warnings.
    To know the length of the warning summary string, execute the
    getWarningSummarySize function. The warning summary string is cleared by
    the clear function.

    Parameters
    ----------
    None

    Returns
    -------
    error : integer
        Error status
    results : string
        Warning summary string.
    size : integer
        Length of the warning summary string.
    """
    size_c = INT(1)
    B1530.WGFMU_getWarningSummarySize(byref(size_c))
    result_c = CHAR(size_c.value + 1)
    error = B1530.WGFMU_getWarningSummary(result_c, byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, result_c.value, size_c.value)

def getWarningSummarySize(size):
    """
    This function returns the length of the warning summary string which
    contains all warnings.

    Parameters
    ----------
    None

    Returns
    -------
    error : integer
        Error status.
    size : integer
        Length of the warning summary string.
    """
    size_c = INT()
    error = B1530.WGFMU_getWarningSummarySize(byref(size_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, size_c.value)

def initialize():
    """
    This function resets all WGFMU channels. This function does not clear the
    software setup information of the instrument library.

    Parameters
    ----------
    None

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_initialize()
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def isMeasureEnabled(chanId):
    """
    This function returns if the specified channel is enabled or disabled for
    the measurement. This function is not available for the channels in the DC
    mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status.
    status : integer
        Measurement status of channel.

    Notes
    -----
    If status=7000 (WGFMU_MEASURE_ENABLED_DISABLE), the channel cannot perform
    measurement even if the channel is either Fast IV or PG mode and the
    running sequence pattern tries measurement.
    """
    status_c = INT()
    error = B1530.WGFMU_isMeasureEnabled(INT(chanId), byref(status_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, status_c.value)

def isMeasureEventCompleted(chanId, pattern, event, cycle, loop, count):
    """
    This function specifies a measurement event setup (chanId, pattern, event,
    cycle, loop, and count), and returns the corresponding execution status
    (complete, measId, index, and length).

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    pattern : string
        Name of waveform pattern to get the event address.
    event : string
        Name of event to get the event address.
    cycle : integer
        Usage count. The value starts from 0. This parameter means how many
        times the specified pattern is used in the sequence of the specified
        channel.
    loop : numeric
        Loop count. The value starts from 0. This parameter means how many
        times the specified pattern is looped in the sequence of the specified
        channel.
    count : integer
        Event count. The value starts from 0. This parameter means how many
        times the specified event is used in the specified pattern.

    Returns
    -------
    error : integer
        Error status.
    complete : integer
        Execution status of the specified measurement event.
    measId : integer
        Measurement event index used for getMeasureEventAttribute.
    index : integer
        First data index assigned to the specified measurement event.
    length : integer
        Number of sampling points for the specified measurement event.
    """
    pattern_c = CHAR(pattern, len(pattern))
    event_c = CHAR(event, len(event))
    complete_c = INT()
    measId_c = INT()
    index_c = INT()
    length_c = INT()
    error = B1530.WGFMU_isMeasureEventCompleted(INT(chanId), pattern_c,
                                                event_c, INT(cycle),
                                                DOUBLE(loop), INT(count),
                                                byref(complete_c),
                                                byref(measId_c),
                                                byref(index_c),
                                                byref(length_c))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return (error, complete_c.value, measId_c.value, index_c.value,
            length_c.value)

def openLogFile(fname):
    """
    This function opens a file used to log errors and warnings. If the
    specified file does not exist, this function creates new file. If the
    specified file exists, this function appends the log information to the
    file. Error occurs if an invalid path is specified, a file is not created,
    or a log information is not written.

    Parameters
    ----------
    chanId : string
        Name of log file to store errors and warnings information.

    Returns
    -------
    error : integer
        Error status.
    """
    fname_c = CHAR(fname, len(fname))
    error = B1530.WGFMU_openLogFile(fname_c)
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def openSession(address):
    """
    This function opens the communication session with the B1500A by using the
    WGFMU instrument library.

    Parameters
    ----------
    address : string
        VISA address of the B1500A("GPIB0::17::INSTR" for example).

    Returns
    -------
    error : integer
        Error status.
    """
    address_c = CHAR(address, len(address))
    error = B1530.WGFMU_openSession(address_c)
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setForceDelay(chanId, delay):
    """
    This function sets the device delay time of the specified source channel in
    the Fast IV mode or the PG mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    delay : numeric
        Device delay time, in second. delay must be -50 ns to 50 ns, in 625 ps
        resolution. If the value is not multiple number of 625 ps, the value is
        rounded to the nearest multiple number. For example, if the value is
        1.5 ns, the value is rounded to 1.25 ns.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_setForceDelay(INT(chanId), DOUBLE(delay))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setForceVoltageRange(chanId, vRange):
    """
    This function sets the voltage output range of the specified source
    channel. The setting is applied to the channel by the update,
    updateChannel, execute, or the functions of the DC measurement group.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    vRange : integer
        Voltage output range.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_setForceVoltageRange(INT(chanId), INT(vRange))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setMeasureCurrentRange(chanId, iRange):
    """
    This function sets the voltage output range of the specified source
    channel. The setting is applied to the channel by the update,
    updateChannel, execute, or the functions of the DC measurement group.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    iRange : integer
        Current output range.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_setMeasureCurrentRange(INT(chanId), INT(iRange))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setMeasureDelay(chanId, delay):
    """
    This function sets the device delay time of the specified measurement
    channel in the Fast IV mode or the PG mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    delay : numeric
        Device delay time, in second. delay must be -50 ns to 50 ns, in 625 ps
        resolution. If the value is not multiple number of 625 ps, the value is
        rounded to the nearest multiple number. For example, if the value is
        1.5 ns, the value is rounded to 1.25 ns.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_setMeasureDelay(INT(chanId), DOUBLE(delay))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setMeasureEnabled(chanId, status):
    """
    This function enables or disables the measurement ability of the specified
    channel. This function is not available for the channels in the DC mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    status : integer
        Enables or disables the measurement ability of the channel.

    Returns
    -------
    error : integer
        Error status.

    Notes
    -----
    If status=7000 (WGFMU_MEASURE_ENABLED_DISABLE), the channel cannot perform
    measurement even if the channel is either Fast IV or PG mode and the
    running sequence pattern tries measurement.
    """
    error = B1530.WGFMU_setMeasureEnabled(INT(chanId), INT(status))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setMeasureEvent(pattern, event, time, points, interval, average, rdata):
    """
    This function defines a measurement event which is a sampling measurement
    performed by the WGFMU channel while it outputs a waveform pattern.
    Waveform pattern specified by pattern must be created before this function
    is executed. See createPattern and createXxxPattern to create a pattern
    data.
    If time, interval, or average value is not multiple number of 10 ns, the
    value is rounded to the nearest multiple number. For example, if the value
    is 32 ns, the value is rounded to 30 ns.

    Parameters
    ----------
    pattern : string
        Waveform pattern name. The measurement event is performed while the
        WGFMU channel outputs this waveform pattern.
    event : string
        Measurement event name. The event name is not unique. The name can be
        used for another measurement event, such as an event to set a different
        sampling condition within the same waveform pattern, an event for the
        other waveform pattern, and so on.
    time : numeric
        Measurement start time, in second. Sampling measurement is started at
        this time. Time origin is the origin of the specified pattern. The
        sampling measurement will be stopped at the following eventEndTime. If
        you set average=0, add 10-8 (10 ns) to the formula.
            +---------------------------------------------------------+
            | eventEndTime = time + interval * (points - 1) + average |
            +---------------------------------------------------------+
        The time and eventEndTime must be 0 to the total time of pattern in
        10-8 (10 ns) resolution.
    points : integer
        Number of sampling points. Positive value. Note that the measurement
        data must be read before the total number of data stored in the channel
        exceeds about 4,000,000. The number of data which can be stored in the
        hardware memory depends on the average value.
    interval : numeric
        Sampling interval, in second. 10-8 (10 ns) to 1.34217728, in 10-8 
        (10 ns) resolution.
    average : numeric
        Averaging time, in second. 0 (no averaging), or 10-8 (10 ns) to
        0.020971512 (approximately 20 ms), in 10-8 (10 ns) resolution. Do not
        have to exceed the interval value. If nonzero value is specified, the
        channel repeats measurement in 5 ns interval while the average period,
        and returns the averaging result data. For example, if a measurement
        starts at 0 ns and average=20 ns, measurement is performed at 0, 5, 10,
        and 15 ns. And time data for the averaging result data is
        :math:`10 ns = (0+20)/2.`
    rdata : integer
        Averaging data output mode or raw data output mode.

    Returns
    -------
    error : integer
        Error status.

    Notes
    -----
    If a pattern contains the multiple events which change the averaging
    conditions, the interval between the measurement start times (time) of the
    adjacent events must be >= 100 ns. Improper interval causes a runtime
    error.
    """
    pattern_c = CHAR(pattern, len(pattern))
    event_c = CHAR(event, len(event))
    error = B1530.WGFMU_setMeasureEvent(pattern_c, event_c, DOUBLE(time),
                                        INT(points), DOUBLE(interval),
                                        DOUBLE(average), INT(rdata))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setMeasureMode(chanId, mode):
    """
    This function sets the measurement mode. The setting is applied to the
    channel by the update, updateChannel, execute, or the functions of the DC
    measurement group.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    mode : integer
        Measurement mode of the specified channel.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_setMeasureMode(INT(chanId), INT(mode))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setMeasureVoltageRange(chanId, vRange):
    """
    This function sets the voltage measurement range of the specified
    measurement channel. The setting is applied to the channel by the update,
    updateChannel, execute, or the functions of the DC measurement group. The
    setting is not effective for the current measurement mode.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    vRange : integer
        Voltage measurement range.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_setMeasureVoltageRange(INT(chanId), INT(vRange))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setOperationMode(chanId, mode):
    """
    This function sets the operation mode of the specified channel. The setting
    is applied to the channel by the update, updateChannel, execute, or the
    functions of the DC measurement group.
    In the Fast IV mode, the channel can perform the voltage force and current
    measurement (VFIM) or the voltage force and voltage measurement (VFVM). In
    the PG mode, the channel can perform the voltage force and voltage
    measurement (VFVM). The output voltage will be divided by the internal
    50 Ohms resistor and the load impedance.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    mode : integer
        Operation mode.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_setOperationMode(INT(chanId), INT(mode))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setRangeEvent(pattern, event, time, eRange):
    """
    This function defines a range event which is the range change operation for
    the current measurement performed by the WGFMU channel while it outputs a
    waveform pattern. This function is available only for the current
    measurements in the Fast IV mode. Waveform pattern specified by pattern
    must be created before this function is executed. See createPattern and
    createXxxPattern to create a pattern data.

    Parameters
    ----------
    pattern : string
        Waveform pattern name. The range event is performed while the WGFMU
        channel outputs this waveform pattern.
    event : string
        Range event name.
    time : numeric
        Range change time, in second. Range change is performed at this time.
        Time origin is the origin of the specified pattern. 0 to the total time
        of pattern in 10 ns resolution. The event end time will be time+10 ns.
        If the value is not multiple number of 10 ns, the value is rounded to
        the nearest multiple number. For example, if the value is 32 ns, the
        value is rounded to 30 ns.
    eRange : integer
        Current measurement range.

    Returns
    -------
    error : integer
        Error status.

    Notes
    -----
    To set a pattern with the multiple events which change the range setup
    three times or more continuously, the time difference between the
    measurement start time (time) of the adjacent events must be > 2 us. To set
    a pattern with both of the range event and the measurement event, the range
    event must be set to a term out of average defined in the measurement
    event.
    """
    pattern_c = CHAR(pattern, len(pattern))
    event_c = CHAR(event, len(event))
    error = B1530.WGFMU_setRangeEvent(pattern_c, event_c, DOUBLE(time),
                                      INT(eRange))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setTimeout(timeout):
    """
    This function sets timeout of the present session.

    Parameters
    ----------
    timeout : numeric
        Timeout value, in second. 1 or more, 1 us resolution. Error occurs if
        the timeout value is less than 1. Default value is 100 s. If the
        doSelfCalibration or doSelfTest function is executed when the timeout
        setting is less than 600 s, the timeout is automatically changed to
        600 s and returned to the previous value after the function is
        completed.

    Returns
    -------
    error : integer
        Error status.

    Notes
    -----
    The instrument library checks the set ready bit (bit 4) of the status byte
    when a function is executed. If the set ready bit is not raised, the
    instrument library continues checking the status byte until the set ready
    bit is raised or timeout occurs. Timeout will be caused by the following
    reason.
        * Improper GPIB address is specified by the openSession function.
        * The timeout value is too short to complete the function.
    Appropriate timeout value will be the maximum time required to complete the
    function.
    """
    error = B1530.WGFMU_setTimeout(DOUBLE(timeout))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setTriggerOutEvent(pattern, event, time, duration):
    """
    This function defines a trigger output event which is the trigger output
    operation performed by the WGFMU channel while it outputs a waveform
    pattern. Event trigger output mode must be set by setTriggerOutMode.
    Waveform pattern specified by pattern must be created before this function
    is executed. See createPattern and createXxxPattern to create a pattern
    data.

    Parameters
    ----------
    pattern : string
        Waveform pattern name. The trigger output event is performed while the
        WGFMU channel outputs this waveform pattern.
    event : string
        Trigger output event name.
    time : numeric
        Trigger output time, in second. Numeric. Trigger is output at this
        time. Time origin is the origin of the specified pattern. 0 to the
        total time of pattern in 10 ns resolution. The event end time will be
        time+duration. If the value is not multiple number of 10 ns, the value
        is rounded to the nearest multiple number. For example, if the value is
        32 ns, the value is rounded to 30 ns.
    duration : numeric
        Duration time of output trigger, in second.

    Returns
    -------
    error : integer
        Error status.

    Notes
    -----
    If time = duration = 0 is set, the channel outputs the trigger when it
    starts to apply the initial voltage of the specified pattern.
    """
    pattern_c = CHAR(pattern, len(pattern))
    event_c = CHAR(event, len(event))
    error = B1530.WGFMU_setTriggerOutEvent(pattern_c, event_c, DOUBLE(time),
                                           DOUBLE(duration))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setTriggerOutMode(chanId, mode, polarity):
    """
    This function sets the trigger output mode of the specified channel.

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).
    mode : integer
        Trigger output mode.
    polarity : integer
        Trigger polarity.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_setTriggerOutMode(INT(chanId), INT(mode),
                                          INT(polarity))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setVector(pattern, time, voltage):
    """
    This function specifies a scalar data by using time and voltage, and adds
    it to the specified waveform pattern or replaces the scalar previously
    defined in the specified waveform pattern with the scalar specified by this
    function. The latest execution is always effective.
    Waveform pattern specified by pattern must be created before this function
    is executed. See createPattern and createXxxPattern to create a pattern
    data.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to add a vector.
    time : numeric
        Absolute time value, not incremental time value, in second. The value
        must be time >= 0 in 10 ns resolution. If the specified value does not
        satisfy this requirement, the vector is not added or replaced. If
        time=0, the initial voltage of the pattern is replaced. If time is not
        multiple number of 10 ns, the value is rounded to the nearest multiple
        number. For example, if the value is 72 ns, it is rounded to 70 ns.
    voltage : numeric
        Output voltage, in V.

    Returns
    -------
    error : integer
        Error status.
    """
    pattern_c = CHAR(pattern, len(pattern))
    error = B1530.WGFMU_setVector(pattern_c, DOUBLE(time), DOUBLE(voltage))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setVectors(pattern, time, voltage, size):
    """
    This function specifies multiple scalar data by using time and voltage, and
    adds them to the specified waveform pattern or replaces the scalar
    previously defined in the specified waveform pattern with the scalar
    specified by this function. The latest execution is always effective.
    Waveform pattern specified by pattern must be created before this function
    is executed. See createPattern and createXxxPattern to create a pattern
    data.

    Parameters
    ----------
    pattern : string
        Name of waveform pattern to add a vector.
    time : numeric array
        Absolute time value, not incremental time value, in second. Array
        elements must be corresponding to the voltage array elements together
        in the element order. The value must be time >= 0 in 10 ns resolution.
        If the specified value does not satisfy this requirement, the vector is
        not added or replaced. If time=0, the initial voltage of the pattern is
        replaced. If time is not multiple number of 10 ns, the value is rounded
        to the nearest multiple number. For example, if the value is 72 ns, it
        is rounded to 70 ns.
    voltage : numeric array
        Output voltage, in V. Array elements must be corresponding to the time
        array elements together in the element order.

    Returns
    -------
    error : integer
        Error status.
    """
    pattern_c = CHAR(pattern, len(pattern))
    time_c = (DOUBLE * size)()
    time_c[:] = time[:]
    voltage_c = (DOUBLE * size)()
    voltage_c[:] = voltage[:]
    error = B1530.WGFMU_setVectors(pattern_c, byref(time_c), byref(voltage_c),
                                   INT(size))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def setWarningLevel(level):
    """
    This function sets the warning level. The warning level affects to the
    getWarningSummary, getWarningSummarySize, and openLogFile functions.

    Parameters
    ----------
    level : integer
        Warning level.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_setWarningLevel(INT(level))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def treatWarningsAsErrors(level):
    """
    This function sets the threshold between warning and error by specifying
    the warning level.
        +---------------------------------------------------------------------+
        | If level = WGFMU_WARNING_LEVEL_OFF, no warning is assumed as error. |
        +---------------------------------------------------------------------+
        | If level = WGFMU_WARNING_LEVEL_SEVERE, the warning of this level    |
        | will be assumed as error and the others will be warning.            |
        +---------------------------------------------------------------------+
        | If level = WGFMU_WARNING_LEVEL_NORMAL, the warning of this level and|
        | WGFMU_WARNING_LEVEL_SEVERE will be assumed as error and the others  |
        | will be warning.                                                    |
        +---------------------------------------------------------------------+
        | If level = WGFMU_WARNING_LEVEL_INFORMATION, all warning will be     |
        | assumed as error.                                                   |
        +---------------------------------------------------------------------+

    Parameters
    ----------
    level : integer
        Warning level which will be the threshold between warning and error.

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_treatWarningsAsErrors(INT(level))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def update():
    """
    This function updates the setting of all WGFMU channels in the Fast IV mode
    or the PG mode. After this function, all WGFMU channels apply the initial
    voltage set by the createPattern function.
    
    This function updates the setting of all WGFMU channels in the Fast IV mode
    or the PG mode. After this function, all WGFMU channels apply the initial
    voltage set by the createPattern function. This function applies the setup
    of the following function to the channel.
        * setOperationMode
        * setForceVoltageRange
        * setMeasureCurrentRange
        * setMeasureVoltageRange
        * setMeasureMode

    Parameters
    ----------
    None

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_update()
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def updateChannel(chanId):
    """
    This function updates the setting of the specified channel in the Fast IV
    mode or the PG mode. After this function, the channel applies the initial
    voltage set by the createPattern function.
    
    This function applies the setup of the following function to the channel.
        * setOperationMode
        * setForceVoltageRange
        * setMeasureCurrentRange
        * setMeasureVoltageRange
        * setMeasureMode

    Parameters
    ----------
    chanId : integer
        Channel number (101 to 1002).

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_updateChannel(INT(chanId))
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error

def waitUntilCompleted():
    """
    This function waits until all connected WGFMU channels in the Fast IV mode
    or the PG mode are in the ready to read data status. Error occurs if a
    sequencer is not running or if no channel is in the Fast IV mode or the PG
    mode.

    Parameters
    ----------
    None

    Returns
    -------
    error : integer
        Error status.
    """
    error = B1530.WGFMU_waitUntilCompleted()
    error = [error, _errorCode[error]]
    if error[0]!=0:
        functionInfo = inspect.stack()[0]
        callerInfo = inspect.stack()[1]
        
        erFunctionInfo = inspect.getframeinfo(functionInfo[0])
        erCallerInfo = inspect.getframeinfo(callerInfo[0])
        
        error.append(erFunctionInfo.function)
        error.append(erCallerInfo.lineno)
        ErrorModule.callError(error[0], error[1], error[2], error[3])
    return error
