from os import path
from hashlib import md5
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
# from weasyprint import HTML

from gradeconvert import to_letter_grade, to_percentage_grade
from enums import LetterGradeCutoffs, GradeCodes, Cols


def get_lettergrade_breakdown(grade_df_subset):
    def count_of_grades(letter_grade):
        def matches_letter_grade(row):
            score = row[Cols.Score.value]
            score_possible = row[Cols.ScorePossible.value]
            row_letter_grade = to_letter_grade(score, score_possible)
            return row_letter_grade == letter_grade
        return grade_df_subset[grade_df_subset.apply(matches_letter_grade, axis=1)].size
    
    return pd.Series((
        count_of_grades("A"),
        count_of_grades("B"),
        count_of_grades("C"),
        count_of_grades("D"),
        count_of_grades("F"),
    ), index=("A", "B", "C", "D", "F"))

def calculate_negative_impact(score, possible_score, category_weight, num_assignments):
    if score is None:
        return 0 
    elif score < 0:
        raise ValueError("Score {} is negative!".format(score))
    elif score > possible_score:
        raise ValueError("Score {} greater than possible_score {}".format(score, possible_score))
    elif category_weight < 0 or category_weight > 100:
        raise ValueError("Category weight greater than 100 percent!")

    percent_score = to_percentage_grade(score, possible_score)
    impact = (100 - percent_score) * (category_weight / 100) / float(num_assignments)
    return impact

def count_zeroes(df):
    s = df[Cols.Score.value]
    s = s[ (s == "0") | (s == 0) ]
    return len(s)

def count_blanks(df):
    s = df[Cols.Score.value]
    s = s[ (s == None) | (s == "") ]
    return len(s)

def count_grade_code(df, grade_code):
    s = df[Cols.Score.value]
    s = s[ (s == grade_code.value) ]
    return len(s) 

def aggregate_assignments(grade_df_subset):
    def average_assignments(df):
        assignment_grades = [to_percentage_grade(row[Cols.Score.value], row[Cols.ScorePossible.value])
                                for _,row in df.iterrows()]
        # remove None values
        assignment_grades = [a for a in assignment_grades if a is not None]
        if len(assignment_grades) > 0:
            avg = np.mean(assignment_grades)
            if np.isnan(avg):
                print(assignment_grades)
            return avg
        # if all assignments were None, return None.
        else:
            return None 


    def create_assignment_row(group):

        # This is either a float percentage score or None.
        # If None, it means that every student's score
        # was marked for 'ignoring' -- ie, either with
        # GradeCodes.Excused or empty ("")
        group_average_percentage_or_nan = average_assignments(group)
        assignment_row = {
                Cols.Score.value: group_average_percentage_or_nan,
                Cols.ScorePossible.value: float(100),
                "NumAssignments": len(group.index),
                "NumMissing": count_grade_code(group, GradeCodes.Incomplete),
                "NumIncomplete": count_grade_code(group, GradeCodes.Incomplete),
                "NumExcused": count_grade_code(group ,GradeCodes.Excused),
                "NumZero": count_zeroes(group),
                "NumBlank": count_blanks(group)
            }

        # add the rest of the columns to assignment_row by taking
        # the first element from group. We expect all of these
        # values to best case be the same, worst case to not matter
        # if slightly different.
        for col in Cols:
            if col.value not in (Cols.Score.value,
                    Cols.ScorePossible.value,
                    Cols.StudentId.value,
                    Cols.StudentLastname.value,
                    Cols.StudentFirstname.value):
                assignment_row[col.value] = group.iloc[0][col.value]

        return assignment_row

    # group assignments by AssignmentName, ClassName, and AssignedDate
    # to obtain individual assignments, even in cases where multiple
    # assignments in same class have same name (!)
    gdf = grade_df_subset.groupby([Cols.AssignmentName.value, 
                                   Cols.ClassName.value,
                                   Cols.AssignedDate.value])

    aggregated_df = pd.DataFrame()
    for name, group in gdf:
        row = create_assignment_row(group)
        aggregated_df = aggregated_df.append(row, ignore_index=True)
        
    return aggregated_df


def filter_by_teacher(grade_df_subset, teacher_fullname):
    return grade_df_subset[lambda row: row[Cols.TeacherFullname.value] == teacher_fullname]


