import csv
import re
from collections import OrderedDict
from datetime import datetime

def process_csv_file(filename):
    """
    Read data from the CSV file and process it
    :param filename: name of file to process
    :return:
    """

    data_with_dates_and_hours = []  # Initialize an empty list to store processed timestamp into date with hours
    with open(filename, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        # Loop through each row in the CSV
        for row in csv_reader:
            timestamp = row["Timestamp_EasternTime"]

            # Parse the timestamp into a datetime object
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            date = dt.strftime("%Y-%m-%d %H")  # Format the datetime as "YYYY-MM-DD HH"

            # Create a new dictionary with date and hour
            data_with_date_and_hour = {
                "Date": date
            }

            # Copy all other columns to the new dictionary
            for column_name, value in row.items():
                if column_name != "Timestamp_EasternTime":  # We no longer need the Timestamp column, so we exclude it
                    data_with_date_and_hour[column_name] = value

            # Append the processed data into the list we created for it.
            data_with_dates_and_hours.append(data_with_date_and_hour)

    return data_with_dates_and_hours


def aggregate_data(data):
    """
    Aggregate data
    :param data: data to aggregate
    :return:
    """

    aggregated_dictionary = {}  # Initialize a dictionary to aggregate data
    for items in data:

        # We created a key for the dictionary by joining date, 'G', and the site identifier, G means gemeration
        generation_key = '_'.join([str(items['Date']), 'G', items['Site']])

        # Create a key for the dictionary by joining date, 'I', and the site identifier, I means Irradiance
        irradiance_key = '_'.join([str(items['Date']), 'I', items['Site']])

        # Check if our Generation and Irradiance key exists in the aggregated_dictionary
        if generation_key in aggregated_dictionary:
            aggregated_dictionary[generation_key].append(float(items['Generation_Meter_Reading_KWh']))
        else:
            aggregated_dictionary[generation_key] = [float(items['Generation_Meter_Reading_KWh'])]

        if irradiance_key in aggregated_dictionary:
            aggregated_dictionary[irradiance_key].append(float(items['Irradiance_Wh_m2']))
        else:
            aggregated_dictionary[irradiance_key] = [float(items['Irradiance_Wh_m2'])]

    return aggregated_dictionary


def sum_irr_and_agg_irr_gen(data):
    """
    Generate sum of irradiance
    :param data: data to generate sum of irradiance
    :return: sum of irradiance, aggregated generation, and aggregated irradiance
    """

    aggregated_generation = {}  # Initialize a dictionary to store aggregated generation data
    aggregated_irradiance = {}  # Initialize a dictionary to store aggregated irradiance data
    sum_irradiance = {}  # Initialize a dictionary to store the sum of irradiance data
    for _key, values in data.items():
        if _key.find('_G_') != -1:
            aggregated_generation[_key] = sum(values)
        else:
            aggregated_irradiance[_key] = sum(values) / len(
                values
            )  # Calculate average irradiance
            sum_irradiance[_key] = sum(values)  # Calculate the sum of irradiance

    return sum_irradiance, aggregated_generation, aggregated_irradiance


def period_generation_difference_by_site(data):
    """
    Calculate differences in generation values between consecutive hours
    :param data: data to calculate differences in generation values between consecutive hours
    :return:
    """

    key_list_site_A = []  # Initialize lists to store keys and values for site A
    value_list_site_A = []
    key_list_site_B = []  # Initialize lists to store keys and values for site B
    value_list_site_B = []
    key_list_site_C = []  # Initialize lists to store keys and values for site C
    value_list_site_C = []

    data = OrderedDict(sorted(data.items()))
    for key, value in data.items():
        if re.search('_G_A', key):  # Check if the key contains '_G_A'
            key_list_site_A.append(key)
            value_list_site_A.append(value)
        elif re.search('_G_B', key):  # Check if the key contains '_G_B'
            key_list_site_B.append(key)
            value_list_site_B.append(value)
        else:  # Handle keys that do not contain '_G_A' or '_G_B'
            key_list_site_C.append(key)
            value_list_site_C.append(value)

    # Calculate differences in generation values between consecutive hours
    difference_in_generation_by_period_site_A = [value_list_site_A[j + 1] - value_list_site_A[j] for j in
                                                 range(len(value_list_site_A)) if j < (len(value_list_site_A) - 1)]
    difference_in_generation_by_period_site_A.insert(0, 0.0)
    difference_in_generation_by_period_site_B = [value_list_site_B[k + 1] - value_list_site_B[k] for k in
                                                 range(len(value_list_site_B)) if k < (len(value_list_site_B) - 1)]
    difference_in_generation_by_period_site_B.insert(0, 0.0)
    difference_in_generation_by_period_site_C = [value_list_site_C[l + 1] - value_list_site_C[l] for l in
                                                 range(len(value_list_site_C)) if l < (len(value_list_site_C) - 1)]
    difference_in_generation_by_period_site_C.insert(0, 0.0)

    # Create dictionaries mapping keys to their corresponding differences
    res_diff_A = dict(map(lambda i, j: (i, j), key_list_site_A, difference_in_generation_by_period_site_A))
    res_diff_B = dict(map(lambda i, j: (i, j), key_list_site_B, difference_in_generation_by_period_site_B))
    res_diff_C = dict(map(lambda i, j: (i, j), key_list_site_C, difference_in_generation_by_period_site_C))

    return res_diff_A, res_diff_B, res_diff_C


def aggregate_irr(data):
    """
    Aggregate irradiance data
    :param data:
    :return:
    """
    aggregated_dictionary_irradiance = {}  # Initialize a dictionary to aggregate irradiance data
    for items in data:

        # Create a key for the dictionary by joining date, 'I', and the site identifier
        irradiance_key = '_'.join([str(items['Date']), 'I', items['Site']])

        # Check if the key exists in the dictionary
        if irradiance_key in aggregated_dictionary_irradiance:
            aggregated_dictionary_irradiance[irradiance_key].append(float(items['Irradiance_Wh_m2']))
        else:
            aggregated_dictionary_irradiance[irradiance_key] = [float(items['Irradiance_Wh_m2'])]
    return aggregated_dictionary_irradiance


def percent_irradiance(data, sum_irr):
    """
    Calculate percentages of irradiance
    :param data:
    :param sum_irr:
    :return: percentages of irradiance
    """
    percent200_I = {}  # Initialize a dictionary to store percentages
    for key in data.keys():
        if sum_irr[key] > 200:  # Check if the sum of irradiance is greater than 200
            percent200_I[key] = [j / sum_irr[key] * 100 for j in data[key]]  # Calculate percentages
        else:
            percent200_I[key] = None  # Set to None if sum of irradiance is not greater than 200

    return percent200_I


def merge_data_calculations(data):
    """
    Merge data and calculations
    :return: list of data and calculations
    """
    data_list = []  # Initialize a list to store the final data
    percent200_I = data["percent200_I"]
    res_diff_A = data["res_diff_A"]
    res_diff_B = data["res_diff_B"]
    res_diff_C = data["res_diff_C"]
    aggregated_irradiance = data["aggregated_irradiance"]
    aggregated_generation = data["aggregated_generation"]

    for key in aggregated_generation.keys():
        if "_A" in key:
            if percent200_I[key[:13] + "_I_" + key[16]] is not None:
                data_list.append(
                    [
                        key[:13] + ":00:00",  # Date in HH:MM:SS format
                        key[16],  # Site identifier
                        res_diff_A[key],  # Difference in generation values for site A
                        aggregated_irradiance[
                            key[:13] + "_I_" + key[16]
                            ],  # Average irradiance for site A
                        sum(percent200_I[key[:13] + "_I_" + key[16]])
                        / len(
                            percent200_I[key[:13] + "_I_" + key[16]]
                        ),  # Sunshine share percentage for site A
                    ]
                )
            else:
                data_list.append(
                    [
                        key[:13] + ":00:00",  # Date in HH:MM:SS format
                        key[16],  # Site identifier
                        res_diff_A[key],  # Difference in generation values for the site
                        aggregated_irradiance[
                            key[:13] + "_I_" + key[16]
                            ],  # Average irradiance for the site
                        percent200_I[key[:13] + "_I_" + key[16]],  # Sunshine share as None
                    ]
                )

        elif "_B" in key:
            if percent200_I[key[:13] + "_I_" + key[16]] is not None:
                data_list.append(
                    [
                        key[:13] + ":00:00",  # Date in HH:MM:SS format
                        key[16],  # Site identifier
                        res_diff_B[key],  # Difference in generation values for site B
                        aggregated_irradiance[
                            key[:13] + "_I_" + key[16]
                            ],  # Average irradiance for site B
                        sum(percent200_I[key[:13] + "_I_" + key[16]])
                        / len(
                            percent200_I[key[:13] + "_I_" + key[16]]
                        ),  # Sunshine share percentage for site B
                    ]
                )
            else:
                data_list.append(
                    [
                        key[:13] + ":00:00",  # Date in HH:MM:SS format
                        key[16],  # Site identifier
                        res_diff_B[key],  # Difference in generation values for the site
                        aggregated_irradiance[
                            key[:13] + "_I_" + key[16]
                            ],  # Average irradiance for the site
                        percent200_I[key[:13] + "_I_" + key[16]],  # Sunshine share as None
                    ]
                )
        else:
            if percent200_I[key[:13] + "_I_" + key[16]] is not None:
                data_list.append(
                    [
                        key[:13] + ":00:00",  # Date in HH:MM:SS format
                        key[16],  # Site identifier
                        res_diff_C[key],  # Difference in generation values for site C
                        aggregated_irradiance[
                            key[:13] + "_I_" + key[16]
                            ],  # Average irradiance for site C
                        sum(percent200_I[key[:13] + "_I_" + key[16]])
                        / len(
                            percent200_I[key[:13] + "_I_" + key[16]]
                        ),  # Sunshine share percentage for site C
                    ]
                )
            else:
                data_list.append(
                    [
                        key[:13] + ":00:00",  # Date in HH:MM:SS format
                        key[16],  # Site identifier
                        res_diff_C[key],  # Difference in generation values for the site
                        aggregated_irradiance[
                            key[:13] + "_I_" + key[16]
                            ],  # Average irradiance for the site
                        percent200_I[key[:13] + "_I_" + key[16]],  # Sunshine share as None
                    ]
                )

    return data_list


def write_to_csv(data_list, filename):
    """
    Write data to CSV file
    :param data_list: data to write to CSV file
    :param filename: name of file to write to
    :return:
    """
    with open(filename, mode="w") as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write the header row
        csv_writer.writerow(
            [
                "Date",
                "Site",
                "Generation_KWh",
                "Average_irradiance_Wh_m2",
                "Sunshine_share_%",
            ]
        )

        # Write each row of data
        for row in data_list:
            csv_writer.writerow(row)


if __name__ == "__main__":
    transformed_data = process_csv_file("sample-dataset.csv")
    aggregated_data = aggregate_data(transformed_data)
    _sum_irr, _agg_gen, _agg_irr = sum_irr_and_agg_irr_gen(aggregated_data)
    _agg_irr_dict = aggregate_irr(transformed_data)
    _res_diff_A, _res_diff_B, _res_diff_C = period_generation_difference_by_site(_agg_gen)
    _percent200_I = percent_irradiance(_agg_irr_dict, _sum_irr)

    _data = {
        "percent200_I": _percent200_I,
        "res_diff_A": _res_diff_A,
        "res_diff_B": _res_diff_B,
        "res_diff_C": _res_diff_C,
        "aggregated_irradiance": _agg_irr,
        "aggregated_generation": _agg_gen,
    }
    _data_list = merge_data_calculations(_data)
    write_to_csv(_data_list, "Kolawole_Kushimo.csv")
