#TODO: If I wanna speed the whole thing up, I need to set file paths in the init function and only update upon file browsing in the GUI
#TODO: Add a README for others

# These are all part of Python's standard library (not external/3rd-party)
import sys
import csv
import statistics
import re
import math

class WeatherCalc:
    def __init__(self) -> None:
        pass
        

    """This function is a helper for daylight_temp and windchills. It converts the
    date that is inputted from a YYYY-MM-DD format to a M/D/Y format"""

    def date_format_helper(self, date):

        # creates an array so we can reformat the date to make it usable
        date_arr = date.split('-')

        # removes leading zeroes (there are no leading zeroes in the CSV file dates)
        for x in range(len(date_arr)):

            # Assumes we are not adding years that start with 0 (can't have temp 
            # data from that time period, anyways)
            date_arr[x] = date_arr[x].lstrip('0')
            if x == 0:

                # Assumes that every year will be four digits i.e. 2016 and not 0600
                # or something (similar to above assumption)
                date_arr[x] = date_arr[x][2:]

        # formats date into M/D/Y format (as in the CSV files)
        try:
            ret = date_arr[1] + '/' + date_arr[2] + '/' + date_arr[0]
        except:
            ret = "Error"

        return ret


    def daylight_temp(self, csv_file, date):
        formatted_date = self.date_format_helper(date)

        if formatted_date == "Error":
            return "Date Error"

        temp_data = []
        try:
            with open(csv_file, newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        csv_date_and_time_info = row["DATE"].split()
                    
                        csv_date = csv_date_and_time_info[0]

                        # must convert csv_time into format comparable to sunrise/sunset
                        csv_time = int(csv_date_and_time_info[1].replace(':', ''))
                        csv_sunrise = int(row["DAILYSunrise"])
                        csv_sunset = int(row["DAILYSunset"])

                        # data added to list if same date and between sunrise and sunset and
                        # the temp data is not M (missing) or blank
                        if csv_date == formatted_date and \
                            csv_sunrise < csv_time < csv_sunset and row[
                            "HOURLYDRYBULBTEMPF"] != ('M' and ''):

                            # Removes the suspect value indicator ('s') if it is part of the
                            # data (specifically just removes non-number characters)
                            csv_temp = re.sub("[^0-9]", '', row["HOURLYDRYBULBTEMPF"])

                            temp_data.append(float(csv_temp))

                    except:
                        return "File Error"
        
        except:
            return "File Error"

        # handles the case that no data was added to the temp_data (the inputted date has no data/valid data)
        if len(temp_data) == 0:
            # sys.stdout.write('0'+'\n')
            # sys.stdout.write('0')
            # return [0, 0]
            return "Date has no valid data"

        # finds the average and std dev using the built-in statistics library
        average_temp = statistics.mean(temp_data)
        std_dev_temp = statistics.stdev(temp_data)

        # Information is written to the stdout (terminal), could have also used 
        # print()
        sys.stdout.write(str(average_temp)+'\n')
        sys.stdout.write(str(std_dev_temp))

        # returns an array with average temperature and standard deviation of the 
        # temperature
        return [average_temp, std_dev_temp]


    def windchills(self, csv_file, date):
        formatted_date = self.date_format_helper(date)

        if formatted_date == "Error":
            return "Date Error"

        windchill_data = []
        try:

            with open(csv_file, newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    csv_date = row["DATE"].split()[0]

                    # checks if temperature data exists
                    if (row["HOURLYDRYBULBTEMPF"] != ('M' and '')):

                        # removes suspect value indicator ('s')
                        # we use dry bulb temp because that is air temp (which is used
                        # in wind chill formula)
                        csv_temp = float(
                            re.sub("[^0-9]", '', row["HOURLYDRYBULBTEMPF"]))
                    else:
                        csv_temp = '*'  # sets csv_temp value to * if data doesn't exist

                    # data added to list if same date, temperature data exists,
                    # temperature is less than 40, and wind speed data exists
                    if csv_date == formatted_date and csv_temp != '*' and \
                        csv_temp <= 40 and row["HOURLYWindSpeed"] != ('M' and ''):

                        csv_wind_velocity = float(
                            re.sub("[^0-9]", '', row["HOURLYWindSpeed"]))

                        # formula taken from LCD_documentation.pdf
                        calculated_windchill = 35.74 + 0.6215 * \
                            (csv_temp) - 35.75*(csv_wind_velocity**0.16) + \
                            0.4275*(csv_temp)*(csv_wind_velocity**0.16)

                        # rounds the calculated_windchill to the closest integer
                        calculated_windchill = round(calculated_windchill)

                        # Info written to stdout (terminal) and added to data array
                        sys.stdout.write(str(calculated_windchill)+'\n')
                        windchill_data.append(float(calculated_windchill))
        
        except:
            return "File Error"
        
        if len(windchill_data) == 0:
            return "Date has no valid data"

        # I opted to return a list rather than using yield and returning a generator
        # object because there is a pretty limited number of data points per day +
        # we might want to iterate through the values multiple times without
        # re-running the function (generators don't allow this)
        return windchill_data


    """this is a helper function for similar_day which considers four cases based on 
    whether a given key pointing to a list as a value exists in both dictionaries:
    if it exists in neither, 0 is returned; if it exists in one, the absolute 
    value of the sum of that list is returned; if it exists in both, the absolute 
    value of the sum of the sums of the lists is returned"""

    def avg_diff_helper(self, file_1_dict, file_2_dict, date, key):
        if key not in file_1_dict[date] and key not in file_2_dict[date]:
            return 0
        if key in file_1_dict[date] and key in file_2_dict[date]:
            return abs(statistics.mean(file_1_dict[date][key]) - statistics.mean(file_2_dict[date][key]))
        if key in file_1_dict[date] and key not in file_2_dict[date]:
            return abs(statistics.mean(file_1_dict[date][key]))
        if key not in file_1_dict[date] and key in file_2_dict[date]:
            return abs(statistics.mean(file_2_dict[date][key]))


    """this is a helper function for file_dict_helper which handles generating the 
    lists that make up the values of the keys of the dicts contained within the
    greater dict"""

    def file_dict_list_generator(self, file_dict, row, csv_date, row_key,  list_name):
        # checks if data is missing or blank, does nothing if it is
        if row[row_key] != ('M' and ''):
            # makes sure the value is only numbers before converting to float
            csv_value = float(re.sub("[^0-9]", '', row[row_key]))

            # if the 'list_name' is not in the dict as a key, adds it with
            # the list as the val. If it is already in the list, appends the
            # relevant value to the list
            if list_name not in file_dict[csv_date]:
                file_dict[csv_date][list_name] = [csv_value]
            else:
                file_dict[csv_date][list_name].append(csv_value)


    """This is a helper function for similar_day which takes in a csv_file and moves
    the dates plus relevant data for similar_day into a dict of dicts of lists"""


    def file_dict_helper(self, csv_file):
        # initializes our dict of dict of lists
        file_dict = {}
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                csv_date = row["DATE"].split()[0]

                # If the date is not in the dictionary, adds it
                if csv_date not in file_dict:
                    file_dict[csv_date] = {}

                # creates a list of dry bulb temp measurements for a date (in F)
                self.file_dict_list_generator(
                    file_dict, row, csv_date, "HOURLYDRYBULBTEMPF"
                    ,"DRY BULB TEMPS")

                # creates a list of wet bulb temp measurements for a date (in F)
                self.file_dict_list_generator(
                    file_dict, row, csv_date, "HOURLYWETBULBTEMPF"
                    ,"WET BULB TEMPS")

                # creates a list of humidity measurements for a date
                self.file_dict_list_generator(
                    file_dict, row, csv_date, "HOURLYRelativeHumidity"
                    ,"RELATIVE HUMIDITIES")

                # creates a list of pressure measurements for a date
                self.file_dict_list_generator(
                    file_dict, row, csv_date, "HOURLYStationPressure"
                    ,"STATION PRESSURES")

                # creates a list of altimeter setting measurements for a date
                self.file_dict_list_generator(
                    file_dict, row, csv_date, "HOURLYAltimeterSetting"
                    ,"ALTIMETER SETTINGS")

                # creates lists of the u and v components of the wind vectors 
                # (requires wind speed not to be 0)
                if re.search('/d', row["HOURLYWindSpeed"]) and re.search(
                    '/d', row["HOURLYWindDirection"]):

                    csv_wind_speed = float(
                        re.sub("[^0-9]", '', row["HOURLYWindSpeed"]))
                    csv_wind_direction = math.radians(
                        float(re.sub("[^0-9]", '', row["HOURLYWindDirection"])))

                    # formulas for u and v components of the wind vectors, we
                    # multiply by "-1" because wind direction is measured based on
                    # the direct that the wind is coming in from, but, for vectors,
                    # we are interested in the direction that wind is going
                    csv_wind_vector_u_component = -1 * \
                        (csv_wind_speed) * math.sin(csv_wind_direction)
                    csv_wind_vector_v_component = -1 * \
                        (csv_wind_speed) * math.cos(csv_wind_direction)

                    # list generation in the dict, very similar to
                    # file_dict_list_generator
                    if "WIND VECTOR U COMPONENTS" not in file_dict[csv_date]:
                        file_dict[csv_date]["WIND VECTOR U COMPONENTS"] = [
                            csv_wind_vector_u_component]
                    else:
                        file_dict[csv_date]["WIND VECTOR U COMPONENTS"].append(
                            csv_wind_vector_u_component)

                    if "WIND VECTOR V COMPONENTS" not in file_dict[csv_date]:
                        file_dict[csv_date]["WIND VECTOR V COMPONENTS"] = [
                            csv_wind_vector_v_component]
                    else:
                        file_dict[csv_date]["WIND VECTOR V COMPONENTS"].append(
                            csv_wind_vector_v_component)

        return file_dict


    def similar_day(self, csv_file_1, csv_file_2):

        try:
            # initializes both of our full file dicts using a helper
            file_1_dict = self.file_dict_helper(csv_file_1)
            file_2_dict = self.file_dict_helper(csv_file_2)

            # initializes the most_similar_date as an empty string and the
            # lowest_similarity_score as the maximum size
            most_similar_date = ""
            lowest_similarity_score = sys.maxsize

            # for loop that goes through every date and checks if it has a lower
            # similarity score than the current lowest and then updates the date
            # accordingly
            for date in file_1_dict:
                if date in file_2_dict:  # checks if the date exists in both dicts

                    # setting difference of averages values using a helper
                    avg_dry_bulb_temp_diff = self.avg_diff_helper(
                        file_1_dict, file_2_dict, date, "DRY BULB TEMPS")
                    avg_wet_bulb_temp_diff = self.avg_diff_helper(
                        file_1_dict, file_2_dict, date, "WET BULB TEMPS")
                    avg_humidity_diff = self.avg_diff_helper(
                        file_1_dict, file_2_dict, date, "RELATIVE HUMIDITIES")
                    avg_pressure_diff = self.avg_diff_helper(
                        file_1_dict, file_2_dict, date, "STATION PRESSURES")
                    avg_altimeter_diff = self.avg_diff_helper(
                        file_1_dict, file_2_dict, date, "ALTIMETER SETTINGS")
                    avg_wind_vector_u_component_diff = self.avg_diff_helper(
                        file_1_dict, file_2_dict, date, "WIND VECTOR U COMPONENTS")
                    avg_wind_vector_v_component_diff = self.avg_diff_helper(
                        file_1_dict, file_2_dict, date, "WIND VECTOR V COMPONENTS")

                    # the formula for similarity scores (explained in 
                    # README_solution.txt)
                    weighted_summation = 0.25 * avg_dry_bulb_temp_diff + 0.25 * \
                        avg_wet_bulb_temp_diff + 0.125 * avg_humidity_diff + 0.075 * \
                        avg_pressure_diff + 0.05 * avg_altimeter_diff + 0.125 * \
                        avg_wind_vector_u_component_diff + 0.125 * \
                            avg_wind_vector_v_component_diff

                    # if the value is lower than the current lowest score, updates 
                    # values
                    if weighted_summation < lowest_similarity_score:
                        most_similar_date = date
                        lowest_similarity_score = weighted_summation

            # changing the date into the correct format
            similar_date_arr = most_similar_date.split('/')
            for x in range(len(similar_date_arr)):
                if x == len(similar_date_arr) - 1:  # index where the year value is

                    # we have to assume that we are in the 2000s, as that is when the
                    # csv files take place and the csv files only give us the last 2
                    # digits of the year
                    similar_date_arr[x] = "20" + similar_date_arr[x]

                # if the month or day are only of a length of a 1, adds a 0 to the front
                # ,so they fit format expectations
                elif len(similar_date_arr[x]) == 1:
                    similar_date_arr[x] = "0" + similar_date_arr[x]

            # sets most_similar_date to the correctly formatted form of the date
            most_similar_date = similar_date_arr[2] + '-' + \
                similar_date_arr[0] + '-' + similar_date_arr[1]
        
        except:
            return "Similar Day Files Error"

        # write the value to stdout and also returns it
        sys.stdout.write(most_similar_date)
        return most_similar_date


# # handles the argument inputs based on the assignment instructions
# if sys.argv[1] == "daylight_temp":
#     daylight_temp(sys.argv[2], sys.argv[3])
# elif sys.argv[1] == "windchills":
#     windchill_list = windchills(sys.argv[2], sys.argv[3])
# elif sys.argv[1] == "similar_day":
#     similar_day(sys.argv[2], sys.argv[3])
