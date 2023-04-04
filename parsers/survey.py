import json
from objects.response import Response

def parse_responses(stage):
    """
    Parses JSON responses from the specified stage and creates Response objects for each participant. 

    Args:
    - stage (str): the stage of the competition to parse responses from
    
    Returns:
    - full (list): a list of Response objects representing all participants
    - bygrade (dict): a dictionary of Response objects, with keys as grades and values as lists of participants in that grade

    """
    with open(f"data/feedback/{stage}.json", 'r') as f:
        responses = json.load(f)
    full = []
    bygrade = {9: [], 10: [], 11: []}
    for response in responses:
        re = Response()
        re.name = response[2][1]
        re.oblast = response[3][1]
        re.school = response[4][1]
        re.gradeStudy = int(response[5][1].split(" ")[1])
        re.gradeParticipate = int(response[6][1].split(" ")[1])
        re.langStudy = response[7][1]
        re.langParticipate = response[8][1]
        re.gender = response[9][1]
        re.email = response[10][1] if "@" in response[10][1] else None
        re.firstTime = response[11][1] != "Да"
        re.prepTime = response[12][1]
        re.prepStyle = response[13][1]
        re.knewQazChO = response[14][1] == "Да"
        re.knewSyllabus = response[15][1] == "Да"
        re.knewQazolymp = response[16][1] == "Да"
        re.prepDesc = response[17][1]
        re.difficulty = int(response[18][1])
        re.interest = int(response[19][1])
        re.volume = int(response[20][1])
        re.feedback = response[21][1]
        for problem in response[22:]:
            grade, num = problem[0].split("№")[1].split('.')[0].split('-')
            if int(grade) == re.gradeParticipate:
                setattr(re, f"problem{num}", problem[1])
                re.numprobs = int(num)
        full.append(re)
        bygrade[re.gradeParticipate].append(re)
    return full, bygrade


if __name__ == "__main__":
    o = parse_responses("respa")
    print(o)