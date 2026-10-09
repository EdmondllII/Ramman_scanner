"""验证步骤之间只使用已有结果，不隐式校正、平均或插值。"""

from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from raman.lineshapes import lopc_fh
from raman.reconstruction import reconstruct_lopc_fh
from work.visualization.plot_parameter_heatmap import parameter_image


class WorkflowBoundaryTests(unittest.TestCase):
    def test_fitting_passes_corrected_signal_without_background_subtraction(self):
        from work.fitting import run
        signal = np.array([-1., 2., 3., 1.])
        data = SimpleNamespace(kind='cube', spectral_axis=np.arange(4.),
                               y=np.array([0.]), intensity=signal.reshape(1, 1, 4))
        with TemporaryDirectory() as directory, patch.object(run, 'READ_DATA', return_value=data), \
                patch.object(run, 'detect_peaks', return_value=np.array([])) as detect:
            _, metadata = run.process_cube('corrected.tif', directory)
        np.testing.assert_array_equal(detect.call_args.args[1], signal)
        self.assertNotIn('background_file', metadata)

    def test_baseline_produces_corrected_input_for_gaussian_path(self):
        from work.baseline import run
        import tifffile
        cube = np.array([[[3., 4., 5.]]])
        data = SimpleNamespace(kind='cube', spectral_axis=np.arange(3.), y=np.array([0.]), intensity=cube)
        with TemporaryDirectory() as directory, patch.object(run, 'READ_DATA', return_value=data), \
                patch.object(run, 'BASELINE_METHOD', return_value=(np.array([2., 3., 4.]), np.ones(3))):
            run.process_cube('raw.tif', directory)
            np.testing.assert_array_equal(tifffile.imread(Path(directory) / 'corrected.tif'), cube - 1.)

    def test_heatmap_selects_peak_without_averaging(self):
        rows = [dict(x='0', y='0', peak_id='1', model='lorentzian', position='415'),
                dict(x='0', y='0', peak_id='2', model='lopc_fh', position='735')]
        np.testing.assert_array_equal(parameter_image(rows, 'position', 2, 'lopc_fh'), [[735.]])
        with self.assertRaises(ValueError):
            parameter_image(rows + [rows[1]], 'position', 2)

    def test_spectrum_arithmetic_uses_aligned_input_only(self):
        for name, expected in [('add_spectra.py', [4., 6.]), ('subtract_spectra.py', [-2., -2.])]:
            with self.subTest(script=name), \
                    patch('raman.io.read_csv_spectrum', side_effect=[(np.array([1., 2.]), np.array([1., 2.])),
                                                                   (np.array([1., 2.]), np.array([3., 4.]))]), \
                    patch('numpy.savetxt') as save:
                runpy.run_path(str(Path('work/reconstruction') / name), run_name='__main__')
                np.testing.assert_array_equal(save.call_args.args[1][:, 1], expected)

    def test_spectrum_arithmetic_rejects_axes_instead_of_interpolating(self):
        for name in ('add_spectra.py', 'subtract_spectra.py'):
            with self.subTest(script=name), \
                    patch('raman.io.read_csv_spectrum', side_effect=[(np.array([1., 2.]), np.ones(2)),
                                                                   (np.array([1., 3.]), np.ones(2))]), \
                    patch('numpy.savetxt') as save:
                with self.assertRaises(ValueError):
                    runpy.run_path(str(Path('work/reconstruction') / name), run_name='__main__')
                save.assert_not_called()

    def test_reconstruction_matches_shared_full_A_model(self):
        x = np.linspace(720., 750., 101)
        values = dict(amplitude=10., omega_p=220., gamma_p=80., gamma_ph=7.,
                      omega_l=735., omega_t=533., epsilon_inf=9.5, C=-.3)
        np.testing.assert_array_equal(reconstruct_lopc_fh(x, **values), lopc_fh(x, **values))


if __name__ == '__main__':
    unittest.main()
