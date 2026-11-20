"""Run with: python3 -m unittest discover tests"""
import copy, glob, json, os, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from check_visual import check
import make_visual

EXAMPLES = sorted(glob.glob(os.path.join(ROOT, "examples", "*.json")))


def load(name):
    with open(os.path.join(ROOT, "examples", name), encoding="utf-8") as f:
        return json.load(f)


class CheckerTests(unittest.TestCase):
    def test_every_example_passes(self):
        self.assertEqual(len(EXAMPLES), 4)
        for path in EXAMPLES:
            with open(path, encoding="utf-8") as f:
                errors, _ = check(json.load(f))
            self.assertEqual(errors, [], path)

    def test_two_blue_elements_is_an_error(self):
        spec = load("ladder.json")
        spec["steps"][0]["matters"] = True
        errors, _ = check(spec)
        self.assertTrue(any("exactly one element" in e for e in errors))

    def test_banned_characters_are_caught(self):
        spec = load("number.json")
        spec["takeaway"] = "one thing; then another"
        errors, _ = check(spec)
        self.assertTrue(any("banned" in e for e in errors))

    def test_text_limits_are_enforced(self):
        spec = load("compare.json")
        spec["title"] = "x" * 60
        errors, _ = check(spec)
        self.assertTrue(any("limit 48" in e for e in errors))

    def test_unknown_type_is_rejected(self):
        errors, _ = check({"type": "pie"})
        self.assertTrue(errors)


class RendererTests(unittest.TestCase):
    def test_same_spec_gives_same_drawing(self):
        spec = load("boxes.json")
        a = make_visual.build_html(spec, 1500)
        b = make_visual.build_html(copy.deepcopy(spec), 1500)
        self.assertEqual(a, b)

    def test_changed_spec_changes_the_wobble(self):
        spec = load("boxes.json")
        other = copy.deepcopy(spec)
        other["subtitle"] = "a different subtitle"
        self.assertNotEqual(make_visual.build_html(spec, 1500), make_visual.build_html(other, 1500))

    def test_signature_falls_back_to_placeholder(self):
        spec = load("number.json")
        spec.pop("signature")
        self.assertIn("Your Name", make_visual.build_html(spec, 1500))


if __name__ == "__main__":
    unittest.main()
