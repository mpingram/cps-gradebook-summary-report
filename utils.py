import numpy as np
from enums import LetterGradeCutoffs, GradeCodes

# str -> boolean
def is_numeric(value):
    try:
        float(value)
        return True
    except:
        return False

# int | float -> float
def calc_percentage(score, max_score):
    percentage = (float(score) / float(max_score)) * 100
    if percentage > 100:
        return float(100)
    elif percentage < 0:
        return float(0)
    else:
        return percentage

# string | float | int -> float | None
def to_percentage_grade(score, max_score):
    if is_numeric(score):
        # if max score is blank or not numeric, return None rather than try to guess
        if not max_score or not is_numeric(max_score):
            raise ValueError("max_score {} is not numeric!".format(max_score))
            return None
        else:
            return calc_percentage(float(score), float(max_score))

    elif isinstance(score, str):
        if score == GradeCodes.Missing.value:
            return float(0)
        elif (score == GradeCodes.Excepted.value or
              score == GradeCodes.Incomplete.value):
            return None
        elif score.upper() == "A":
            return np.mean((LetterGradeCutoffs.A.value, LetterGradeCutoffs.B.value))
        elif score.upper() == "B":
            return np.mean((LetterGradeCutoffs.B.value, LetterGradeCutoffs.C.value))
        elif score.upper() == "C":
            return np.mean((LetterGradeCutoffs.C.value, LetterGradeCutoffs.D.value))
        elif score.upper() == "D":
            return np.mean((LetterGradeCutoffs.D.value, LetterGradeCutoffs.F.value))
        elif score.upper() == "F":
            return np.mean((LetterGradeCutoffs.F.value, LetterGradeCutoffs.Zero.value))
        else:
            return None

# int | float | None -> str | None
def percentage_grade_to_letter_grade(percentage_grade):
    if percentage_grade is None:
        return None
    if percentage_grade >= LetterGradeCutoffs.A.value:
        return "A"
    elif percentage_grade >= LetterGradeCutoffs.B.value:
        return "B"
    elif percentage_grade >= LetterGradeCutoffs.C.value:
        return "C"
    elif percentage_grade >= LetterGradeCutoffs.D.value:
        return "D"
    else:
        return "F"

# string | float | int -> ("A","B","C","D","F") | None
def to_letter_grade(score, max_score):

    if is_numeric(score):
        if is_numeric(max_score):
            percentage_grade = to_percentage_grade(float(score), float(max_score))
            return percentage_grade_to_letter_grade(percentage_grade)
        else:
            # if max_score is not numeric, skip this grade rather
            # than trying to guess
            raise ValueError("max_score {} is not numeric!".format(max_score))
            return None
    elif isinstance(score, str):
        if score == GradeCodes.Missing.value:
            return "F"
        elif (score == GradeCodes.Excepted.value or
              score == GradeCodes.Incomplete.value):
            return None
        elif score.upper() in ("A", "B", "C", "D", "F"):
            return score.upper()
        else:
            return None
