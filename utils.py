import matplotlib.pyplot as plt 
import math
import pickle

def segregate(prods,n_prods,alpha):
		S1,S2,S3,S4 = [],[],[],[]
		for i in range(n_prods):
			prod = prods[i]
			if(prod.q>=alpha and prod.r>=0):
				S1.append(prod)
			elif(prod.q>alpha and prod.r<0):
				S2.append(prod)
			elif(prod.q<alpha and prod.r>0):
				S3.append(prod)
			else:
				S4.append(prod)
		return S1,S2,S3,S4

def allocate(x,obj,quant):
	obj.k_rem -= quant
	x[obj.index] += quant
	return x

def get_optimal_allocation(prods,n_prods,alpha):
	S1,S2,S3,S4 = segregate(prods,n_prods,alpha)
	# print("S1 : %d, S2 : %d, S3 : %d, S4 : %d" %(len(S1),len(S2),len(S3),len(S4)))
	x = [0 for i in range(n_prods)]
	d = 0
	
	for prod in S1 :
		x = allocate(x,prod,prod.k)
		d = d + prod.k*(prod.q-alpha)
	# print("After allocating to S1, excess quality : %f" %(d))

	S2.sort(key=lambda x: x.r/(alpha-x.q))
	S3.sort(key=lambda x: x.r/(alpha-x.q), reverse=True)

	p,q=0,0

	while d>0 and p<len(S3):
		prod = S3[p]
		w = min(prod.k_rem,d/(alpha-prod.q))
		# print("For S3, prod.q = %f, and quantity to take is %f" %(prod.q,w))
		x = allocate(x,prod,w)
		d -= w*(alpha - prod.q)
		if prod.k_rem == 0 :
			p += 1

	# print("Last step")
	while p<len(S3) and q<len(S2):
		prod2,prod3 = S2[q],S3[p]
		val2,val3 = prod2.r/(alpha-prod2.q) , prod3.r/(alpha-prod3.q)
		if val2>=val3 :
			break

		ratio = abs((alpha-prod2.q) / (alpha-prod3.q))
		# print(prod2.q,prod3.q,ratio)
		w2 = prod2.k_rem
		w3 = prod2.k_rem*ratio
		if(w3>prod3.k_rem):
			# print("Product 3 is the limiting manufacturer")
			w3 = prod3.k_rem
			w2 = prod3.k_rem/ratio
		# w = min(prod1.k_rem/(alpha-prod1.q),prod2.k_rem/(alpha-prod2.q))
		# print("Taking the following quantities :",w2,w3,sep=" ")
		x = allocate(x,prod2,w2)
		x = allocate(x,prod3,w3)
		if prod2.k_rem == 0 :
			q += 1
		if prod3.k_rem == 0 :
			p += 1
	return x,d

def myPlot(df,title,filepath):
	plt.plot(df)
	plt.title(title)
	plt.savefig(filepath+".png")
	plt.close()


def myPlotxy(dfx,dfy,title,filepath):
	plt.plot(dfx,dfy)
	plt.title(title)
	plt.savefig(filepath)
	plt.close()

# def myPlotlog(dfy,title,filepath):
# 	fig = plt.figure()
# 	ax = fig.add_subplot(1, 1, 1)
# 	line, = ax.plot(dfy)
# 	ax.set_yscale('log')
# 	plt.title(title)
# 	plt.savefig(filepath+".png")
# 	plt.close()

def myPlotlog(dfy,title,filepath):
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	line, = ax.plot(dfy)
	T = len(dfy)
	dfx = [math.log(i+1) for i in range(T)]
	plt.plot(dfx,dfy)
	plt.title(title)
	plt.savefig(filepath+".png")
	plt.close()

def myPlot2(xmax,df,actualVal,title,filepath):
	plt.axhline(y=actualVal)
	plt.plot(df)
	plt.ylim((0,5))
	print("Actual Value : ",actualVal)
	plt.title(title)
	plt.savefig(filepath+".png")
	plt.close()

def saveVar(var,filename):
	with open(filename,'wb') as f:
		pickle.dump(var,f)