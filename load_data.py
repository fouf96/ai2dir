import numpy as np
import os

import logging

logger = logging.Logger(__name__)


class DataAggregator:
    BASEPATH = "/Users/arthun/code/data/KI test"

    RAW_DATA = "raw_data"

    PIXELS = 32
    ROWS = 2

    def __init__(self, experiment: str = "20230213_KI_test_30_000"):
        self.experiment = experiment
        self.path = os.path.join(self.BASEPATH, experiment)
        self.preallocate()
        self.load()
        self.save()

    def preallocate(self):
        p = os.path.join(self.path, self.RAW_DATA)
        delays = os.listdir(p)
        self.ndelays = len(delays)

        # Load first file to get shape of rawdata
        names = os.listdir(os.path.join(p, delays[0]))
        self.nscans = len(names)

        path = os.path.join(p, delays[0], names[0])

        d = next(iter(np.load(path).values()))

        shape = [self.ndelays, self.nscans] + list(d.shape)

        self.data = np.zeros(shape)

    def load(self):
        p = os.path.join(self.path, self.RAW_DATA)

        for didx, delay in enumerate(os.listdir(p)):
            path = os.path.join(p, delay)
            if not os.path.isdir(path):
                logger.debug(f"Skipping delay/folder or file {delay}.")
                continue
            
            for sidx, scan in enumerate(os.listdir(path)):
                path = os.path.join(p, delay, scan)
                if path[:-3] != "npy":
                    logger.debug(f"Skipping array/folder or file {scan}.")
                    continue
                
                logger.debug(f"Loading {path}, into {didx=}, {sidx=}.")
                self.data[didx, sidx] = next(iter(np.load(os.path.join(p, delay, scan)).values()))

    def save(self):
        path = os.path.join(self.BASEPATH, self.experiment)
        logger.info(f"Saving loaded data to {path}.")
        np.save(path, self.data)

if __name__ == "__main__":
    experiments = os.listdir(DataAggregator.BASEPATH)
    for experiment in experiments:
        if os.path.isdir(os.path.join(DataAggregator.BASEPATH, experiment)):
            ds = DataAggregator(experiment=experiment)
        else:
            logger.debug(f"Skipped experiment/folder or file {experiment}.")
