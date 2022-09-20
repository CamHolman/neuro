import numpy as np


def subset_epoch_events(event_times, epoch_start_times, epoch_stop_times):
    """ Given 1D array of event times, subset only those times in epochs of interest

    ex. all spikes within trial epochs, all position times in navigation epoch
    """
    # Convert float/int times to list 
    convert_types = [int, float, np.float64]
    if type(epoch_start_times) in convert_types or type(epoch_stop_times) in convert_types:
        epoch_start_times = [epoch_start_times]
        epoch_stop_times  = [epoch_stop_times]
    
    # Main
    EE = np.array([])
    for ix in range(len(epoch_start_times)):
        EE = np.append(EE,
            event_times[
                (event_times > epoch_start_times[ix]) & \
                (event_times < epoch_stop_times[ix])
                ],   
            axis = 0)
    return EE

def subset_epoch_data(data, event_times, epoch_start_times, epoch_stop_times):
    """ 
    Given 1D or 2D array of data (ex 1D head direction degrees, 2D position times) 
    and 1D array of matched event_times (ex times at which HD is recorded) with 
    matching indicies/length:

    Pull out data that falls in epochs of interes (ex navigation epochs)
    """
    # Convert float/int times to list 
    if type(epoch_start_times) in [float, int] or type(epoch_stop_times) in [float, int]:
        epoch_start_times = [epoch_start_times]
        epoch_stop_times  = [epoch_stop_times]

    # Main
    epoch_ixs = np.array([], dtype=int)
    for ix in range(len(epoch_start_times)):
        epoch_ixs_ix = np.where((epoch_start_times[ix] < event_times) & (event_times < epoch_stop_times[ix]))
        epoch_ixs = np.append(epoch_ixs, epoch_ixs_ix[0])
    
    if data.ndim == 1:
        epoch_data = data[epoch_ixs]
    elif data.ndim == 2:
        epoch_data = data[:, epoch_ixs]
    else:
        raise ValueError('data must be 1D or 2D')
    
    return epoch_data