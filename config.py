import json
import os
from zipfile import ZipFile
import numpy as np


class ExperimentConfig:
    ANALOG_INPUT_CONFIG_POSTFIX = " analog input configuration.json"

    def __init__(self, base_path: str, experiment: str, laboratory: str = "i-lab"):
        self.base_path = base_path
        self.experiment = experiment
        self.laboratory = laboratory

        self.get_names()

        self.path = os.path.join(self.base_path, self.experiment, self.config_zip_name)

    def get_names(self):
        self.config_zip_name = f"hwconfigxxx_{self.experiment}.zip"

        if self.laboratory == "i-lab":
            self.analog_input_config_name = "I-Lab" + self.ANALOG_INPUT_CONFIG_POSTFIX

    def load_config_zip(self):
        with ZipFile(self.path) as zip:
            with zip.open(self.analog_input_config_name) as aic:
                self.analog_input_configuration = json.load(aic)

    def get_indices(self):
        # Note that this entire logic breaks if the input config is in a
        # bad/weird order. But by convention it should be sorted
        # anyways.
        probe_pixels = []
        reference_pixels = []
        self.choppers = {}
        r2r = []
        for idx, key in enumerate(self.analog_input_configuration):
            if "probe pixel" in key:
                probe_pixels.append(idx)
            elif "reference pixel" in key:
                reference_pixels.append(idx)
            elif "Chopper" in key:
                self.choppers[key] = idx
            elif "R2R" in key:
                r2r.append(idx)
            elif "pyro" in key:
                self.pyro_detector = idx
            elif "wobbler" in key:
                self.wobbler = idx

        self.probe_pixels = np.asarray(probe_pixels, dtype=int)
        self.reference_pixels = np.asarray(reference_pixels, dtype=int)
        self.r2r = np.asarray(r2r, dtype=int)


import unittest


class TestExperimentConfig(unittest.TestCase):
    BASEPATH = "/Users/arthun/code/data/KI test"
    EXPERIMENT = "20230213_KI_test_30_000"

    ANALOG_INPUT_CONFIGURATION_PATH = ""

    RAW_DATA = "raw_data"

    PIXELS = 64
    ROWS = 2

    CHOPPER_IDX = 66

    def test_load_config_zip(self):
        exp_config = ExperimentConfig(self.BASEPATH, self.EXPERIMENT)
        exp_config.load_config_zip()

    def test_get_indices(self):
        exp_config = ExperimentConfig(self.BASEPATH, self.EXPERIMENT)
        exp_config.load_config_zip()
        exp_config.get_indices()


if __name__ == "__main__":
    unittest.main()
