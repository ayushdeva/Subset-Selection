import math
import numpy as np
from mip import Model, xsum, maximize, BINARY
INF = 1e7

def segregate(prods,n_prods,alpha):
    S1,S2,S3,S4 = [],[],[],[]
    for i in range(n_prods):
        prod = prods[i]
        if(prod.q>=alpha and prod.r>=0):
            S1.append(prod)
        elif(prod.q<alpha and prod.r>0):
            S2.append(prod)
        elif(prod.q>alpha and prod.r<0):
            S3.append(prod)
        else:
            S4.append(prod)
    return S1,S2,S3,S4

def gss(prods,n_prods,alpha):
    S1,S2,S3,S4 = segregate(prods,n_prods,alpha)
    # print("S1 : %d, S2 : %d, S3 : %d, S4 : %d" %(len(S1),len(S2),len(S3),len(S4)))
    x = np.array([1.0 for i in range(n_prods)])
    d = 0
    for prod in S1 :
        x[prod.index] = 0
        d = d + (prod.q-alpha)

    # import pdb; pdb.set_trace()
    S2.sort(key=lambda x: x.r/(alpha-x.q),reverse=True)
    S3.sort(key=lambda x: x.r/(alpha-x.q))
    
    # import pdb; pdb.set_trace()
    p,q=0,0
    while d>0 and p<len(S2):
        prod = S2[p]
        if (alpha-prod.q <= d) :
            x[prod.index] = 0
            d -= (alpha-prod.q)
            p+=1
        else:
            x[prod.index] -= d/(alpha-prod.q)
            d = 0
    
    # import pdb; pdb.set_trace()
    while (p<len(S2)) and (q<len(S3)):
        prod2,prod3 = S2[p],S3[q]
        val2,val3 = prod2.r/(alpha-prod2.q) , prod3.r/(alpha-prod3.q)
        if val2<=val3 :
            break
        q_limiting = min(x[prod2.index]*(alpha-prod2.q),x[prod3.index]*(prod3.q-alpha))
        x[prod2.index] -= q_limiting / (alpha - prod2.q)
        x[prod3.index] -= q_limiting / (prod3.q - alpha)
        import pdb; pdb.set_trace()
        if x[prod2.index] == 0 :
            p += 1
        if x[prod3.index] == 0 :
            q += 1

    # If a S3 bucket product is chosen partially, dropping it might lead to violation of QC. Hence, safe side, keep it fully and incur some extra regret 
    if (q != len(S3)) and (x[S3[q].index] < 1):
        x[S3[q].index] = 0
    
    # import pdb; pdb.set_trace()
    return np.floor(1-x),d

def get_allocation(d,n,qdiff,pt,n_decimals):
    selected = [0 for i in range(n)]
    curr_d = d
    for i in range(n):
        selected[i] = pt[i][int((curr_d+n)*(10**n_decimals))]
        curr_d += selected[i]*qdiff[i]
    return selected


def dp(ind,d,n,rev,qdiff,util,vec,max_reward,ans):
    if(ind==n) and (d<0):
        return max_reward,ans

    if (ind==n) and (d>=0):
        if(util > max_reward):
            max_reward = util
            ans = np.array(vec)
        return max_reward,ans

    max_reward,ans = dp(ind+1,d,n,rev,qdiff,util,vec+[0],max_reward,ans)
    max_reward,ans = dp(ind+1,d+qdiff[ind],n,rev,qdiff,util+rev[ind],vec+[1],max_reward,ans)
    return max_reward,ans

def dp_it(ind,d,n,rev,qdiff,n_decimals,mem):
    mem = [[-1 for i in range(n*4*(10**n_decimals))] for i in range(n+1)]

    for i in range(n*4*(10**n_decimals)):
        if(i < 2*n*(10**n_decimals)):
            mem[n][i] = -INF
        else:
            mem[n][i] = 0
    
    for ind in range(n-1,-1,-1):
        for i in range(n*(10**n_decimals),n*3*(10**n_decimals)):
            mem[ind][i] = max(rev[ind] + mem[ind+1][int(i+(10**n_decimals)*qdiff[ind])], mem[ind+1][i])
    
    import pdb; pdb.set_trace()
    selected = [0 for i in range(n)]
    curr_d = int( 2*n*(10**n_decimals) + (10**n_decimals)*d )
    for ind in range(n):
        if (rev[ind]==0) and (qdiff[ind]==0):
            selected[ind] = 0
        elif (rev[ind] + mem[ind+1][int(curr_d+(10**n_decimals)*qdiff[ind])] > mem[ind+1][int(curr_d)]):
            selected[ind] = 1
        else :  
            selected[ind] = 0
        curr_d += selected[ind]*(10**n_decimals)*qdiff[ind]
    return selected

def dpss(prods,n_prods,alpha,n_decimals=2,to_mem=False):
    S1,S2,S3,S4 = segregate(prods,n_prods,alpha)
    # print(S1,S2,S3,S4)
    # import pdb; pdb.set_trace()
    x = np.array([0 for i in range(n_prods)])
    d = 0
    for prod in S1 :
        x[prod.index] = 1
        d += (prod.q-alpha)
    # import pdb; pdb.set_trace()
    rev = [0 for i in range(n_prods)]
    qdiff = [0 for i in range(n_prods)]
    for prod in S2:
        ind = prod.index
        rev[ind] = prod.r
        qdiff[ind] = prod.q - alpha
    for prod in S3:
        ind = prod.index
        rev[ind] = prod.r
        qdiff[ind] = prod.q - alpha
    selected = np.array([0 for i in range(n_prods)])
    path_trace = [[-1 for i in range(n_prods*2*(10**n_decimals))] for i in range(n_prods+1)]
    mem = [[-1 for i in range(n_prods*2*(10**n_decimals))] for i in range(n_prods+1)]
    # import pdb; pdb.set_trace()
    if to_mem == False :
        vec = []
        ans = np.array([0 for i in range(n_prods)])
        max_reward, selected = dp(0,d,n_prods,rev,qdiff,0,vec,0,ans)
    else:
        selected = dp_it(0,d,n_prods,rev,qdiff,n_decimals,mem)
    # import pdb; pdb.set_trace()
    return x+selected,d


def ilp(prods,n_prods,alpha):
    S1,S2,S3,S4 = segregate(prods,n_prods,alpha)
    x = np.array([0.0 for i in range(n_prods)])
    d = 0
    for prod in S1 :
        x[prod.index] = 1
        d = d + (prod.q-alpha)
    rev = [-1.0 for i in range(n_prods)]
    qdiff = [-1.0 for i in range(n_prods)]
    for prod in S2:
        ind = prod.index
        rev[ind] = prod.r
        qdiff[ind] = prod.q - alpha
    for prod in S3:
        ind = prod.index
        rev[ind] = prod.r
        qdiff[ind] = prod.q - alpha
    
    m = Model('ilp')
    m.verbose = False
    y = [m.add_var(var_type=BINARY) for i in range(n_prods)]
    m.objective = maximize(xsum(rev[i] * y[i] for i in range(n_prods)))
    m += xsum(qdiff[i] * y[i] for i in range(n_prods)) >= -1*d
    m.optimize()
    selected = np.array([y[i].x for i in range(n_prods)])
    import pdb; pdb.set_trace()
    selected = np.floor(selected+0.01)
    import pdb; pdb.set_trace()
    return x+selected,d

