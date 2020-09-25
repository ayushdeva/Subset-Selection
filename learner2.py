import math
from utils import *

class Producer():
	def __init__(self,c,k,R,index):
		self.index = index
		self.q_est = 0.5
		self.q_pos = 1.0
		self.freq = 0
		self.c = c
		self.k = k
		self.q = self.q_pos
		self.r = R*self.q_pos - c
		self.k_rem = self.k 	#remaining capacity for current iteration. Needs to be resetted every time
		self.q_history = [self.q]
		self.q_est_history = [0.5]

class LearnerAgent():
	def __init__(self,env,burnout,alpha_margin):
		self.R = env.R
		self.alpha = env.alpha + alpha_margin
		self.ucb_coeff = 0.3
		self.n, self.prods = self.initialize_prod(env)
		self.burnout = burnout

	def initialize_prod(self,env):
		n = env.n
		prods = [None for i in range(n)]
		for i in range(n):
			prod = env.producers[i]
			new_prod = Producer(prod.c,prod.k,self.R,prod.index)
			prods[prod.index] = new_prod
		return n,prods

	def reset(self):
		for prod in self.prods:
			prod.k_rem = prod.k

	def print_estimates(self):
		for prod in self.prods:
			print("(",prod.q_est,",",prod.q_pos,")",end=" ")
		print()

	def run(self,round):
		if(round <= self.burnout):
			x = [self.prods[i].k for i in range(self.n)]
		else:
			x,d = get_optimal_allocation(self.prods,self.n,self.alpha)
		return x

	def update(self,qualities,T,round_no):
		for i in range(self.n):
			#qualities[i][1] : number of products chosen in this round from manufacturer i
			#qualities[i][2] : sum total of qualities of all the products procured from manufactuer i in this round
			n_times = qualities[i][1]
			curr_q = self.prods[qualities[i][0]].q_est
			curr_freq = self.prods[qualities[i][0]].freq
			if qualities[i][1] != 0:
				new_q = (curr_q*curr_freq + qualities[i][2])/(curr_freq+qualities[i][1])
				new_freq = curr_freq + qualities[i][1]
				self.prods[qualities[i][0]].q_est = new_q
				self.prods[qualities[i][0]].freq = new_freq
				# self.prods[qualities[i][0]].q_pos = new_q +  self.ucb_coeff*math.sqrt((3*math.log(T))/2*new_freq)
				# print(round_no,new_freq,math.sqrt((3*math.log(round_no))/(2*new_freq)))
				self.prods[qualities[i][0]].q_pos = new_q + self.ucb_coeff*math.sqrt((3*math.log(round_no))/(2*new_freq))
				self.prods[qualities[i][0]].q_pos = min(1.0,self.prods[qualities[i][0]].q_pos)
				self.prods[qualities[i][0]].q = self.prods[qualities[i][0]].q_pos
				self.prods[qualities[i][0]].q_history.append(self.prods[qualities[i][0]].q)
				self.prods[qualities[i][0]].q_est_history.append(self.prods[qualities[i][0]].q_est)
				#if(round_no>=100):
					#self.prods[qualities[i][0]].q = self.prods[qualities[i][0]].q_est
				self.prods[qualities[i][0]].r = self.R*self.prods[qualities[i][0]].q - self.prods[qualities[i][0]].c

		# print("These are the updated q_values")
		# print(self.prods[5].q)
		# for i in range(self.n):
		# 	print(self.prods[i].q,end=",")
		# print()
