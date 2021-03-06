import csv
import numpy as np 
import matplotlib.pyplot as plt
import random
import math
import time
import progressbar
import argparse

DBUG = False
NUM_PERIOD = 100 #How many time period to run?  (default: 500)
NUM_SEEDS = 10 #How many different seeds to run? (default: 100)
POPULATION_SIZE = 500 # How many people are in the population (default: 500)

AVERAGE_H_PAYOFF = 100 #
AVERAGE_L_PAYOFF = 75 #
STANDARD_DEVIATION = 20 #Standard deviation for the idiosyncratic shock
NUM_CONSUMERS_SAMPLED = [2, 6, 10, 16, 24, 50, 100, 200] #In the paper, this is N 
ALPHA = 0.1 #Percent of the population to become "Potential switcher"
GAMMA = 0.5

USE_ERS = False
ENDOGENOUS_SWITCHING = False
USE_STAR_RATINGS = False

OUTPUT_FILE = "out.csv"

STAR_THRESHOLD = [0, 0.7, 0.9, 1, 1.1]

#######################################################
# STAR RATING SYSTEM 
# [0, 0.7, 0.9, 1, 1.1]
# Threshold for ratio (actual_payoff)/(expected_payoff)
#######################################################
class Consumer:
    """
    Params: id: the consumer id, unique to this consumer
            product_type: what is initial product type for this consumer?
    """
    def __init__(self, id, product_type, expected_payoff=90):
        self.id = id
        self.product_type = product_type
        self.current_payoff = 0.0 #Payoff at time t 
        self.prev_payoff = 0.0 #Payoff at time t-1
        self.payoff = [] 
        self.chosen_product = []
        self.expected_payoff = expected_payoff
        self.star_ratings = [] 
    
    """
    Obtain the payoff for this time period given the consumer's current product type
    """
    def update_payoff(self): 
        base_payoff = AVERAGE_L_PAYOFF
        if self.product_type == "HIGH":
            base_payoff = AVERAGE_H_PAYOFF
        idiosyncratic_shock = np.random.normal(loc=0.0, scale=STANDARD_DEVIATION)
        self.payoff.append(idiosyncratic_shock+base_payoff)
        
        #Determine star rating
        ratio = (idiosyncratic_shock+base_payoff) / (self.expected_payoff)
        for i in range(len(STAR_THRESHOLD)): 
            if ratio < STAR_THRESHOLD[i]: 
                self.star_ratings.append(i)
                break 
            if i == len(STAR_THRESHOLD) - 1: 
                #We reach the end. and it's not less than 
                self.star_ratings.append(i)
    
        #Update expected payoff
        self.expected_payoff = GAMMA * (idiosyncratic_shock+base_payoff) + (1-GAMMA) * self.expected_payoff
    
    '''
    Return a list of consumer ids, indicating which consumer to check
    '''
    def get_reviews(self, num_consumer_sampled, sample_type, h_consumer_ids=[], l_consumer_ids=[]): 
        if sample_type == 'SRS': 
            #Sample N+1 random consumers from the market
            #The +1 is used as a back-up in case one of the value
            #is the current consumer
            temp_sampled = np.random.choice(POPULATION_SIZE,
                size=num_consumer_sampled+1, 
                replace=False
            )
            sampled_ids = temp_sampled[0:num_consumer_sampled]
            
            #Check if the consumer is among those to be sampled
            #If yes, replace with a different consumer.
            for i in range(len(sampled_ids)):
                if sampled_ids[i] == self.id: 
                    sampled_ids[i] = temp_sampled[num_consumer_sampled]
            return sampled_ids
        elif sample_type == 'ERS': 
            h_reviewer_ids = []
            l_reviewer_ids = []

            #Make a copy so we don't actually change the input array
            h_consumer_ids_temp = h_consumer_ids
            l_consumer_ids_temp = l_consumer_ids

            #Determine how many from each class we are sampling
            samples_per_class = num_consumer_sampled//2

            #Check if current use is in one of the list, then remove that id from the sampling pool
            if self.id in h_consumer_ids_temp: 
                h_consumer_ids_temp.remove(self.id)
            if self.id in l_consumer_ids_temp: 
                l_consumer_ids_temp.remove(self.id)
            
            #Randomly select N//2 people from the H consumer population
            if(len(h_consumer_ids_temp) > samples_per_class):
                h_reviewer_ids = random.sample(h_consumer_ids_temp, samples_per_class)
            else:
                h_reviewer_ids = h_consumer_ids_temp
            
            #Randomly select N//2 people from the L consumer population
            if(len(l_consumer_ids_temp) > samples_per_class):
                l_reviewer_ids = random.sample(l_consumer_ids_temp, samples_per_class)
            else: 
                l_reviewer_ids = l_consumer_ids_temp
            
            #Join the two lists together
            return h_reviewer_ids + l_reviewer_ids

    '''
    Determine whether this consumer should switch his/her product
    Params: sampled_ids: the ids of the sampled reviewers
            consumer_population: a list/array of all consumers
    '''
    def should_switch(self, sampled_ids, consumer_population):
        # Keep track of total payoff and number of people with each type of product
        low_payoff_total = 0
        high_payoff_total = 0
        num_high = 0 
        num_low = 0
        if not (USE_STAR_RATINGS):
            for sampled_id in sampled_ids: 
                current_consumer = consumer_population[sampled_id]
                if(current_consumer.product_type == "HIGH"):
                    num_high += 1
                    high_payoff_total = high_payoff_total + current_consumer.payoff[-1]
                else: 
                    num_low += 1 
                    low_payoff_total = low_payoff_total + current_consumer.payoff[-1]
            
            #Add his/her own review 
            if self.product_type == "HIGH":
                num_high += 1
                high_payoff_total += self.payoff[-1]
            else: 
                num_low += 1
                low_payoff_total += self.payoff[-1]
        else: 
            for sampled_id in sampled_ids: 
                current_consumer = consumer_population[sampled_id]
                if(current_consumer.product_type == "HIGH"):
                    num_high += 1
                    high_payoff_total = high_payoff_total + current_consumer.star_ratings[-1]
                else: 
                    num_low += 1
                    low_payoff_total = low_payoff_total + current_consumer.star_ratings[-1]
            if self.product_type == "HIGH": 
                num_high += 1 
                high_payoff_total += self.star_ratings[-1]
            else: 
                num_low += 1 
                low_payoff_total += self.star_ratings[-1]
                
        #Check if both high and low are represented
        if (num_high == 0) or (num_low == 0): 
            if (DBUG): 
                print("Only 1 type of product observed from consumer {}".format(self.id))
            return self.product_type

        #Compute average
        high_average = high_payoff_total / num_high
        #Determine: to switch or not to switch
        low_average = low_payoff_total / num_low
        
        if (DBUG): 
            print("High average payoff: {}".format(high_average))
            print("Low average payoff: {}".format(low_average))
        '''
        If the average payoff for the H reviews are higher than the L reviews, 
        pick HIGH for the next period. 
        If the average payoff for the H reviews are lower than the L reviews, 
        pick LOW for the next period. 
        If they are equal (highly unlikely), keep the same product type
        '''
        if (high_average > low_average):
            if(DBUG): 
                print("Consumer {} previous product: {}. New product: {}".format(self.id, self.product_type, "HIGH")) 
            self.product_type = "HIGH"
        elif (high_average < low_average):
            if(DBUG): 
                print("Consumer {} previous product: {}. New product: {}".format(self.id, self.product_type, "LOW")) 
            self.product_type = "LOW"

    '''
    Determine whether this consumer should switch his/her product using 
    endogenous switching rule
    '''
    def is_disatisfied(self):
        if self.payoff[-1] >= self.expected_payoff:
            return False
        else: 
            if random.uniform(0, 1) < (1 - (self.payoff[-1]/self.expected_payoff)):
                return True
            else: 
                return False 
