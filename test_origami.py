import unittest
from origami import Network
from pleat import Pleat
from gadgets import AndGadget, OrGadget, NotGadget, NandGadget

class TestGadgets(unittest.TestCase):
    def test_not(self):
        g = NotGadget("n1", ["a"], ["out"])
        self.assertEqual(g.evaluate([True]), [False])
        self.assertEqual(g.evaluate([False]), [True])
        self.assertEqual(g.evaluate([None]), [None])

    def test_and(self):
        g = AndGadget("and1", ["a","b"], ["out"])
        
        cases = [
            ([False, False], [False]),
            ([False, True], [False]),
            ([True, False], [False]),
            ([True, True], [True]),
        ]
        for ins, outs in cases:
            self.assertEqual(g.evaluate(ins), outs)
        self.assertEqual(g.evaluate([True, None]), [None])

    def test_or(self):
        g = OrGadget("or1", ["a","b"], ["out"])
        cases = [
            ([False, False], [False]),
            ([False, True], [True]),
            ([True, False], [True]),
            ([True, True], [True]),
        ]
        for ins, outs in cases:
            self.assertEqual(g.evaluate(ins), outs)
        self.assertEqual(g.evaluate([None, False]), [None])

    def test_nand(self):
        g = NandGadget("n1", ["a","b"], ["out"])
        cases = [
            ([False, False], [True]),
            ([False, True], [True]),
            ([True, False], [True]),
            ([True, True], [False]),
        ]
        for ins, outs in cases:
            self.assertEqual(g.evaluate(ins), outs)
        self.assertEqual(g.evaluate([True, None]), [None])

class TestIntegrationHalfAdder(unittest.TestCase):
    def test_half_adder_all(self):
        
        spec = {
            "pleats": ["a","b","or1_out","and1_out","not1_out","sum","carry"],
            "gadgets": [
                {"type": "OR", "id": "g_or", "inputs": ["a","b"], "outputs": ["or1_out"]},
                {"type": "AND", "id": "g_and", "inputs": ["a","b"], "outputs": ["and1_out"]},
                {"type": "NOT", "id": "g_not", "inputs": ["and1_out"], "outputs": ["not1_out"]},
                {"type": "AND", "id": "g_and2", "inputs": ["or1_out","not1_out"], "outputs": ["sum"]},
                {"type": "AND", "id": "g_carry", "inputs": ["a","b"], "outputs": ["carry"]},
            ],
            "inputs": {"a": None, "b": None}
        }
        net = Network.from_spec(spec)
        
        cases = [
            (False, False, False, False),
            (False, True, True, False),
            (True, False, True, False),
            (True, True, False, True),
        ]
        for a,b, sum_expected, carry_expected in cases:
            net.set_inputs({"a": a, "b": b})
            pleats, logs = net.run(log=False)
            self.assertEqual(pleats["sum"], sum_expected, f"sum failed for {a},{b}")
            self.assertEqual(pleats["carry"], carry_expected, f"carry failed for {a},{b}")

if __name__ == "__main__":
    unittest.main()
