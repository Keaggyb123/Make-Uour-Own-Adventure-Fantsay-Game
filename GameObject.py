import openai
import json
import IPython
import configparser
import random

def call_gpt(prompt):
    response = openai.Completion.create(model="text-davinci-003", 
                                        prompt=prompt, 
                                        temperature=0.7, 
                                        max_tokens=200,
                                        top_p=1)
    return response['choices'][0]['text']

def generate_randomInt(current,previous):
    while True:
        random_number = random.randint(0, 6)
        if random_number != current and random_number != previous:
            break
    return random_number

def get_image(prompt):
    response = openai.Image.create(
      prompt=prompt,
      n=1,
      size="512x512")
    image_url = response['data'][0]['url']
    IPython.display.display(IPython.display.Javascript('window.open("{url}");'.format(url=image_url)))

def AddAPI_Key():
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_key = config["openai"]["api_key"]
    openai.api_key = api_key

class GptGame:
    """ Game Object to track player progress """
    
    def __init__(self):
        
        self.background_info = ''
        self.current_state = []
        self.redo_stack = []
        self.name = ''
        self.player_class = ''
        self.starting_location = ''
        self.main_quest = ''
        self.side_quests = []
        # davinci-003 max token 4000
        # assuming 3.5char per token and room for 800 char response
        self.max_context_length = 3000
        
    def choose_name(self):
        print("What is your name? ")
        self.name = input()
        
    def choose_class(self):
        print('Character Class Suggestions: ')
        print("What class are you? (Swordmaster, Rogue, Ranger, Paladin, etc) ")
        self.player_class = input()
        
    def choose_starting_location(self):
        print('Starting Location Suggestions: ')
        print("Where are you located?  (a Throne Room, a Dungeon, an Abandoned Village etc) ") 
        self.starting_location = input()
        
    def update_max_context_length(self):
        self.max_context_length = input("max_context_length: ")
        
    def begin_game(self):
        # GENERATE BACKSTORY
        player_intro = f'You are a {self.player_class} called {self.name} in a dungeons and dragons story.\n'
        intro_prompt = 'What is your backstory? only give me a few sentences. call me "you"\n'
        prompt =  player_intro + intro_prompt
        backstory = call_gpt(prompt)
        self.background_info += f'You are {self.name} the {self.player_class}.\n' + backstory
        
        # GENERATE STARTER GEAR
        prompt = self.background_info + '\n\n' + 'What equiptment do you have? Refer to me as "you"'
        equiptment = call_gpt(prompt)
        self.background_info += equiptment
        
        # GENERATE INTRODUCTION
        prompt = self.background_info + '\n\n' + f'You are currently {self.starting_location}. What are you doing right now? Refer to yourself as "you".'
        # open ended location
        #'Where are you and what are you doing right now? Refer to yourself as "you".''
        game_start = call_gpt(prompt)
        self.background_info += game_start
        
        # GENERATE MAIN QUEST
        prompt = self.background_info + '\n\n' + 'What is your end goal? Give me only one sentence. Phrase it as a video game quest. Main Quest: '
        self.main_quest = call_gpt(prompt).replace('\n','')
        
        # GENERATE 1 SIDE QUEST
        prompt = self.background_info + '\n\n' + 'Give me one small task can you do in the area? Phrase it as a video game quest. Side Quest: '
        self.side_quests = [call_gpt(prompt).replace('\n','')]
        
    """ SAVE/LOAD GAME """
    
    def save_game(self):
        
        session_info = {'background_info': self.background_info,
                        'current_state': self.current_state,
                        'redo_stack': self.redo_stack,
                        'name': self.name,
                        'player_class': self.player_class,
                        'starting_location': self.starting_location,
                        'main_quest': self.main_quest,
                        'side_quests': self.side_quests,
                        'max_context_length': self.max_context_length}
        session_key = self.name + ' the ' + self.player_class
        
        with open('save_data.json', 'r') as openfile:
            save_data = json.load(openfile)
        
        save_data[session_key] = session_info
        
        with open('save_data.json', 'w') as outfile:
            outfile.write(json.dumps(save_data, indent=4))
        
        print('GAME SAVED SUCCESSFULLY')
            
    def load_game(self):
        
        with open('save_data.json', 'r') as openfile:
            save_data = json.load(openfile)
            
        print('Available Game Saves: ')
        for character in save_data:
            print(character)
        
        chosen_character = input('Character to Load: ')
        session_to_load = save_data[chosen_character]
        
        # LOAD DATA
        self.background_info = session_to_load['background_info']
        self.current_state = session_to_load['current_state']
        self.redo_stack = session_to_load['redo_stack']
        self.name = session_to_load['name']
        self.player_class = session_to_load['player_class']
        self.starting_location = session_to_load['starting_location']
        self.main_quest = session_to_load['main_quest']
        self.side_quests = session_to_load['side_quests']
        self.max_context_length = session_to_load['max_context_length']
        
        print('GAME LOADED SUCCESSFULLY')
        
    """ CONTEXT PROCESSING """
    
    def str_list_compressor(self, str_list):
        while len(str_list[0]) > self.max_context_length:
            #compress length
            prompt = f'Summarize the following text in less than {self.max_context_length} characters:\n\nText: ' + str_list[0] + '\n\nSummary: '
            str_list[0] = call_gpt(prompt)
        if len(str_list) > 1:
            return [str_list[0] + str_list[1]] + str_list[2:]
        else:
            return str_list[0]
    
    def process_context(self, str_list):
        output = str_list
        while type(output) != str:
            output = self.str_list_compressor(output)
        return output
        
    """ ACTIONS """

    def do(self):
        # clear redo_stack
        self.redo_stack = []
        user_input = input('I ')
        # retreive context of past actions
        context_info = self.process_context([self.background_info] + self.current_state)
        # call gpt3
        prompt = context_info + '\n\n' + 'You ' + user_input
        do_results = call_gpt(prompt).replace('\n','')
        while do_results.replace(' ', '') == '':
            prompt += ' '
            do_results = call_gpt(prompt).replace('\n','')
        # store gpt output
        self.current_state += ['You ' + user_input + do_results]
        # display results
        print(do_results)
            
    def say(self):
        # clear redo_stack
        self.redo_stack = []
        user_input = input('I Say')
        # retreive context of past actions
        context_info = self.process_context([self.background_info] + self.current_state)
        for action in self.current_state:
            context_info += '\n\n' + action
        # call gpt3
        prompt = context_info + '\n\n' + 'You Say: ' + '"' + user_input + '"' + '\n\nWhat happens next?'
        say_results = call_gpt(prompt).replace('\n','')
        while say_results.replace(' ', '') == '':
            prompt += ' '
            say_results = call_gpt(prompt).replace('\n','')
        # store gpt output
        self.current_state += ['You Say: ' + '"' + user_input + '"' + '\n' +say_results]
        #display results
        print(say_results)
        
    def see(self):
        user_input = input('I See')
        get_image(user_input)
           
    # Unstable - directing interacting with GPT can lead to odd results
    # ex: it may reply in first person
    def write_story(self):
        # clear redo_stack
        self.redo_stack = []
        user_input = input('I ')
        # retreive context of past actions
        context_info = self.process_context([self.background_info] + self.current_state)
        for action in self.current_state:
            context_info += '\n\n' + action
        # call gpt3
        prompt = context_info + '\n\n' + user_input + '\n\nWhat happens next?'
        write_results = call_gpt(prompt).replace('\n','')
        while write_results.replace(' ', '') == '':
            prompt += ' '
            write_results = call_gpt(prompt).replace('\n','')
        # store gpt output
        self.current_state += [user_input + write_results]
        # display results
        print(write_results)
            
    def continue_story(self):
        yesOrNo = input()
        if yesOrNo.lower() == 'y':
            # clear redo_stack
            self.redo_stack = []
            # retreive context of past actions
            context_info = self.process_context([self.background_info] + self.current_state)
            for action in self.current_state:
                context_info += '\n\n' + action
            # call gpt3
            prompt = context_info + '\n\n' + 'What happens next?'
            continue_results = call_gpt(prompt).replace('\n','')
            while continue_results.replace(' ', '') == '':
                prompt += ' '
                continue_results = call_gpt(prompt).replace('\n','')
            # store gpt output
            self.current_state += [continue_results]
            # display results
            print(continue_results)
        
    def introduce_fact(self):
        # clear redo_stack
        self.redo_stack = []
        user_input = input('Insert Fact Here: ')
        self.current_state += [user_input]
        
    def generate_side_quest(self):
        prompt = self.background_info + '\n\n' + 'Give me one small task can you do in the area? Phrase it as a video game quest. Side Quest: '
        generated_quest = call_gpt(prompt).replace('\n','')
        print(generated_quest)
        self.side_quests += [generated_quest]
    
    """ UNDO/REDO """
    
    def undo(self):
        if len(self.current_state) == 0:
            print('NO ACTION TO BE UNDONE')
        else:
            last_action = self.current_state.pop()
            self.redo_stack.append(last_action)
            print('ACTION SUCCESSFULLY UNDONE')
        
    def redo(self):
        if len(self.redo_stack) == 0:
            print('NO ACTION TO BE REDONE')
        else:
            action_to_redo = self.redo_stack.pop()
            self.current_state.append(action_to_redo)
            print('ACTION SUCCESSFULLY REDONE')
    
    """ INFORMATION DISPLAY """
        
    def display_current_state(self):
        full_game_state = str(self.background_info)
        for action in self.current_state:
            full_game_state += '\n\n' + action
        print(full_game_state)
        
    def display_questbook(self):
        print('QUEST BOOK')
        print('-----------------------------------------------------------------------------------------------------')
        print('Main Quest: ' + self.main_quest + '\n')
        print('Side Quests: ')
        for i, quest in enumerate(self.side_quests):
            print(f'    {i+1}. ' + quest)
        print('-----------------------------------------------------------------------------------------------------')
