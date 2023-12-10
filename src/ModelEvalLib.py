# some functions to calculate results of model outputs
# Evan, 2023-11-10

import numpy as np

# silence the warning note
import warnings
warnings.filterwarnings("ignore")

class CalculateMetrics:
    def __init__(self, observed, simulated):
        # Check if the lengths of the input sequences are consistent
        if len(observed) != len(simulated):
            raise ValueError("Lengths of the observed and simulated sequences are not consistent")

        self.observed = observed
        self.simulated = simulated

    def get_mb(self):
        # Calculate the mean bias (MB)
        mb = np.mean(self.simulated - self.observed)
        return mb

    def get_r(self):
        # Calculate the correlation coefficient (R)
        r = np.corrcoef(self.observed, self.simulated)[0, 1]
        return r

    def get_rmse(self):
        # Calculate the root mean square error (RMSE)
        rmse = np.sqrt(np.mean((self.simulated - self.observed) ** 2))
        return rmse

    def get_ioa(self):
        # Calculate the index of agreement (IOA)
        numerator = np.sum((self.simulated - self.observed) ** 2)
        denominator = np.sum((np.abs(self.simulated - np.mean(self.observed)) + np.abs(self.observed - np.mean(self.observed))) ** 2)
        ioa = 1 - (numerator / denominator)
        return ioa

    def get_nmb(self):
        # Calculate the normalized mean bias (NMB)
        nmb = (np.mean(self.simulated - self.observed) / np.mean(self.observed)) * 100
        return nmb

    def get_nme(self):
        # Calculate the normalized mean error (NME)
        nme = (np.sqrt(np.mean((self.simulated - self.observed) ** 2)) / np.mean(self.observed)) * 100
        return nme
