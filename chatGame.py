import GameObject as obj
obj.AddAPI_Key()

def start_game():
    current = 0
    previous = 0
    print("Welcome to Fantasy Adverture Quest!")
    print('A Game made using the power of GPT')
    gptGame = obj.GptGame()
    print('Hello Adventurer')
    input()
    gptGame.choose_name() 
    gptGame.choose_class()
    gptGame.choose_starting_location()
    gptGame.begin_game()
    gptGame.display_questbook()
    gptGame.display_current_state()
    actions = ['What do you want to do? ',
                  'What do you want to say? ',
                  'What do you see? ',
                  'What happens next?',
                  'Do you want to let the Gods Decide?(Y/N)',
                  'You have a new Side Quest!',
                  'What is a little know fact about your Character?']
    methods = {
        0: gptGame.do,
        1: gptGame.say,
        2: gptGame.see,
        3: gptGame.write_story,
        4: gptGame.continue_story,
        5: gptGame.generate_side_quest,
        6: gptGame.introduce_fact
    }
    print(actions[0])
    methods[0]()
    i = 0
    while i < 10:
        i = 1+i
        if i % 3==0:
            yorn = input('Do you want to continue playing? (Y/N)')
            if yorn.lower() == 'n':
                print('Thank you for Playing')
                break
        numb = obj.generate_randomInt(current,previous)  
        print(actions[numb])
        methods[numb]()
        previous = current
        current = numb
        i = 1+i
        