"""
Create an array of P consumers. Randomize the initial product type (50/50). 
"""
def initialize_population(): 
    consumers = [] 
    for i in range(POPULATION_SIZE):
        #Obtain a number between 0 and 1
        if random.uniform(0, 1) > 0.5: 
            new_consumer = Consumer(id=i, product_type="HIGH")
            if (DBUG):
                print("Initialize consumer {} with {} product type".format(i, "HIGH"))
            consumers.append(new_consumer)
        else: 
            new_consumer = Consumer(id=i, product_type="LOW")
            if (DBUG):
                print("Initialize consumer {} with {} product type".format(i, "LOW"))
            consumers.append(new_consumer)
    
    return consumers
        

"""
Select the consumer ids that represent potential switchers
Return: A list of potential switchers
"""
def select_potential_switchers(consumer_population):
    sampled_ids = np.random.choice(
        POPULATION_SIZE, 
        size=math.floor(ALPHA * POPULATION_SIZE),
        replace=False
    )

    if(DBUG): 
        print("Sampled ids: {}".format(sampled_ids))

    potential_switchers = []
    for i in range(len(sampled_ids)):
        potential_switchers.append(consumer_population[sampled_ids[i]])
    return potential_switchers
    


'''
Compute the percentage of the consumers currently choosing H
Params: consumer_population: array/list consisting of all consumers in the market
Return: proportion of the market choosing H (0 < x < 1)
'''
def compute_marketshare(consumer_population): 
    #Count number of "HIGH"
    num_high = 0
    for consumer in consumer_population: 
        if consumer.product_type == "HIGH": 
            num_high += 1
    
    return num_high / len(consumer_population)

