#####---------- Modules ----------#####

from concurrent.futures import ThreadPoolExecutor
import atexit
import calendar
import datetime
import difflib
import keyword
import os
import pathlib
import random
import readline
import re
import shelve
import shlex
import shutil
import string
import sys
import tempfile
import termios
import time
import tty
import zipfile
try:
    import holidays
    import password_strength
    import requests
    import simpleeval
    import speedtest
    import zxcvbn
except ModuleNotFoundError:print("Installing packages.\n");os.system("pip install -r requirements.txt")

#####---------- Prepare Data ----------#####

data = {
"Username": f"User {random.randint(1, 100)}",
"Loading": True,
"CommandHistory": [],
}
with shelve.open("Data") as db:
    for key, value in data.items():
        if key in db:pass
        else:db[key] = value

#####---------- Get Data ----------#####

def get_username()->str:
    username = shelve.open("Data")["Username"].strip();username = username
    if not username:shelve.open("Data")["Username"] = f"User {random.randint(1, 100)}";return username
    return username

def get_loading()->bool:
    loading = shelve.open("Data")["Loading"];loading = loading
    if loading in [True, False]:return loading#True if loading == "True" else False
    shelve.open("Data")["Loading"] = True;return True

def get_command_history()->list:
    return shelve.open("Data")["CommandHistory"]

#####---------- Main ----------#####

def getch(prompt:str="")->str:
    print("\033[?25h", end="");print(prompt, end="", flush=True);fd = sys.stdin.fileno();old_settings = termios.tcgetattr(fd)
    try:tty.setraw(sys.stdin.fileno());ch = sys.stdin.read(1);print(ch, end="", flush=True)
    finally:termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print();print("\033[?25l", end="");return ch

def loading_animation()->None:
    if get_loading():
        for i in range(1, len("PyCommandExecutor")+1):print(f"\r{'PyCommandExecutor'[:i]}", end="", flush=True);time.sleep(random.uniform(0, .20))
        print("\n\033[A\033[K", end="")

def holiday()->str: # Replace US with your country code.
    return holidays.country_holidays("US").get(datetime.date.today(), "Today is not a holiday.")

@atexit.register
def exit_program()->None:
    print("\033[0m\033[?25h", end="")

