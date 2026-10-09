"""完整 A 项公式、优化器一致性和自由 C 参数的回归验证。"""

import unittest

import numpy as np

from raman.fitting.faust_henry import faust_henry_factor
from raman.fitting.lopc import lopc
from raman.fitting.lopc_fh import fit, lopc_fh
from raman.lineshapes import lopc_fh_convolved


class FullATermTests(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(720., 750., 121)
        self.values = dict(amplitude=10., omega_p=220., gamma_p=80., gamma_ph=7.,
                           omega_l=735., omega_t=533., epsilon_inf=9.5)

    def test_zero_C_recovers_original_model(self):
        np.testing.assert_allclose(lopc_fh(self.x, C=0., **self.values), lopc(self.x, **self.values))

    def test_zero_instrument_width_recovers_intrinsic_model(self):
        np.testing.assert_allclose(
            lopc_fh_convolved(self.x, sigma_inst=0., C=.2, **self.values),
            lopc_fh(self.x, C=.2, **self.values),
            rtol=1.e-12,
        )

    def test_instrument_convolution_preserves_finite_shape(self):
        intrinsic = lopc_fh(self.x, C=.2, **self.values)
        convolved = lopc_fh_convolved(self.x, sigma_inst=1., C=.2, **self.values)
        self.assertTrue(np.all(np.isfinite(convolved)))
        self.assertLess(float(np.max(convolved)), float(np.max(intrinsic)))

    def test_zero_phonon_damping_limit(self):
        C = .4
        factor = faust_henry_factor(self.x, omega_p=220., gamma_p=80., gamma_ph=0.,
                                    omega_l=735., omega_t=533., C=C)
        expected = ((533.**2 * (1 + C) - self.x**2) / (533.**2 - self.x**2))**2
        np.testing.assert_allclose(factor, expected, rtol=1.e-12)

    def test_no_carrier_limit_has_finite_positive_response(self):
        for C in (-.5, 0., .5):
            values = {**self.values, 'omega_p': 0.}
            result = lopc_fh(self.x, C=C, **values)
            self.assertTrue(np.all(np.isfinite(result) & (result >= 0.)))

    def test_torch_and_numpy_match_with_C_gradient(self):
        from raman.fitting.adam_prefit_fh import lopc_fh_torch, torch

        C = torch.tensor(-.3, dtype=torch.float64, requires_grad=True)
        predicted = lopc_fh_torch(self.x, C=C, **self.values)
        np.testing.assert_allclose(predicted.detach().numpy(), lopc_fh(self.x, C=-.3, **self.values), rtol=1.e-12)
        predicted.sum().backward()
        self.assertTrue(np.isfinite(C.grad.item()))
        self.assertNotEqual(C.grad.item(), 0.)

    def test_lm_recovers_free_C_without_bounds(self):
        y = lopc_fh(self.x, C=-.3, **self.values)
        result = fit(self.x, y, centers=[735.], omega_t=533., omega_p=220.,
                     gamma_p=80., gamma_ph=7., C=-.25, vary_centers=False)
        self.assertTrue(result.success)
        np.testing.assert_allclose(result.best_fit, y, rtol=1.e-4, atol=1.e-6)
        self.assertAlmostEqual(result.params['C'].value, -.3, places=3)
        self.assertTrue(result.params['C'].vary)
        self.assertEqual(result.params['C'].min, -np.inf)
        self.assertEqual(result.params['C'].max, np.inf)

    def test_adam_then_lm_uses_full_model_and_weights(self):
        y = lopc_fh(self.x, C=-.3, **self.values)
        weights = np.linspace(1., 2., self.x.size)
        result = fit(self.x, y, centers=[735.], omega_t=533., omega_p=220.,
                     gamma_p=80., gamma_ph=7., C=-.25, weights=weights,
                     optimizer='adam_then_lm', adam_options={'max_steps': 10})
        self.assertNotIn('error', result.adam_prefit)
        self.assertIn('C', result.adam_prefit)
        self.assertGreater(result.adam_prefit['omega_l'], 533.)
        np.testing.assert_allclose(result.residual, weights * (y - result.best_fit))
        np.testing.assert_allclose(result.best_fit, y, rtol=1.e-4, atol=1.e-6)


if __name__ == '__main__':
    unittest.main()
