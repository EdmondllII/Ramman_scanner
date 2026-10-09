"""验证固定权重的饱和性质及两个优化器的目标函数。"""

import unittest
from unittest.mock import patch

import numpy as np

from raman.fitting import lorentzian
from raman.fitting.lopc import fit, lopc
from raman.fitting.weighting import saturation_weights


class WeightedFittingTests(unittest.TestCase):
    def test_saturation_and_unit_weight_switch(self):
        y = np.array([-1., 0., 3., 6., 9., 300.])
        w = saturation_weights(y, alpha=4., scale=3.) ** 2
        np.testing.assert_allclose(w[:2], 1.)
        self.assertTrue(np.all(np.diff(w) >= 0.))
        self.assertTrue(np.all(np.diff(w[1:5], n=2) < 0.))
        self.assertAlmostEqual(w[-1], 5.)
        np.testing.assert_array_equal(saturation_weights(y, alpha=0.), np.ones_like(y))

    def test_lorentzian_weights_follow_filtered_sorted_data(self):
        x = np.array([2., 1., np.nan, 0., -1., -2.])
        y = np.array([1., 3., 9., 5., 3., 1.])
        weights = saturation_weights(y)
        result = lorentzian(x, y, centers=[0.], weights=weights)
        keep = np.isfinite(x)
        order = np.argsort(x[keep])
        expected = weights[keep][order]
        np.testing.assert_allclose(result.weights, expected)
        np.testing.assert_allclose(result.residual, (result.data - result.best_fit) * expected)
        self.assertAlmostEqual(result.chisqr, np.sum(result.residual ** 2))

    def test_adam_and_lm_share_weights(self):
        from raman.fitting.adam_prefit import adam_prefit_lopc

        x = np.linspace(720., 750., 101)
        initial = dict(amplitude=10., omega_l=735., omega_p=220., gamma_p=80., gamma_ph=7.)
        predicted = lopc(x, omega_t=533., epsilon_inf=9.5, **initial)
        y = predicted + np.linspace(0., .2, x.size)
        weights = saturation_weights(y)
        prefit = adam_prefit_lopc(x, y, initial_values=initial, omega_t=533.,
                                  epsilon_inf=9.5, weights=weights, max_steps=1)
        expected_loss = np.mean((weights * (predicted - y) / max(np.max(abs(y)), 1.)) ** 2)
        self.assertAlmostEqual(prefit['adam_loss'], expected_loss, places=12)
        with patch('raman.fitting.adam_prefit.adam_prefit_lopc', return_value=prefit) as adam:
            result = fit(x[::-1], y[::-1], centers=[735.], omega_t=533.,
                         omega_p=220., gamma_p=80., gamma_ph=7.,
                         optimizer='adam_then_lm', weights=weights[::-1])
        np.testing.assert_allclose(adam.call_args.kwargs['weights'], weights)
        np.testing.assert_allclose(result.weights, weights)
        np.testing.assert_allclose(result.residual, (y - result.best_fit) * weights)


if __name__ == '__main__':
    unittest.main()
