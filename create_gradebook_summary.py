from enums import LetterGradeCutoffs, Cols, GradeCodes
import gbutils
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
    teacher_fullname = grade_df.iloc[0]["TeacherFullname"]
    # create images
    diagram_urls = []
    for subject_name, group in gdf:
        ### FIXME: CHAVEZ-SPECIFIC LOGIC ###
        # only perform the pie charting if the subject is Reading, Math, Sci, Soc Sci, or Writing
        import re
        matchObj = re.search("CHGO READING FRMWK|MATHEMATICS STD|SCIENCE  STANDARDS|SOCIAL SCIENCE STD|WRITING STANDARDS", subject_name)
        if not matchObj:
            continue
        ### END CHAVEZ-SPECIFIC LOGIC ###
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
            html += """<img style="width: 350px;" src="{0}"/>""".format(url)
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
    NUM_ASSIGNMENTS_TO_DISPLAY = 5
    # drop all assignments with None, Excused, Incomplete or "" grades.
    assignments_df = assignments_df[~assignments_df["Score"].isin(("", None, GradeCodes.Excused, GradeCodes.Incomplete))]
    # group assignments by subject name
    assignments_df_by_subject = assignments_df.groupby("SubjectName", as_index=False)
    # go through assignments and calculate negative impact scores, adding new column for them
    def create_negative_impact_column(df):
        df["Negative Impact"] = df.apply(lambda row: gbutils.calculate_negative_impact(
                                                        row[Cols.Score.value], 
                                                        row[Cols.ScorePossible.value], 
                                                        row[Cols.CategoryWeight.value],
                                                        len(assignments_df[ 
                                                            (assignments_df["CategoryName"] == row["CategoryName"]) &
                                                            (assignments_df["ClassName"] == row["ClassName"])
                                                        ]),
                                                    ), axis=1)
        #df["Negative Impact"] = df["Negative Impact"].fillna(value=np.nan)
        df["Negative Impact"] = df["Negative Impact"].astype(float)
        df["Score"] = df["Score"].astype(float)
        df = df[[
            "SubjectName",
            "ASGName",
            "CategoryName",
            "CategoryWeight",
            "Score",
            "Negative Impact"
            ]]
        df = df.groupby("ASGName", as_index=False).agg({
            "SubjectName": "first",
            "CategoryName": "first",
            "CategoryWeight": "first",
            "Score": "mean",
            "Negative Impact": "mean"
            })
        return df

    assignments_df = assignments_df_by_subject.apply(create_negative_impact_column)
    assignments_df.reset_index(inplace=True, drop=True)
    # keep only the top 5 highest impact assignments
    assignments_df = assignments_df.sort_values(["Negative Impact"], ascending=False)
    assignments_df = assignments_df.head(5)
    # rename Score -> AvgScore
    assignments_df["AvgScore"] = assignments_df["Score"]
    # set index to SubjectName
    assignments_df.set_index("SubjectName", inplace=True)
    # keep only the columns we want
    assignments_df = assignments_df[[
        "ASGName",
        "CategoryName",
        "CategoryWeight",
        "AvgScore",
        "Negative Impact"
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
    for _, row in unused_cats_df.iterrows():
        assignments_df = assignments_df.append(pd.DataFrame({
                    "SubjectName": row["SubjectName"],
                    "CategoryName": row["CategoryName"],
                    "CategoryWeight": row["CategoryWeight"],
                    "Score": np.nan,
                    "NumAssignments": np.nan,
                    "NumBlank": np.nan,
                    "NumExcused": np.nan,
                    "NumIncomplete": np.nan,
                    "NumMissing": np.nan,
                    "NumZero": np.nan
                }, index=[0]), ignore_index=True)
        
    assignments_df["Score"] = assignments_df["Score"].astype(float)
    assignments_pivot = assignments_df.pivot_table(index=["SubjectName"], 
                                                   columns=["CategoryName"],
                                                   aggfunc={
                                                        "CategoryWeight": 'first',
                                                        "Score": np.mean,
                                                        "NumAssignments": 'count',
                                                        "NumBlank": np.sum,
                                                        "NumExcused": np.sum,
                                                        "NumIncomplete": np.sum,
                                                        "NumMissing": np.sum,
                                                        "NumZero": np.sum,
                                                    }).stack()
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
    assignments_pivot.style.set_properties(**{'font-size':'6pt'})
    # color NumAssignments red if there are no assignments
    def highlight_rows_with_no_assignments(row):
        return ["background-color: #ff6347;" if (row["NumAssignments"] == 0) else "" for elem in row]
    
    return assignments_pivot.style.apply(highlight_rows_with_no_assignments, axis=1).render()


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

def create_gradebook_summary(teacher_fullname):

    # get data in df form
    grade_df = get_grade_df()
    unused_cats_df = get_unused_cats_df()
    assignments_df = get_assignments_df()

    # filter dfs by teacher
    grade_df = grade_df[grade_df["TeacherFullname"] == teacher_fullname]
    unused_cats_df = unused_cats_df[unused_cats_df["TeacherFullname"] == teacher_fullname]
    assignments_df = assignments_df[assignments_df["TeacherFullname"] == teacher_fullname]

    template_vars = {}

    template_vars["grade_breakdown_diagrams"] = render_grade_breakdown_diagrams(grade_df)
    template_vars["failing_students"] = render_failing_students_table(grade_df)
    template_vars["unused_categories"] = render_unused_categories_df(unused_cats_df)
    template_vars["negative_impact_assignments"] = render_negative_impact_assignments(assignments_df)
    template_vars["category_table"] = render_category_table(assignments_df, unused_cats_df)
    template_vars["missing_zero_assignments"] = render_missing_zero_assignments(assignments_df)

    template_vars["report_name"] = "Gradebook Report - {}".format(teacher_fullname)
    render_template(template_vars)
