import unittest

from rca.programmes.utils import format_study_mode


class TestFormatStudyMode(unittest.TestCase):
    def test_common_last_word(self):
        study_modes = [
            "Full-time study",
            "Part-time study",
        ]
        result = format_study_mode(study_modes)
        self.assertEqual(result, "Full-time or part-time study")

    def test_different_last_word(self):
        study_modes_list = [
            [
                "Study online",
                "Study on campus",
            ],
            [
                "Full-time",
                "Part-time",
            ],
        ]
        result1 = format_study_mode(study_modes_list[0])
        self.assertEqual(result1, "Study online or study on campus")

        result2 = format_study_mode(study_modes_list[1])
        self.assertEqual(result2, "Full-time or part-time")

    def test_custom_separator(self):
        study_modes = [
            "Option A",
            "Option B",
            "Option C",
        ]
        result = format_study_mode(study_modes, separator=" / ")
        self.assertEqual(result, "Option a / option b / option c")
