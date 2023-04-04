import parsers.parse_respa
import parsers.parse_oblast
import numpy as np
from objects.graph import Graph
import plotly.graph_objects as go
import tools
import os 

class Analyzer:

    def __init__(self, year, bygrade, olymp=''):
        self.ROUND3 = tools.rounder(3)
        self.year = year
        self.bygrade = bygrade
        self.OLYMP = olymp

    def results_for_problem(self, data, probnum, scale=100):
        return [getattr(obj, f"problem{probnum}")["rel"]*scale for obj in data if not obj.only_total]

    def total_results(self, data, scale=100/70):
        return [obj.total*scale for obj in data]
    
    def heat_map_for_grade(self, grade, do_fit=True):
        graph = Graph()
        data = self.bygrade[grade]
        numprobs = [obj.numprobs for obj in data if not obj.only_total]
        if not numprobs:
            return
        NUMPROB = max(numprobs)
        arrays = [self.results_for_problem(data, i+1) for i in range(NUMPROB)]
        corrs = np.corrcoef(arrays)
        cortext = [self.ROUND3(cor) for cor in corrs]
        labels = [f"№{i}" for i in range(1, NUMPROB+1)]
        traces = [go.Heatmap(z=corrs, text=cortext, texttemplate="%{text}", x=labels, y=labels, colorscale='dense')]
        graph.plot_heatmap(traces, f"results/{self.year}/{self.OLYMP}grade{grade}", f"Корреляция между задачами ({grade} кл.)")
        if do_fit:
            bestfit = [[np.polyfit(self.results_for_problem(data, i+1), self.results_for_problem(data, j+1), 1)
                        for j in range(NUMPROB)] for i in range(NUMPROB)]
            ffit = [[f"{self.ROUND3(arr[0])}x+{self.ROUND3(arr[1])}" for arr in row] for row in bestfit]
            traces = [go.Heatmap(z=corrs, text=ffit, texttemplate="%{text}", x=labels, y=labels, colorscale='dense')]
            graph.plot_heatmap(traces, f"results/{self.year}/{self.OLYMP}grade{grade}-fit", f"Корреляция между задачами ({grade} кл.)")

    def line_two_problems(self, grade, i, j):
        graph = Graph()
        data = self.bygrade[grade]
        x = self.results_for_problem(data, i)
        y = self.results_for_problem(data, j)
        fit = np.polyfit(x, y, 1)
        corr = np.corrcoef(x, y)
        xgrid = np.mgrid[0:100:2j]
        eq = f"y={self.ROUND3(fit[0])}x+{self.ROUND3(fit[1])}<br>R^2 = {self.ROUND3(corr[0, 1]**2)}"
        yfit = np.vectorize(lambda x: fit[0]*x+fit[1])(xgrid)
        traces = [go.Scatter(x=x, y=y, mode='markers', name="Результаты"),
                  go.Scatter(x=xgrid, y=yfit, mode='lines', name="Best fit")]
        graph.plot_linechart(traces, f"results/{self.year}/{self.OLYMP}grade{grade}-{i}-{j}", f"Корреляция между задачами {i} и {j}", f"Задача №{i}", f"Задача №{j}", eq)

    def histograms_for_grade(self, grade):
        graph = Graph()
        data = self.bygrade[grade]
        numprobs = [obj.numprobs for obj in data if not obj.only_total]
        if not numprobs:
            return
        NUMPROB = max(numprobs)
        x = self.total_results(data)
        titles = [f"Задача №{i+1}" for i in range(NUMPROB)] + ["Общий балл"]
        traces = [(go.Histogram(x=self.results_for_problem(data, i+1), nbinsx=10, histnorm='probability', name=f"Задача №{i+1}"), i//3+1, i%3+1) for i in range(NUMPROB)] \
            + [(go.Histogram(x=x, nbinsx=10, histnorm='probability', name="Общий балл"), NUMPROB//3+1, NUMPROB%3+1)]
        graph.plot_subplot_histograms(NUMPROB//3+1, 3, traces, 
                                      f"results/{self.year}/{self.OLYMP}grade{grade}-dist-problemwise", titles)
        # graph.plot_histogram(traces, f"results/{self.year}/grade{grade}-dist", f"Распределение баллов в {grade} кл.")

    def box_plots_for_grade(self, grade):
        graph = Graph()
        data = self.bygrade[grade]
        numprobs = [obj.numprobs for obj in data if not obj.only_total]
        if not numprobs:
            return
        NUMPROB = max(numprobs)
        traces = [go.Box(x=self.results_for_problem(data, i+1), name=f"Задача №{i+1}") for i in range(NUMPROB)] + \
                [go.Box(x=self.total_results(data), name='Общий балл')]
        graph.plot_box_plots(reversed(traces), f"results/{self.year}/{self.OLYMP}grade{grade}-dist-box", "Распределение баллов по задачам")

if __name__ == "__main__":
    # First, let's analyze respa results
    # OLYMP = "respa/"
    # for year in (2023, 2022, 2021):
    #     a = Analyzer(year, parsers.parse_respa.parse_results(year), OLYMP)
    #     for grade in (9, 10, 11):
    #         a.heat_map_for_grade(grade)
    
    # a = Analyzer(2023, parsers.parse_respa.parse_results(2023), OLYMP)
    # a.line_two_problems(11, 2, 8)
    # a.line_two_problems(11, 2, 7)
    # a.line_two_problems(11, 3, 8)
    # a.line_two_problems(11, 4, 5)
    # a.line_two_problems(11, 5, 6)
    # a.line_two_problems(10, 2, 5)
    # a.line_two_problems(10, 4, 5)
    # a.line_two_problems(10, 4, 6)
    # a.line_two_problems(10, 4, 7)
    # a.line_two_problems(10, 5, 6)

    # for year in (2023, 2022, 2021):
    #     a = Analyzer(year, parsers.parse_respa.parse_results(year), OLYMP)
    #     for grade in (9, 10, 11):
    #         a.histograms_for_grade(grade)
    #         a.box_plots_for_grade(grade)

    # Now, let's do some oblast stuff
    OLYMP = "oblast/"
    # bygrade, byoblast = parsers.parse_oblast.parse_results()
    # a = Analyzer(2023, bygrade, OLYMP)
    # for grade in (9, 10, 11):
    #     a.heat_map_for_grade(grade)
    #     a.histograms_for_grade(grade)
    #     a.box_plots_for_grade(grade)

    # base_path = 'export/html/results/2023/oblast/'
    # # Create a folder for each name
    # for oblast in byoblast:
    #     folder_path = os.path.join(base_path, oblast)
    #     os.makedirs(folder_path, exist_ok=True)

    # for oblast, oblbygrade in byoblast.items():
    #     a = Analyzer(2023, oblbygrade, f"{OLYMP}{oblast}/")
    #     for grade in (9, 10, 11):
    #         a.heat_map_for_grade(grade, do_fit=False)
    #         a.histograms_for_grade(grade)
    #         a.box_plots_for_grade(grade)

    pass