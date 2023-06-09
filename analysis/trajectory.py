from objects.student import Student
import parsers.parse_oblast
import parsers.parse_respa
from parsers.find_overlaps import find_similar_matches
import numpy as np
from objects.graph import Graph
import plotly.graph_objects as go
import tools

class Analyzer:
    YEAR = 2023

    def __init__(self):
        self.ROUND3 = tools.rounder(3)
        self.respa_bygrade = parsers.parse_respa.parse_results(self.YEAR)
        self.oblast_bygrade, self.oblast_byoblast = parsers.parse_oblast.parse_results()
        self.gradeToStudent = {}
        self.oblToGrToStuds = {}

    def combine_students(self, grade, oblast=None, include_arbitrage=False):
        """Combine students by grade and optionally by oblast.

        Parameters:
            - self (object): Object instance
            - grade (int): Grade level (9, 10, or 11)
            - oblast (str, optional): Name of the oblast (region) of interest (default is None)

        Returns:
            - dict: A dictionary mapping grades to a list of Student objects. Each Student object contains the name and scores of the participant, and can belong to either the RESPA or OBlast Olympiad (or both).

        Description:
        This function combines participant scores from either the RESPA or the Oblast Olympiad, or both, by matching the names of the participants. The resulting dictionary maps grades to a list of Student objects, each containing the name and scores of the corresponding participant. If an oblast is specified, the function combines only the scores of participants from that oblast.
        """
        grToStudents = {}
        if not oblast:
            name_to_objs = find_similar_matches([self.respa_bygrade[grade], self.oblast_bygrade[grade]], "name", testing=False)
        else:
            name_to_objs = find_similar_matches([self.respa_bygrade[grade], self.oblast_byoblast[oblast][grade]], "name", testing=False)
        for name, objs in name_to_objs.items():
            student = Student()
            student.name = name
            for obj in objs:
                total = obj.total
                if hasattr(obj, "oblast"):
                    student.oblast = obj.oblast
                if include_arbitrage and obj.olymp_name == "oblast":
                    total += obj.arbitrage
                setattr(student, f"{obj.olymp_name}_score", total)
            grToStudents.setdefault(grade, []).append(student)
            self.gradeToStudent.setdefault(grade, []).append(student)
        return grToStudents

    def get_oblast_respa_arrays(self, data, scale=100/70):
        """
        Given a list of objects containing the `oblast_score` and `respa_score` attributes, this function returns two arrays
        `obl` and `resp`, where `obl` contains the values of `oblast_score` attribute of the objects in `data`, scaled by the
        given `scale` factor, and `resp` contains the values of `respa_score` attribute of the objects in `data`, scaled by the
        same factor.

        :param self: the object instance
        :param data: a list of objects containing `oblast_score` and `respa_score` attributes
        :param scale: the factor by which to scale the `oblast_score` and `respa_score` values (default: 100/70)
        :return: a tuple containing two arrays `obl` and `resp`, where `obl` contains the scaled `oblast_score` values and
                `resp` contains the scaled `respa_score` values
        """
        obl, resp = [], []
        for obj in data:
            if hasattr(obj, "oblast_score") and hasattr(obj, "respa_score"):
                obl.append(obj.oblast_score*scale)
                resp.append(obj.respa_score*scale)
        return obl, resp
    
    def calculate_correlation(self, grade):
        """Calculates the correlation coefficient between the scores of students from oblast and respa stages for a given grade.

        Parameters:
            - grade (int): The grade level of the students for which to calculate the correlation coefficient.
        
        Returns:
            - The correlation coefficient as a numpy array."""
        data = self.gradeToStudent[grade]
        oblast, respa = self.get_oblast_respa_arrays(data)
        return np.corrcoef(oblast, respa)

    def plot_correlations_by_grade(self, grades):
        graph = Graph()
        graph.SAVE_HTML = True
        corrs = []
        for grade in grades:
            self.combine_students(grade, include_arbitrage=True)
            data = self.gradeToStudent[grade]
            oblast, respa = self.get_oblast_respa_arrays(data)
            labels = [f"{obj.name}<br>{obj.oblast}" for obj in data]
            corr = np.corrcoef(oblast, respa)[0, 1]
            corrs.append(corr)
            fit = np.polyfit(oblast, respa, 1)
            xgrid = np.mgrid[0:100:2j]
            eq = f"y={self.ROUND3(fit[0])}x+{self.ROUND3(fit[1])}<br>R^2 = {self.ROUND3(corr**2)}"
            yfit = np.vectorize(lambda x: fit[0]*x+fit[1])(xgrid)
            traces = [go.Scatter(x=oblast, y=respa, mode='markers', name="Результаты", text=labels),
                        go.Scatter(x=xgrid, y=yfit, mode='lines', name="Best fit")]
            graph.plot_data(traces, f"trajectory/gr{grade}-data", f"Корреляция между баллами областного и<br>заключительного этапа РО ({grade} кл., {self.YEAR-1}-{self.YEAR} уч. год)", xtitle="Баллы (из 100%) на теор. туре областного этапа", ytitle="Баллы (из 100%) на теор. туре<br>заключительного этапа",
            eq=dict(xref="paper", yref="paper", x=0, y=1, text=eq, showarrow=False),
            yaxisparams=dict(range=[0, 60], dtick=10),
            xaxisparams=dict(range=[0, 100], dtick=10),
            layoutparams=dict(width=720, height=500, margin=dict(b=0, t=100)))
        yValLabels = [self.ROUND3(cor) for cor in corrs]
        traces = [go.Bar(y=corrs, x=[f"{grade} класс" for grade in grades], #marker_color=self.BINARY[i],
                                 text=yValLabels, textposition='auto', )] #legendrank=1-i
        graph.plot_data(traces, f"trajectory/bygrade", f"Корреляция между баллами областного и заключительного этапа<br>({self.YEAR-1}-{self.YEAR} уч. год)",
                        yaxisparams=dict(range=[0, 1], showgrid=False, dtick=0.2),
                        xaxisparams=dict(showgrid=False),
                        layoutparams=dict(barmode="stack", width=1080, height=250,
                                          margin=dict(b=0, t=75)))

    def plot_correlations_by_oblast(self, grades):
        graph = Graph()
        oblasts = sorted(self.oblast_byoblast)
        xVals = []
        corrs = []
        for oblast in oblasts:
            obl_scores, resp_scores = [], []
            for grade in grades:
                grToStuds = self.combine_students(grade, oblast, include_arbitrage=True)
                if grade not in grToStuds:
                    print(f"{oblast} doesn't  have results for {grade}")
                    continue
                data = grToStuds[grade]
                obl, resp = self.get_oblast_respa_arrays(data)
                obl_scores.extend(obl)
                resp_scores.extend(resp)
            if len(obl_scores) <= 2:
                continue
            corr = np.corrcoef(obl_scores, resp_scores)[0, 1]
            corrs.append(corr)
            xVals.append(oblast)

            fit = np.polyfit(obl_scores, resp_scores, 1)
            xgrid = np.mgrid[0:100:2j]
            eq = f"y={self.ROUND3(fit[0])}x+{self.ROUND3(fit[1])}<br>R^2 = {self.ROUND3(corr**2)}"
            yfit = np.vectorize(lambda x: fit[0]*x+fit[1])(xgrid)
            traces = [go.Scatter(x=obl_scores, y=resp_scores, mode='markers', name="Результаты"),
                        go.Scatter(x=xgrid, y=yfit, mode='lines', name="Best fit")]
            graph.plot_data(traces, f"trajectory/obl-{oblast}", f"Корреляция между баллами областного и<br>заключительного этапа РО ({oblast}, {self.YEAR-1}-{self.YEAR} уч. год)", xtitle="Баллы (из 100%) на теор. туре областного этапа", ytitle="Баллы (из 100%) на теор. туре<br>заключительного этапа",
                eq=dict(xref="paper", yref="paper", x=0, y=1, text=eq, showarrow=False),
                yaxisparams=dict(range=[0, 60], dtick=10),
                xaxisparams=dict(range=[0, 100], dtick=10),
                layoutparams=dict(width=720, height=500, margin=dict(b=0, t=100)))
        
        obl_scores, resp_scores = [], []
        for grade in grades:
            self.combine_students(grade)
            data = self.gradeToStudent[grade]
            obl, resp = self.get_oblast_respa_arrays(data)
            obl_scores.extend(obl)
            resp_scores.extend(resp)
        xVals.append("Суммарно")
        corrs.append(np.corrcoef(obl_scores, resp_scores)[0, 1])
        traces = [go.Bar(y=corrs, x=xVals, text=[self.ROUND3(cor) for cor in corrs], 
                         textposition='auto')]
        graph.plot_data(traces, f"trajectory/byoblast", f"Корреляция между баллами областного и<br>заключительного этапа по областям ({self.YEAR-1}-{self.YEAR} уч. год)",
                        yaxisparams=dict(range=[0, 1], showgrid=False, dtick=0.2),
                        xaxisparams=dict(showgrid=False),
                        layoutparams=dict(barmode="stack", width=1080))
        


if __name__ == "__main__":
    a = Analyzer()
    # for grade in (11, 10, 9):
    #     a.combine_students(grade)
    #     a.calculate_correlation(grade)
    
    # A few notes: it matches 41/45 students in grade 11
    #                         46/53             grade 10
    #                         44/47             grade 9
    grades = [9, 10, 11]
    a.plot_correlations_by_grade(grades)
    # a.plot_correlations_by_oblast(grades)