"""回归验证寻峰和拟合的非负要求，以及 LOPC 无窗口参数限制。"""

import unittest

import numpy as np

from raman.fitting import detect_peaks, gaussian, lorentzian, voigt
from raman.fitting.lopc import fit, lopc


class FittingConstraintsTests(unittest.TestCase):
    def test_detection_excludes_negative_local_maximum_without_clipping(self):
        x = np.arange(9, dtype=float)
        y = np.array([-3., -1., -3., 0., 2., 0., -1., 0., -1.])
        original = y.copy()
        np.testing.assert_array_equal(
            detect_peaks(x, y, prominence=0., distance=1), [4., 7.]
        )
        np.testing.assert_array_equal(y, original)

    def test_ordinary_models_cannot_fit_a_negative_peak(self):
        x = np.linspace(-10., 10., 201)
        y = -5. * np.exp(-0.5 * x ** 2)
        for fitter in (gaussian, lorentzian, voigt):
            with self.subTest(model=fitter.__module__):
                result = fitter(x, y, centers=[0.], sigma=1., vary_centers=False)
                self.assertGreaterEqual(result.params['p1_amplitude'].value, 0.)
                self.assertGreaterEqual(result.params['p1_height'].value, 0.)
                self.assertLess(np.max(np.abs(result.best_fit)), 1.e-5)

    def test_lopc_lm_frequency_outside_old_window(self):
        x = np.linspace(760., 820., 121)
        y = lopc(x, amplitude=10., omega_l=780., omega_t=533.,
                 epsilon_inf=9.5, omega_p=100., gamma_p=80., gamma_ph=7.)
        result = fit(x, y, centers=[780.], omega_t=533., omega_p=100.,
                     gamma_p=80., gamma_ph=7.)
        self.assertGreater(result.params['omega_l'].value, 750.)
        np.testing.assert_allclose(result.best_fit, y, rtol=1.e-6, atol=1.e-8)
        for name in ('amplitude', 'omega_l', 'omega_p', 'gamma_p', 'gamma_ph'):
            self.assertEqual(result.params[name].max, np.inf)
        self.assertGreaterEqual(result.params['amplitude'].value, 0.)

    def test_adam_preserves_exact_solution_outside_old_window(self):
        from raman.fitting.adam_prefit import adam_prefit_lopc

        x = np.linspace(760., 820., 121)
        initial = dict(amplitude=10., omega_l=780., omega_p=100.,
                       gamma_p=80., gamma_ph=7.)
        y = lopc(x, omega_t=533., epsilon_inf=9.5, **initial)
        result = adam_prefit_lopc(x, y, initial_values=initial,
                                 omega_t=533., epsilon_inf=9.5, max_steps=3)
        self.assertGreater(result['omega_l'], 750.)
        predicted = lopc(x, omega_t=533., epsilon_inf=9.5,
                         **{name: result[name] for name in initial})
        np.testing.assert_allclose(predicted, y, rtol=1.e-6, atol=1.e-8)


if __name__ == '__main__':
    unittest.main()
