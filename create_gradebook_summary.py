from enums import LetterGradeCutoffs, Cols, GradeCodes
from gbutils import calculate_negative_impact
from gradeconvert import to_letter_grade
import pandas as pd
import numpy as np
import os.path as path
from data_access import get_grade_df, get_assignments_df, get_unused_cats_df
from plots import create_lettergrade_breakdown_diagram

import jinja2
import weasyprint

def render_grade_breakdown_diagrams(grade_df):
    """df -> html"""

    IMAGE_DIR = "./images/"
    # group filtered df by subject
    gdf = grade_df.groupby("SubjectName")
    teacher_fullname = grade_df.iloc[1]["TeacherFullname"]
    # create images
    diagram_urls = []
    for subject_name, group in gdf:
        diagram_url = path.join(IMAGE_DIR, "{} {}.png".format(subject_name, teacher_fullname))
        diagram_url = diagram_url.replace(" ", "_")
        success, err = create_lettergrade_breakdown_diagram(grades=group["QuarterAvg"],
                                                         output_url=diagram_url,
                                                         label=subject_name)
        if success:
            diagram_urls.append(diagram_url)
        else:
            print(err)


    def create_html(diagram_urls):
        html = """<div width="100%">"""
        for url in diagram_urls:
            html += """<img style="width: 200px;" src="{0}"/>""".format(url)
        html += """</div>"""
        return html

    return create_html(diagram_urls)

def render_failing_students_table(grade_df):
    """df -> html"""
    def get_failing_students_by_class(df):
        """df -> grouped df"""
        # filter df by students with scores of F
        df = df[df.apply(lambda row: to_letter_grade(row["QuarterAvg"], 100) == "F", axis=1)]
        # group by className
        df = df.sort_values("ClassName")
        return df

    failing_students = get_failing_students_by_class(grade_df)
    # keep only the columns we want to render
    failing_students = failing_students[[
        "ClassName",
        "StudentFirstName",
        "StudentLastName",
        "StudentID",
        "QuarterAvg"
    ]]
    failing_students = failing_students.set_index("ClassName")
    return failing_students.to_html()

def render_unused_categories_df(unused_cats_df):
    """df -> html"""
    unused_cats_df = unused_cats_df.set_index("SubjectName")
    # keep only the columns we want
    unused_cats_df = unused_cats_df[[
        "CategoryName",
        "CategoryWeight",
    ]]
    unused_cats_df = unused_cats_df.drop_duplicates()
    return unused_cats_df.to_html()

def render_negative_impact_assignments(assignments_df):
    """df -> html"""
    NUM_ASSIGNMENTS_TO_DISPLAY = 3
    # drop all assignments with None, Excused, Incomplete or "" grades.
    assignments_df = assignments_df[~assignments_df["Score"].isin(("", None, GradeCodes.Excused, GradeCodes.Incomplete))]
    # group assignments by subject name
    assignments_df_by_subject = assignments_df.groupby("SubjectName", as_index=False)
    # go through assignments and calculate negative impact scores, adding new column for them
    def create_negative_impact_column(df):
        df["Negative Impact"] = df.apply(lambda row: calculate_negative_impact(
                                                        row[Cols.Score.value], 
                                                        row[Cols.ScorePossible.value], 
                                                        row[Cols.CategoryWeight.value],
                                                        len(assignments_df[ 
                                                            (assignments_df["CategoryName"] == row["CategoryName"]) &
                                                            (assignments_df["ClassName"] == row["ClassName"])
                                                        ].index),
                                                    ), axis=1)
        #df["Negative Impact"] = df["Negative Impact"].fillna(value=np.nan)
        df["Negative Impact"] = df["Negative Impact"].astype(float)
        df["Score"] = df["Score"].astype(float)
        # get total number of assignments in this category
        df["Total # Assignments in Category"] = df.apply(lambda row: len(assignments_df[ 
                                                (assignments_df["CategoryName"] == row["CategoryName"]) &
                                                (assignments_df["ClassName"] == row["ClassName"])
                                          ].index), axis=1)
        # keep only the top 5 highest impact assignments
        df.sort_values(["Negative Impact"], ascending=False, inplace=True)
        df = df.head(5)
        return df

    assignments_df = assignments_df_by_subject.apply(create_negative_impact_column)
    assignments_df.reset_index(inplace=True, drop=True)
    # rename Score -> AvgScore
    assignments_df["AvgScore"] = assignments_df["Score"]
    # set index to SubjectName
    assignments_df.set_index("SubjectName", inplace=True)
    # keep only the columns we want
    assignments_df = assignments_df[[
        "CategoryName",
        "CategoryWeight",
        "Total # Assignments in Category",
        "ASGName",
        "Negative Impact",
        "AvgScore",
    ]]
    return assignments_df.to_html()

