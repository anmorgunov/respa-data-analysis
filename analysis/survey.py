from parsers import survey
from objects.graph import Graph
import plotly.graph_objects as go
import tools

class Analyzer:
    
    STAGES = "region oblast respa".split()
    GREEN3 = ["#99d98c", "#52b69a", "#168aad"]
    BLUEPINK = ["#4ea8de", "#ff8fab"]
    BINARY = ["#5390d9", "#9d4edd"]
    BINARYHOT = ["#EF7A85", "#788BFF"]
    VIOLET5 = ["#e0aaff", "#c77dff", "#9d4edd", "#7b2cbf", "#5a189a"]
    RED5 = ["#fff0f3", "#ffccd5", "#ffb3c1", "#ff4d6d", "#c9184a"]
    GREEN5 = ["#d8f3dc", "#b7e4c7", "#95d5b2", "#57c84d", "#2eb62c"]
    LIKERT = ['#D35269', '#EF7A85', '#EAEAEA', '#788BFF', '#5465FF']
    stageToInd = {"respa": 0, "oblast": 1, "region": 2}
    xValsStages = ["Заключительный", "Областной", "Районный"]

    def __init__(self):
        self.ROUND1 = tools.rounder(1)
        self.ROUND2 = tools.rounder(2)
        self.raw = {}
        for stage in self.STAGES:
            self.raw[stage] = survey.parse_responses(stage)
    
    def school_distribution(self):
        graph = Graph()
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
        newData = {}
        schools = ["Школа в селе", "Школа в городе", "Специализированная<br>школа"]
        for stage, numbers in data.items():
            for school, number in zip(schools, numbers):
                newData.setdefault(school, [None, None, None])[self.stageToInd[stage]] = self.ROUND1(number/sum(data[stage])*100)
        traces = []
        for i, (stage, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=self.xValsStages, x=yVals, name=stage, orientation='h', marker_color=self.GREEN3[i],
                                 text=yValLabels, textposition='auto', legendrank=2-i))
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
                                 text=yValLabels, textposition='auto', legendrank=2-i))
        graph.horizontal_bar_plot(traces, "demographics/language", "Язык обучения и язык на котором ученики читают задания РО")

    def gender_distribution(self):
        graph = Graph()
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
                newData.setdefault(gender, [None, None, None])[self.stageToInd[stage]] = self.ROUND1(count/sum(data[stage])*100)
        traces = []
        for i, (gender, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=self.xValsStages, x=yVals, name=gender, orientation='h', marker_color=self.BLUEPINK[i],
                                 text=yValLabels, textposition='auto', legendrank=1-i))
        graph.horizontal_bar_plot(traces, "demographics/gender", "Пол участников РО")

    def first_timers(self):
        graph = Graph()
        data = {"respa": [0, 0], "oblast": [0, 0], "region": [0, 0]} # first time | returning
        for stage in self.STAGES:
            for student in self.raw[stage][0]:
                if student.firstTime:
                    data[stage][0] += 1
                else:
                    data[stage][1] += 1
        newData = {}
        kinds = ["Участвует первый раз", "Участвовал в<br>предыдущие годы"]
        for stage, kinddist in data.items():
            for kind, count in zip(kinds, kinddist):
                newData.setdefault(kind, [None, None, None])[self.stageToInd[stage]] = self.ROUND1(count/sum(data[stage])*100)
        traces = []
        for i, (kind, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=self.xValsStages, x=yVals, name=kind, orientation='h', marker_color=self.BINARY[i],
                                 text=yValLabels, textposition='auto', legendrank=1-i))
        graph.horizontal_bar_plot(traces, "demographics/firsttimers", "Какая доля учеников участвует на РО в первый раз?")
    
    def first_timers_by_grade(self, grade):
        graph = Graph()
        data = {"respa": [0, 0], "oblast": [0, 0], "region": [0, 0]} # first time | returning
        for stage in self.STAGES:
            for student in self.raw[stage][1][grade]:
                if student.firstTime:
                    data[stage][0] += 1
                else:
                    data[stage][1] += 1
        newData = {}
        kinds = ["Участвует первый раз", "Участвовал в<br>предыдущие годы"]
        for stage, kinddist in data.items():
            for kind, count in zip(kinds, kinddist):
                newData.setdefault(kind, [None, None, None])[self.stageToInd[stage]] = self.ROUND1(count/sum(data[stage])*100)
        traces = []
        for i, (kind, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=self.xValsStages, x=yVals, name=kind, orientation='h', marker_color=self.BINARY[i],
                                 text=yValLabels, textposition='auto', legendrank=1-i))
        graph.horizontal_bar_plot(traces, f"demographics/firsttimers-grade{grade}", f"Какая доля учеников ({grade} кл.) участвует на РО в первый раз?")

    def preparation_time(self):
        graph = Graph()
        keyToInd = {"Меньше двух недель": 0, "От двух недель до месяца": 1,
                    "От месяца до 3 месяцев": 2, "От 3 месяцев до 6 месяцев": 3,
                    "Больше 6 месяцев": 4}
        data = {"respa": [0, 0, 0, 0, 0], "oblast": [0, 0, 0, 0, 0], 
                "region": [0, 0, 0, 0, 0]} # <2 weeks|2-4 weeks|1-3 months|3-6 months|>6 months
        for stage in self.STAGES:
            for student in self.raw[stage][0]:
                data[stage][keyToInd[student.prepTime]] += 1
        newData = {}
        for stage, timedist in data.items():
            for time, count in zip(keyToInd, timedist):
                newData.setdefault(time, [None]*3)[self.stageToInd[stage]] = self.ROUND1(count/sum(data[stage])*100)
        traces = []
        for i, (time, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=self.xValsStages, x=yVals, name=time, orientation='h', marker_color=self.VIOLET5[i],
                                 text=yValLabels, textposition='auto'))
        graph.horizontal_bar_plot(traces, "demographics/preptime", "Как долго ученики готовятся к РО?")
                
    def preparation_style(self):
        graph = Graph()
        keyToInd = {"Я готовился<br>с учителем": 0, "Я готовился<br>больше с учителем,<br>нежели самостоятельно": 1,
                    "Готовился в равной<br>степени самостоятельно<br>и с учителем": 2, "Я готовился<br>больше самостоятельно,<br>нежели с учителем": 3,
                    "Я готовился<br>самостоятельно": 4}
        data = {"respa": [0, 0, 0, 0, 0], "oblast": [0, 0, 0, 0, 0], 
                "region": [0, 0, 0, 0, 0]}
        for stage in self.STAGES:
            for student in self.raw[stage][0]:
                for key in keyToInd:
                    if key.replace("<br>", " ") == student.prepStyle:
                        data[stage][keyToInd[key]] += 1
        newData = {}
        for stage, styledist in data.items():
            for style, count in zip(keyToInd, styledist):
                newData.setdefault(style, [None]*3)[self.stageToInd[stage]] = self.ROUND1(count/sum(data[stage])*100)
        traces = []
        for i, (style, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=self.xValsStages, x=yVals, name=style, orientation='h', marker_color=self.LIKERT[i],
                                 text=yValLabels, textposition='auto', legendrank=4-i))
        graph.horizontal_bar_plot(traces, "demographics/prepstyle", "Как ученики готовятся к РО: с учителем или самостоятельно?")

    def did_you_know(self):
        graph = Graph()
        knewQazChO, knewSyllabus, knewQazolymp = [0, 0], [0, 0], [0, 0]
        for student in self.raw["region"][0]:
            if student.knewQazChO:
                knewQazChO[0] += 1
            else:
                knewQazChO[1] += 1
            if student.knewSyllabus:
                knewSyllabus[0] += 1
            else:
                knewSyllabus[1] += 1
            if student.knewQazolymp:
                knewQazolymp[0] += 1
            else:
                knewQazolymp[1] += 1
        def share(data, ind):
            return self.ROUND1(data[ind]/sum(data)*100)
        
        newData = {"Да": [share(knewQazChO, 0), share(knewSyllabus, 0), share(knewQazolymp, 0)],
                   "Нет": [share(knewQazChO, 1), share(knewSyllabus, 1), share(knewQazolymp, 1)]}
        keyToInd = {"Знали ли вы<br>про существование<br>Коллегии химиков (qazcho.kz)?": 0,
                    "Знали ли вы<br>про существование<br>«силлабуса» республиканских<br>олимпиад?": 1,
                    "Знали ли вы<br>про существование<br>базы с заданиями прошлых<br>лет (qazolymp.kz)?": 2}
        traces = []
        for i, (yesno, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=list(keyToInd), x=yVals, name=yesno, orientation='h', marker_color=self.BINARYHOT[1-i],
                                 text=yValLabels, textposition='auto', legendrank=1-i))
        graph.horizontal_bar_plot(traces, "demographics/shortquestions", "Степень осведомленности участников РО о доступных ресурсах")

    def problem_difficulty(self, grade):
        graph = Graph()
        data = {"respa": [0, 0, 0, 0, 0],
                "oblast": [0, 0, 0, 0, 0],
                "region": [0, 0, 0, 0, 0],}
        for stage in self.STAGES:
            for student in self.raw[stage][1][grade]:
                data[stage][student.difficulty-1] += 1
        newData = {}
        for stage, diffdist in data.items():
            for difficulty, count in zip(range(5), diffdist):
                newData.setdefault(difficulty, [None]*3)[self.stageToInd[stage]] = self.ROUND1(count/sum(data[stage])*100)
        traces = []
        for i, (diff, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=self.xValsStages, x=yVals, name=f"{diff+1}/5", orientation='h', marker_color=self.RED5[i],
                                 text=yValLabels, textposition='auto', legendrank=4-i))
        graph.horizontal_bar_plot(traces, f"demographics/difficulty-grade{grade}", f"Насколько задания теоретического тура ({grade} кл.) были сложными? (1 - легкие, 5 - сложные)")

    def problem_volume(self, grade):
        graph = Graph()
        data = {"respa": [0, 0, 0, 0, 0],
                "oblast": [0, 0, 0, 0, 0],
                "region": [0, 0, 0, 0, 0],}
        for stage in self.STAGES:
            for student in self.raw[stage][1][grade]:
                data[stage][student.volume-1] += 1
        newData = {}
        for stage, diffdist in data.items():
            for difficulty, count in zip(range(5), diffdist):
                newData.setdefault(difficulty, [None]*3)[self.stageToInd[stage]] = self.ROUND1(count/sum(data[stage])*100)
        traces = []
        for i, (diff, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=self.xValsStages, x=yVals, name=f"{diff+1}/5", orientation='h', marker_color=self.RED5[i],
                                 text=yValLabels, textposition='auto', legendrank=4-i))
        graph.horizontal_bar_plot(traces, f"demographics/volume-grade{grade}", f"Насколько задания теоретического тура ({grade} кл.) были объемными? (1 - времени было достаточно, 5 - времени не хватало)")

    def problem_interest(self, grade):
        graph = Graph()
        data = {"respa": [0, 0, 0, 0, 0],
                "oblast": [0, 0, 0, 0, 0],
                "region": [0, 0, 0, 0, 0],}
        for stage in self.STAGES:
            for student in self.raw[stage][1][grade]:
                data[stage][student.interest-1] += 1
        newData = {}
        for stage, diffdist in data.items():
            for difficulty, count in zip(range(5), diffdist):
                newData.setdefault(difficulty, [None]*3)[self.stageToInd[stage]] = self.ROUND1(count/sum(data[stage])*100)
        traces = []
        for i, (diff, yVals) in enumerate(newData.items()):
            yValLabels = [f"{val}%" for val in yVals]
            traces.append(go.Bar(y=self.xValsStages, x=yVals, name=f"{diff+1}/5", orientation='h', marker_color=self.GREEN5[i],
                                 text=yValLabels, textposition='auto', legendrank=4-i))
        graph.horizontal_bar_plot(traces, f"demographics/interest-grade{grade}", f"Насколько задания теоретического тура ({grade} кл.) были интересными? (1 - скучные, 5 - интересные)")
         
if __name__ == "__main__":
    a = Analyzer()
    a.school_distribution()
    a.language_distribution()
    a.gender_distribution()
    a.first_timers()
    for grade in (9, 10, 11):
        a.first_timers_by_grade(grade)
    a.preparation_time()
    a.preparation_style()
    a.did_you_know()
    for grade in (9, 10, 11):
        a.problem_difficulty(grade)
        a.problem_volume(grade)
        a.problem_interest(grade)