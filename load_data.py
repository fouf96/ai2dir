import config
import numpy as np
import os

import logging

logger = logging.Logger(__name__)


class DataAggregator:
    BASEPATH = "/Users/arthun/Google Drive/AI 2D-IR/KI test"

    def __init__(
        self, experiment: str = "20230213_KI_test_30_000", laboratory: str = "i-lab"
    ):
        self.experiment = experiment
        self.path = os.path.join(self.BASEPATH, experiment)
        self.laboratory = (
            laboratory  # this should be automatically parsed from data set
        )

        self.config = config.ExperimentConfig(
            self.BASEPATH, experiment, laboratory="i-lab"
        )

        self.preallocate()
        self.load()
        self.save()

    def preallocate(self):
        p = os.path.join(self.path, self.config.raw_data_folder_name)
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
        p = os.path.join(self.path, self.config.raw_data_folder_name)

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
                self.data[didx, sidx] = next(
                    iter(np.load(os.path.join(p, delay, scan)).values())
                )

    def save(self):
        path = os.path.join(self.BASEPATH, self.experiment)
        logger.info(f"Saving loaded data to {path}.")
        np.save(path, self.data)


import unittest


class TestDataAggregator(unittest.TestCase):
    def test_init(self):
        da = DataAggregator()


if __name__ == "__main__":
    unittest.main()

    experiments = os.listdir(DataAggregator.BASEPATH)
    for experiment in experiments:
        if os.path.isdir(os.path.join(DataAggregator.BASEPATH, experiment)):
            ds = DataAggregator(experiment=experiment)
        else:
            logger.debug(f"Skipped experiment/folder or file {experiment}.")
