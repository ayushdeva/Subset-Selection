import pickle as pl
import matplotlib.pyplot as plt


filename = ["regret__100_10.0_100000","regret__100_20.0_100000","regret__100_50.0_100000","regret__100_100.0_100000"]
# filename = ["regret__50_50.0_50000","regret__100_50.0_100000","regret__250_50.0_50000"]
legend = ["epsilon = 0.1","epsilon = 0.05","epsilon = 0.02","epsilon = 0.01"]
# legend = ["n=50","n=100","n=150"]
colors = ['--r','-b','--g','-y']
out_fil = "regret-epsilon-test.png"


for files,color in zip(filename,colors):
	with open(files,'rb') as f:
		regret = pl.load(f)

	print(len(regret),regret[0:10])
	plt.plot(regret[0:50000],color)

plt.title("R3 vs t")
plt.xlabel("Rounds(t)")
plt.ylabel("Regret")
plt.legend(legend,loc='center right')
plt.savefig(out_fil, dpi=300)
# plt.show()
