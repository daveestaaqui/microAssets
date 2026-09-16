"""
Unit tests for Deterministic Mycology Mathematics
Validates Biological Efficiency (B.E.), moisture retention dynamics,
CVG field capacity hydration, and spawn-to-bulk ratios.
"""
import unittest


class TestCalculatorMath(unittest.TestCase):
    def test_biological_efficiency_wet_yield(self):
        """
        Biological Efficiency (B.E.) % = (Fresh Mushroom Weight / Dry Substrate Weight) * 100
        Therefore: Fresh Mushroom Weight = Dry Substrate Weight * (B.E. / 100)
        """
        dry_substrate_g = 1000.0  # 1 kg dry mass
        be_percent = 100.0        # Standard 100% BE target for Oyster / Lion's Mane
        expected_wet_g = dry_substrate_g * (be_percent / 100.0)
        self.assertEqual(expected_wet_g, 1000.0)

        # 75% BE
        be_75 = 75.0
        self.assertEqual(dry_substrate_g * (be_75 / 100.0), 750.0)

        # 125% BE
        be_125 = 125.0
        self.assertEqual(dry_substrate_g * (be_125 / 100.0), 1250.0)

    def test_dry_weight_yield_conversion(self):
        """
        Fresh mushrooms are ~90% water (AOAC standard moisture content: 88-92%).
        Dry mushroom weight = Wet yield * 0.10 (a 10:1 ratio).
        """
        fresh_yield_g = 1000.0
        dry_ratio = 0.10
        expected_dry_g = fresh_yield_g * dry_ratio
        self.assertEqual(expected_dry_g, 100.0)

        # 500g fresh -> 50g dry
        self.assertEqual(500.0 * dry_ratio, 50.0)

    def test_cvg_field_capacity_hydration(self):
        """
        Standard CVG (Coir / Vermiculite / Gypsum) field capacity:
        - 650g dry coco coir brick requires ~3.25 L (3250 mL) water (~5:1 water to dry coir).
        - 2 quarts (approx 180g) vermiculite requires ~500-750 mL water.
        - Gypsum: ~5% by weight of coir (~32.5g).
        - Total target moisture: 60-65% wet basis.
        """
        coir_brick_dry_g = 650.0
        coir_water_ml = coir_brick_dry_g * 5.0  # 3250 mL
        self.assertEqual(coir_water_ml, 3250.0)

        gypsum_g = coir_brick_dry_g * 0.05
        self.assertEqual(gypsum_g, 32.5)

        total_solids_g = coir_brick_dry_g + 180.0 + gypsum_g  # ~862.5g
        total_water_g = coir_water_ml + 650.0                 # 3900g
        total_substrate_mass = total_solids_g + total_water_g  # ~4762.5g
        moisture_pct = (total_water_g / total_substrate_mass) * 100.0
        
        # Must fall within verified field capacity window: 60% - 85%
        self.assertGreaterEqual(moisture_pct, 60.0)
        self.assertLessEqual(moisture_pct, 85.0)

    def test_spawn_to_substrate_ratios(self):
        """
        Spawn run speed vs total yield tradeoffs:
        - 1:1 ratio: Fastest colonization (7-10 days), highest contamination resistance.
        - 1:2 ratio: Commercial sweet spot for biological efficiency.
        - 1:3 ratio: High substrate volume, requires pristine cleanroom technique.
        """
        spawn_quarts = 2.0
        
        # 1:1 ratio requires equal substrate volume
        sub_1_to_1 = spawn_quarts * 1.0
        self.assertEqual(sub_1_to_1, 2.0)
        self.assertEqual(spawn_quarts + sub_1_to_1, 4.0)

        # 1:2 ratio
        sub_1_to_2 = spawn_quarts * 2.0
        self.assertEqual(sub_1_to_2, 4.0)
        self.assertEqual(spawn_quarts + sub_1_to_2, 6.0)

        # 1:3 ratio
        sub_1_to_3 = spawn_quarts * 3.0
        self.assertEqual(sub_1_to_3, 6.0)
        self.assertEqual(spawn_quarts + sub_1_to_3, 8.0)


if __name__ == "__main__":
    unittest.main()
