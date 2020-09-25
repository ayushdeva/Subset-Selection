import environment
import math
import learner2
import pickle
import numpy as np
from utils import *
import sys

""" 
Points to Note:

1. Keep the ordering of manufacturers constant at places that are permanent, for example in Environment.producers 

"""

def get_inputs():
    n = int(input("Enter the number of manufacturers"))
    #alpha = float(input("Enter threshold quality"))
    print("Now, for each manufacturer, enter its quality(0-1), cost and capacity")
    Q,K,C = [],[],[]
    for i in range(n):
        r,s,t = input().split(",")
        Q.append(float(r))
        K.append(float(s))
        C.append(float(t))
    return n,Q,K,C

def main():
    n,Q,K,C = get_inputs()
    nsim = int(sys.argv[1])
    nrounds = int(sys.argv[2])
    error_margin_quality = float(sys.argv[3])
    optimistic_margin = error_margin_quality
    # burnout = int(float(3*math.log(nsim))/float(2*(error_margin_quality**2)))
    burnout = int(1.0/float(error_margin_quality**2))
    print("Burnout : ",burnout)
    R,alpha = 100,0.7
    for i in range(n):
        if(abs(R*Q[i]-C[i]) < 1):
            print(i,Q[i],C[i])
    # exit(0)
    suffix = "_"+str(n)+"_"+str((1/error_margin_quality))+"_"+str(nsim)
    print(n,Q,K,C)
    env = environment.Environment(n,Q,C,K,R,alpha)
    # learner = learner1.LearnerAgent(env)
    
    opt_allocation,excess_qual = env.get_optimal(0.0)
    env.reset()
    opt_allocation_margin,excess_qual_margin = env.get_optimal(error_margin_quality)
    print("excess quality : ",excess_qual)                             
    print(opt_allocation,opt_allocation_margin,sep="\n")
    opt_reward = env.get_expected_reward(opt_allocation)
    opt_reward_margin = env.get_expected_reward(opt_allocation_margin)
    # print(opt_reward)

    # check = 1
    # for i in range(n):
    #     manu1 = env.producers[i]
    #     manu2 = 

    max_revenue = env.get_max_revenue()
    print(opt_reward,opt_reward_margin,max_revenue)
    # exit(0)
    total_regret = np.array([[0 for k in range(nsim)],[0 for k in range(nsim)]])
    regrets = np.array([0 for k in range(nsim)])
    correctness = np.array([0 for k in range(nsim)])
    average_quals = np.array([0 for k in range(nsim)],dtype=np.float)
    observed_indeces = [1,2,3,4]

    for j in range(nrounds):
        learner = learner2.LearnerAgent(env,burnout,optimistic_margin)
        # learner = learner2.LearnerAgent(env,burnout,0.00)
        cum_regret = 1
        once_correct = 0

        for i in range(nsim):
            print("Iteration no %d Round no %d" %(i,j))
            # allocation = learner.run()
            allocation_test = learner.run(i+burnout)
            learner.reset()
            allocation = learner.run(i)
            # print(allocation)
            # print("Allocation\n",allocation)
            # print(opt_allocation)
            qualities = env.get_qualities(allocation)
            # print("Rewards:\n",qualities)
            # if(qualities[5][1] == 0):
            #     observed_quals.append(0)
            # else:
            #     print("Observed Quality : ",float(qualities[observed_index][2])/float(qualities[observed_index][1]))
            #     print("Actual Quality :",env.producers[observed_index].q)
            
            correct_test,abs_correct_test,avg_qual_test = env.check_const(allocation_test, 0.00)
            correct,abs_correct,avg_qual = env.check_const(allocation, 0.00)
            once_correct = max(once_correct,abs_correct)
            correctness[i] += correct_test
            print("Correctness: ",correct_test," Once correct: ",once_correct)
            average_quals[i] += avg_qual

            if(i > burnout):
                regret = 0 
                if not correct:
                    print("Not Even marginally correct")
                    regret = max_revenue
                elif not abs_correct:
                    print("Marginally correct")
                    regret = env.get_regret(allocation,0.00)
                else:
                    print("Totally correct")
                    regret = env.get_regret(allocation,opt_reward)
                # regret = max(0,regret)
                cum_regret += float(regret)
                regrets[i] += regret
                total_regret[0][i] = math.log(cum_regret)
                total_regret[1][i] += float(cum_regret)
            # print("Regret: ",regret)
        	# print(allocation)
        	
            learner.update(qualities,env.T,i+2)
            learner.reset()
            if(i == burnout):
                print(Q)
                learner.print_estimates()
            #record outputs
        # learner.completeReset()

    saveVar(regrets,'./Variables/regret_'+suffix)
    saveVar(total_regret[0],'./Variables/totregret_'+suffix)
    saveVar(total_regret[1],'./Variables/lnregret_'+suffix)
    saveVar(correctness,'./Variables/correct_'+suffix)
    saveVar(average_quals,'./Variables/avg_quals_'+suffix)
    for observed_index in observed_indeces:
        saveVar(learner.prods[observed_index].q_est_history,'./Variables/q_history_'+str(observed_index)+"_"+suffix)

    myPlot(regrets/float(nrounds),'Regret Analysis - Regret in revenue','./Plots/Regret_'+suffix)
    myPlot(total_regret[0]/float(nrounds),'Total Regret Till that moment','./Plots/TotalRegretlogT1_'+suffix)
    # myPlotxy(total_regret[0],total_regret[1]/nrounds,'Cumulative Regret vs logT','./Plots/TotalRegretlogT1_'+suffix)
    myPlotlog(total_regret[1]/nrounds,'Cumulative Regret vs logT','./Plots/TotalRegretlogT2_'+suffix)
    myPlot(total_regret[1]/nrounds,'Total Regret Till that moment','./Plots/TotalRegret_'+suffix)
    myPlot(correctness/nrounds,'Correctness','./Plots/Correctness'+suffix)
    myPlot(average_quals/float(nrounds),'Average Qualities','./Plots/AverageQuals'+suffix)
    for observed_index in observed_indeces:
        myPlot2(nsim,learner.prods[observed_index].q_history,env.producers[observed_index].q,'Variation of quality','./Plots/q_track_'+str(observed_index))
        myPlot2(nsim,learner.prods[observed_index].q_est_history,env.producers[observed_index].q,'Variation of Mean quality','./Plots/q_mean_track_'+str(observed_index))
  
if __name__== "__main__":
    main()