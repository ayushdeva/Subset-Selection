import numpy as np
from utils import *
from scipy.stats import bernoulli

class Manufacturer():
	def __init__(self,q,c,k,index,R):
		self.index = index
		self.q = q
		self.c = c
		self.k = k
		self.k_rem = k
		self.r = R*q - c

class Environment():
	def __init__(self,n,Q,C,K,R,alpha):
		self.n = n
		self.T = 0
		self.alpha = alpha
		self.R = R
		self.producers = []
		for i in range(n):
			self.producers.append(Manufacturer(Q[i],C[i],K[i],i,self.R))

	def generate_qualities(self,prod,quant):
		avg_quality = sum(bernoulli.rvs(size=int(quant),p=prod.q))
		# reward = self.R*int(avg_quality) - quant*prod.c 
		# print(reward)
		return avg_quality

	def get_regret(self,x,opt_reward):
		reward = self.get_expected_reward(x)
		print("Reward : ",reward)
		print("Regret : ",opt_reward-reward)
		return opt_reward-reward

	def get_qualities(self,x):
		#[(index of producer, quantity allocated, realized total qualities)]
		qualities = [[i,0,0] for i in range(self.n)]  
		for i in range(self.n):
			qualities[i][1] = x[i]
			self.T += x[i]
			qualities[i][2] = self.generate_qualities(self.producers[i],x[i])
		return qualities

	def get_expected_reward(self,x):
		reward = 0
		for i in range(self.n):
			prod = self.producers[i]
			reward += x[i]*(prod.r)
		return reward		

	def get_optimal(self,error_margin):
		return get_optimal_allocation(self.producers,self.n,self.alpha-error_margin)

	def reset(self):
		for prod in self.producers:
			prod.k_rem = prod.k

	def get_max_revenue(self):
		max_rev = 0
		for i in range(self.n):
			prod = self.producers[i]
			max_rev += max(0,prod.r)
		return max_rev

	def check_const(self,x,margin):
		total_quality = 0 
		total_quant = 0
		for i in range(self.n):
			prod = self.producers[i]
			total_quality += x[i]*prod.q
			total_quant += x[i]
		avg_qual = float(total_quality)/float(total_quant)
		if(avg_qual >= self.alpha):
			return 1,1,avg_qual
		if(avg_qual >= self.alpha-margin):
			return 1,0,avg_qual
		return 0,0,avg_qual