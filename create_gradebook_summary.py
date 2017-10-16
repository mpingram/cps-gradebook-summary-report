from enums import LetterGradeCutoffs
import gbutils
from gradeconvert import to_percentage_grade, to_letter_grade
import pandas as pd
import os.path as path
import matplotlib.pyplot as plt

def create_lettergrade_breakdown_diagram(**kwargs):
    """Returns URL of a diagram of letter grade distribution for given grade data.
    
    Keyword args:
    grades: float[] -- list of percentage grades as floats.
    output_url: str -- valid url to save diagram to. 
    label: str? -- (optional) label for diagram

    Returns:
    (success: bool, err: Error | None)
    """
    grades = kwargs.get("grades", None)
    output_url = kwargs.get("output_url", None)
    diagram_label = kwargs.get("label", None)

    if grades is None:
        raise ValueError("Missing required keyword argument grades")
    if output_url is None:
        raise ValueError("Missing required keyword argument output_url")
    
    def create_pie_chart_image(letter_grades, output_url):
        """Creates image at URL. Returns success(bool), err(Error | None)
        
        Positional args:
        letter_grades: str[] of type ("A" | "B" | "C" | "D" | "F").
        output_url: str of valid URL to save image to.

        Returns:
        (success: bool, err: Error | None)
        """
        # count number of students with each grade
        letters = ["A", "B", "C", "D", "F"]
        letter_grade_counts = {letter: letter_grades.count(letter) for letter in letters 
                if letter_grades.count(letter) != 0}
        # create pie chart sizes and label them with corresponding letter grade
        sizes = []
        labels = []
        for letter, count in letter_grade_counts.items():
            labels.append(letter)
            sizes.append(count)
        # create pie chart
        fig1, ax1 = plt.subplots()
        pie_chart = ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
        if diagram_label is not None:
            plt.title(diagram_label)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        try:
            plt.savefig(output_url)
            return (True, None)
        except IOError as ioErr:
            return (False, ioErr)
        except BaseException as e:
            return (False, e)
        finally:
            # grungy necessity due to matplotlib: clear the global
            # figure that's been created due to earlier call to plt.
            plt.clf()

    letter_grades = [to_letter_grade(grade, 100) for grade in grades]
    letter_grades = [grade for grade in letter_grades if grade is not None]

    return create_pie_chart_image(letter_grades, output_url)

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

def get_assignments_df(filepath):
    ASSIGNMENT_DATA_FILEPATH = "./source/CPSAllAssignmentsandGradesExtract(SlowLoad).csv"
    df = pd.read_csv(ASSIGNMENT_DATA_FILEPATH)
    # fill NaN's with empty string
    df.fillna("", inplace=True)

    # add column with teacher full name
    df["TeacherFullname"] = df.apply(lambda row:
       "{} {}".format(row.loc["TeacherFirst"], row.loc["TeacherLast"]), axis=1)
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

def create_gradebook_summary(teacher_fullname):

    IMAGE_DIR = "./images/"
    template_vars = {}

    # I. get grade breakdown pie charts
    # --
    # get grade data df
    grade_df = get_grade_df()
    # filter grade_df by teacher
    grade_df = grade_df[grade_df["TeacherFullname"] == teacher_fullname]
    # group filtered df by class (Subject + Homeroom) 
    grade_gdf_by_class = grade_df.groupby("ClassName")
    # create images
    diagram_urls = []
    for class_name, group in grade_gdf_by_class:
        diagram_url = path.join(IMAGE_DIR, "{}-{}.png".format(class_name, teacher_fullname))
        success, err = create_lettergrade_breakdown_diagram(grades=group["QuarterAvg"],
                                                         output_url=diagram_url,
                                                         label=class_name)
        if success:
            diagram_urls.append(diagram_url)
        else:
            print(err)

    template_vars["diagram_urls"] = diagram_urls 

    # II. get # of failing students, grouped by subject and homeroom
    # --
    # get grade data df
    grade_df = get_grade_df()
    # filter grade_df by teacher
    grade_df = grade_df[grade_df["TeacherFullname"] == teacher_fullname]
    # filter grade_df again by students with scores of F
    grade_df = grade_df[grade_df.apply(lambda row: to_letter_grade(row["QuarterAvg"], 100) == "F", axis=1)]
    # group filtered df by class (Subject + Homeroom) 
    grade_gdf_by_class = grade_df.groupby("ClassName")
    failing_students = grade_gdf_by_class
    template_vars["failing_students"] = failing_students

    # III. Get list of unused categories by class.
    # --
    # get assignments and categories in dataframes
    unused_cats_df = get_unused_cats_df()
    # filter unused categories by teacher
    unused_cats_df = unused_cats_df[unused_cats_df["TeacherFullname"] == teacher_fullname]
    # group unused cats by class
    unused_cats_df_by_class = unused_cats_df.groupby("ClassName")
    template_vars["unused_categories"] = unused_cats_df_by_class

    # IV.

#    failing_students_by_subject = df.groupby(Cols.SubjectName.value, 
#                                             Cols.Homeroom.value).filter(lambda row:
#            to_percentage_grade(row[Cols.Score.value], row[Cols.ScorePossible.value]) <= LetterGradeCutoffs.F)
#
#    # III. get list of unused categories, grouped by subject
#        # FIXME: I think we need addl data source for this 
#
#    # IV. get top 5 assignments with highest negative impact,
#    #       grouped by subject
#    assignments_df = aggregate_by_assignments(df)
#    assignments_df["Negative Impact"] = assignments_df.apply(lambda row: 
#                                                    gbutils.calculate_negative_impact(
#                                                        row[Cols.Score.value], 
#                                                        row[Cols.ScorePossible.value], 
#                                                        row[Cols.CategoryWeight.value]), axis=1)
#    sorted_assignments_df = assignments_df.sort_values("Negative Impact")
#    negative_impact_assignments = sorted_assignments_df.groupby(Cols.SubjectName.value).top(5)
#
#    # V. get category table, by subject, showing name, weight, # assignments,
#    #       and avg score
#    assignments_df_filtered = assignments_df[[
#        Cols.Score.value,
#        Cols.ScorePossible.value,
#        Cols.SubjectName.value,
#        Cols.CategoryName.value, 
#        Cols.CategoryWeight.value, 
#        "NumAssignments",
#        "AverageScore",
#    ]]
#    subject_categories_gdf = assignments_df_filtered.groupby(Cols.SubjectName.value)
#    subject_categories_gdf.apply(lambda group: 
#            group.groupby(Cols.CategoryName.value).apply(gbutils.aggregate_by_assignments))
#
#    # VI. get list of missing/0 assignments, desc sorted
#    sorted_assignments_df = assignments_df.sort_values("NumMissingOrZero")
#    missing_zero_assignments = sorted_assignments_df.groupby(Cols.SubjectName.value).top(5)
#
#    # VII(?). get list of excepted/blank/inc assignments, desc sorted

if __name__ == "__main__":
    # DEBUG  
    DEBUG_NAME = "Karen Baggot"
    create_gradebook_summary(DEBUG_NAME)
