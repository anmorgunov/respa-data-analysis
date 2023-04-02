from parsers import survey
from objects.graph import Graph
import plotly.graph_objects as go
import tools

class Analyzer:
    
    STAGES = "region oblast respa".split()
    GREEN3 = ["#99d98c", "#52b69a", "#168aad"]
    BLUEPINK = ["#4ea8de", "#ff8fab"]

    def __init__(self):
        self.ROUND1 = tools.rounder(1)
        self.ROUND2 = tools.rounder(2)
        self.raw = {}
        for stage in self.STAGES:
            self.raw[stage] = survey.parse_responses(stage)
    
    def school_distribution(self):
        graph = Graph()
        stageToIn = {"region": 2, "oblast": 1, "respa": 0}
        data = {
            "respa": [0, 0, 0],
            "oblast": [0, 0, 0],
            "region": [0, 0, 0], # кол-во сельских, кол-во городских, кол-во спец
        }
        for stage in self.STAGES:
            for student in self.raw[stage][0]:
                if "селе" in student.school:
                    data[stage][0] += 1
                elif "городе" in student.school:
                    data[stage][1] += 1
                else:
                    data[stage][2] += 1
        xVals = ["Заключительный", "Областной", "Районный"]
        newData = {}
        schools = ["Школа в селе", "Школа в городе", "Специализированная<br>школа"]
        for stage, numbers in data.items():
            for school, number in zip(schools, numbers):
                newData.setdefault(school, [None, None, None])[stageToIn[stage]] = self.ROUND1(number/sum(data[stage])*100)
        traces = []
        for i, (stage, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=xVals, x=yVals, name=stage, orientation='h', marker_color=self.GREEN3[i],
                                 text=yValLabels, textposition='auto'))
        title = 'В каких школах учатся участники РО?'
        graph.horizontal_bar_plot(traces, "demographics/schools", title)

    def language_distribution(self):
        graph = Graph()
        langToInd = {"На русском": 0, "На казахском": 1, "На английском": 2}
        keyToInd = {"respa": {"study": 1, "participate": 0},
                    "oblast": {"study": 3, "participate": 2},
                    "region": {"study": 5, "participate": 4},}
        data = {
            "respa": {
                "study": [0, 0, 0], # rus kaz eng
                "participate": [0, 0, 0]
            },
            "oblast": {
                "study": [0, 0, 0],
                "participate": [0, 0, 0]
            },
            "region": {
                "study": [0, 0, 0],
                "participate": [0, 0, 0]
            }
        }
        for stage in self.STAGES:
            for student in self.raw[stage][0]:
                data[stage]["study"][langToInd[student.langStudy]] += 1
                data[stage]["participate"][langToInd[student.langParticipate]] += 1
        newData = {}
        languages = ["На русском", "На казахском", "На английском"]
        for stage, subdata in data.items():
            for key, numbers in subdata.items():
                for lang, number in zip(languages, numbers):
                    newData.setdefault(lang, [None, None, None, None, None, None])[keyToInd[stage][key]] = self.ROUND1(number/sum(data[stage][key])*100)
        traces = []
        xVals = ["Заключительный<br>Язык участия", "Заключительный<br>Язык обучения",
                 "Областной<br>Язык участия", "Областной<br>Язык обучения",
                 "Районный<br>Язык участия", "Районный<br>Язык обучения"]
        for i, (lang, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=xVals, x=yVals, name=lang, orientation='h', marker_color=self.GREEN3[2-i],
                                 text=yValLabels, textposition='auto'))
        graph.horizontal_bar_plot(traces, "demographics/language", "Язык обучения и язык на котором ученики читают задания РО")

    def gender_distribution(self):
        graph = Graph()
        keyToInd = {"respa": 0, "oblast": 1, "region": 2}
        data = {"respa": [0, 0], "oblast": [0, 0], "region": [0, 0]} # male female
        for stage in self.STAGES:
            for student in self.raw[stage][0]:
                if student.gender == 'Мужской':
                    data[stage][0] += 1
                else:
                    data[stage][1] += 1
        newData = {}
        genders = ["Мужской", "Женский"]
        for stage, genderdist in data.items():
            for gender, count in zip(genders, genderdist):
                newData.setdefault(gender, [None, None, None])[keyToInd[stage]] = self.ROUND1(count/sum(data[stage])*100)
        traces = []
        xVals = ["Заключительный", "Областной", "Районный"]
        for i, (gender, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=xVals, x=yVals, name=gender, orientation='h', marker_color=self.BLUEPINK[i],
                                 text=yValLabels, textposition='auto'))
        graph.horizontal_bar_plot(traces, "demographics/gender", "Пол участников РО")

if __name__ == "__main__":
    a = Analyzer()
    a.school_distribution()
    a.language_distribution()
    a.gender_distribution()