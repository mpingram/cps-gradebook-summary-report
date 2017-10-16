import unittest
import gbutils_test_mockdata
import pandas as pd
from os import path
from enums import Cols
from gbutils import (
        get_grade_df,
        get_lettergrade_breakdown,
        get_lettergrade_breakdown_diagram_urls,
        calculate_negative_impact,
        aggregate_assignments,
        filter_by_teacher
)

class AggregateAssignments(unittest.TestCase):
    
    # have decided that aggregate_assignments can return None for Score.

    def test__should_return_df_of_correct_length(self):
        data_filepath = "./source/grade_data.csv"
        df = get_grade_df(data_filepath)

        # should return dataframe with size matching the number of unique assignments
        unique_assignments = df.groupby([Cols.AssignmentName.value,
                                                Cols.ClassName.value])


        aggregaged_assignments = aggregate_assignments(df)

        self.assertEqual(len(aggregaged_assignments), len(unique_assignments))

    def test__should_accurately_average_assignments(self):
        mock_gradebook_df = gbutils_test_mockdata.mock_gradebook_df
        expected_output = gbutils_test_mockdata.mock_gradebook_df_aggregated_assignments
        actual_output = aggregate_assignments(mock_gradebook_df)

        actual_output_dicts = actual_output.to_dict("records")
        expected_output_dicts = expected_output.to_dict("records")

        for i, act_dict in enumerate(actual_output_dicts):
            exp_dict = expected_output_dicts[i]
            self.maxDiff = None
            self.assertDictEqual(act_dict, exp_dict)



class CalculateNegativeImpact(unittest.TestCase):
    
    def test__should_assign_higher_score_to_heavier_weighted_scores(self):
        high_weight = 50
        low_weight = 49
        score = 50
        possible_score = 100 

        impact_high_weight = calculate_negative_impact(score, possible_score, high_weight)
        impact_low_weight = calculate_negative_impact(score, possible_score, low_weight)

        self.assertLess(impact_low_weight, impact_high_weight)

    def test__should_throw_on_unexpected_values(self):
        weight = 110
        score = 40
        possible_score = 20

        def run_calculate_negative_impact():
            return calculate_negative_impact(score, possible_score, weight)

        self.assertRaises(ValueError, run_calculate_negative_impact)

class GetLetterGradeBreakdownDiagramUrls(unittest.TestCase):

    data_filepath = "./source/grade_data.csv"
    df = get_grade_df(data_filepath)

    # just check and see if the files exist
    def test__diagrams_should_be_created(self):
        urls = get_lettergrade_breakdown_diagram_urls(self.df, "./images")
        def all_urls_are_files(urls):
            for url in urls:
                if not path.isfile(url):
                    return False
            return True
        self.assertTrue(all_urls_are_files(urls))

    def test__diagrams_should_be_grouped_by_class(self):
        num_subjects = self.df[Cols.ClassName.value].unique().size
        urls = get_lettergrade_breakdown_diagram_urls(self.df, "./images")
        num_urls = len(urls)
        self.assertEqual(num_subjects, num_urls)

class GetGradeDf(unittest.TestCase):

    data_filepath = "./source/grade_data.csv"
    expected_cols = [col_enum.value for col_enum in Cols]
    df = get_grade_df(data_filepath)

    def test__should_match_col_definitions(self):
        df_cols = set(self.df.columns)
        cols = set(self.expected_cols)
        self.assertTrue(df_cols == cols)

    def test__should_not_match_wrong_col_definitions(self):
        df_cols = set(self.df.columns)
        cols = set(("Foo", "Bar"))
        self.assertFalse(df_cols == cols)

class FilterByTeacher(unittest.TestCase):

    data_filepath = "./source/grade_data.csv"
    df = get_grade_df(data_filepath)
    teachername = df.sample(n=1)[Cols.TeacherFullname.value].iloc[0]
    
    def test__should_filter_teachers(self):
        print("Filtering by teacher {}".format(self.teachername))
        t_df = filter_by_teacher(self.df, self.teachername)
        only_contains_teachername = True 
        for i, row in t_df.iterrows():
            if row[Cols.TeacherFullname.value] != self.teachername:
                only_contains_teachername = False
                break
        self.assertTrue(only_contains_teachername)

class GetLetterGradeBreakdown(unittest.TestCase):

    data_filepath = "./source/grade_data.csv"
    df = get_grade_df(data_filepath)

    def test__should_return_series(self):
        breakdown = get_lettergrade_breakdown(self.df)
        self.assertTrue(isinstance(breakdown, pd.Series))

    def test__should_return_lettergrade_indexed_series(self):
        breakdown = get_lettergrade_breakdown(self.df)
        self.assertTrue(set(breakdown.index) == set(["A","B","C","D","F"]))

    def test__numbers_should_add_up(self):
        breakdown = get_lettergrade_breakdown(self.df)
        total = self.df.size
        breakdown_total = 0
        for lettergrade, num_records in breakdown.iteritems():
            breakdown_total += num_records
        # get_lettergrade_breakdown may drop blank records, meaning that
        # total may be more than breakdown_total
        self.assertLessEqual(breakdown_total, total)

if __name__ == "__main__":
    unittest.main()
