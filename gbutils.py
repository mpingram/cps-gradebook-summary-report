from os import path
from hashlib import md5
import pandas as pd
from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML

from utils import to_letter_grade, to_percentage_grade
from enums import LetterGradeCutoffs, GradeCodes, Cols

def get_grade_df(filepath):

    def get_subject_name(class_name):
        return class_name[:class_name.rfind("(")].strip()
    def get_homeroom(class_name):
        return class_name[class_name.rfind("(") + 1: class_name.rfind(")")]

    grade_df = pd.read_csv(filepath)

    # add column with teacher full name
    grade_df[Cols.TeacherFullname.value] = grade_df.apply(lambda row:
       "{} {}".format(row.loc[Cols.TeacherFirstname.value], row.loc[Cols.TeacherLastname.value]), axis=1)
    # add column with subject name for each class
    grade_df[Cols.SubjectName.value] = grade_df.apply(lambda row:
        get_subject_name(row[Cols.ClassName.value]), axis=1)
    grade_df[Cols.Homeroom.value] = grade_df.apply(lambda row:
        get_homeroom(row[Cols.ClassName.value]), axis=1)

    return grade_df

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

def get_lettergrade_breakdown_diagram_urls(grade_df_subset, folder_path):
    gdf = grade_df_subset.groupby(Cols.ClassName.value)
    diagram_urls = []
    for classname, group in gdf:
        subj_grade_breakdown = get_lettergrade_breakdown(group)
        pie_chart = subj_grade_breakdown.plot.pie()
        classname = classname
        diagram_url = path.join(folder_path, "{}.png".format(classname))
        try: 
            pie_chart.get_figure().savefig(diagram_url)
            diagram_urls.append(diagram_url)
        except IOError as ioErr:
            print("Cannot save figure at {}".format(diagram_url))
            raise ioErr
    return diagram_urls

def calculate_negative_impact(score, possible_score, category_weight):
    percent_score = to_percentage_score(score, possible_score)
    impact = (100 - percent_score) * category_weight
    return impact

def aggregate_assignments(grade_df_subset):
    # get average percentage grade for each assignment
    gdf = grade_df_subset.groupby([Cols.AssignmentName.value, 
                                   Cols.SubjectName.value, 
                                   Cols.GradeLevel.value])
    def average_assignments(group):
        assignment_grades = [to_percentage_grade(row[Cols.Score.value], row[Cols.ScorePossible.value])
                                for row in group]
        return np.mean(assignment_grades)

    return gdf.apply(lambda group: pd.DataFrame({
            Cols.Score.value: average_assignments(group),
            Cols.ScorePossible.value: float(100),
            Cols.SubjectName.value: group[Cols.SubjectName.value],
            Cols.AssignmentName.value: group[Cols.AssignmentName.value],
            Cols.CategoryName.value: group[Cols.CategoryName.value],
            "NumAssignments": group.size,
            "NumMissingOrZero": group[group[Cols.Score.value] == GradeCodes.Missing
                                        or group[Cols.Score.value] == "0" 
                                        or group[Cols.Score.value] == 0].size
        }))


def filter_by_teacher(grade_df_subset, teacher_fullname):
    return grade_df_subset[lambda row: row[Cols.TeacherFullname.value] == teacher_fullname]


