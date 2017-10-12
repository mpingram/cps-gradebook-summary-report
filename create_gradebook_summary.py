from enums import Cols, LetterGradeCutoffs
import gbutils
from utils import to_percentage_grade, to_letter_grade

def create_gradebook_summary(all_grades_df, teacher_fullname):
    # filter all_grades_df by selected teacher
    df = gbutils.filter_by_teacher(all_grades_df, teacher_fullname)

    # I. get grade breakdown pie charts
    lettergrade_breakdown_diagram_urls = gbutils.get_lettergrade_breakdown_diagram_urls(df) 

    # II. get # of failing students, grouped by subject and homeroom
    failing_students_by_subject = df.groupby(Cols.SubjectName.value, 
                                             Cols.Homeroom.value).filter(lambda row:
            to_percentage_grade(row[Cols.Score.value], row[Cols.ScorePossible.value]) <= LetterGradeCutoffs.F)

    # III. get list of unused categories, grouped by subject
        # FIXME: I think we need addl data source for this 

    # IV. get top 5 assignments with highest negative impact,
    #       grouped by subject
    assignments_df = aggregate_by_assignments(df)
    assignments_df["Negative Impact"] = assignments_df.apply(lambda row: 
                                                    gbutils.calculate_negative_impact(
                                                        row[Cols.Score.value], 
                                                        row[Cols.ScorePossible.value], 
                                                        row[Cols.CategoryWeight.value]), axis=1)
    sorted_assignments_df = assignments_df.sort_values("Negative Impact")
    negative_impact_assignments = sorted_assignments_df.groupby(Cols.SubjectName.value).top(5)

    # V. get category table, by subject, showing name, weight, # assignments,
    #       and avg score
    assignments_df_filtered = assignments_df[[
        Cols.Score.value,
        Cols.ScorePossible.value,
        Cols.SubjectName.value,
        Cols.CategoryName.value, 
        Cols.CategoryWeight.value, 
        "NumAssignments",
        "AverageScore",
    ]]
    subject_categories_gdf = assignments_df_filtered.groupby(Cols.SubjectName.value)
    subject_categories_gdf.apply(lambda group: 
            group.groupby(Cols.CategoryName.value).apply(gbutils.aggregate_by_assignments))

    # VI. get list of missing/0 assignments, desc sorted
    sorted_assignments_df = assignments_df.sort_values("NumMissingOrZero")
    missing_zero_assignments = sorted_assignments_df.groupby(Cols.SubjectName.value).top(5)

    # VII(?). get list of excepted/blank/inc assignments, desc sorted
