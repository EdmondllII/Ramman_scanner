"""验证评估只比较已有曲线及其输入约定。"""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np

from raman.evaluation import spectrum_metrics
from work.evaluation.evaluate_fit import evaluate_files


class SpectrumEvaluationTests(unittest.TestCase):
    def test_known_residual_and_gradient_metrics(self):
        metrics = spectrum_metrics([0., 1., 2.], [0., 2., 4.], [1., 1., 5.])
        self.assertEqual(metrics['chisqr'], 3.)
        self.assertEqual(metrics['rmse'], 1.)
        self.assertEqual(metrics['rsquared'], .625)
        self.assertEqual(metrics['gradient_chisqr'], 8.)

    def test_nonmonotonic_axis_rejected(self):
        with self.assertRaises(ValueError):
            spectrum_metrics([0., 2., 1.], [1., 2., 3.], [1., 2., 3.])

    def test_csv_comparison_filters_invalid_points_and_writes_residual_only(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            target, fitted = base / 'target.csv', base / 'fitted.csv'
            np.savetxt(target, [[0., 1.], [1., np.nan], [2., 3.], [3., 4.]], delimiter=',')
            np.savetxt(fitted, [[0., 0.], [1., 1.], [2., 2.], [3., 3.]], delimiter=',')
            payload = evaluate_files(target, fitted, base / 'out', regions={'upper': (2., 3.)})
            self.assertEqual(payload['metrics']['full_spectrum']['valid_points'], 3)
            self.assertEqual(payload['metrics']['upper']['valid_points'], 2)
            self.assertEqual(payload['metrics']['full_spectrum']['rmse'], 1.)
            data = np.loadtxt(base / 'out/fit_spectrum.csv', delimiter=',', skiprows=1)
            self.assertEqual(data.shape, (3, 4))
            np.testing.assert_allclose(data[:, 3], data[:, 1] - data[:, 2])
            self.assertNotIn('diagnostics', payload)
            self.assertNotIn('nvarys', payload['metrics']['full_spectrum'])

    def test_mismatched_axes_rejected_before_outputs(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            target, fitted = base / 'target.csv', base / 'fitted.csv'
            np.savetxt(target, [[0., 1.], [1., 2.]], delimiter=',')
            np.savetxt(fitted, [[0., 1.], [2., 2.]], delimiter=',')
            with self.assertRaises(ValueError):
                evaluate_files(target, fitted, base / 'out')
            self.assertFalse((base / 'out').exists())


if __name__ == '__main__':
    unittest.main()
