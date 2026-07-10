import importlib.util
import sys
import unittest
from pathlib import Path


DAEMONS = Path(__file__).parents[1] / "src" / "daemons"


def load(name):
    path = DAEMONS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class DaemonImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(DAEMONS))

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(DAEMONS))

    def test_ipfix_exports_inventory_types(self):
        module = load("ipfix_exporter")
        self.assertTrue(hasattr(module, "InventoryCache"))
        self.assertTrue(hasattr(module, "Onu"))

    def test_optics_uses_ipfix_inventory(self):
        load("ipfix_exporter")
        module = load("onu_optics")
        self.assertTrue(callable(module.build_xml))

    def test_dhcp_has_plane_discovery(self):
        module = load("onu_dhcp")
        self.assertTrue(callable(module.lt_envs))


if __name__ == "__main__":
    unittest.main()
