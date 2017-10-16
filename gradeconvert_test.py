import unittest
import numpy as np
from random import random, randint, choices, choice
import math
import string
from enums import LetterGradeCutoffs, GradeCodes

from gradeconvert import (
        is_numeric,
        calc_percentage,
        to_percentage_grade,
        to_letter_grade,
        percentage_grade_to_letter_grade
   ) 

class ToLetterGrade(unittest.TestCase):
    
    A = LetterGradeCutoffs.A.value
    B = LetterGradeCutoffs.B.value
    C = LetterGradeCutoffs.C.value
    D = LetterGradeCutoffs.D.value
    F = LetterGradeCutoffs.F.value
    Zero = LetterGradeCutoffs.Zero.value


    grade_codes_meaning_zero = [
            GradeCodes.Missing.value
        ]

    grade_codes_meaning_ignore = [
            GradeCodes.Excused.value,
            GradeCodes.Incomplete.value
        ]

    lettergrades = ["A", "B", "C", "D", "F"]

    def test__should_not_change_letter_grade(self):
        score = choice(self.lettergrades)
        max_score = ""
        self.assertEqual(to_letter_grade(score, max_score), score)

    def test__should_throw_on_bad_string_inputs(self):
        score = "wkajfwe"
        max_score = ""
        self.assertRaises(ValueError, lambda: to_letter_grade(score, max_score))

    def test__should_accurately_interpret_grade_codes(self):
        max_score = ""
        for code in self.grade_codes_meaning_zero:
            self.assertEqual(to_letter_grade(code, max_score), "F")

        for code in self.grade_codes_meaning_ignore:
            self.assertIs(to_letter_grade(code, max_score), None)

    def test__should_accurately_interpret_blanks(self):
        score = ""
        max_score = 20
        self.assertEqual(to_letter_grade(score, max_score), None)

    def test__should_accurately_compute_letter_grades(self):

        score = 85
        max_score = 100
        self.assertEqual(to_letter_grade(score, max_score), "B")

        score = 75
        max_score = 100
        self.assertEqual(to_letter_grade(score, max_score), "C")

        score = 65
        max_score = 100
        self.assertEqual(to_letter_grade(score, max_score), "D")

        score = 2
        max_score = 2
        self.assertEqual(to_letter_grade(score, max_score), "A")

        score = 2
        max_score = 3
        self.assertEqual(to_letter_grade(score, max_score), "D")

        score = 1
        max_score = 20
        self.assertEqual(to_letter_grade(score, max_score), "F")

        score = LetterGradeCutoffs.B.value
        max_score = 100
        self.assertEqual(to_letter_grade(score, max_score), "B")

        score = LetterGradeCutoffs.A.value
        max_score = 100
        self.assertEqual(to_letter_grade(score, max_score), "A")

        score = LetterGradeCutoffs.F.value
        max_score = 100
        self.assertEqual(to_letter_grade(score, max_score), "F")


    def test__should_handle_higher_scores_than_max_score(self):
        score = 86
        max_score = 85
        self.assertEqual(to_letter_grade(score, max_score), "A")

        score = 9001 
        max_score = 100
        self.assertEqual(to_letter_grade(score, max_score), "A")

    def test__should_throw_on_negative_number_inputs(self):
        score = -10
        max_score = 100
        self.assertRaises(ValueError, lambda: to_letter_grade(score, max_score))

    def test__should_throw_on_None_inputs(self):
        score = None
        max_score = 100
        self.assertRaises(ValueError, lambda: to_letter_grade(score, max_score))


