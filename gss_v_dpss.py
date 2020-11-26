import environment
import math
import pickle
import numpy as np
from utils import *
import sys
import random
import time
from collections import defaultdict
import pandas as pd

""" 
Points to Note:

1. Keep the ordering of manufacturers constant at places that are permanent, for example in Environment.producers 

"""

import pdb; pdb.set_trace = lambda: None

def get_inputs(filename,R=100):
    f = open(filename,'r')
    n = int(f.readline())
    alpha = float(f.readline())
    #alpha = float(input("Enter threshold quality"))
    Q,C = [],[]
    for i in range(n):
        r,s = f.readline().split(",")
        # r,s = input().split(",")
        Q.append(float(r))
        C.append(float(s))
    return n,alpha,R,Q,C

def generate_inputs(n=10,alpha='random',R=100):
    n_decimals = 4
    if(alpha == 'random'):
        alpha = round(random.random(),n_decimals)
    Q,C = [],[]
    
    temp1 = int(n/3)
    for i in range(temp1):
        q = round(random.uniform(alpha,1.0),n_decimals)
        Q.append(q)
        c = round(random.uniform(alpha*R,R),n_decimals)
        C.append(c)

    for i in range(temp1,n):
        q = round(random.random(),n_decimals)
        Q.append(q)
        c = round(random.uniform(0,R),n_decimals)
        C.append(c)
    
    return n,alpha,R,Q,C

def main():
    try:
        filename = sys.argv[1]
    except Exception as e:
        pass
    # n,alpha,R,Q,C = get_inputs(filename)
    # n_agents = int(sys.argv[1])
    # n_agents = [5,8,10,12,15,17,20]
    suffix = sys.argv[1]
    n_agents = [2,3,5,8,10,12,14,16,18,20,25,40,50,60,80,100,200,400,600,800,1000,5000,10000,100000]
    n_iters = 100
    algos = ['gss','dpss','dpss_mem','ilp']
    # algos = ['gss','dpss_mem']
    # algos = ['gss','dpss']
    alphas = [0.25,0.5,0.7,0.8,0.95]

    rows = []
    exp_start = time.process_time()
    total_combinations,count = len(n_agents)*len(algos)*len(alphas)*n_iters,0
    for n in n_agents:
        for alpha in alphas :
            for j in range(n_iters):
                print(f"n: {n}, alpha: {alpha}, iteration no.: {j}")
                print(f"time passed: {time.process_time() - exp_start}, completion: {int((count*100)/total_combinations)}%")
                n,alpha,R,Q,C = generate_inputs(n=n,alpha=alpha,R=100)
                # for i in range(n):
                #     if(abs(R*Q[i]-C[i]) < 1):
                #         print(i,Q[i],C[i])
                env = environment.Environment(n,Q,C,R,alpha)
                
                for algo in algos:
                    count+=1
                    start = time.process_time()
                    opt_allocation,excess_qual = env.get_optimal(0.0,algo)
                    util = env.get_expected_reward(opt_allocation)
                    import pdb; pdb.set_trace()
                    row = {}
                    row['n'],row['alpha'],row['algo'] = n,alpha,algo
                    row['iter'],row['util'] = j,util
                    row['time'] = time.process_time() - start
                    rows.append(row)
        
        if n>=20:
            algos = ['gss','dpss_mem','ilp']
        
        if n>=100:
            algos = ['gss','ilp']
    
    # print(opt_allocations)
    import pdb; pdb.set_trace()
    df = pd.DataFrame(rows)
    output_folder = 'Comparison/'
    df.to_csv(output_folder+"output_"+suffix+".csv")

  
if __name__== "__main__":
    main()