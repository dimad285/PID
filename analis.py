import os
import statistics
import matplotlib.pyplot as plt
import math
import csv

def read_data_from_files(directory):
    data_paths = {}
    for root, dirs, files in os.walk(directory):
        distance = os.path.basename(root)  # Use folder name as distance
        for file in files:
            if file.endswith('.txt'):  # Assuming your data files are .txt
                if distance not in data_paths:
                    data_paths[distance] = []
                data_paths[distance].append(os.path.join(root, file))
    return data_paths

def process_file(file_path, range_value):
    time, voltage = [], []
    with open(file_path, 'r') as file:
        #file.readline()  # Skip the header or first line
        for line in file:
            if line.strip() == '':
                break
            values = [float(i) for i in line.split('\t')[:3]]
            time.append(values[0])
            voltage.append(values[1])
    if len(voltage) > range_value:
        mean_voltage = statistics.mean(voltage[-range_value:])
        standard_deviation = math.sqrt(sum((x - mean_voltage) ** 2 for x in voltage[-range_value:]) / (range_value - 1))
    else:
        mean_voltage = voltage[0]  # Or some other default value
        standard_deviation = 0  # Or some other default value
    return mean_voltage, standard_deviation

def sort_data(data):
    return sorted(data, key=lambda x: x[0])

def write_to_csv(file_path, data):
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Distance', 'Pressure', 'Mean Voltage'])
        for distance, items in data.items():
            for item in items:
                csvwriter.writerow([distance, item[0], item[1]])

def plot_data(datasets):
    plt.figure()
    for distance, data in datasets.items():
        pressures, mean_voltages = zip(*sorted(data, key=lambda x: x[0]))
        plt.plot(pressures, mean_voltages, label=f'Distance {distance}')
    plt.yscale('log')
    plt.xscale('log')
    plt.grid(True, 'both', 'both')
    plt.legend()
    plt.title('Voltage vs Pressure at Different Distances')
    plt.xlabel('Pressure')
    plt.ylabel('Mean Voltage')
    plt.show()

def main():
    directory = 'Log'
    range_value = 5
    data_paths = read_data_from_files(directory)
    processed_data = {}

    for distance, file_paths in data_paths.items():
        processed_data[distance] = []
        for file_path in file_paths:
            mean_voltage, standard_deviation = process_file(file_path, range_value)
            pressure = float(os.path.basename(file_path).rstrip('.txt'))
            processed_data[distance].append((pressure, mean_voltage))

    write_to_csv('results.csv', processed_data)
    plot_data(processed_data)

if __name__ == '__main__':
    main()
