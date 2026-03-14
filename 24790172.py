# CITS1401 Final Project
# Author: Victoria Mok
# Student ID: 24790172

def main(csvfile):
    OP1 = output_1(csvfile)
    OP2 = output_2(csvfile)
    
    return OP1, OP2
    
    
# function to read csv file
def read_file(csvfile, target_headers):
    
    try:
        with open(csvfile, 'r') as infile:
            
            # find names of headers
            header_line = infile.readline().strip().split(',')
            headers = []
            
            # make headers lowercase
            for names in header_line:
                headers.append(names.lower().strip())
            
            # make a dictionary to find the indexes of each relevant heading
            headers_indexes = {}
            data = {}
            

            for name in target_headers:
                if name in headers:
                    headers_indexes[name] = headers.index(name)
                else:
                    return {} # when column does not exist, exit
                data[name] = []
            
            
            organisation_ids = []
            
            for line in infile:
                
                # handle when the row has no data (only white space)
                if not line.strip():
                    continue
                
                row = line.strip().split(',')
                    
                
                try:
                    skip_row = False
                    for name in target_headers:
                        if headers_indexes[name] >= len(row) or not row[headers_indexes[name]].strip():
                            # when there is missing data, skip the row
                            skip_row = True
                            break
                    if skip_row:
                        continue
                    
                    # check for duplicate organisation id
                    # if organisation id doesn't exist, skip row
                    if 'organisation id' in headers:
                        organisations_id = row[headers.index('organisation id')]
                        if organisations_id in organisation_ids:
                            continue
                        organisation_ids.append(organisations_id)
                    
                    # add data for each of the required columns
                    for name in target_headers:
                        value = row[headers_indexes[name]]
                        data[name].append(value)
                        
                except (ValueError, IndexError) as e:
                    print(f'Skipping row with {e}')
                    continue
                
            return data
                
    # handle error when file does not exist
    except FileNotFoundError:
        print(f'Could not find file {csvfile}')
        return {}
    
    
# function that takes the extracted data and groups by country to use in output 1
def group_by_country(data):
    
    grouped = {}
    
    number_rows = len(data['country'])
    
    for i in range(number_rows):
        try:
            # make sure to get rid of unwanted white space in the country name
            country = data['country'][i].strip()
            
            # initialise dictionary if country does not already exist
            if country not in grouped:
                grouped[country] = {
                    'profits in 2020(million)': [],
                    'profits in 2021(million)': [],
                    'number of employees': [],
                    'median salary': []
                }
            
            # append respective data into lists in the dictionary
            grouped[country]['profits in 2020(million)'].append(int(data['profits in 2020(million)'][i]))
            grouped[country]['profits in 2021(million)'].append(int(data['profits in 2021(million)'][i]))
            grouped[country]['number of employees'].append(int(data['number of employees'][i]))
            grouped[country]['median salary'].append(int(data['median salary'][i]))
        except ValueError:
            continue
        
    return grouped


# function for output 1
def output_1(csvfile):
    
    output = {}
    
    # information to be extracted from the file
    target_headers = [
        'profits in 2020(million)',
        'profits in 2021(million)',
        'number of employees',
        'median salary',
        'country'
        ]
    
    data = read_file(csvfile, target_headers)
    
    # handle when error was found whilst reading the file
    if not data:
        return {}
    
    dictionary = group_by_country(data)
    
    try:
        # find t_test score and minkowski distance for each country
        for country in dictionary:
            t_score = t_test_score(dictionary[country]['profits in 2020(million)'], dictionary[country]['profits in 2021(million)'])
            m_distance = minkowski_distance(dictionary[country]['number of employees'], dictionary[country]['median salary'])
            output[country] = [t_score, m_distance]
                           
        return output
    
    except (ValueError, ZeroDivisionError) as e:
        print(f'{e} occurred during calculation, exiting gracefully')
        return {}
    
    
# function to find output 2     
def output_2(csvfile):
    
    # information to be extracted from the file
    target_headers = [
        'category',
        'organisation id',
        'profits in 2020(million)',
        'profits in 2021(million)',
        'number of employees'
        ]
    
    data = read_file(csvfile, target_headers)
    
    # handle if there is error in reading the file from previous function
    if not data:
        return {}
    
    dictionary = {}
            
    num_organisations = len(data['organisation id'])
    
    # populate dictionary with data ie. nested dictionary with organisation id and required information
    for i in range(num_organisations):
        try:
            # remove any white spaces from category name
            category = data['category'][i].strip()
            organisation_id = data['organisation id'][i]
            profit_change = percentage_change(int(data['profits in 2020(million)'][i]), int(data['profits in 2021(million)'][i]))
            
            information = [int(data['number of employees'][i]), profit_change]
        
            # initialise category if it doesn't exist
            if category not in dictionary:
                dictionary[category] = {}
                
            dictionary[category][organisation_id] = information
            
        except (ValueError, ZeroDivisionError):
            return {}
    
    # find the rank for each of the organisations grouped by category
    # ranked by the first term, then second term ie. number of employees, then profit change if tied
    # all sorted in descending order
    for category, organisations in dictionary.items():
        sorted_organisations = sorted(organisations.items(), key=lambda x:(-x[1][0], -x[1][1]))
        
        for i in range(len(sorted_organisations)):
            organisation_id, information = sorted_organisations[i]
            dictionary[category][organisation_id].append(i + 1)
    
    return dictionary


# function to find mean
def mean(data):
    if data == []:
        raise ZeroDivisionError('Mean requires at least one point of data')
    return sum(data) / len(data)


# function to find standard deviation
def standard_deviation(observed_values):
    number_of_values = len(observed_values)
    
    # raise an error if the number of values is below 2
    if number_of_values < 2:
        raise ValueError('Standard deviation requires at least two points of data')
    
    if any(v < 0 for v in observed_values):
        raise ValueError('Negative values are not valid')
        
    mean_value = mean(observed_values)
    total = 0
    
    for i in range (number_of_values):
        value_squared = (observed_values[i] - mean_value) ** 2
        total += value_squared
        
    std_dev = (total / (number_of_values - 1)) ** 0.5 
    
    return std_dev


# function to find t-test score
def t_test_score(profit_2020, profit_2021):
    mean_2020 = mean(profit_2020)
    mean_2021 = mean(profit_2021)
    sd_2020 = standard_deviation(profit_2020)
    sd_2021 = standard_deviation(profit_2021)
    sample_size_2020 = len(profit_2020)
    sample_size_2021 = len(profit_2021)
    
    score = (mean_2020 - mean_2021) / ((sd_2020 ** 2 / sample_size_2020) + (sd_2021 ** 2 / sample_size_2021)) ** 0.5
    
    return round(score, 4)


# function to find the minkowski distance
def minkowski_distance(number_employees, median_salary):
    total = 0
    sample_number = len(median_salary)
    
    if len(number_employees) != sample_number:
        raise ValueError('Number of employees does not match number of median salaries')
    
    if any(v < 0 for v in number_employees) or any(v < 0 for v in median_salary):
        raise ValueError('Negative number is not valid')
    
    for i in range(sample_number):
        total += (abs(number_employees[i] - median_salary[i])) ** 3
    
    distance = total ** (1 / 3)
    
    return round(distance, 4)
    
    
# function to find the percentage change
def percentage_change(profit_2020, profit_2021):
    if profit_2020 == 0:
        raise ValueError('Division by zero in percentage change')
    
    absolute_change = ((abs(profit_2020 - profit_2021)) / profit_2020) * 100
    
    return round(absolute_change, 4)