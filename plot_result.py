#################################################
## GONNA TRY TO PARSE THE RESULT
#################################################
import matplotlib.pyplot as plt 
import csv 
import numpy as np 
import argparse 
import progressbar

NUM_PERIOD = 100
NUM_SEEDS = 10
NUM_CONSUMERS_SAMPLED = [2, 6, 10, 16, 24, 50, 100, 200]
T_TO_PLOT = [10, 25, 50, 100, 200, 500, ]
SUBPLOT_ROW = 3
SUBPLOT_COL = 2

#t, N, seed, marketshare?? --> we can do an average based on seed, then extract t, N 

def read_result_csv(filename):
    total_lines = NUM_PERIOD * NUM_SEEDS * len(NUM_CONSUMERS_SAMPLED)
    print("Reading {}".format(filename))

    widgets = [
        ' [', progressbar.Timer(), '] ', progressbar.Bar(), 
        ' (', progressbar.ETA(), ')'
    ]    

    #bar = progressbar.ProgressBar(widgets=widgets, max_value=total_lines)

    result_arr = np.zeros((len(NUM_CONSUMERS_SAMPLED), NUM_SEEDS, NUM_PERIOD))
    with progressbar.ProgressBar(widgets=widgets, max_value=total_lines) as bar:
        with open(filename) as csv_file: 
            csv_reader = csv.reader(csv_file, delimiter=',')
            row_count = 0
            for row in csv_reader: 
                
                period = int(row[1])
                num_consumers = int(row[2])
                seed = int(row[0])
                marketshare = float(row[3])

                result_arr[NUM_CONSUMERS_SAMPLED.index(num_consumers), seed, period] = marketshare
                row_count += 1

                bar.update(row_count)
                # if (row_count % 1000 == 0):
                #     print("Row {}".format(row_count))
    return result_arr

def compute_averages(result_arr): 
    #For each N, compute average for each t
    return np.mean(result_arr, 1)

def plot_averages(average_ers, average_srs, output_file): 
    # (Num N) x (T)
    plt.figure(figsize=(15, 10))

    for idx, t in enumerate(T_TO_PLOT): 
        all_marketshares_ers = average_ers[:, t-1]
        all_marketshares_srs = average_srs[:, t-1]
        #Subplot 
        plt.subplot(SUBPLOT_ROW, SUBPLOT_COL, (idx+1))
        plt.plot(NUM_CONSUMERS_SAMPLED, all_marketshares_ers)
        plt.plot(NUM_CONSUMERS_SAMPLED, all_marketshares_srs)
        plt.title("t={}".format(t), fontsize=12)
        plt.xlabel('# reviewers', fontsize=12)
        plt.ylabel('H marketshare', fontsize=12)
    plt.legend(['ERS', 'SRS'])
    plt.tight_layout()
    plt.savefig(output_file)



if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description="Plot result obtained from experiment")
    parser.add_argument('--num_seed', type=int, help="How many seeds?")
    parser.add_argument('--num_period', type=int, help="How many period?")
    parser.add_argument('--ERS', type=str, help="File containing the result from ERS")
    parser.add_argument('--SRS', type=str, help="File containing the result from SRS")
    parser.add_argument('--output', type=str, help="Output file path")

    args = parser.parse_args()
    NUM_SEEDS = args.num_seed
    NUM_PERIOD = args.num_period

    result_ers = read_result_csv(args.ERS)
    averages_ers = compute_averages(result_ers)
    result_srs = read_result_csv(args.SRS)
    averages_srs = compute_averages(result_srs)
    #print("Shape of result: {}".format(result.shape))
    #print("Shape of averages: {}".format(compute_averages(result).shape))
    plot_averages(averages_ers, averages_srs, args.output)
    

