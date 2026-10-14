"""完整 A 项公式、优化器一致性和自由 C 参数的回归验证。"""

import unittest

import numpy as np

from raman.fitting.faust_henry import faust_henry_factor
from raman.fitting.lopc import lopc
from raman.fitting.lopc_fh import fit, lopc_fh
from raman.fitting.lopc_fh_convolved import fit as fit_convolved
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
                     gamma_p=80., gamma_ph=7., C=-.25, vary_omega_l=False)
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

    def test_vary_flags_freeze_adam_and_lm_together(self):
        y = lopc_fh(self.x, C=-.3, **self.values)
        result = fit(
            self.x, y, centers=[735.], omega_t=533., omega_p=220.,
            gamma_p=80., gamma_ph=7., C=-.25, optimizer="adam_then_lm",
            adam_options={"max_steps": 5}, vary_amplitude=False,
            vary_omega_p=False, vary_gamma_p=False, vary_gamma_ph=False,
            vary_omega_l=False, vary_omega_t=False,
            vary_epsilon_inf=False, vary_C=False,
        )
        self.assertNotIn("error", result.adam_prefit)
        for name in ("amplitude", "omega_p", "gamma_p", "gamma_ph",
                     "omega_l", "omega_t", "epsilon_inf", "C"):
            self.assertFalse(result.params[name].vary)
            self.assertAlmostEqual(
                result.params[name].value, result.adam_prefit[name], places=12
            )

    def test_vary_omega_t_keeps_fixed_omega_l(self):
        y = lopc_fh(self.x, C=-.3, **self.values)
        result = fit(
            self.x, y, centers=[735.], omega_t=533., omega_p=220.,
            gamma_p=80., gamma_ph=7., C=-.25, vary_omega_l=False,
            vary_omega_t=True,
        )
        self.assertFalse(result.params["omega_l"].vary)
        self.assertTrue(result.params["omega_t"].vary)
        self.assertAlmostEqual(result.params["omega_l"].value, 735., places=12)
        self.assertLess(result.params["omega_t"].value, result.params["omega_l"].value)

    def test_convolved_torch_matches_numpy_and_parameter_gradients(self):
        from raman.fitting.adam_prefit_fh import lopc_fh_convolved_torch, torch

        # 覆盖实际 1498 点位移轴上的局部窗口，以及不同的仪器宽度。
        axis = np.linspace(350., 800., 1498)
        x = axis[(axis >= 720.) & (axis <= 750.)]
        values = {**self.values, "C": -.3}
        for sigma in (0., .3, 1., 3.):
            with self.subTest(sigma=sigma):
                tensors = {k: torch.tensor(v, dtype=torch.float64, requires_grad=True)
                           for k, v in values.items()}
                predicted = lopc_fh_convolved_torch(x, sigma_inst=sigma, **tensors)
                np.testing.assert_allclose(
                    predicted.detach().numpy(),
                    lopc_fh_convolved(x, sigma_inst=sigma, **values),
                    rtol=1.e-10, atol=1.e-12,
                )
                predicted.sum().backward()
                for name, value in values.items():
                    step = 1.e-5 * max(abs(value), 1.)
                    above = lopc_fh_convolved(x, sigma_inst=sigma,
                                             **{**values, name: value + step}).sum()
                    below = lopc_fh_convolved(x, sigma_inst=sigma,
                                             **{**values, name: value - step}).sum()
                    np.testing.assert_allclose(tensors[name].grad.item(),
                                               (above - below) / (2 * step),
                                               rtol=2.e-4, atol=1.e-8)

    def test_convolved_adam_lm_uses_weights_and_fixed_parameters(self):
        values = {**self.values, "C": -.3}
        y = lopc_fh_convolved(self.x, sigma_inst=1., **values)
        weights = np.linspace(1., 2., self.x.size)
        options = dict(centers=[735.], omega_t=533., omega_p=220.,
                       gamma_p=80., gamma_ph=7., C=-.25, sigma_inst=1.,
                       optimizer="adam_then_lm", adam_options={"max_steps": 5},
                       vary_amplitude=False, vary_omega_p=False, vary_gamma_p=False,
                       vary_gamma_ph=False, vary_omega_l=False,
                       vary_omega_t=False, vary_epsilon_inf=False)
        for vary_C in (False, True):
            with self.subTest(vary_C=vary_C):
                result = fit_convolved(self.x, y, weights=weights,
                                       vary_C=vary_C, **options)
                self.assertNotIn("error", result.adam_prefit)
                self.assertEqual(result.params["sigma_inst"].value, 1.)
                self.assertEqual(result.adam_prefit["sigma_inst"], 1.)
                self.assertFalse(result.params["sigma_inst"].vary)
                for name in values:
                    if name == "C" and vary_C:
                        continue
                    self.assertFalse(result.params[name].vary)
                    self.assertAlmostEqual(result.params[name].value,
                                           result.adam_prefit[name], places=12)
                    if name != "amplitude":
                        self.assertEqual(result.params[name].value,
                                         -.25 if name == "C" else values[name])
                predicted = lopc_fh_convolved(self.x, sigma_inst=1.,
                    **{name: result.adam_prefit[name] for name in values})
                expected_loss = np.mean((weights * (predicted - y) /
                                         max(np.max(np.abs(y)), 1.)) ** 2)
                self.assertAlmostEqual(result.adam_prefit["adam_loss"], expected_loss,
                                       places=12)
                np.testing.assert_allclose(result.residual, weights * (y - result.best_fit))

    def test_convolved_adam_optimizes_material_parameters_with_fixed_lo(self):
        from raman.fitting.adam_prefit_fh import adam_prefit_lopc_fh

        initial = {**self.values, "C": -.3}
        y = lopc_fh_convolved(self.x, sigma_inst=1.,
                             **{**initial, "omega_t": 530., "epsilon_inf": 10.})
        result = adam_prefit_lopc_fh(
            self.x, y, initial_values=initial, omega_t=533., epsilon_inf=9.5,
            convolved=True, sigma_inst=1., max_steps=5,
            vary_amplitude=False, vary_omega_p=False, vary_gamma_p=False,
            vary_gamma_ph=False, vary_omega_l=False, vary_C=False,
            vary_omega_t=True, vary_epsilon_inf=True,
        )
        self.assertEqual(result["omega_l"], 735.)
        self.assertGreater(result["omega_t"], 0.)
        self.assertLess(result["omega_t"], result["omega_l"])
        self.assertNotEqual(result["omega_t"], initial["omega_t"])
        self.assertNotEqual(result["epsilon_inf"], initial["epsilon_inf"])

    def test_zero_convolution_preserves_adam_lm_optimization(self):
        y = lopc_fh(self.x, C=-.3, **self.values)
        options = dict(centers=[735.], omega_t=533., omega_p=220.,
                       gamma_p=80., gamma_ph=7., C=-.25,
                       optimizer="adam_then_lm", adam_options={"max_steps": 5},
                       vary_omega_t=True, vary_epsilon_inf=True)
        plain = fit(self.x, y, **options)
        convolved = fit_convolved(self.x, y, sigma_inst=0., **options)
        for name in (*self.values, "C"):
            self.assertAlmostEqual(plain.adam_prefit[name], convolved.adam_prefit[name])
        np.testing.assert_allclose(plain.best_fit, convolved.best_fit, atol=1.e-9)

    def test_instrument_width_gradient_matches_finite_difference(self):
        from raman.fitting.adam_prefit_fh import lopc_fh_convolved_torch, torch

        values = {**self.values, "C": -.3, "omega_p": 80., "gamma_p": 300.}
        axis = np.linspace(350., 800., 1498)
        x = axis[(axis >= 720.) & (axis <= 750.)]
        # 使用真实采样网格，在 6 sigma 截断点数不跳变处检查连续导数。
        for initial in (.3, 1., 3.):
            with self.subTest(sigma=initial):
                sigma = torch.tensor(initial, dtype=torch.float64, requires_grad=True)
                predicted = lopc_fh_convolved_torch(x, sigma_inst=sigma, **values)
                loss = predicted.square().sum()
                loss.backward()
                step = 1.e-5
                above = np.sum(lopc_fh_convolved(x, sigma_inst=initial + step, **values)**2)
                below = np.sum(lopc_fh_convolved(x, sigma_inst=initial - step, **values)**2)
                self.assertNotEqual(sigma.grad.item(), 0.)
                np.testing.assert_allclose(sigma.grad.item(), (above - below) / (2 * step),
                                           rtol=2.e-4, atol=1.e-8)

    def test_free_instrument_width_is_optimized_in_both_stages(self):
        values = {**self.values, "C": -.3, "omega_p": 80., "gamma_p": 300.}
        y = lopc_fh_convolved(self.x, sigma_inst=1.7, **values)
        weights = np.linspace(1., 2., len(self.x))
        result = fit_convolved(
            self.x, y, centers=[735.], omega_t=533., omega_p=80., gamma_p=300.,
            gamma_ph=7., C=-.3, sigma_inst=1., vary_sigma_inst=True,
            vary_omega_p=False, vary_gamma_p=False, vary_gamma_ph=False,
            vary_omega_l=False, vary_omega_t=False, vary_epsilon_inf=False, vary_C=False,
            optimizer="adam_then_lm", adam_options={"max_steps": 80}, weights=weights,
        )
        self.assertNotIn("error", result.adam_prefit)
        self.assertNotEqual(result.adam_prefit["sigma_inst"], 1.)
        self.assertAlmostEqual(result.init_params["sigma_inst"].value,
                               result.adam_prefit["sigma_inst"])
        self.assertTrue(result.params["sigma_inst"].vary)
        self.assertEqual(result.params["sigma_inst"].min, 0.)
        self.assertEqual(result.params["sigma_inst"].max, np.inf)
        self.assertAlmostEqual(result.params["sigma_inst"].value, 1.7, places=4)
        np.testing.assert_allclose(result.residual, weights * (y - result.best_fit))
        np.testing.assert_allclose(result.best_fit, y, rtol=1.e-6, atol=1.e-8)

    def test_free_instrument_width_requires_positive_initial_value(self):
        with self.assertRaisesRegex(ValueError, "positive initial sigma_inst"):
            fit_convolved(self.x, lopc_fh(self.x, C=0., **self.values), centers=[735.],
                          omega_t=533., sigma_inst=0., vary_sigma_inst=True)


if __name__ == '__main__':
    unittest.main()
