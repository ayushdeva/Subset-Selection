import environment
import math
import learner2
import pickle
import numpy as np
from utils import *
import sys
import time
import random

""" 
Points to Note:

1. Keep the ordering of manufacturers constant at places that are permanent, for example in Environment.producers 

"""

import pdb; pdb.set_trace = lambda: None

def get_inputs(filename,R=100):
    f = open(filename,'r')
    n = int(f.readline())
    alpha = float(f.readline())
    Q,C = [],[]
    for i in range(n):
        r,s = f.readline().split(",")
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
    nrounds = int(sys.argv[1])
    nsim = int(sys.argv[2])
    error_margin_quality = float(sys.argv[3])
    # filename = sys.argv[4]
    # n,alpha,R,Q,C = get_inputs(filename)
    optimistic_margin = error_margin_quality

    # burnout = int(float(3*math.log(nsim))/float(2*(error_margin_quality**2)))
    burnout = int(1.0/float(error_margin_quality**2))
    print("Burnout : ",burnout)
    
    # for i in range(n):
    #     if(abs(R*Q[i]-C[i]) < 1):
    #         print(i,Q[i],C[i])
    # # exit(0)
    n_input = int(sys.argv[4])
    # algo_name = sys.argv[5]
    suffix = sys.argv[5]
    # exit(0)

    start_time = time.process_time()
    algos = ['dpss','gss']
    total_regret,regrets,correctness = {},{},{}
    for algo in algos : 
        total_regret[algo] = np.array([[0 for k in range(nsim)],[0 for k in range(nsim)]])
        regrets[algo] = np.array([0 for k in range(nsim)])
        correctness[algo] = np.array([0 for k in range(nsim)])
    # average_quals = np.array([0 for k in range(nsim)],dtype=np.float)
    observed_indeces = [1,2,3,4]

    for j in range(nrounds):
        n,alpha,R,Q,C = generate_inputs(n=n_input)
        env = environment.Environment(n,Q,C,R,alpha)
        learners = {}
        cum_regret = {}
        once_correct = {}
        for algo in algos:
            learners[algo] = learner2.LearnerAgent(env,burnout,optimistic_margin,algo)
            cum_regret[algo] = 1
            once_correct[algo] = 0

        opt_allocation,excess_qual = env.get_optimal(0.0,'dpss')
        import pdb; pdb.set_trace()
        opt_allocation_margin,excess_qual_margin = env.get_optimal(error_margin_quality,'dpss')
        import pdb; pdb.set_trace()
        print(opt_allocation,opt_allocation_margin,sep="\n")
        opt_reward = env.get_expected_reward(opt_allocation)
        opt_reward_margin = env.get_expected_reward(opt_allocation_margin)
        max_revenue = env.get_max_revenue()
        print(opt_reward,opt_reward_margin,max_revenue)
        import pdb; pdb.set_trace() 

        for i in range(nsim):
            print("Iteration no %d Round no %d" %(i,j))
            print(f'Time elapsed : {time.process_time()-start_time}, Completion : {((j*nsim+i)*100)/(nsim*nrounds)}')
            # allocation = learner.run()
            for algo in algos:
                learner = learners[algo]
                allocation_test = learner.run(i+burnout)
                allocation = learner.run(i)
                # print(allocation)
                # print("Allocation\n",allocation)
                # print(opt_allocation)
                qualities = env.get_qualities(allocation) # TODO: to be updated
                # print("Rewards:\n",qualities)
                # if(qualities[5][1] == 0):
                #     observed_quals.append(0)
                # else:
                #     print("Observed Quality : ",float(qualities[observed_index][2])/float(qualities[observed_index][1]))
                #     print("Actual Quality :",env.producers[observed_index].q)
                
                correct_test,abs_correct_test,avg_qual_test = env.check_const(allocation_test, error_margin_quality)
                correct,abs_correct,avg_qual = env.check_const(allocation, error_margin_quality)
                once_correct[algo] = max(once_correct[algo],abs_correct)
                correctness[algo][i] += correct_test
                print("Correctness: ",correct_test," Once correct: ",once_correct[algo])

                if(i > burnout):
                    regret = 0 
                    if not correct:
                        print("Not Even marginally correct")
                        regret = max_revenue
                    elif not abs_correct:
                        print("Marginally correct")
                        regret = env.get_regret(allocation,opt_reward_margin)
                    else:
                        print("Totally correct")
                        regret = env.get_regret(allocation,opt_reward)
                        # regret = env.get_regret(allocation,opt_reward)
                    # regret = max(0,regret)
                    cum_regret[algo] += float(regret)
                    regrets[algo][i] += regret
                    total_regret[algo][0][i] = math.log(cum_regret[algo])
                    total_regret[algo][1][i] += float(cum_regret[algo])
                # print("Regret: ",regret)
                # print(allocation)
                
                learner.update(qualities,env.T,i+2)
            # if(i % burnout == 0):
            #     print(Q)
            #     env.print_estimates()
            #     learner.print_estimates()
            #     temp2 = input()
            #record outputs
        # learner.completeReset()
    import pdb; pdb.set_trace()
    for algo in algos:
        saveVar(regrets[algo],'./Variables/regret_'+suffix+'_'+algo)
        saveVar(total_regret[algo][0],'./Variables/totregret_'+suffix+'_'+algo)
        # saveVar(total_regret[1],'./Variables/lnregret_'+suffix)
        saveVar(correctness[algo],'./Variables/correct_'+suffix+'_'+algo)
        # saveVar(average_quals,'./Variables/avg_quals_'+suffix)
        # for observed_index in observed_indeces:
            # saveVar(learner.prods[observed_index].q_est_history,'./Variables/q_history_'+str(observed_index)+"_"+suffix+'_'+algo)

        myPlot(regrets[algo]/float(nrounds),'Regret Analysis - Regret in revenue','./Plots/Regret_'+suffix+'_'+algo)
        # myPlot(total_regret[0]/float(nrounds),'Total Regret Till that moment','./Plots/TotalRegretlogT1_'+suffix)
        # myPlotxy(total_regret[0],total_regret[1]/nrounds,'Cumulative Regret vs logT','./Plots/TotalRegretlogT1_'+suffix)
        # myPlotlog(total_regret[1]/nrounds,'Cumulative Regret vs logT','./Plots/TotalRegretlogT2_'+suffix)
        myPlot(total_regret[algo][1]/nrounds,'Total Regret Till that moment','./Plots/TotalRegret_'+suffix+'_'+algo)
        myPlot(correctness[algo]/nrounds,'Correctness','./Plots/Correctness'+suffix+'_'+algo)
        # myPlot(average_quals/float(nrounds),'Average Qualities','./Plots/AverageQuals'+suffix)
        # for observed_index in observed_indeces:
        #     myPlot2(nsim,learner.prods[observed_index].q_history,env.producers[observed_index].q,'Variation of quality','./Plots/q_track_'+str(observed_index))
        #     myPlot2(nsim,learner.prods[observed_index].q_est_history,env.producers[observed_index].q,'Variation of Mean quality','./Plots/q_mean_track_'+str(observed_index))
  
if __name__== "__main__":
    main()