"""
Literally .... the main function...
"""
def main(): 
    print("------------- Starting Experiment --------------")
    all_marketshares = [] 
    all_times = [] 
    all_num_reviewers = [] 
    all_seeds = []

    widgets = [
        ' [', progressbar.Timer(),  '] ', progressbar.Bar(), 
        ' (', progressbar.ETA(), ') '
    ]

    for num_reviewer in NUM_CONSUMERS_SAMPLED:
        print("Running experiment with {} reviewers".format(num_reviewer))
        #Run for num_seed tries
        #bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength, widgets=widgets)
        for seed in progressbar.progressbar(range(NUM_SEEDS), widgets=widgets):
            #print("Seed {}".format(seed))
            
            #Seed both of our generators
            np.random.seed(seed)
            random.seed(seed)

            consumer_population = initialize_population()
            h_marketshare = []

            #Run for NUM_PERIOD period
            for t in range(NUM_PERIOD):
                #For each consumer, obtain new payoff
                for consumer in consumer_population: 
                    consumer.update_payoff()

                h_marketshare.append(compute_marketshare(consumer_population))
                all_marketshares.append(compute_marketshare(consumer_population))
                all_times.append(t) 
                all_num_reviewers.append(num_reviewer)
                all_seeds.append(seed)
                #print("Market share at period {} is: {}".format(t, h_marketshare[-1]))

                if (t != 0):
                    #If not the first period, select potential switcher based on whether endogneous switching is ON or OFF
                    if not (ENDOGENOUS_SWITCHING): 
                        potential_switchers = select_potential_switchers(consumer_population)
                    else: 
                        potential_switchers = [consumer for consumer in consumer_population if consumer.is_disatisfied()]

                    #For each potential switcher, determine if they should switch
                    for potential_switcher in potential_switchers:
                        #Get the reviews first
                        if USE_ERS == True: 
                            h_consumers = [x.id for x in consumer_population if x.product_type=="HIGH"]
                            l_consumers = [x.id for x in consumer_population if x.product_type=="LOW"]
                            reviewer_ids = potential_switcher.get_reviews(num_reviewer, "ERS", h_consumers, l_consumers)
                        else: 
                            reviewer_ids = potential_switcher.get_reviews(num_reviewer,"SRS")
                        
                        #Then determine whether to switch
                        potential_switcher.should_switch(reviewer_ids, consumer_population)

    # Save to csv file 
    with open(OUTPUT_FILE, mode='w', newline='') as csvfile: 
        csv_writer = csv.writer(csvfile, delimiter=',')

        for i in range(len(all_marketshares)):
            csv_writer.writerow([all_seeds[i], all_times[i], all_num_reviewers[i], all_marketshares[i]])
            

#######################################################
## 1. Fake reviews: How much impact fake reviews have? What if 5% of reviews are fake??
##      Other paper has more info on this (Hanna-Bhole)
## 2. Add an additional middle product: 
## 3. Subjective with top/bottom reviews
#######################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", type=str, help="Either ERS or SRS")
    parser.add_argument("--num_period", type=int, help="How many time period to run for")
    parser.add_argument("--num_seed", type=int, help="How many seeds to run for")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--debug", type=bool, default=False)
    parser.add_argument("--endogenous", type=bool , default=False, help="Whether endogenous switching is enabled")
    parser.add_argument("--star_rating", type=bool, help="Whether to use star ratings instead of objective payoff")

    args = parser.parse_args()
    print(args)

    if args.type == "ERS": 
        USE_ERS = True
    elif args.type == "SRS": 
        USE_ERS = False 
    else: 
        print("Illegal type. Either ERS or SRS")

    NUM_PERIOD = args.num_period
    NUM_SEEDS = args.num_seed
    OUTPUT_FILE = args.output
    ENDOGENOUS_SWITCHING = args.endogenous
    USE_STAR_RATINGS = args.star_rating

    main()

            

