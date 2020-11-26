#!/usr/bin/env python
# coding: utf-8

# In[132]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# In[65]:


filename = '../Comparison/output_exp1_all.csv'


# In[66]:


all_data = pd.read_csv(filename)


# In[67]:


all_data


# In[68]:


# For a particular alpha, variation of mean utility and mean time with 'n' for different algorithms
alpha = 0.8
df = all_data[all_data['alpha'] == alpha]
utils = df.groupby(['n','algo']).agg({'util':'mean'})
time_taken = df.groupby(['n','algo']).agg({'time':'mean'})
utils = utils.unstack(fill_value=0)
time_taken = time_taken.unstack(fill_value=0)


# In[ ]:


utils.columns = utils.columns.get_level_values(1)


# In[85]:


utils['gss:dpss'] = utils['gss']/utils['dpss']
utils['gss:ilp'] = utils['gss']/utils['ilp']


# In[112]:


plt.plot(utils.index,utils['gss:ilp'])
# plt.plot(utils.index,utils['gss:dpss'])
plt.xscale('log')


# In[188]:


ratios = df.groupby(['n','algo','iter']).agg({'util':'mean'})
ratios = ratios.unstack(level=1,fill_value=0)
ratios.columns = ratios.columns.get_level_values(1)
ratios['gss:dpss'] = ratios['gss']/ratios['dpss']
ratios['gss:ilp'] = ratios['gss']/ratios['ilp']
tmp1 = ratios['gss:dpss']
tmp2 = ratios['gss:ilp']


# In[190]:


tmp1 = tmp1.unstack(level=0)
n_agents = [2,3,5,8,10,12,14,16,18,20]
tmp1 = tmp1[n_agents]
tmp1 = tmp1.replace([np.inf, -np.inf], np.nan)

tmp1_mean = {}
tmp1_var = {}
tmp1_vals = []
for i in n_agents:
    a = tmp1[i]
    a = a.dropna()
    a = np.array(a)
    tmp1_vals.append(a)
    tmp1_mean[i] = np.mean(a)
    tmp1_var[i] = np.var(a)


# In[195]:


# plt.boxplot(tmp1_vals,positions=n_agents)
plt.boxplot(tmp1_vals)
plt.xticks([i+1 for i in range(len(n_agents))],n_agents)


# In[172]:


x,y = zip(*tmp1_var.items())
plt.plot(x,y)


# In[166]:





# In[70]:


time_taken


# In[53]:


utils.to_csv('../Comparison/utils_withdp1.csv')
time_taken.to_csv('../Comparison/time_withdp1.csv')