def Main()->None:
    print("\033c\033[?25l", end="")
    loading_animation()
    print("""\033[92;1m__   ___         ___                                    _  ___                      _               __
\ \ | _ \ _  _  / __| ___  _ __   _ __   __ _  _ _   __| || __|__ __ ___  __  _  _ | |_  ___  _ _  / /
 > >|  _/| || || (__ / _ \| '  \ | '  \ / _` || ' \ / _` || _| \ \ // -_)/ _|| || ||  _|/ _ \| '_|< <
/_/ |_|   \_, | \___|\___/|_|_|_||_|_|_|\__,_||_||_|\__,_||___|/_\_\\\___|\__| \_,_| \__|\___/|_|   \_\\
          |__/\033[0m\n""")
    print(f"Welcome to PyCommandExecutor, {get_username()}!\n\nEnter \"Commands?\" for commands, \"Exit Imm\" to exit.\nUsername: \"{get_username()}\"\nLoading: {get_loading()}\nHoliday: {holiday()}\n{time.strftime('Date: %A, %B %d, %Y')}\n{time.strftime('Time: %I:%M:%S %p')}\n")
    valid_commands = [
"Loading", "RerunCode", "Matrix", "SelectRandomNumber", "DaysUntil",
"TimeToLoadUrl", "Timer", "Calendar", "SelfDestruct", "Stopwatch",
"SelectRandomItem", "DeleteCommandHistory", "GenerateUsername", "CheckInternetSpeed", "Commands?",
"ShowCommandHistory", "Exit", "Time", "GeneratePassword", "Clear",
"Reset", "ChangeUsername", "CheckInternet", "CheckPasswordStrength", "UpdateCode",
 
    ]
    input_text = "\033[1;92m>>>\033[1;33m "
    stopwatch = False
    previous_directory = None
    running = True
    start_time = time.time()
    while running:
        try:
            print("\033[?25h", end="");command = input("\033[1;90m[\033[0m YYYY/MM/DD HH:MM:SS XM \033[1;90m] "+input_text).strip();print("\033[90m\033[?25l", end="") # Command - ex. Commands? | Evaluate - ex. 1 + 1 | Print text - ex. "Hello, World"
            if command:
                time_of_command = time.strftime("%Y/%m/%d %I:%M:%S %p");print(f"\033[A\033[K\033[1;90m[\033[0m {time_of_command} \033[1;90m] {input_text}{command}\033[0;90m");parts = shlex.split(command);main_command = parts[0]
                try:print(simpleeval.simple_eval(command));print();continue
                except:pass
                if command not in ["ShowCommandHistory", "DeleteCommandHistory"]:
                    with shelve.open("Data") as db:temp_list = db["CommandHistory"];temp_list.append(f"\"{command}\" - {time_of_command}");db["CommandHistory"] = temp_list
            else:print("\033[A\033[K", end="");continue
            if command == "Commands?":print("""- Commands?
- ShowCommandHistory
- DeleteCommandHistory
- Clear
- Reset
- SelfDestruct
- RerunCode
- UpdateCode
- Exit NA｜(Imm)
- ChangeUsername <<Username>>
- Loading (True)｜(False)｜(Check)
- Time
- DaysUntil <<Year-Month-Day>> NA｜<<Year-Month-Day>>
- Calendar NA｜<<Year>>
- Timer <<Hour-Minute-Second>>｜<<Minute-Second>>
- Stopwatch (Start)｜(Stop)｜(Reset)
- SelectRandomItem <<ListOfItems>>
- SelectRandomNumber <<Number>> <<Number>>
- GeneratePassword <<Length>> <<NumberOfPasswords>> NA｜(Letters) NA｜(Numbers) NA｜(SpecialCharacters)
- CheckPasswordStrength <<Password>>
- GenerateUsername <<NumberOfUsernames>>
- Matrix
- TimeToLoadUrl <<Url>>
- CheckInternet
- CheckInternetSpeed
""")
            elif command == "UpdateCode":
                print()
                while True:
                    confirm = getch("\033[A\033[KConfirm (Y/N): ").lower()
                    if confirm == "y":
                        print(f"\033[A\033[K", end="");repo_url = "https://github.com/AnonymousUser12345-droid/PyCommandExecutor/archive/refs/heads/main.zip";current_dir = pathlib.Path(__file__).parent.resolve();response = requests.get(repo_url);response.raise_for_status()
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:tmp_file.write(response.content);zip_path = tmp_file.name
                        with tempfile.TemporaryDirectory() as temp_dir:
                            with zipfile.ZipFile(zip_path, "r") as zip_ref:zip_ref.extractall(temp_dir)
                            extracted_dir = pathlib.Path(temp_dir) / "PyCommandExecutor-main"
                            for item in extracted_dir.iterdir():
                                if item.name not in [".git", ".github", "__pycache__"]:
                                    dest = current_dir / item.name
                                    if item.is_dir():
                                        if dest.exists():shutil.rmtree(dest)
                                        shutil.copytree(item, dest)
                                    else:shutil.copy2(item, dest)
                        os.remove(zip_path);print("\033[A\033[KUpdate completed successfully.\n");exit()
                    elif confirm == "n":print("\033[A\033[KUpdate code cancelled.\n");break
                    else:continue
            elif main_command == "DaysUntil":
                if len(parts) >= 2:
                    try:
                        target_date = datetime.datetime.strptime(parts[1], "%Y/%m/%d").date()
                        if len(parts) >= 3:
                            target_date2 = datetime.datetime.strptime(' '.join(parts[2:]), "%Y/%m/%d").date()
                            if target_date > target_date2:print("Invalid argument. Target date cannot be in the past.\n");continue
                            else:days_left = (target_date2 - target_date).days
                            if days_left == 0:print(f"The target date is today if the current date is {target_date}.\n")
                            else:print(f"There are {days_left} day{'' if days_left == 1 else 's'} left until {target_date2} if the current date is {target_date}.\n")
                        else:
                            today = datetime.date.today()
                            if target_date < today:print("Invalid argument. Target date cannot be in the past.\n");continue
                            else:days_left = (target_date - today).days
                            if days_left == 0:print("The target date is today.\n")
                            else:print(f"There are {days_left} day{'' if days_left == 1 else 's'} left until {target_date}.\n")
                    except ValueError as e:print(f"Invalid argument. {e}. Please use the format years-months-days.\n")
                else:print("Invalid argument. Please enter Year-Month-Day and NA or Year-Month-Day.\n")
            elif command == "Matrix":
                while True:
                    try:
                        if random.random() < .09:print(end='\n', flush=True)
                        if random.random() < .005625:print(end='\n\n', flush=True)
                        if random.random() < .0003515625:print(end='\n\n\n', flush=True)
                        if random.random() < .00002197265625:print(end='\n\n\n\n', flush=True)
                        if random.random() < .000001373291015625:print(end='\n\n\n\n\n', flush=True)
                        random_gibberish_code = list("".join(random.choice(string.ascii_letters+string.digits+string.punctuation+" "+"  "+"   "+"    "+"     ")) for _ in range(random.randint(random.randint(28, 60), random.randint(84, 90))))
                        for _ in range(1, random.randint(1, 10)+1):pos = random.randint(0, len(random_gibberish_code));random_gibberish_code[pos:pos] = list(random.choice([random.choice((''.join(char.upper() if random.random() < .5 else char.lower() for char in keyword), keyword.upper(), keyword.lower(), keyword)) for keyword in keyword.kwlist+["then", "fi", "do", "done", "esac", "function", "select", "read", "echo", "test"]]))
                        print("\033[0m"+random.choice(["\033[32m", "\033[92m", "\033[1;32m", "\033[2;32m", "\033[1;92m", "\033[2;92m"])+"".join(random_gibberish_code), flush=True);time.sleep(0.01)
                    except (KeyboardInterrupt, EOFError):print();print();break
            elif main_command == "CheckPasswordStrength":
                if len(parts) > 1:
                    if not ' '.join(parts[1:]).strip():print("Invalid arument. Please enter Password.\n");continue
                    result = zxcvbn.zxcvbn(' '.join(parts[1:]).replace(" ", ""));result2 = password_strength.PasswordStats(' '.join(parts[1:]));repeated = len([m.group(0) for m in re.finditer(r'(.)\1+', ' '.join(parts[1:]))]);print(f"""Password:                             \"{' '.join(parts[1:])}\"\nLength:                               {len(' '.join(parts[1:]))}\nEntropy:                              {result2.entropy_bits:.1f} bit{'' if result2.entropy_bits in [0, 1] else 's'}\nComposition:\nLetters:                              {len(re.findall(r'[A-Z]', ' '.join(parts[1:]))) + len(re.findall(r'[a-z]', ' '.join(parts[1:])))}\nUppercase:                            {len(re.findall(r'[A-Z]', ' '.join(parts[1:])))}\nLowercase:                            {len(re.findall(r'[a-z]', ' '.join(parts[1:])))}\nNumbers:                              {len(re.findall(r'[0-9]', ' '.join(parts[1:])))}\nSpecialCharacters:                    {len(' '.join(parts[1:])) - (len(re.findall(r'[A-Z]', ' '.join(parts[1:]))) + len(re.findall(r'[a-z]', ' '.join(parts[1:]))) + len(re.findall(r'[0-9]', ' '.join(parts[1:]))))}\nRepeated:                             {repeated}\nScore:                                {result['score']}/4\nStrength:                             {result2.strength()}\nConsidered random:                    {result['score'] >= 3}\nEstimated crack time:                 {result['crack_times_display']['offline_slow_hashing_1e4_per_second']}\nWarning:                              {result['feedback']['warning'] or 'No warning'}\nSuggestions:                          {' '.join(result['feedback']['suggestions']) or 'No suggestions'}\n""")
                else:print("Invalid arument. Please enter Password.\n")
            elif main_command == "GeneratePassword":
                if len(parts) >= 3:
                    try:length = int(parts[1])
                    except ValueError:print("Invalid argument. Please enter a number for the length.\n");continue
                    try:num_of_passwords = int(parts[2])
                    except ValueError:print("Invalid argument. Please enter a number for the number of passwords.\n");continue
                    if length < 1:print("Invalid argument. Password length must be at least 1 character.\n");continue
                    if num_of_passwords < 1:print("Invalid argument. Number of passwords must be at least 1.\n");continue
                    if len(parts[3:]) != len(set(parts[3:])):print("Invalid argument. Each option can only be specified once.\n");continue
                    if not set(parts[3:]).issubset({"Letters", "Numbers", "SpecialCharacters"}):print("Invalid argument. Options must be Letters, Numbers, or SpecialCharacters.\n");continue
                    Letters = "Letters" in set(parts[3:])
                    Numbers = "Numbers" in set(parts[3:])
                    SpecialCharacters = "SpecialCharacters" in set(parts[3:])
                    characters = ""
                    if Letters:characters += string.ascii_letters
                    if Numbers:characters += string.digits
                    if SpecialCharacters:characters += string.punctuation
                    if not characters:print("Invalid argument. Please select at least one character type.\n");continue
                    def password(length,characters):
                        while True:
                            password = ''.join(random.choices(characters, k=length))
                            if zxcvbn.zxcvbn(password)["score"] >= 3 and password_strength.PasswordPolicy.from_names(strength=0.66).test(password) == []:return password
                    def generate_password(length,num_of_passwords,characters):
                        with ThreadPoolExecutor() as executor:passwords = [future.result() for future in [executor.submit(password,length,characters) for _ in range(num_of_passwords)]];print(f"Generated password{'' if num_of_passwords == 1 else 's'}:");print("\n".join([f"{i}. {password}" for i, password in enumerate(passwords, 1)])+"\n")
                    generate_password(length,num_of_passwords,characters)
                else:print("Invalid argument. Please enter Length, NumberOfPasswords, NA or Letters, Numbers and NA or SpecialCharacters.\n")
            elif main_command == "TimeToLoadUrl":
                if len(parts) > 1:
                    url = ' '.join(parts[1:])
                    if " " in url:print("Invalid argument. Url cannot contain spaces.\n");break
                    if ("https" or "http") not in url:url = "https://"+url
                    start_time = time.time();requests.get(url);end_time = time.time();print(f"Time spent: [{int((end_time - start_time) // 3600):02d}:{int((end_time - start_time) % 3600 // 60):02d}:{int((end_time - start_time) % 60):02d}.{int(((end_time - start_time) - int(end_time - start_time)) * 1000):02d}] loading url.\n")
                else:print("Invalid argument. Please enter Url.\n")
            elif command == "CheckInternetSpeed":
                while True:
                    try:start_time = time.time();st = speedtest.Speedtest();st.get_best_server();print(f"Download speed: {(st.download() / 10000000):.2f} Mbps\nUpload speed:   {(st.upload() / 1000000):.2f} Mbps\nPing:           {(st.results.ping):.2f} ms");end_time = time.time();print(f"Duration:       [{int((end_time - start_time) // 3600):02d}:{int((end_time - start_time) % 3600 // 60):02d}:{int((end_time - start_time) % 60):02d}.{int(((end_time - start_time) - int(end_time - start_time)) * 1000):02d}]\n");break
                    except TimeoutError:time.sleep(5);continue
            elif command == "CheckInternet":
                try:requests.get("https://www.google.com", timeout=10).raise_for_status();internet_connection = True
                except Exception:internet_connection = False
                print(f"The internet connection is {'' if internet_connection else 'un'}stable.\n")
            elif main_command == "Stopwatch":
                if len(parts) > 1:
                    if ' '.join(parts[1:]) == "Start":
                        if stopwatch == False:stopwatch_start_time = time.time();stopwatch = True;print("Stopwatch is running.\n")
                        else:print("Stopwatch is already running.\n")
                    elif ' '.join(parts[1:]) == "Stop":
                        if stopwatch:elapsed = time.time() - stopwatch_start_time;stopwatch = False;print(f"Stopwatch stopped.\nElapsed time: [{int((elapsed) // 3600):02d}:{int((elapsed) % 3600 // 60):02d}:{int((elapsed) % 60):02d}.{int(((elapsed) - int(elapsed)) * 1000):02d}]\n")
                        else:print("Stopwatch is not running.\n")
                    elif ' '.join(parts[1:]) == "Reset":stopwatch = False;stopwatch_start_time = None;print("Stopwatch reset.\n")
                    else:print("Invalid argument. Please enter Start, Stop or Reset.\n")
                else:print("Invalid argument. Please enter Start or Stop or Reset.\n")
            elif main_command == "GenerateUsername":
                if len(parts) >= 2:
                    try:num_of_usernames = int(' '.join(parts[1:]))
                    except ValueError:print("Invalid argument. Please enter a number for the number of usernames.\n");continue
                    if num_of_usernames < 1:print("Invalid argument. Please enter a number greater than or equal to 1.\n");continue
                    for i in range(1, num_of_usernames + 1):noun = random.choice(["airplane","apple","automobile","ball","balloon","banana","beach","bird","boat","boot","bottle","box","breeze","bug","bush","butter","canoe","carrot","cartoon","cello","chair","cheese","coast","coconut","comet","cream","curtain","daisy","desk","diamond","door","earth","elephant","emerald","fire","flamingo","flower","flute","forest","free","giant","giraffe","glove","grape","grasshopper","hair","hat","hill","house","ink","iris","jade","jungle","kangaroo","kayak","lake","lemon","lightning","lion","lotus","lump","mango","mint","monkey","moon","motorcycle","mountain","nest","oboe","ocean","octopus","onion","orange","orchestra","owl","path","penguin","phoenix","piano","pineapple","planet","pond","potato","prairie","quail","rabbit","raccoon","raid","rain","raven","river","road","rosebud","ruby","sea","ship","shoe","shore","shrub","sitter","skates","sky","socks","sparrow","spider","squash","squirrel","star","stream","street","sun","table","teapot","terrain","tiger","toast","tomato","trail","train","tree","truck","trumpet","tuba","tulip","umbrella","unicorn","unit","valley","vase","violet","violin","water","wind","window","zebra","zoo"]);adjective = random.choice(["ancient","antique","aquatic","baby","basic","big","bitter","black","blue","bottle","bottled","brave","breezy","bright","brown","calm","charming","cheerful","chummy","classy","clear","clever","cloudy","cold","cool","crispy","curly","daily","deep","delightful","dizzy","down","dynamic","elated","elegant","excited","exotic","fancy","fast","fearless","festive","fluffy","fragile","fresh","friendly","funny","fuzzy","gentle","gifted","gigantic","graceful","grand","grateful","great","green","happy","heavy","helpful","hot","hungry","husky","icy","imaginary","invisible","jagged","jolly","joyful","joyous","kind","large","light","little","lively","lovely","lucky","lumpy","magical","manic","melodic","mighty","misty","modern","narrow","new","nifty","noisy","normal","odd","old","orange","ordinary","painless","pastel","peaceful","perfect","phobic","pink","polite","precious","pretty","purple","quaint","quick","quiet","rapid","red","rocky","rough","round","royal","rugged","rustic","safe","sandy","shiny","silent","silky","silly","slender","slow","small","smiling","smooth","snug","soft","sour","strange","strong","sunny","sweet","swift","thirsty","thoughtful","tiny","uneven","unusual","vanilla","vast","violet","warm","watery","weak","white","wide","wild","wilde","windy","wise","witty","wonderful","yellow","young","zany"]);print(f"""{random.choice([f"{random.choice([adjective.title(), adjective.lower(), adjective.upper()])}{random.choice(['_', '-', '.', ''])}{random.choice([noun.title(), noun.lower(), noun.upper()])}", f"{random.choice([noun.title(), noun.lower(), noun.upper()])}"])}{''.join(str(random.randint(1, 9)) for _ in range(random.randint(1, 4))) if random.choice([True, False]) else ''}""")
                    print()
                else:print("Invalid argument. Please enter NumberOfUsernames.\n")
            elif main_command == "Calendar":
                if len(parts) > 1:
                    try:print(calendar.calendar(int(' '.join(parts[1:]))));print('' if ' '.join(parts[1:]) != str(datetime.date.today().year) else f'Date: {time.strftime(f"%A, %B %d, %Y")}\n\n', end='')
                    except ValueError:print("Invalid argument. Year must be a number.\n")
                else:print(calendar.calendar(datetime.date.today().year));print(f'Date: {time.strftime(f"%A, %B %d, %Y")}\n')
            elif command == "Clear":print("\033c", end="")
            elif command == "RerunCode":print("\033c", end="");os.system(f"python {__file__}")
            elif main_command == "ChangeUsername":
                if len(parts) > 1:
                    new_name = ' '.join(parts[1:]).lstrip()
                    if not new_name:print("Invalid argument. Username cannot be empty.\n");continue
                    if new_name == "default":shelve.open("Data")["Username"] = f"User {random.randint(1, 100)}"
                    else:shelve.open("Data")["Username"] = new_name
                else:print("Invalid argument. Please enter Username.\n")
            elif main_command == "Loading":
                if len(parts) > 1:
                    loading = shelve.open("Data")["Loading"]
                    if ' '.join(parts[1:]) == "True":
                        if loading == False:shelve.open("Data")["Loading"] = True;loading = True;print("Loading successfully set to True.\n")
                        else:print("Loading already set to True.\n")
                    elif ' '.join(parts[1:]) == "False":
                        if loading:shelve.open("Data")["Loading"] = False;loading = False;print("Loading successfully set to False.\n")
                        else:print("Loading already set to False.\n")
                    elif ' '.join(parts[1:]) == "Check":print("Loading:", get_loading());print()
                    else:print("Invalid argument. Please enter True, False or Check.\n")
                else:print("Invalid argument. Please enter True or False or Check.\n")
            elif main_command == "Timer":
                if len(parts) > 1:
                    try:
                        time_str = ' '.join(parts[1:]);time_parts = list(map(int, time_str.split(':')))
                        if len(time_parts) == 2:hours = 0;minutes, seconds = time_parts
                        elif len(time_parts) == 3:hours, minutes, seconds = time_parts
                        else:print("Invalid argument. Please use the format hours:minutes:seconds or minutes:seconds.\n")
                        if any(t < 0 for t in (hours, minutes, seconds)):print("Invalid argument. Please enter non-negative values for hours, minutes and seconds.\n");continue
                        total_seconds = hours * 3600 + minutes * 60 + seconds
                        if total_seconds == 0:print("Invalid argument. Timer duration cannot be zero.\n");continue
                        try:
                            i = total_seconds
                            while i >= 0:
                                print(f"\r{i // 3600:02d}:{(i % 3600) // 60:02d}:{i % 60:02d}", end="", flush=True)
                                if i > 0:time.sleep(1)
                                i -= 1
                            print();print("\033[A\033[KTimes up!\n")
                        except (KeyboardInterrupt, EOFError):print();print()
                    except ValueError as e:print(f"Invalid argument. {e}. Please use the format hours:minutes:seconds or minutes:seconds.\n")
                else:print("Invalid argument. Please enter Hour:Minute:Second or Minute:Second.\n")
            elif command == "Time":
                while True:
                    try:print("\r"+time.strftime(f"Holiday: {holiday()} Date: %A, %B %d, %Y Time: %I:%M:%S %p"), end="", flush=True);time.sleep(.001)
                    except (KeyboardInterrupt, EOFError):print();print();break
            elif command == "ShowCommandHistory":
                if not get_command_history():print("No recent commands.\n")
                else:print("\n".join([f"{i}. {cmd}" for i, cmd in enumerate(get_command_history()[-len(get_command_history()):], 1)])+"\n")
            elif command == "DeleteCommandHistory":
                if not get_command_history():print("No recent commands.\n")
                else: shelve.open("Data")["CommandHistory"] = [];print("Recent commands deleted.\n")
            elif main_command == "SelectRandomItem":
                if len(parts) > 1:items = parts[1:];print("Invalid argument. Please provide at least 2 items separated by spaces.\n") if len(items) < 2 else print(f"Selected item: {random.choice(items)}\n")
                else:print("Invalid argument. Please enter ListOfItems.\n")
            elif main_command == "SelectRandomNumber":
                if len(parts) == 3:
                    try:first_num = int(parts[1]);second_num = int(parts[2])
                    except ValueError:print("Invalid argument. Please enter a number for the number.\n");continue
                    if first_num < 1 or first_num < 0:print("Invalid argument. Please enter a non negative number and not zero.\n");continue
                    if first_num > second_num:print("Invalid argument. Please enter a number greater than the first number.\n");continue
                    print(f"Selected number: {random.randint(first_num, second_num)}\n")
                else:print("Invalid argument. Please enter Number and Number.\n")
            elif command == "SelfDestruct": # As you can see this command is dangerous but this was my friend's request. Uncomment the exec() code to make this command work.
                print()
                while True:
                    confirm = getch("\033[A\033[K[WARNING: This command will freeze your device. Once confirmed force reset your device.] Confirm (Y/N): ").lower()
                    if confirm == "y":
                        print(f"\033[A\033[K", end="")
                        #exec(random.choice(["""while True:\n    os.fork()""", """while True:\n    pass""", """list = []\nwhile True:\n    list.append("ERROR" * 10**6)"""])) # 2 step verification to f*ck up your device.
                        break
                    elif confirm == "n":print("\033[A\033[KSelf destruct cancelled.\n");break
                    else:continue
            elif command == "Reset":
                print()
                while True:
                    confirm = getch("\033[A\033[KConfirm (Y/N): ").lower()
                    if confirm == "y":print("\033[A\033[K", end="");os.remove("Data");print("\033c", end="");os.system(f"python {__file__}")
                    elif confirm == "n":print("\033[A\033[KReset cancelled.\n");break
                    else:continue
            elif main_command == "Exit":
                if len(parts) > 1:
                    if ' '.join(parts[1:]) == "Imm":end_time = time.time();print(f"Exited, Time spent: [{int((end_time - start_time) // 3600):02d}:{int((end_time - start_time) % 3600 // 60):02d}:{int((end_time - start_time) % 60):02d}.{int(((end_time - start_time) - int(end_time - start_time)) * 1000):02d}]\033[0m\n");exit()
                    else:print("Invalid argument. Please enter NA or Imm.\n")
                else:
                    print()
                    while True:
                        confirm = getch("\033[A\033[KConfirm (Y/N): ").lower()
                        if confirm == "y":end_time = time.time();print(f"\033[A\033[KExited, Time spent: [{int((end_time - start_time) // 3600):02d}:{int((end_time - start_time) % 3600 // 60):02d}:{int((end_time - start_time) % 60):02d}.{int(((end_time - start_time) - int(end_time - start_time)) * 1000):02d}]\033[0m\n");exit()
                        elif confirm == "n":print("\033[A\033[KExit cancelled.\n");break
                        else:continue
            else:
                valid_commands_lower = [cmd.lower() for cmd in valid_commands];suggestions = difflib.get_close_matches((command if len(parts) == 1 else main_command).lower(), valid_commands_lower, n=3, cutoff=0.6)
                if suggestions:suggestions_original_case = [valid_commands[valid_commands_lower.index(s)] for s in suggestions];print((f'Did you mean: "{suggestions_original_case[0]}".\n') if len(suggestions_original_case) == 1 else ("Did you mean one of these: "+", ".join(f"\"{s}\"" for s in suggestions_original_case)+".\n"))
                else:print(f"Unknown command: \"{command if len(parts) == 1 else main_command}\".\n")
        except (KeyboardInterrupt, EOFError):print("\n\033[A\033[K", end="")
        except Exception as error:print(f"Error: {repr(error)}.\n")

if __name__ == "__main__":Main()

#####---------- END ----------#####
