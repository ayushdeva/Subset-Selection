import random
random.seed(2)

n = 500
Q,K,C = [],[],[]

alpha = 0.7
epsilon = 0.01
R = 100

#S1 : 20
# n1 = 20
# for i in xrange(n1):
# 	q = float(random.randint(0,301))/1000
# 	Q.append(q)
# 	K.append(10)
# 	breakeven_cost = R*q



for i in range(int(n/10)):
	q = float(random.randint(1000*alpha,1000))/1000.0
	Q.append(q)
	K.append(1)
	c = float(random.randint(60,100))
	C.append(c)

for i in range(n):
	q = float(random.randint(0,1000))/1000.0
	Q.append(q)
	K.append(1)
	c = float(random.randint(0,100))
	C.append(c)

print(n)
for i in range(n):
	print(Q[i],K[i],C[i],sep=",")
