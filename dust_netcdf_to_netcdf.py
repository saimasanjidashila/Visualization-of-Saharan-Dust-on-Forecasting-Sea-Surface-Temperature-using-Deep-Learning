#!/usr/bin/env python3
import os
import xarray as xr
import numpy as np

# Path to the data folder and output file
data_folder = "/Volumes/Work/Thesis/Paul_miller/Thesis_Work/Dust/dust_data/"
output_path = "ducmass_filtered_2020_2024.nc"

# Initialize an empty list to store filtered data
filtered_data = []

# Process files by year
for year in range(2020, 2025):
    print(f"Processing year: {year}")
    year_folder = os.path.join(data_folder, str(year))
    
    for file_name in sorted(os.listdir(year_folder)):
        file_path = os.path.join(year_folder, file_name)
        
        # Skip hidden or non-NetCDF files
        if not file_name.endswith(".nc4") or file_name.startswith("._"):
            print(f"Skipping file: {file_name}")
            continue
        
        try:
            # Open the dataset
            ds = xr.open_dataset(file_path)
            print(f"Available times in {file_name}: {ds['time'].values}")
            
            # Extract the date from the file name
            try:
                # Adjust the index to correctly extract the date
                file_date = file_name.split(".")[3][:-4]  # Extract '20200501' from the filename
                print(f"Extracted date: {file_date}")
            except IndexError:
                print(f"Error extracting date from file: {file_name}")
                continue
            
            # Generate primary and fallback datetime objects
            try:
                primary_time = np.datetime64(f"{file_date[:4]}-{file_date[4:6]}-{file_date[6:]}T12:30:00")
                fallback_time = np.datetime64(f"{file_date[:4]}-{file_date[4:6]}-{file_date[6:]}T11:30:00")
                print(f"Primary time: {primary_time}, Fallback time: {fallback_time}")
            except Exception as e:
                print(f"Error generating time for {file_name}: {e}")
                continue
            
            # Check for primary or fallback times
            if primary_time in ds['time'].values:
                print(f"Primary time {primary_time} found in {file_name}.")
                ducmass_1230 = ds['DUCMASS'].sel(time=primary_time)
                filtered_data.append(ducmass_1230)
            elif fallback_time in ds['time'].values:
                print(f"Fallback time {fallback_time} found in {file_name}.")
                ducmass_1130 = ds['DUCMASS'].sel(time=fallback_time)
                filtered_data.append(ducmass_1130)
            else:
                print(f"Neither primary nor fallback time found in {file_name}.")
        
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
        finally:
            if 'ds' in locals():  # Ensure dataset is closed
                ds.close()

# Combine all filtered data into a single dataset
if filtered_data:
    combined_ds = xr.concat(filtered_data, dim="time")
    combined_ds.to_netcdf(output_path)
    print(f"Filtered data saved to {output_path}")
else:
    print("No data processed.")
