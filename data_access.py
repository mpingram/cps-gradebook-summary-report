import pandas as pd
from gradeconvert import to_percentage_grade, to_letter_grade
import gbutils
import os.path as path

def get_grade_df():
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

    return df

def get_assignments_df():
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
    return df

def get_categories_df():
    CATEGORY_DATA_FILEPATH = "./source/CPSTeacherCategoriesandTotalPointsLogic.csv"
    df = pd.read_csv(CATEGORY_DATA_FILEPATH)
    # fill NaN's with empty string
    df.fillna("", inplace=True)

    # add column with teacher full name
    df["TeacherFullname"] = df.apply(lambda row:
            "{} {}".format(row.loc["TeacherFirstName"], row.loc["TeacherLastName"]), axis=1)
    return df

def get_unused_cats_df():
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
    return df
