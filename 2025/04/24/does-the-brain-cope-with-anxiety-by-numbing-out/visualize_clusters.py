import mne
from pathlib import Path
import os
import pickle
from pyprojroot import here
import numpy as np
import pandas as pd
from mne.channels import find_ch_adjacency
from mne.stats import spatio_temporal_cluster_test
from scipy import stats
from collections import OrderedDict

# --- FUNCTIONS THAT GET CALLED FROM R --- #

def get_channel_coordinates(channels):    
    '''
    Gives x, y, z coordinates for EEG channels for plotting
    
    --- PARAMETERS ---
    ------------------
    channels (list of str): 10-20 names of channels to get coordinates for
    '''
    
    # Load montage at assumed location
    file = Path('content/post/hep/Standard-10-20-Cap81.locs')
    montage = mne.channels.read_custom_montage(here() / file)
    ch_pos = montage.get_positions()['ch_pos']
    ch_pos = OrderedDict((key, value*1000) for key, value in ch_pos.items())
    ch_pos = pd.DataFrame(ch_pos).transpose()
    ch_pos.columns = ['x', 'y', 'z']
    ch_pos.insert(0, 'channel', ch_pos.index)
    ch_pos = ch_pos[ch_pos['channel'].isin(channels)]
    
    return ch_pos


# STATISTICS #


def permutation_cluster_test(item,
                             low_anchor,
                             bads,
                             time_window_min=0.25,
                             initial_alpha=0.01,
                             path=Path('analysis/data/derivatives/hep/06-evoked-clean')):
                                 
    '''
    Conducts a permutation-based clustering analysis across a median split of
    item, analyzing time points from time_window_min to end of epoch. 
    
    --- PARAMETERS ---
    ------------------
    item (str): Item name
    low_anchor (str): Name of low anchor on the scale (all lowercase)
    time_window_min (float): Analyze time points after this value
    initial_alpha (float): Alpha for finding initial clusters
    path (pathlib.Path): Path to directory containing data
    
    --- RETURNS ---
    ---------------
    out (dict) containing results of permutation test:
        t_obs: (N_timepoints x M_channels) matrix with t values as elements
        clusters: list of (array(time_idx, ...), array(channel_idx, ...)) tuples of all found clusters
        p_values: np.array of shape (N_clusters,) where each element is a p value
    '''

    # Open dictionary 
    assert(isinstance(item, str))
    file = 'eeg_dict_{}.pkl'.format(item)
    full_path = path / Path(file)
    with open(full_path, 'rb') as f:
        dic = pickle.load(f)
    # Ensure bads is a list of ints
    if isinstance(bads, list):
        bads = [int(x) for x in bads]
    else:
        bads = [int(bads)]
        
    # Get numpy arrays of shape (subjects, time, chans) for each condition
    low, high = _format_for_clustering(dic, low_anchor, bads)
    
    # Get a sample evoked object for computing distances
    probe_set = dic[list(dic.keys())[0]][low_anchor]
    sample_evoked = probe_set[list(probe_set.keys())[0]]
    adjacency, _ = find_ch_adjacency(sample_evoked.info, 'eeg')
    
    # Get the first index of timepoint thats >= the min timepoint
    time_window_idx = [i for i, e in enumerate(sample_evoked.times) if e >= time_window_min][0]
    times = sample_evoked.times[time_window_idx:]
    channels = sample_evoked.info['ch_names']
    
    # Format data as list of arrays
    X = [low[:, time_window_idx:, :],
        high[:, time_window_idx:, :]]
        
    # Configure parameters
    df = low.shape[0] - 1
    t_crit = stats.t.ppf(1 - initial_alpha, df)
    tail = 0 
    
    # Run test
    t_obs, clusters, p_values, _ = spatio_temporal_cluster_test(
        X,
        n_permutations=1000,
        threshold=t_crit,
        tail=tail,
        n_jobs=None,
        seed = 1510,
        buffer_size=None,
        adjacency=adjacency,
        stat_fun=_my_t
    )
    
    out = {'t_obs': t_obs, 'clusters': clusters, 'p_values': p_values, 
    'times': times, 'channels': channels}
    
    return out
    
    
    
    
    
# --- GETS CALLED FROM PYTHON ONLY --- #

def _format_for_clustering(dic, low_anchor, bads):
    '''
    Take in EEG data summarized as dictionary and output in format amenable to 
    permutation-based cluster analysis
    
    --- PARAMETERS ---
    ------------------
    path (str): Experience sampling item to be analyzed
    dic (dict): Dictionary with dic[subject][condition][probe] giving an evoked
    low_anchor (str): Name of low anchor on the scale for the item being summarized
                      (Comes in as all lowercase)
    bads (list of ints): Bad subject ids
    
    --- RETURNS ---
    Two numpy arrays of shape (subjects, timepoints, channels)
    The first is the array for the low anchor condition
    The second is the array for the high anchor condition
    '''
    
    # Extract condition names as strings
    conditions = list(dic[list(dic.keys())[0]].keys())
    conditions = [x.lower() for x in conditions]
    assert(len(conditions) == 2)
    c_low = conditions[0] if conditions[0] == low_anchor else conditions[1]
    c_high = conditions[0] if c_low == conditions[1] else conditions[1]
    
    # Init lists for subject data by condition
    subjects_low = []
    subjects_high = []
    
    # Generates list of (chans, timepoints), where each element is a different 
    # subject
    for subject in dic:
        # If subject is missing a condition, skip
        if not dic[subject][c_low] or not dic[subject][c_high]:
            print('Dropping subject {}. Missing a condition.'.format(subject))
            continue
        # If subject id is in bads, skip
        if int(subject.split('-')[1]) in bads:
            print('Dropping subject {}. In bads.'.format(subject))
            continue
        # Return list of evokeds for each condition
        c_low_evokeds = list(dic[subject][c_low].values())
        c_high_evokeds = list(dic[subject][c_high].values())
        subjects_low.append(mne.grand_average(c_low_evokeds).get_data())
        subjects_high.append(mne.grand_average(c_high_evokeds).get_data())
        
        
    # Convert list to extra dim of array and transpose
    low = np.stack(subjects_low, axis = 0).transpose(0, 2, 1)
    high = np.stack(subjects_high, axis = 0).transpose(0, 2, 1)
    
    return low, high
    

def _my_t(a, b):
    # t is positive for first argument being larger
    out = stats.ttest_rel(a, b)
    return out.statistic