class ToPercentageGrade(unittest.TestCase):

    A = LetterGradeCutoffs.A.value
    B = LetterGradeCutoffs.B.value
    C = LetterGradeCutoffs.C.value
    D = LetterGradeCutoffs.D.value
    F = LetterGradeCutoffs.F.value
    Zero = LetterGradeCutoffs.Zero.value

    grade_codes_meaning_zero = [
            GradeCodes.Missing.value
        ]

    grade_codes_meaning_ignore = [
            GradeCodes.Excused.value,
            GradeCodes.Incomplete.value
        ]

    def test__should_convert_scores_and_max_to_percentages(self):
        score = 0.0
        max_score = 20.0
        self.assertEqual(0.0, to_percentage_grade(score, max_score))

        score = 10
        max_score = 100
        self.assertEqual(10.0, to_percentage_grade(score, max_score))
        
        score = 49
        max_score = 49
        self.assertEqual(100.0, to_percentage_grade(score,  max_score))

    def test__should_convert_special_grade_codes(self):
        max_score = 20
        for code in self.grade_codes_meaning_zero:
            self.assertEqual(to_percentage_grade(code, max_score), 0.0)

        for code in self.grade_codes_meaning_ignore:
            self.assertIs(to_percentage_grade(code, max_score), None)

    def test__should_convert_empty_string(self):
        score = ""
        max_score = 20
        self.assertEqual(to_percentage_grade(score, max_score), None)

    def test__should_convert_letter_grades(self):
        def is_within(lower, upper, value, lower_inclusive=False):
            if lower_inclusive:
                return value >= lower and value <= upper
            else:
                return value > lower and value <= upper

        score = "A"
        max_score = ""
        percentage_grade = to_percentage_grade(score, max_score)
        self.assertTrue(is_within(self.B, self.A, percentage_grade))
        self.assertFalse(is_within(self.Zero, self.B, percentage_grade, lower_inclusive=True))

        score = "B"
        max_score = ""
        percentage_grade = to_percentage_grade(score, max_score)
        self.assertTrue(is_within(self.C, self.B, percentage_grade))
        self.assertFalse(is_within(self.Zero, self.C, percentage_grade, lower_inclusive=True))

        score = "C"
        max_score = ""
        percentage_grade = to_percentage_grade(score, max_score)
        self.assertTrue(is_within(self.D, self.C, percentage_grade))
        self.assertFalse(is_within(self.Zero, self.D, percentage_grade, lower_inclusive=True))

        score = "D"
        max_score = ""
        percentage_grade = to_percentage_grade(score, max_score)
        self.assertTrue(is_within(self.F, self.D, percentage_grade))
        self.assertFalse(is_within(self.Zero, self.F, percentage_grade, lower_inclusive=True))

        score = "F"
        max_score = ""
        percentage_grade = to_percentage_grade(score, max_score)
        self.assertTrue(is_within(self.Zero, self.F, percentage_grade, lower_inclusive=True))

    def test__should_throw_on_unparseable_grades(self):
        score = 10
        max_score = "weh"
        self.assertRaises(ValueError, lambda: to_percentage_grade(score, max_score))

        score = "1o12" 
        max_score = 100
        self.assertRaises(ValueError, lambda: to_percentage_grade(score, max_score))

        score = None
        max_score = None
        self.assertRaises(ValueError, lambda: to_percentage_grade(score, max_score))
        
        score = math.nan
        max_score = 100
        self.assertRaises(ValueError, lambda: to_percentage_grade(score, max_score))


class CalcPercentage(unittest.TestCase):

    def test__should_throw_on_non_numeric_inputs(self):
        self.assertRaises(ValueError, lambda: calc_percentage(None, 100))

    def test__should_throw_on_negative_inputs(self):
        self.assertRaises(ValueError, lambda: calc_percentage(-10, -10))

    def test__should_return_accurate_percentages(self):
        expected = 20.0
        self.assertEqual(expected, calc_percentage(4,20))

    def test__should_return_accurate_percentages_random(self):
        def trial():
            num_one = random() * 100
            num_two = random() * 100
            bigger = max((num_one, num_two))
            smaller = min((num_one, num_two))
            expected = smaller/bigger * 100
            if expected == calc_percentage(smaller, bigger):
                return True
            else:
                return False

        success = True
        for _ in range(0, 20):
            if not trial():
                success = False
        self.assertTrue(success)

    def test__should_handle_higher_score_than_max_score(self):
        score = 86
        max_score = 85
        self.assertEqual(calc_percentage(score, max_score), 100.0)

        score = 1000000000000
        max_score = 2
        self.assertEqual(calc_percentage(score, max_score), 100.0)


class IsNumeric(unittest.TestCase):

    def test__should_return_true_for_floats(self):
        random_float = random() * (random() * 100)
        self.assertTrue(is_numeric(random_float))

    def test__should_return_true_for_ints(self):
        random_int = randint(-1000, 1000)
        self.assertTrue(is_numeric(random_int))

    def test__should_return_true_for_convertible_strings(self):
        convertible_string = "86.229"
        self.assertTrue(is_numeric(convertible_string))

    def test__should_return_false_for_random_single_letter_strings(self):
        single_letter_string = "A"
        self.assertFalse(is_numeric(single_letter_string))

    def test__should_return_false_for_random_strings(self):
        random_string = ''.join(choices(string.ascii_uppercase + string.digits, k=5))
        self.assertFalse(is_numeric(random_string))

    def test__should_return_false_for_None(self):
        self.assertFalse(is_numeric(None))

    def test__should_return_false_for_NaN(self):
        self.assertFalse(is_numeric(math.nan))

    def test__should_return_fals_for_empty_string(self):
        self.assertFalse(is_numeric(""))


if __name__ == "__main__":
    unittest.main()
