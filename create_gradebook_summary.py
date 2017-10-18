from enums import LetterGradeCutoffs, Cols, GradeCodes
import gbutils
from gradeconvert import to_letter_grade
import pandas as pd
import os.path as path
from data_access import get_grade_df, get_assignments_df, get_unused_cats_df
from plots import create_lettergrade_breakdown_diagram

import jinja2
import weasyprint

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
    return failing_students.to_html()

def render_grade_breakdown_diagrams(grade_df):
    """df -> html"""
    IMAGE_DIR = "./images/"
    # group filtered df by class (Subject + Homeroom) 
    gdf = grade_df.groupby("ClassName")
    # create images
    diagram_urls = []
    for class_name, group in gdf:
        diagram_url = path.join(IMAGE_DIR, "{}.png".format(class_name))
        success, err = create_lettergrade_breakdown_diagram(grades=group["QuarterAvg"],
                                                         output_url=diagram_url,
                                                         label=class_name)
        if success:
            diagram_urls.append(diagram_url)
        else:
            print(err)
    # TODO: render html for each diagram_url
    return """<span style="color:red">Implement me!</span>"""

def render_unused_categories_df(unused_cats_df):
    """df -> html"""
    # keep only the columns we want
    unused_cats_df = unused_cats_df[[
        "ClassName",
        "CategoryName",
        "CategoryWeight",
    ]]
    # sort unused cats by class
    unused_cats_df = unused_cats_df.sort_values("ClassName")
    unused_cats_df = unused_cats_df.set_index("ClassName")
    return unused_cats_df.to_html()

def render_negative_impact_assignments(assignments_df):
    """df -> html"""
    NUM_ASSIGNMENTS_TO_DISPLAY_PER_CLASS = 5
    # drop all assignments with None, Excused, Incomplete or "" grades.
    assignments_df = assignments_df[~assignments_df["Score"].isin(("", None, GradeCodes.Excused, GradeCodes.Incomplete))]
    # group assignments by class name
    assignments_gdf_by_class = assignments_df.groupby(Cols.ClassName.value)
    # go through groups and calculate negative impact scores, adding new column for them
    def add_negative_impact_score_column_and_sort(df):
        num_assignments = len(df)
        df["Negative Impact"] = df.apply(lambda row: gbutils.calculate_negative_impact(
                                                    row[Cols.Score.value], 
                                                    row[Cols.ScorePossible.value], 
                                                    row[Cols.CategoryWeight.value],
                                                    num_assignments), axis=1)
        df = df.sort_values("Negative Impact", ascending=False)
        # keep only the top 5 highest impact assignments for each category
        df = df.head(NUM_ASSIGNMENTS_TO_DISPLAY_PER_CLASS)
        return df
    negative_impact_assignments = assignments_gdf_by_class.apply(add_negative_impact_score_column_and_sort)
    # keep only the columns we want
    negative_impact_assignments = negative_impact_assignments[[
        "ClassName",
        "ASGName",
        "CategoryName",
        "CategoryWeight",
        "Score",
        "Negative Impact"
    ]]
    negative_impact_assignments.set_index("ClassName")
    return negative_impact_assignments.to_html()

def render_category_table(assignments_df, unused_cats_df):
    # filter the cols we want to keep
    assignments_df = assignments_df[[
            "ClassName",
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
                    "ClassName": row["ClassName"],
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
    assignments_pivot = assignments_df.pivot_table(index=["ClassName"], 
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
    return assignments_pivot.to_html()


def render_template(template_vars):
    report_name = teamplate_vars["Report Name"]

    # render html
    TEMPLATE_DIR = "templates"
    TEMPLATE_FILE = "gb_report_template.html"
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    html_report = template.render(template_vars)

    # render pdf
    OUTPUT_DIR = "./reports"
    # save report as PDF to output dir
    STYLESHEET_FILE = "./templates/typography.css"
    weasyprint.HTML(string=html_report, base_url="./").write_pdf(path.join(OUTPUT_DIR, "{}.pdf".format(report_name), stylesheets=[STYLESHEET_FILE]))


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

    template_vars["report_name"] = "{} Grade Report".format(teacher_fullname)

    template_vars["diagram_urls"] = render_grade_breakdown_diagrams(grade_df)
    template_vars["failing_students"] = render_failing_students_table(grade_df)
    template_vars["unused_categories"] = render_unused_categories_df(unused_cats_df)
    template_vars["negative_impact_assignments"] = render_negative_impact_assignments(assignments_df)
    template_vars["category_table"] = render_category_table(assignments_df, unused_cats_df)

    # VI. get list of missing/0 assignments, desc sorted
    # --
    # import assignments df
    assignments_df = get_assignments_df()
    # filter assignments by teacher
    assignments_df = assignments_df[assignments_df["TeacherFullname"] == teacher_fullname]
    # group by ClassName
    assignments_gdf_by_class = assignments_df.groupby(Cols.ClassName.value)
    missing_zero_assignments = assignments_gdf_by_class.apply(lambda group: pd.Series({
                "# Missing / Zero assignments": group["NumMissing"].sum() + group["NumZero"].sum()
            })
        )
    # remove rows with no missing / empty assignments
    missing_zero_assignments = missing_zero_assignments[missing_zero_assignments["# Missing / Zero assignments"] != 0]

    template_vars["missing_zero_assignments"] = missing_zero_assignments.to_html()

    render_template(template_vars)

if __name__ == "__main__":
    # DEBUG  
    DEBUG_NAME = "Karen Baggot"
    create_gradebook_summary(DEBUG_NAME)
