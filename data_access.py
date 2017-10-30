import pandas as pd
import numpy as np
from gradeconvert import to_percentage_grade, to_letter_grade
import gbutils
import os.path as path

CACHED_GRADE_DF = None
CACHED_ASSIGNMENTS_DF = None
CACHED_CATEGORIES_DF = None
CACHED_UNUSED_CATEGORIES_DF = None

def get_subject_from_class_name(class_name):
    class_name = class_name.replace("[", "(")
    class_name = class_name.replace("]", ")")
    subject_name = class_name[:class_name.find("(")].strip()
    if not subject_name:
        raise ValueError("No subject_name parsed from {}".format(class_name))
    #homeroom = class_name[class_name.find("(") + 1:class_name.rfind(")")].strip()
    return subject_name

def get_grade_df():

    global CACHED_GRADE_DF
    if CACHED_GRADE_DF is not None:
        return CACHED_GRADE_DF

    GRADE_DATA_FILEPATH = "./source/ESCumulativeGradesExtract.csv"
    df = pd.read_csv(GRADE_DATA_FILEPATH)
    # fill NaN's with empty string
    df.fillna("", inplace=True)

    # add column with teacher full name
    df["TeacherFullname"] = df.apply(lambda row:
       "{} {}".format(row.loc["TeacherFirstName"], row.loc["TeacherLastName"]), axis=1)
    
    # add column with ClassName (SubjectName + StudentHomeroom)
    df["ClassName"] = df.apply(lambda row:
            "{} ({})".format(row.loc["SubjectName"], row.loc["StudentHomeroom"]), axis=1)

    CACHED_GRADE_DF = df
    return df

def get_assignments_df():

    global CACHED_ASSIGNMENTS_DF
    if CACHED_ASSIGNMENTS_DF is not None:
        return CACHED_ASSIGNMENTS_DF

    ASSIGNMENT_DATA_FILEPATH = "./source/CPSAllAssignmentsandGradesExtract(SlowLoad).csv"
    df = pd.read_csv(ASSIGNMENT_DATA_FILEPATH)
    # fill NaN's with empty string
    df.fillna("", inplace=True)
    # add column with teacher full name
    df["TeacherFullname"] = df.apply(lambda row:
        "{} {}".format(row.loc["TeacherFirst"], row.loc["TeacherLast"]), axis=1)
    # aggregate data on assignment level, folding individual student
    # assignments into averaged student assignments
    df = gbutils.aggregate_assignments(df)
    # add column with subject name
    df["SubjectName"] = df.apply(lambda row:
            get_subject_from_class_name(row["ClassName"]), axis=1)

    CACHED_ASSIGNMENTS_DF = df
    return df

def get_categories_df():

    global CACHED_CATEGORIES_DF
    if CACHED_CATEGORIES_DF is not None:
        return CACHED_CATEGORIES_DF

    CATEGORY_DATA_FILEPATH = "./source/CPSTeacherCategoriesandTotalPointsLogic.csv"
    df = pd.read_csv(CATEGORY_DATA_FILEPATH)
    # fill NaN's with empty string
    df.fillna("", inplace=True)

    # add column with teacher full name
    df["TeacherFullname"] = df.apply(lambda row:
            "{} {}".format(row.loc["TeacherFirstName"], row.loc["TeacherLastName"]), axis=1)

    df["SubjectName"] = df.apply(lambda row:
            get_subject_from_class_name(row["ClassName"]), axis=1)

    CACHED_CATEGORIES_DF = df
    return df

def get_unused_cats_df():

    global CACHED_UNUSED_CATEGORIES_DF
    if CACHED_UNUSED_CATEGORIES_DF is not None:
        return CACHED_UNUSED_CATEGORIES_DF

    UNUSED_CATS_FILEPATH = "./source/CPSUnusedCategoriesinTeacherGradebooks.csv"
    source_df = pd.read_csv(UNUSED_CATS_FILEPATH)
    # keep only the columns we care about
    df = pd.DataFrame()
    # rename "Column Name" -> "ColumnName" for consistency w/ other data sources
    df["ClassName"] = source_df["Class Name"]
    df["CategoryName"] = source_df["Unused Category"]
    df["CategoryWeight"] = source_df["Category Weight"]
    df["TotalClassAssignments"] = source_df["Total Class Assignments"]
    # add column with teacher full name
    df["TeacherFullname"] = source_df.apply(lambda row:
            "{} {}".format(row.loc["Teacher First"], row.loc["Teacher Last"]), axis=1)
    # add column with subject by parsing it from class
    df["SubjectName"] = source_df.apply(lambda row:
            get_subject_from_class_name(row["Class Name"]), axis=1)

    CACHED_UNUSED_CATEGORIES_DF = df
    return df
