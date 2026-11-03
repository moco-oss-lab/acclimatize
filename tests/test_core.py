import unittest

from acclimatize import Stop, assess_itinerary
from acclimatize.cli import parse_stops


class AssessItineraryTests(unittest.TestCase):
    def test_gradual_ascent_is_ok(self):
        stops = [
            Stop("Lima", 0, nights=2),
            Stop("Sacred Valley", 2800, nights=2),
            Stop("Machu Picchu", 2430, nights=1),
            Stop("Cusco", 3400, nights=2),
        ]
        self.assertTrue(assess_itinerary(stops).ok)

    def test_direct_jump_to_very_high_is_high_severity(self):
        stops = [Stop("Lima", 0, nights=2), Stop("Uyuni", 3656, nights=1)]
        report = assess_itinerary(stops)
        self.assertFalse(report.ok)
        self.assertEqual(report.warnings[0].severity, "high")

    def test_moderate_jump_above_3000_warns(self):
        stops = [Stop("Base", 3100, nights=1), Stop("High Camp", 3700, nights=1)]
        report = assess_itinerary(stops)
        self.assertFalse(report.ok)
        self.assertEqual(report.warnings[0].severity, "medium")

    def test_small_step_above_3000_is_ok(self):
        stops = [Stop("Cusco", 3400, nights=1), Stop("Puno", 3827, nights=1)]
        self.assertTrue(assess_itinerary(stops).ok)

    def test_descent_never_warns(self):
        stops = [Stop("Cusco", 3400, nights=1), Stop("Machu Picchu", 2430, nights=1)]
        self.assertTrue(assess_itinerary(stops).ok)

    def test_invalid_stop_rejected(self):
        with self.assertRaises(ValueError):
            Stop("Nowhere", -1)
        with self.assertRaises(ValueError):
            Stop("Nowhere", 100, nights=0)


class ParseStopsTests(unittest.TestCase):
    def test_parse(self):
        stops = parse_stops("Lima:0:2, Cusco:3400:2")
        self.assertEqual([s.name for s in stops], ["Lima", "Cusco"])
        self.assertEqual(stops[1].altitude_m, 3400)

    def test_parse_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_stops("Lima")


if __name__ == "__main__":
    unittest.main()