def render_category_table(assignments_df, unused_cats_df):
    # filter the cols we want to keep
    assignments_df = assignments_df[[
            "SubjectName",
            "CategoryName",
            "CategoryWeight",
            "Score",
            "NumAssignments",
            "NumBlank",
            "NumExcused",
            "NumIncomplete",
            "NumMissing",
            "NumZero",
        ]]

    #print(assignments_df)
    assignments_df["Score"] = assignments_df["Score"].astype(float)
    assignments_pivot = assignments_df.pivot_table(index=["SubjectName"], 
                                                   columns=["CategoryName"],
                                                   aggfunc={
                                                        "CategoryWeight": 'first',
                                                        "Score": np.mean,
                                                        "NumAssignments": lambda row: row.size,
                                                        "NumBlank": np.sum,
                                                        "NumExcused": np.sum,
                                                        "NumIncomplete": np.sum,
                                                        "NumMissing": np.sum,
                                                        "NumZero": np.sum,
                                                   }).stack()
    # append unused categories to the end; because categories are unused (ie have no assignments),
    # they don't show up in the assignments_df
    for _, row in unused_cats_df.iterrows():
        new_assignments_row = pd.DataFrame({
                    "SubjectName": row["SubjectName"],
                    "CategoryName": row["CategoryName"],
                    "CategoryWeight": row["CategoryWeight"],
                    "Score": np.nan,
                    "NumAssignments": 0,
                    "NumBlank": 0,
                    "NumExcused": 0,
                    "NumIncomplete": 0,
                    "NumMissing": 0,
                    "NumZero": 0
                }, index=["temp_value"])
        new_assignments_row.set_index(["SubjectName", "CategoryName"], inplace=True)
        # Only append new_assignments_row to dataframe if a category with the same
        # name isn't already there.
        # (sometimes, an unused category with the same name as a used category shows up
        #    in that case, obviously it's not in fact an unused category and it should be ignored)
        if not (row["SubjectName"], row["CategoryName"]) in assignments_pivot.index:
            assignments_pivot = assignments_pivot.append(new_assignments_row)

    assignments_pivot = assignments_pivot.round(decimals=1)
    assignments_pivot = assignments_pivot.fillna("n/a")
    assignments_pivot["AvgScore"] = assignments_pivot["Score"]
    assignments_pivot = assignments_pivot[[
            "CategoryWeight",
            "AvgScore",
            "NumAssignments",
            "NumMissing",
            "NumZero"
        ]]
    try:
        assignments_pivot.style.set_properties(**{'font-size':'6pt'})
    except ValueError as e:
        print(assignments_pivot)
    # color NumAssignments red if there are no assignments
    def highlight_rows_with_no_assignments(row):
        return ["background-color: #ff6347;" if (row["NumAssignments"] == 0) else "" for elem in row]
    
    return assignments_pivot.style.apply(highlight_rows_with_no_assignments, axis=1).render()


CACHED_MOST_RECENT_ASSIGNMENT_DATE = None
def get_most_recent_assignment_entered_date():
    global CACHED_MOST_RECENT_ASSIGNMENT_DATE
    if CACHED_MOST_RECENT_ASSIGNMENT_DATE is not None:
        return CACHED_MOST_RECENT_ASSIGNMENT_DATE

    assignments_df = get_assignments_df()
    if (assignments_df["GradeEnteredOn"].dtype != 'datetime64'):
        dates = pd.to_datetime(assignments_df["GradeEnteredOn"])
    else:
        dates = assignments_df["GradeEnteredOn"]
    most_recent_date = dates.max()
    CACHED_MOST_RECENT_ASSIGNMENT_DATE = most_recent_date
    return most_recent_date

def render_template(template_vars):
    report_name = template_vars["report_name"]

    # render html
    TEMPLATE_DIR = "templates"
    TEMPLATE_FILE = "gb_report_template.html"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html_report = template.render(template_vars)

    # DEBUG: save html for inspection
    with open("test.html", "w") as test_file:
        test_file.write(html_report)

    # render pdf
    OUTPUT_DIR = "./reports"
    # save report as PDF to output dir
    STYLESHEET_FILE = "./templates/typography.css"
    output_path = path.join(OUTPUT_DIR, "{}.pdf".format(report_name))
    weasyprint.HTML(string=html_report, base_url="./").write_pdf(output_path, stylesheets=[STYLESHEET_FILE])

def render_missing_zero_assignments(assignments_df):
    assignments_gdf_by_subject = assignments_df.groupby("SubjectName")
    missing_zero_assignments = assignments_gdf_by_subject.apply(lambda group: pd.Series({
                "# Missing / Zero assignments": group["NumMissing"].sum() + group["NumZero"].sum()
            })
        )
    # remove rows with no missing / empty assignments
    missing_zero_assignments = missing_zero_assignments[missing_zero_assignments["# Missing / Zero assignments"] != 0]
    return missing_zero_assignments.to_html()

# returns success: boolean
def create_gradebook_summary(teacher_fullname, homeroom):

    # get data in df form
    grade_df = get_grade_df()
    unused_cats_df = get_unused_cats_df()
    assignments_df = get_assignments_df()

    # filter dfs by teacher
    grade_df = grade_df[grade_df["TeacherFullname"] == teacher_fullname]
    unused_cats_df = unused_cats_df[unused_cats_df["TeacherFullname"] == teacher_fullname]
    assignments_df = assignments_df[assignments_df["TeacherFullname"] == teacher_fullname]

    # filter dfs by homeroom
    grade_df = grade_df[grade_df["Homeroom"] == homeroom]
    unused_cats_df = unused_cats_df[unused_cats_df["Homeroom"] == homeroom]
    assignments_df = assignments_df[assignments_df["Homeroom"] == homeroom]

    # if dfs are empty, skip
    if grade_df.empty or assignments_df.empty:
        return False
    
    template_vars = {}

    template_vars["grade_breakdown_diagrams"] = render_grade_breakdown_diagrams(grade_df)
    template_vars["failing_students"] = render_failing_students_table(grade_df)
    #template_vars["unused_categories"] = render_unused_categories_df(unused_cats_df)
    template_vars["negative_impact_assignments"] = render_negative_impact_assignments(assignments_df)
    #template_vars["missing_zero_assignments"] = render_missing_zero_assignments(assignments_df)
    template_vars["category_table"] = render_category_table(assignments_df, unused_cats_df)
    template_vars["most_recent_grade_date"] = get_most_recent_assignment_entered_date()

    template_vars["report_name"] = "Gradebook Report - {} - {}".format(teacher_fullname, homeroom)

    render_template(template_vars)
    return True
