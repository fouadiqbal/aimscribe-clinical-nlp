import unittest
from src.applicability import evaluate_rule, check_card
from src.common import load_cards


class ApplicabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = {c["card_id"]:c for c in load_cards()}

    def test_unknown_is_not_negative(self):
        result = check_card(self.cards["CHI-MED-02"], {"duration_days":12,"dengue_ns1_negative":True,"afebrile_hours":50})
        self.assertEqual(result["status"],"needs_info")
        self.assertIn("warning_signs",result["missing_fields"])

    def test_one_source_prerequisite_changes_status(self):
        patient = {"duration_days":12,"dengue_ns1_negative":True,"afebrile_hours":50,"warning_signs":False}
        self.assertEqual(check_card(self.cards["CHI-MED-02"],patient)["status"],"applicable")
        patient["dengue_ns1_negative"] = False
        self.assertEqual(check_card(self.cards["CHI-MED-02"],patient)["status"],"excluded")

    def test_severe_overrides_some_dehydration(self):
        patient = {"age_years":25,"weight_kg":60,"lethargic_or_unconscious":True,
                   "weak_or_absent_pulse":False,"respiratory_distress":False,
                   "thirsty":True,"sunken_eyes":True,"restless":True}
        self.assertEqual(check_card(self.cards["CHO-MED-01"],patient)["status"],"applicable")
        self.assertEqual(check_card(self.cards["CHO-MED-03"],patient)["status"],"excluded")

    def test_age_boundary(self):
        patient = {"age_years":1,"weight_kg":10,"lethargic_or_unconscious":True}
        self.assertEqual(check_card(self.cards["CHO-MED-01"],patient)["status"],"applicable")
        self.assertEqual(check_card(self.cards["CHO-MED-02"],patient)["status"],"excluded")

    def test_ten_days_still_excluded(self):
        patient = {"duration_days":10,"dengue_ns1_negative":True,"afebrile_hours":50,"warning_signs":False}
        self.assertEqual(check_card(self.cards["CHI-MED-02"],patient)["status"],"excluded")

    def test_false_string_is_unknown(self):
        value,_ = evaluate_rule({"field":"pregnant","op":"eq","value":False},{"pregnant":"false"})
        self.assertIsNone(value)


if __name__ == "__main__":
    unittest.main()
