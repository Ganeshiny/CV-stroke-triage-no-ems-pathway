import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import lognorm
from file_paths import *
from ED_screening_sim import MU, SIGMA

mu = MU      # Mean
sigma = SIGMA   # Standard Deviation

x = np.linspace(0.01, 1000, 1000)
y = lognorm.pdf(x, s=sigma, scale=np.exp(mu))

plt.plot(x, y, label=rf'$\mu={mu:.2f}, \sigma={sigma:.2f}$')
plt.title('Normal Distribution Curve')
plt.xlabel('x')
plt.ylabel('Probability Density')
plt.legend()
plt.grid(True)
plt.savefig(OUT / "lognormal_distribution_of_waittimes.png", dpi=300, bbox_inches="tight")