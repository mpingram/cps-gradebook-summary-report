import numpy as np
import math
from enums import LetterGradeCutoffs, GradeCodes

# str -> boolean
def is_numeric(value):
    try:
        # duck typing nonsense
        value_as_float = float(value)
        if math.isnan(value_as_float):
            return False
        else:
            return True
    except:
        return False

# int | float -> float
def calc_percentage(score, max_score):
    if not is_numeric(score) or not is_numeric(max_score):
        raise ValueError("Not numeric: score {}, maxscore {}".format(score, max_score))
    if score < 0:
        raise ValueError("Bad inputs: score {} out of maxscore {}".format(score, max_score))

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
        # if score is numeric but max score is not numeric,
        # raise an exception
        if not is_numeric(max_score):
            raise ValueError("max_score {} is not numeric!".format(max_score))
        else:
            return calc_percentage(float(score), float(max_score))

    # if score is not numeric and it's a string,
    # try to parse it as a letter grade.
    elif isinstance(score, str):
        if score == GradeCodes.Missing.value:
            return float(0)
        elif score == "":
            return None 
        elif (score == GradeCodes.Excused.value or
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
            raise ValueError("Did not recognize letter grade: {}".format(score))

    else:
        raise ValueError("Bad input: score {}".format(score))

# int | float | None -> str | None
def percentage_grade_to_letter_grade(percentage_grade):
    if percentage_grade is None:
        return None
    if percentage_grade > LetterGradeCutoffs.B.value:
        return "A"
    elif percentage_grade > LetterGradeCutoffs.C.value:
        return "B"
    elif percentage_grade > LetterGradeCutoffs.D.value:
        return "C"
    elif percentage_grade > LetterGradeCutoffs.F.value:
        return "D"
    elif percentage_grade >= LetterGradeCutoffs.Zero.value:
        return "F"
    else:
        raise ValueError("Bad percentage grade: {}".format(percentage_grade))

# string | float | int -> ("A","B","C","D","F") | None
def to_letter_grade(score, max_score):

    if is_numeric(score):
        if is_numeric(max_score):
            try:
                percentage_grade = to_percentage_grade(float(score), float(max_score))
                return percentage_grade_to_letter_grade(percentage_grade)
            except ValueError:
                raise ValueError("Bad inputs: score {}, max_score {}".format(score, max_score))
        else:
            raise ValueError("max_score {} is not numeric!".format(max_score))

    elif isinstance(score, str):
        if score == GradeCodes.Missing.value:
            return "F"
        elif score == "":
            return None 
        elif (score == GradeCodes.Excused.value or
              score == GradeCodes.Incomplete.value):
            return None
        elif score.upper() in ("A", "B", "C", "D", "F"):
            return score.upper()
        else:
            raise ValueError("Cannot parse as letter grade or code: {}".format(score))

    else:
        raise ValueError("Bad input: score {}, max_score {}".format(score, max_score))
