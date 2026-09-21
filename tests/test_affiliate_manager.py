"""
Unit tests for SporlyWorks Affiliate Configuration and Routing
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "affiliate_config.json"


class TestAffiliateManager(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CONFIG_PATH.is_file(), "affiliate_config.json must exist")
        self.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_config_structure(self):
        """Assert core schema fields exist."""
        self.assertIn("version", self.config)
        self.assertIn("partners", self.config)
        self.assertIn("compliance", self.config)

    def test_required_partners_present(self):
        """Verify all primary partners exist in config."""
        expected_partners = {"myyco", "magicbag", "realmushrooms", "nootropicsdepot", "seed", "freshcap"}
        configured = set(self.config["partners"].keys())
        for p in expected_partners:
            self.assertIn(p, configured, f"Partner '{p}' missing from config")

    def test_partner_base_urls(self):
        """Verify all partners have valid https base and fallback URLs."""
        for name, partner in self.config["partners"].items():
            base_url = partner.get("base_url", "")
            fallback_url = partner.get("fallback_url", "")
            self.assertTrue(base_url.startswith("https://"), f"{name} base_url must start with https://")
            self.assertTrue(fallback_url.startswith("https://"), f"{name} fallback_url must start with https://")

    def test_build_url_logic(self):
        """Verify affiliate URL generation without synthetic placeholders."""
        import sys
        marketing_path = str(ROOT / "_marketing")
        if marketing_path not in sys.path:
            sys.path.insert(0, marketing_path)
        from affiliate_config import build_affiliate_url

        # Test active partner MYYCO (verified UAP ID 497)
        myyco_url = build_affiliate_url("myyco", "https://myyco.com")
        self.assertIn("ref=SporlyWorks", myyco_url)

        # Test active partner Magic Bag (verified UAP ID 304)
        mb_url = build_affiliate_url("magicbag", "https://www.magicbag.co")
        self.assertIn("ref=Sporlyworks", mb_url)

        # Test active partner North Spore (verified Awin Publisher ID 3016315)
        ns_url = build_affiliate_url("north_spore", "https://northspore.com")
        self.assertIn("awinaffid=3016315", ns_url)

        # Test unmonetized fallback partner routing cleanly to base_url without fake query params
        rm_url = build_affiliate_url("realmushrooms", "https://shop.realmushrooms.com")
        self.assertEqual(rm_url, "https://shop.realmushrooms.com")
        self.assertNotIn("ref=", rm_url)

        nd_url = build_affiliate_url("nootropicsdepot", "https://nootropicsdepot.com")
        self.assertEqual(nd_url, "https://nootropicsdepot.com")
        self.assertNotIn("YOUR_", nd_url)
        self.assertNotIn("INSERT", nd_url)

    def test_compliance_disclosures(self):
        """Verify regulatory and compliance disclosures are present."""
        compliance = self.config.get("compliance", {})
        self.assertIn("ftc_disclosure", compliance)
        self.assertIn("fda_disclaimer", compliance)
        self.assertIn("microscopy_disclaimer", compliance)
        self.assertTrue(len(compliance["ftc_disclosure"]) > 20)


if __name__ == "__main__":
    unittest.main()
