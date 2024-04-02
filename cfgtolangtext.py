import os
import re
import time

class Roboter:
    def __init__(self, name, liste_Ver = [], liste_FRG = []):
        self.name = name
        self.Ver = liste_Ver
        self.FRG = liste_FRG
class FRG:
    def __init__(self, EA, Langtext, Typ, Signal, robotname = "Default"):
        self.EA = EA
        self.Langtext = Langtext
        self.Typ = Typ
        self.Signal = Signal
        self.Robotname = robotname
class VER:
    def __init__(self, EA, Langtext, Typ, Signal, robotname = "Default"):
        self.EA = EA
        self.Langtext = Langtext
        self.Typ = Typ
        self.Signal = Signal
        self.Robotname = robotname

def initialize(start_path):
    frg_vorlage = os.path.join(start_path, "cfg", "vorlagen", "FRGvorlage.csv")
    ver_vorlage = os.path.join(start_path, "cfg", "vorlagen", "VERvorlage.csv")
    grund_vorlage = os.path.join(start_path, "cfg", "vorlagen", "Grundlage.csv")
    liste_grund = []
    liste_grundlage = []
    with open (grund_vorlage, 'r') as f: 
        liste_grund = f.readlines()
    for ea in liste_grund:
        ea = ea.replace("\n","")
        liste_grundlage.append(ea)
    liste_FRG = splitVorlage(frg_vorlage)
    liste_Ver = splitVorlage(ver_vorlage)
    return liste_FRG, liste_Ver, liste_grundlage
 
def splitVorlage(file):
    lines = []
    liste = list()
    with open(file, 'r', encoding='windows-1252') as f:
        lines = f.readlines()
    for i,line in enumerate(lines):
        if i != 0:
            line = line.replace("\n","")
            splitted = line.split(";")
            liste.append(splitted)
    return liste

def createFrg(liste_FRG):
    liste = []
    for frg in liste_FRG:
        if frg[2] == "E":
            Langtext = f"(E{frg[0]}) Stellungsfreigabe {frg[1]} Anlage > Rob"
            robot_signal = f'diSPS_FrgStellung{frg[1]}'
            liste.append(FRG(robot_signal, Langtext, frg[2], frg[0]))
        if frg[2] == "A":
            Langtext = f"(A{frg[0]}) Werkzeugfreigabe {frg[1]} Rob > Anlage"
            robot_signal = f'doSPS_FrgStellung{frg[1]}'
            liste.append(FRG(robot_signal, Langtext, frg[2], frg[0]))
    return liste

def createVER(liste_VER):
    liste = []
    for frg in liste_VER:
        if frg[2] == "E":
            Langtext = f"(E{frg[0]}) Roboterfreigabe {frg[1]} Rob > Rob"
            robot_signal = f'diSPS_FrgRob{frg[1]}'
            liste.append(VER(robot_signal, Langtext, frg[2], frg[0]))
        if frg[2] == "A":
            Langtext = f"(A{frg[0]}) Roboterverriegelung {frg[1]} Rob > Rob"
            robot_signal = f'doSPS_VerrieglRob{frg[1]}'
            liste.append(VER(robot_signal, Langtext, frg[2], frg[0]))
    return liste

def readSignals(start_path):
    lines=[]
    for file in os.listdir(os.path.join(start_path, "cfg")):
        if file.endswith(".csv"):
            with open(os.path.join(start_path, "cfg", file), 'r', encoding='windows-1252') as f:
                lines = f.readlines()
            lines.remove(lines[0])
    return lines

