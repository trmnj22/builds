"""Fast checks for the parser and the descriptor rule. No Chrome needed: python3 -m unittest discover tests"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import build_cv  # noqa: E402

SAMPLE = """---
note: front matter is dropped
---
# Sam Lee

Perth · sam@example.com

## Experience

### Northwind Retail, Perth | a national homewares retailer
**Store Systems Lead** · 2019 – present
- Ran the **store systems** team.
<!-- page break -->
- Second bullet after a page break.

---
held-back notes that must not appear
"""

RULE = [{"org": "Northwind Retail", "phrase": "a national homewares retailer"}]


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.doc = build_cv.parse(SAMPLE)

    def test_name_and_contact(self):
        self.assertEqual(self.doc["name"], "Sam Lee")
        self.assertEqual(self.doc["contact"], "Perth · sam@example.com")

    def test_entry_row_and_bullets(self):
        kind, entry = self.doc["sections"][0]["items"][0]
        self.assertEqual(kind, "entry")
        self.assertEqual(entry["org"], "Northwind Retail, Perth")
        self.assertEqual(entry["desc"], "a national homewares retailer")
        kinds = [it[0] for it in entry["items"]]
        self.assertEqual(kinds, ["row", "bullet", "pagebreak", "bullet"])
        self.assertEqual(entry["items"][0][2], "2019 – present")

    def test_held_back_notes_dropped(self):
        html = build_cv.build_html(self.doc, "A4", 10.0, 11.0)
        self.assertNotIn("held-back", html)
        self.assertIn("<b>store systems</b>", html)


class DescriptorTests(unittest.TestCase):
    def test_passes_with_phrase(self):
        self.assertEqual(build_cv.descriptor_problems(SAMPLE, build_cv.parse(SAMPLE), RULE), [])

    def test_fails_without_phrase(self):
        md = SAMPLE.replace(" | a national homewares retailer", "")
        self.assertTrue(build_cv.descriptor_problems(md, build_cv.parse(md), RULE))

    def test_longer_name_is_not_a_match(self):
        self.assertFalse(build_cv.names_org("Northwind Retailers Group", "Northwind Retail"))
        self.assertTrue(build_cv.names_org("**Northwind  Retail**, Perth", "Northwind Retail"))


class SpacingTests(unittest.TestCase):
    def test_spread_ends(self):
        self.assertEqual(build_cv.spread(0), (build_cv.LINE_HEIGHT[0], build_cv.GAP[0]))
        self.assertEqual(build_cv.spread(1), (build_cv.LINE_HEIGHT[1], build_cv.GAP[1]))

    def test_pct_rounds_down(self):
        self.assertEqual(build_cv.pct(0.948), "94%")


if __name__ == "__main__":
    unittest.main()
