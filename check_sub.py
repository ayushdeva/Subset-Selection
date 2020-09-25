alpha = 0.7
epsilon = 0.001
R = 100

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

n,Q,K,C = get_inputs()

all_q = []
all_r = []
def check_subset(i,q,c,z):
	# print("currently at ",i," ",n)
	if(i==n and z==0):
		return
	if i==n:
		all_q.append(q/z)
		all_r.append(R*q-c)
		if(float(q)/float(z) > alpha - epsilon and float(q)/float(z) < alpha + epsilon):
			print("We have one such subset")
		return
	
	check_subset(i+1,q,c,z)
	check_subset(i+1,q+Q[i],C[i],z+1)
	return

check_subset(0,0,0,0)
print(len(all_q),len(all_r))