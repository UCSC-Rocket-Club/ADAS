import pandas as pd
import matplotlib.pyplot as plt

# the csv data is converted into a pandas dataframe
data = pd.read_csv("sensors.csv")

data.plot()
plt.show()
