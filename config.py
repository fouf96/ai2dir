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

        self.path = os.path.join(self.base_path, self.experiment)

    def get_names(self):
        self.config_zip_name = f"hwconfigxxx_{self.experiment}.zip"
        self.raw_data_folder_name = "raw_data"

        if self.laboratory == "i-lab":
            self.analog_input_config_name = "I-Lab" + self.ANALOG_INPUT_CONFIG_POSTFIX
            self.pixel_linearization_name = f"i-lab_pixel_linearization_final.json"

        self.delay_file_name = f"delay_file_{self.experiment}.npy"
        self.probe_wn_axis_file_name = f"probe_wn_axis_{self.experiment}.npy"

        self.background_file_name = f"background_{self.experiment}.npy"

    def load_config_zip(self):
        with ZipFile(os.path.join(self.path, self.config_zip_name)) as zip:
            with zip.open(self.analog_input_config_name) as aic:
                self.analog_input_configuration = json.load(aic)
            with zip.open(self.pixel_linearization_name) as lin:
                self.linearization_json = json.load(lin)

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

    def get_delays(self):
        delays = np.load(os.path.join(self.path, self.delay_file_name))
        self.delays = delays[:, 0]
        self.n_delays = self.delays.size

    def get_probe_wn_axis(self):
        self.probe_wn_axis = np.load(
            os.path.join(self.path, self.probe_wn_axis_file_name)
        )

    def get_background(self):
        # Background to has size of number of all input channels
        # i.e. for I-Lab: 72
        self.background = np.load(os.path.join(self.path, self.background_file_name))

    def get_linearization_params(self):
        if not hasattr(self, "probe_pixels"):
            self.get_indices()

        a = np.zeros(self.probe_pixels.size * 2)
        b = np.zeros_like(a)
        c = np.zeros_like(a)
        for pixel, data in self.linearization_json["parameters"].items():
            pixel = int(pixel)
            a[pixel] = data["a"][0]
            b[pixel] = data["b"][0]
            c[pixel] = data["c"][0]

        if self.linearization_json["type"] == "cubicfraction":
            self.linearize = self.__cubic_fraction

    def __cubic_fraction(self, x: np.array) -> np.array:
        return ((self.a * x) ** 3 + (self.b * x)) / (self.c * x + 1) + 0


import unittest


class TestExperimentConfig(unittest.TestCase):
    BASEPATH = "/Users/arthun/Google Drive/AI 2D-IR/KI test"
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

    def test_get_delays(self):
        exp_config = ExperimentConfig(self.BASEPATH, self.EXPERIMENT)
        exp_config.load_config_zip()
        exp_config.get_delays()

    def test_get_probe_wn_axis(self):
        exp_config = ExperimentConfig(self.BASEPATH, self.EXPERIMENT)
        exp_config.load_config_zip()
        exp_config.get_probe_wn_axis()

    def test_get_background(self):
        exp_config = ExperimentConfig(self.BASEPATH, self.EXPERIMENT)
        exp_config.load_config_zip()
        exp_config.get_background()

    def test_get_linearization_params(self):
        exp_config = ExperimentConfig(self.BASEPATH, self.EXPERIMENT)
        exp_config.load_config_zip()
        exp_config.get_linearization_params()


if __name__ == "__main__":
    unittest.main()