def creatRobotList(roboter_file, vorlageliste_frg, vorlageliste_ver):
    vorlageliste_FRG = []
    vorlageliste_VER = []
    robots =[]
    list_frg = []
    list_ver = []
    for nver in vorlageliste_ver:
        vorlageliste_VER.append(nver)
    for nfrg in vorlageliste_frg:
        vorlageliste_FRG.append(nfrg)
    naming_pattern = r'[0-9][0-9][0-9][0-9][0-9][0-9][_][a-zA-Z][a-zA-Z0-9]+'
    for line in roboter_file:
        line = line.replace("\n","")
        splitted = line.split(";")
        freigaben = [frg for frg in vorlageliste_FRG if frg.Signal == splitted[1]]
        verriegelungen = [ver for ver in vorlageliste_VER if ver.Signal == splitted[1]]
        for freigabe in freigaben:
            newfrg = None
            newfrg = FRG(freigabe.EA, freigabe.Langtext, freigabe.Typ, freigabe.Signal)
            if freigabe.Typ == "E":
                if splitted[2].strip() != '' and splitted[2].strip() != '0_0':
                    if bool(re.search(r'^Position ', splitted[2].strip(), re.IGNORECASE)):
                        splitted[2] = splitted[2].lstrip('Position ')
                    if bool(re.search(naming_pattern, splitted[2].strip(), re.IGNORECASE)):
                        match = re.search(naming_pattern, splitted[2].strip(), re.IGNORECASE).group()
                        splitted[2] = splitted[2].replace(match + " ", "")
                    cleaned = splitted[2].strip().replace("ä", "ae").replace("ü", "ue").replace("ö", "oe").replace("ß", "ss").replace("Ä", "Ae").replace("Ü", "Ue").replace("Ö", "Oe")
                    newfrg.Langtext = f'({newfrg.Typ}{newfrg.Signal}) {cleaned}'
                    newfrg.Robotname = splitted[0].strip()
                    robots.append(newfrg.Robotname)
            elif freigabe.Typ == "A":
                if splitted[3].strip() != '' and splitted[3].strip() != '0_0':
                    match = []
                    if bool(re.search(r'^Position ', splitted[3].strip(), re.IGNORECASE)):
                        splitted[3] = splitted[3].lstrip('Position ')
                    if bool(re.search(naming_pattern, splitted[3].strip(), re.IGNORECASE)):
                        match = re.search(naming_pattern, splitted[3].strip(), re.IGNORECASE).group()
                        splitted[3] = splitted[3].replace(match + " ", "")
                    cleaned = splitted[3].strip().replace("ä", "ae").replace("ü", "ue").replace("ö", "oe").replace("ß", "ss").replace("Ä", "Ae").replace("Ü", "Ue").replace("Ö", "Oe")
                    newfrg.Langtext = f'({freigabe.Typ}{freigabe.Signal}) {cleaned}'
                    newfrg.Robotname = splitted[0].strip()
                    robots.append(newfrg.Robotname)
            list_frg.append(newfrg)
        for verriegelung in verriegelungen:
            newver = None
            newver = VER(verriegelung.EA, verriegelung.Langtext, verriegelung.Typ, verriegelung.Signal)
            if verriegelung.Typ == "E":
                if splitted[2].strip() != '' and splitted[2].strip() != '0_0':
                    newver.Langtext = f'({verriegelung.Typ}{verriegelung.Signal}) {splitted[2].strip().replace("ä", "ae").replace("ü", "ue").replace("ö", "oe").replace("ß", "ss").replace("Ä", "Ae").replace("Ü", "Ue").replace("Ö", "Oe")}'
                    newver.Robotname = splitted[0].strip()
                    robots.append(newver.Robotname)
            elif verriegelung.Typ == "A":
                if splitted[3].strip() != '' and splitted[3].strip() != '0_0':
                    newver.Langtext = f'({verriegelung.Typ}{verriegelung.Signal}) {splitted[3].strip().replace("ä", "ae").replace("ü", "ue").replace("ö", "oe").replace("ß", "ss").replace("Ä", "Ae").replace("Ü", "Ue").replace("Ö", "Oe")}'
                    newver.Robotname = splitted[0].strip()
                    robots.append(newver.Robotname)
            list_ver.append(newver)
    robots = sorted(set(robots))
    return list_ver, list_frg, robots

def addToRobot(robots, list_frg, list_ver):
    robot_liste = []
    for robot in robots:
        rob = None
        rob = Roboter(name=robot, liste_Ver = [], liste_FRG = [])
        for frg in list_frg:
            if frg.Robotname == robot:
                rob.FRG.append(FRG(frg.EA, frg.Langtext, frg.Typ, frg.Signal, frg.Robotname))
        for ver in list_ver:
            if ver.Robotname == robot:
                rob.Ver.append(VER(ver.EA, ver.Langtext, ver.Typ, ver.Signal, ver.Robotname))
        robot_liste.append(rob)
    return robot_liste
            
def createLangtext(robot_liste, start_path, liste_grund): 
    for robot in robot_liste:
        csv_file = []
        for grund in liste_grund:
            csv_file.append(grund)
        for frg in robot.FRG:
            csv_file.append(f"{frg.EA};{frg.Langtext}")
        for ver in robot.Ver:
            csv_file.append(f"{ver.EA};{ver.Langtext}")
        try:
            os.makedirs(f"{start_path}/Langtexte")
        except:
            #print("Langtexte allready exists")
            pass
        with open(f"{start_path}/Langtexte/{robot.name}.csv", 'w') as f:
            f.write("\n".join(csv_file))
    
if __name__=="__main__":
    start_path = os.getcwd()
    try:
        liste_FRG, liste_Ver, liste_grund = initialize(start_path)
        vorlageliste_FRG = createFrg(liste_FRG)
        vorlageliste_VER = createVER(liste_Ver)
        roboter_file = readSignals(start_path)
        list_ver, list_frg, robots = creatRobotList(roboter_file, vorlageliste_FRG, vorlageliste_VER)
        robot_list = addToRobot(robots, list_frg, list_ver)
        createLangtext(robot_list, start_path, liste_grund)
    except Exception as e:
        print(f"Problem -> {e}")
        try:
            os.makedirs(f"{start_path}/logs")
        except:
            #print("logs allready exists")
            pass
        timestr = time.strftime("%Y%m%d_%H%M%S")
        with open(f"{start_path}/logs/{timestr}_error.txt", 'a') as f:
            f.write(f"Problem -> {e}\n")