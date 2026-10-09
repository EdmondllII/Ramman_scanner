"""约束算法库的文件职责及模块依赖，允许 io 读取和 Adam 环境适配。"""

import ast
from pathlib import Path
import unittest


class AlgorithmBoundaryTests(unittest.TestCase):
    def test_algorithm_modules_do_not_read_or_write_workflow_files(self):
        forbidden_calls = {
            'open', 'read_text', 'read_bytes', 'write_text', 'write_bytes',
            'mkdir', 'savetxt', 'save', 'savez', 'savez_compressed',
            'loadtxt', 'genfromtxt', 'savefig', 'imread', 'imwrite',
        }
        for path in Path('raman').rglob('*.py'):
            if 'io' in path.parts:
                continue
            with self.subTest(module=str(path)):
                tree = ast.parse(path.read_text(encoding='utf-8'))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        name = node.func.attr if isinstance(node.func, ast.Attribute) else (
                            node.func.id if isinstance(node.func, ast.Name) else None)
                        self.assertNotIn(name, forbidden_calls)

    def test_algorithm_library_does_not_import_workflow(self):
        for path in Path('raman').rglob('*.py'):
            with self.subTest(module=str(path)):
                for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                    if isinstance(node, ast.ImportFrom):
                        self.assertFalse((node.module or '').startswith('work'))
                    elif isinstance(node, ast.Import):
                        self.assertFalse(any(alias.name.startswith('work') for alias in node.names))

    def test_reconstruction_and_evaluation_do_not_import_optimizers(self):
        paths = [*Path('raman/reconstruction').glob('*.py'), Path('raman/evaluation.py')]
        for path in paths:
            with self.subTest(module=str(path)):
                for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                    if isinstance(node, ast.ImportFrom):
                        self.assertNotIn('fitting', (node.module or '').split('.'))
                        # lmfit.lineshapes 仅计算线型；models/minimizer 等负责拟合。
                        module = node.module or ''
                        self.assertFalse(module == 'lmfit' or (
                            module.startswith('lmfit.') and module != 'lmfit.lineshapes'))


if __name__ == '__main__':
    unittest.main()
