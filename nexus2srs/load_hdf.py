"""
Python module with functions to load HDF files and write classic SRS .dat files
"""

import os
import h5py
from numpy import squeeze


def address_name(address):
    """Convert hdf address to name"""
    return os.path.basename(address)


def load_scan_meta_data(filename):
    """
    Create dicts of metadata and scan data from hdf file
    :param filename: str filename of HDF/Nexus file
    :return scandata: {name: array} dict of scanned data, all fields have n length arrays
    :return metadata: {name: value} dict of metadata, all fields are float/int/str
    """

    with h5py.File(filename, 'r') as hdf:

        # --- Load Datasets ---
        # Generate a list of all datasets in file using hdf.visititems
        # Note that loading a dataset is just a link, not loading the actual data yet
        all_addresses = []
        all_datasets = []

        def func(address, obj):
            if isinstance(obj, h5py.Dataset):
                # print(name, obj.ndim, obj.size)
                all_addresses.append(address)
                all_datasets.append(obj)

        hdf.visititems(func)
        n_datasets = len(all_datasets)

        # --- Find Scan Length ---
        # Find datasets with ndim=1 arrays of fixed length
        scan_lengths = [ds.size for ds in all_datasets if ds.ndim == 1 and ds.size > 1]
        print('Scan length max: %d' % max(scan_lengths))
        print('Scan length min: %d' % min(scan_lengths))
        # use max(scan_lenghts) but there might be a better option
        scan_length = max(scan_lengths)

        # --- Load Data ---
        # Loop through each dataset, comparing ids to not replicate data
        #  if dataset is size==1, add to metadata
        #  if dataset is size==scan_length array, add to scandata
        ids = []
        metadata = {}
        scandata = {}
        for n in range(n_datasets):
            if all_datasets[n].id in ids:
                continue
            ids.append(all_datasets[n].id)
            name = address_name(all_addresses[n])

            # --- Metadata ---
            if all_datasets[n].size == 1:
                # metadata[address_name(all_addresses[n])] = squeeze(all_datasets[n])
                try:
                    metadata[name] = float(squeeze(all_datasets[n]))
                except ValueError:
                    metadata[name] = "'%s'" % all_datasets[n][()]

                # This is a horrid hack for cmd
                if name == 'scan_command' and 'cmd' not in metadata:
                    metadata['cmd'] = "'%s'" % all_datasets[n][()]

            # ---Scandata ---
            elif all_datasets[n].ndim == 1 and all_datasets[n].size == scan_length:
                try:
                    # Only add floats
                    scandata[name] = squeeze(all_datasets[n]) * 1.0
                except TypeError:
                    pass
        return scandata, metadata


def nxs2dat(filename):
    """
    Load HDF file and convert to classic SRS .dat file
    :param filename: str filename of HDF/Nexus file
    :return: None
    """

    scandata, metadata = load_scan_meta_data(filename)

    # --- Print data ---
    scan_length = len(next(iter(scandata.values())))
    print('Nexus File: %s' % filename)
    print('Scan length: %s' % scan_length)
    print('--- Metadata ---')
    for name, value in metadata.items():
        print('%s=%s' % (name, value))

    print('\n\n--- Scandata ---')
    print(', '.join(['%10s' % name for name in scandata]))
    for n in range(scan_length):
        print(', '.join(['%10s' % scandata[name][n] for name in scandata]))

    print('\n TheEnd')




