from psychopy import gui, visual, event, core
import csv
import yaml
from typing import Dict
import os
conf: Dict = yaml.load(open('confin.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)
tria: Dict = yaml.load(open('trials.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)

keys_storage = []
decided_storage = []
keys_logic_values = []
decided_logic_values = []
trial_numbers = []
task_type = tria['TRIAL_TYPE']

#Zegar
timer = core.Clock()
reaction_time = []

# Pytanie o ID
info = {"Identyfikator": "", "Wiek": "", "Płeć": ["Mężczyzna", "Kobieta", "Inne"]}
infoDlg = gui.DlgFromDict(dictionary=info, title="Informacje o badanym")
if not infoDlg.OK:
   core.quit()

# Lista opisów dla każdej próby
trial_descriptions = tria['TRIAL_DESCRIPTIONS']

# Lista kart dla każdej próby
cards_list = tria['CARDS_LIST']

# Lista tłumaczeń prób na wartśći logiczne
translations_list = tria['TRANSLATOR']

# Utworzenie okna
win = visual.Window(
   size=conf['RESOLUTION'], fullscr=conf['FULL_SCR'],
   screen=0, winType='pyglet', allowGUI=conf['ALLOW_GUI'],
   allowStencil=False, monitor='testMonitor', color=conf['BACK_COLOR'],
   colorSpace='rgb', blendMode='avg', useFBO=True,
   units=conf['UNITS'])

# Wstęp i zakończenie
def show_in_or_out(inorout_text):
    in_or_out_text = visual.TextStim(win=win, text=inorout_text, pos=(0, conf['TEXT_TRO_Y']), color=conf['TEXT_COLOR'],
                                     wrapWidth=1.5, height=conf['TEXT_HEIGHT'], alignText='center')
    in_or_out_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

# Funkcja wyświetlająca próbę
def show_trial(description, cards,trial_index):

    letters = conf['USED_KEYS']
    over_card_bag = []
    card_text_bag = []
    card_white_bag = []
    card_grey_bag = []
    keys_memory = []


    # Tworzenie opisu zadania
    description_text = visual.TextStim(
        win=win, text=description, pos=(0, conf['TEXT_DES_Y']), color=conf['TEXT_COLOR'], 
        wrapWidth=1.5,height=conf['TEXT_HEIGHT'],alignText='center')
    

    # Tworzenie tekstu czekającego na karty
    waiting_text = visual.TextStim(
        win=win, text=conf["TEXT_WAIT"], color=conf['TEXT_COLOR'], pos=(0,conf['TEXT_WAIT_Y']), 
        height=conf['TEXT_HEIGHT'],alignText='center')
    

    # Tworzenie tekstu czekającego na zatwierdzenie
    confirmation_text = visual.TextStim(
        win=win, text=conf['TEXT_CONFI'], color=conf['TEXT_COLOR'], pos=(0, conf['TEXT_CONFI_Y']), 
        height=conf['TEXT_HEIGHT'],alignText='center')


    # Tworzenie kart i liter nad kartami
    for i, card_label in enumerate(cards):
        x_pos = -0.45 + i * 0.3
        
        card_white = visual.Rect(
            win=win, width=0.25, height=0.35, pos=(x_pos, -0.2 ),
            fillColor=conf['WHITE_CARD_COLOR'], lineColor='black',colorSpace='rgb')
        
        card_grey = visual.Rect(
            win=win, width=0.25, height=0.35, pos=(x_pos, -0.2 ),
            fillColor=conf['GREY_CARD_COLOR'], lineColor='black',colorSpace='rgb')
        
        over_card = visual.TextStim(
            win, text=(letters[i].upper()), pos=(x_pos, conf['TEXT_OVER_Y']), 
            color=conf['TEXT_OVER_COLOR'], height=conf['TEXT_OVER_HEIGHT'], wrapWidth=0.2, alignText='center')

        card_text = visual.TextStim(
            win=win, text=card_label, pos=(x_pos, conf['TEXT_CARD_Y']), 
            color=conf['TEXT_CARD_COLOR'], height=conf['TEXT_CARD_HEIGHT'], wrapWidth=0.2, alignText='center')
        
    
        over_card_bag.append(over_card) # Lista gromadząca "rysunki" liter nad kartą
        card_text_bag.append(card_text) # Lista gromadząca "rysunki" tekstu na kartcie
        card_white_bag.append(card_white) # Lista gromadząca "rysunki" niewybranych kart
        card_grey_bag.append(card_grey) # Lista gromadząca "rysunki" wybranych kart

    # Wstępne rysowanie elementów na ekranie
    description_text.draw()
    waiting_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])


    # Początek pomiaru czasu reakcji
    win.callOnFlip(timer.reset)

    # Rysowanie razem z kartami
    bank = [0,0,0,0] # stan (i wygląd) każdej karty na ekranie - 0: nie wybrana, 1: wybrana
    keys = event.getKeys(keyList=["space"])
    while keys !=["space"]: # pętla się kręci dopóki nie zostanie wciśnieta spacja
        description_text.draw()
        confirmation_text.draw()
        keys = event.getKeys(keyList=["space"]+letters)

        for i in range(4): # pętla zmieniająca stan kart i przyjmująca klawisze
            if keys == [letters[i]]:
                bank[i] = (bank[i]+1)%2 # zmiana stanu karty w banku
                keys_memory.extend(keys) # zapisuje klawisze dla jednej próby
                keys = [] 

        for i in range(4): # pętla uaktualnia stan kart względem banku
            if bank[i] == 0:
                card_white_bag[i].draw()
                card_text_bag[i].draw()
                over_card_bag[i].draw()
            if bank[i] == 1:
                card_grey_bag[i].draw()
                card_text_bag[i].draw()
                over_card_bag[i].draw()

        win.flip(clearBuffer=False)
    win.flip()

    # Rejestrowanie czasu reakcji
    reaction_time.append(str(timer.getTime()))

    # Zapisywanie numeru próby
    trial_numbers.append(str(trial_index+1))

    # Ustawianie przekładu klawiszy na wartości logiczne odpowiadające im w danej turze
    current_translation=translations_list[trial_index]
    current_dict = {letters[i]:current_translation[i] for i in range(4)}

    # Zapisywanie historii wciskania klawiszy przez badanego
    keys_storage.append(keys_memory) # Klawisze
    keys_logic_values.append([str(current_dict[keys_memory[i]]) for i in range(len(keys_memory))]) # Wartości logiczne

    # Zapisywanie ostatecznych odpowiedzi badanego
    decided_memory = [letters[x] for x in range(len(letters)) if bank[x]==1] # Przekłada końcowy stan kart na wybrane klawisze
    decided_storage.append(decided_memory) # Klawisze
    decided_logic_values.append([str(current_dict[decided_memory[i]]) for i in range(len(decided_memory))]) # Wartość logiczna

# Wyświetlanie wstępu
show_in_or_out(conf['TEXT_INTRO'])

# Przechodzenie przez wszystkie próby
for trial_id, (description, cards) in enumerate(zip(trial_descriptions, cards_list)):
   show_trial(description, cards,trial_id)

# Pokazywanie zakończenia
show_in_or_out(conf['TEXT_OUTRO'])
win.close()

# Zapisywanie danych do pliku CSV
csv_filename = conf["FILE_TITLE"]
file_exists = os.path.isfile(csv_filename)
with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=',') #tego mi nie pozwoliło przetestować, ; zamiast ,
    # Nagłówki kolumn (dodawane tylko, gdy plik jest tworzony po raz pierwszy - przy pierwszej osobie badanej)
    if not file_exists:
        writer.writerow(conf["SAVED"])
    # Dane eksperymentu
    for trial_numbers, task_type, keys, decided, keys_logic_values, decided_logic_values,reaction_time in zip(
        trial_numbers, task_type,keys_storage, decided_storage, keys_logic_values, decided_logic_values,reaction_time):
        writer.writerow([info["Identyfikator"], info["Wiek"], info["Płeć"], "".join(trial_numbers), " ".join(task_type),
        " ".join(keys)," ".join(decided)," ".join(keys_logic_values)," ".join(decided_logic_values),"".join(reaction_time)])

core.quit()
