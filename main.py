# Import Modules

import calendar
import datetime
import dbm # For getting error if database file gets corrupted.
import difflib
import importlib
import io
import itertools
import json
import keyword
import os
import random
import readline
import shelve
import shlex
import shutil
import string
import subprocess
import sys
import tempfile
import termios
import time
import tty
import zipfile

# Check Python Packages

REQUIRED_MODULES={
"requests":"requests",
"simpleeval":"simpleeval",
"speedtest":"speedtest-cli",

}

def module_available(module_name)->True|False:
    return importlib.util.find_spec(module_name) is not None

def install_package(package_name)->True|False:
    try:subprocess.check_call([sys.executable,"-m","pip","install",package_name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);return True
    except subprocess.CalledProcessError:return False

missing_modules=[mod for mod in REQUIRED_MODULES if not module_available(mod)]
if missing_modules:
    print("Installing missing modules...\n")
    for module in missing_modules:
        package=REQUIRED_MODULES[module]
        print(f"- Installing {package} for {module}.")
        if not install_package(package):print(f"Error: Failed to install {package}. Please install manually using \"pip install {package}\".\n");sys.exit(1)
    still_missing=[mod for mod in missing_modules if not module_available(mod)]
    if still_missing:
        print("\nWarning: Some modules are still missing after installation:")
        for mod in still_missing:print(f"- {mod} (tried installing {REQUIRED_MODULES[mod]})")
        print("\nPlease install manually using \"pip install -r requirements.txt\" and restart the script.\n");sys.exit(1)

try:
    import requests
    import simpleeval
    import speedtest
    
except ImportError as e:print(f"Critical import error: {repr(e)}");sys.exit(1)

# Check System Packages

REQUIRED_PACKAGES=[
"play-audio",
"fastfetch",

]

def package_available(package_name)->True|False:
    return shutil.which(package_name) is not None

def install_package(package_name)->True|False:
    try:subprocess.check_call(["pkg","install",package_name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);return True
    except subprocess.CalledProcessError:return False

missing_packages=[pkg for pkg in REQUIRED_PACKAGES if not package_available(pkg)]
if missing_packages:
    print("Installing missing packages...\n")
    for package in missing_packages:
        print(f"- Installing {package}.")
        if not install_package(package):print(f"Error: Failed to install {package}. Please install manually using \"pkg install {package}\".\n");sys.exit(1)
    still_missing=[pkg for pkg in missing_packages if not package_available(pkg)]
    if still_missing:
        print("\nWarning: Some packages are still missing after installation:")
        for mod in still_missing:print(f"- {package} (tried installing {package})")
        print(f"\nPlease install manually using \"pkg install {' '.join(still_missing)}\" and restart the script.\n");sys.exit(1)

# Data

default_data={
"Username":f"User {random.randint(1,100)}",
"CommandHistory":[],
"RecentStopwatchElapsedTime":0,
"AlarmFileName":"alarm_sound.mp3" if os.path.exists("alarm_sound.mp3") else None,

}
try:
    with shelve.open("data.db") as db:
        for key,value in default_data.items():
            if key in db:pass
            else:db[key]=value
except dbm.gnu.error as e:print(f"File data.db is corrupted try deleting it using \"rm data.db\".\n");sys.exit(1)

# Other Functions

def getch(prompt:str="")->str:
    print("\033[?25h",end="");print(prompt,end="",flush=True);fd=sys.stdin.fileno();old_settings=termios.tcgetattr(fd)
    try:tty.setraw(sys.stdin.fileno());ch=sys.stdin.read(1);print(ch,end="",flush=True)
    finally:termios.tcsetattr(fd,termios.TCSADRAIN,old_settings)
    print();print("\033[?25l",end="");return ch

def not_implemented(main_command:str)->None:
    print(f"Command functionality has not yet been implemented: \"{main_command}\".\n")

def rerun()->None:
    subprocess.run([sys.executable,__file__])



# Get Data

def version()->float:
    return float(open("version").read())

def username()->str:
    username=shelve.open("data.db")["Username"]
    if not username.strip():shelve.open("data.db")["Username"]=f"User {random.randint(1,100)}";return username
    return username

def command_history()->list[str]:
    return shelve.open("data.db")["CommandHistory"]

def recent_stopwatch_elapsed_time()->float:
    return shelve.open("data.db")["RecentStopwatchElapsedTime"]

def alarm_file_name()->str:
    return shelve.open("data.db")["AlarmFileName"]

def data()->str:
    return f"""Version: {version()}\nUsername: {username()}\nCommand History Size: {len(command_history())}\nRecent Stopwatch Elapsed Time: {recent_stopwatch_elapsed_time():.2f}\nAlarm Sound: {alarm_file_name()}"""



# Main

"""

Prompt Text

╭ [ 2025/08/14 12:00:00 AM ]
╰── >>> Pass

╭ [ YYYY/MM/DD HH:MM:SS XM ]—[ Exit: "Exit Imm" ]
╰── >>> 

"""

def main()->None:
    print(f"""\033c\033[?25l\033[90;1m\
__________        ___________
\______   \___.__.\_   _____/__  ___ ____   ____
 |     ___<   |  | |    __)_\  \/  // __ \_/ ___\ 
 |    |    \___  | |        \>    <\  ___/\  \___
 |____|    / ____|/_______  /__/\_ \\___  >\___  >
           \/             \/      \/    \/     \/
\033[m\nWelcome to PyExec, {username()}!\n\nEnter "\033[1mCommands?\033[m" for commands and "\033[1mExit Imm\033[m" to exit.\n{data()}\n{time.strftime("Date: %Y/%m/%d")}\n{time.strftime("Time: %I:%M:%S %p")}\n""")
    commands="""\
RerunCode
Matrix
RandomInteger
DaysUntil
UpdateCode
TimeToLoadUrl
Timer
Calendar
Stopwatch
RandomChoice
CheckInternetSpeed
Commands?
CommandHistory
Exit
Time
Clear
DeleteData
ChangeUsername
CheckInternet
GetSystemInfo
SeeData
Pass
ChangeAlarmSound

""".split()
    input_text="\033[1;90m╰── \033[m>>>\033[1;37m "
    rset=recent_stopwatch_elapsed_time()
    stopwatch=False
    running=True
    if command_history():
        for command in [k for k,g in itertools.groupby([s[:-25] for s in command_history()])]:readline.add_history(command) # Add commands from the data file to the prompt's history.
    
    start_time=time.time()
    while running:
        try:
            print("\033[?25h",end="")
            command=input("\033[1;90m╭ [\033[m YYYY/MM/DD HH:MM:SS XM \033[1;90m]—[\033[m Exit: \"Exit Imm\" \033[1;90m]\n"+input_text).strip()  # Main prompt. | Things you can do -> Use command - ex. Commands? | Evaluate simple math expressions ex. 1 + 1 | Print string - ex. "Hello, World"
            print("\033[90m\033[?25l",end="")
            if command.strip():
                time_of_command=time.strftime("%Y/%m/%d %I:%M:%S %p");print(f"\033[A\033[K\033[A\033[K\033[1;90m╭ [\033[m {time_of_command} \033[1;90m]\n{input_text}{command}\033[0;90m");parts=shlex.split(command);main_command=parts[0]
                try:print(simpleeval.simple_eval(command));print();continue
                except:pass
                if not " ".join(command.split()) in ["CommandHistory List","CommandHistory Delete"]:
                    with shelve.open("data.db") as db:temp_list=db["CommandHistory"];temp_list.append(f"{command} - {time_of_command}");db["CommandHistory"]=temp_list
            else:print("\033[A\033[K\033[A\033[K",end="");continue
            if main_command == "UpdateCode":
                repo_url="https://github.com/AnonymousUser12345-droid/PyExec/archive/refs/heads/main.zip" # Url to the github repository to download zip file.
                ver_url="https://raw.githubusercontent.com/AnonymousUser12345-droid/PyExec/main/version" # Url to the github repository's version raw file.
                if len(parts) > 1:
                    if " ".join(parts[1:]) == "Check":latest_version=requests.get(ver_url);latest_version.raise_for_status();print(f"Current version  : {version()}\nLatest version   : {latest_version.text}\nUpdate available : {version() > float(latest_version.text)}\nUp to date       : {version() == float(latest_version.text)}\n")
                    else:print("Invalid argument. Options are only Check.\n")
                else:
                    print()
                    while True:
                        confirm=getch("\033[A\033[KConfirm (Y/N): ").lower()
                        if confirm == "y":
                            protected_files=[
                            "data.db",
                            
                            ]
                            response=requests.get(repo_url)
                            response.raise_for_status()
                            latest_version=requests.get(ver_url)
                            latest_version.raise_for_status()
                            if version() > float(latest_version.text):
                                print(f"\033[A\033[KStarting update. Please don't exit.");time.sleep(10);print("\033[A\033[K",end="") # Start update with 10 seconds countdown.
                                for file in os.listdir():
                                    if file not in protected_files:os.remove(file)
                                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                                    root_folder=zip_ref.namelist()[0].split("/")[0]
                                    for file in zip_ref.namelist(): # Extract all files, removing the root folder prefix.
                                        if not file.endswith("/"):  # Skip directories.
                                            new_path=file.replace(root_folder+"/","",1) # Remove the root folder from the path.
                                            zip_ref.extract(file,".")  # Extract directly to current directory.
                                            os.rename(file,new_path)
                                    os.rmdir(root_folder) # Remove the empty root folder.
                                print("\033[A\033[KUpdate completed successfully.\n");exit()
                            else:print("\033[A\033[KUpdate code cancelled. PyExec is already up to date.\n");break
                        elif confirm == "n":print("\033[A\033[KUpdate code cancelled.\n");break
                        else:continue
            elif command == "Commands?":print("""\
GetSystemInfo
Commands?
CommandHistory
└── Arg1
    ├── (List)
    └── (Delete)
ChangeUsername
└── Arg1
    ├── (Default)
    └── <<Username>>
ChangeAlarmSound
└── Arg1
    ├── (Default)
    └── <<AlarmFileName>>
Clear
Pass
SeeData
DeleteData
RerunCode
UpdateCode
└── Arg1
    ├── ()
    └── (Check)
Exit
└── Arg1
    ├── ()
    └── (Imm)
Time
DaysUntil
├── Arg1
│   └── <<Date>>
└── Arg2
    ├── ()
    └── <<Date>>
Calendar
└── Arg1
    ├── ()
    └── <<Year>>
Timer
└── Arg1
    └── <<Time>>
Stopwatch
└── Arg1
    ├── (Start)
    ├── (Stop)
    ├── (Reset)
    └── (RecentElapsedTime)
RandomChoice
└── Arg1
    └── <<List>>
RandomInteger
├── Arg1
│   └── <<Integer>>
└── Arg2
    └── <<Integer>>
Matrix
TimeToLoadUrl
└── Arg1
    └── <<Url>>
CheckInternet
CheckInternetSpeed
""") # │ ├ └ ─

            elif main_command == "ChangeAlarmSound":
                if len(parts) > 1:
                    new_alarm_file_name=" ".join(parts[1:]).strip();allowed_formats="mp3 wav m4a acc flac ogg".split()
                    if not new_alarm_file_name:print("Invalid argument. AlarmFileName cannot be empty.\n");continue
                    if new_alarm_file_name == "Default":shelve.open("data.db")["AlarmFileName"]="alarm_sound.mp3" if os.path.exists("alarm_sound.mp3") else None;print()
                    if not new_alarm_file_name.endswith(tuple(["."+x for x in allowed_formats])):print(f"Invalid argument. AlarmFileName allowed formats are only {', '.join(['.'+x for x in allowed_formats][:-1])+' and .'+allowed_formats[len(allowed_formats)-1]}.\n");continue
                    if not os.path.exists(new_alarm_file_name):print("Invalid argument. AlarmFileName doesn't exist.\n");continue
                    else:shelve.open("data.db")["AlarmFileName"]=new_alarm_file_name;print()
                else:print("""Invalid usage. Usage
ChangeAlarmSound
└── Arg1
    ├── (Default)
    └── <<AlarmFileName>>\n""")
            elif main_command == "Timer":
                if len(parts) > 1:
                    try:
                        time_str=" ".join(parts[1:]);time_parts=list(map(int,time_str.split(":")))
                        if len(time_parts) == 2:hours=0;minutes,seconds=time_parts
                        elif len(time_parts) == 3:hours,minutes,seconds=time_parts
                        else:print("Invalid argument. Please use the format HH:MM:SS.\n")
                        if any(t < 0 for t in (hours,minutes,seconds)):print("Invalid argument. Please enter non-negative values for hours, minutes and seconds.\n");continue
                        total_seconds=hours * 3600+minutes * 60+seconds
                        if total_seconds == 0:print("Invalid argument. Timer duration cannot be zero.\n");continue
                        try:
                            i=total_seconds
                            while i >= 0:
                                print(f"\r{i // 3600:02d}:{(i % 3600) // 60:02d}:{i % 60:02d}",end="",flush=True)
                                if i > 0:time.sleep(1)
                                i -= 1
                            print();print("\033[A\033[KTimes up!")
                            alarm_file=alarm_file_name()
                            if package_available("play-audio") and os.path.exists(alarm_file):
                                while True:
                                    try:subprocess.run(["play-audio","-s","alarm",alarm_file]);time.sleep(.5);continue
                                    except (KeyboardInterrupt,EOFError):raise KeyboardInterrupt
                            else:print()
                        except (KeyboardInterrupt,EOFError):print();print()
                    except ValueError as e:print(f"Invalid argument. {e}. Please use the format HH:MM:SS or MM:SS.\n")
                else:print("""Invalid usage. Usage
Timer
└── Arg1
    └── <<Time>>\n""")
            elif command == "Pass":print() # Litterally useless.
            elif command == "SeeData":print(f"{data()}\n")
            elif command == "GetSystemInfo":os.system("fastfetch");print("\n\033[A\033[K")
            elif command == "Matrix":
                while True:
                    try:
                        for i in range(1,5+1):
                            if random.random() < .09 ** i:print(end="\n" * i,flush=True)
                        random_gibberish_code=list("".join(random.choice(string.ascii_letters+string.digits+string.punctuation+(" " * 10))) for _ in range(random.randint(random.randint(28,60),random.randint(84,90))))
                        for _ in range(1,random.randint(1,10)+1):pos=random.randint(0,len(random_gibberish_code));random_gibberish_code[pos:pos]=list(random.choice([random.choice(("".join(char.upper() if random.random() < .5 else char.lower() for char in keyword),keyword.upper(),keyword.lower(),keyword)) for keyword in keyword.kwlist+["then","fi","do","done","esac","function","select","read","echo","test",]+["auto","break","case","char","const","continue","default","do","double","else","enum","extern","float","for","goto","if","inline","int","long","register","restrict","return","short","signed","sizeof","static","struct","switch","typedef","union","unsigned","void","volatile","while","_Alignas","_Alignof","_Atomic","_Bool","_Complex","_Generic","_Imaginary","_Noreturn","_Static_assert","_Thread_local",]]))
                        print("\033[m"+random.choice(["\033[32m","\033[1;32m"])+"".join(random_gibberish_code),flush=True);time.sleep(.01)
                    except (KeyboardInterrupt,EOFError):print();print();break
            elif main_command == "RandomInteger":
                if len(parts) == 3:
                    try:first_num=int(parts[1])
                    except ValueError:print("Invalid argument. Please enter an integer for the first number.\n");continue
                    try:second_num=int(parts[2])
                    except ValueError:print("Invalid argument. Please enter an integer.\n");continue
                    if first_num > second_num:print("Invalid argument. Please enter an integer greater than the first integer for the second number.\n");continue
                    print(f"{random.randint(first_num,second_num)}\n")
                else:print("""Invalid usage. Usage
RandomInteger
├── Arg1
│   └── <<Integer>>
└── Arg2
    └── <<Integer>>\n""")
            elif main_command == "Stopwatch":
                if len(parts) > 1:
                    if " ".join(parts[1:]) == "Start":
                        if stopwatch == False:stopwatch_start_time=time.time();stopwatch=True;print("Stopwatch is running.\n")
                        else:print("Stopwatch is already running.\n")
                    elif " ".join(parts[1:]) == "Stop":
                        if stopwatch:elapsed=(time.time() - stopwatch_start_time)+rset;rset=elapsed;shelve.open("data.db")["RecentStopwatchElapsedTime"]=elapsed;stopwatch=False;print(f"Stopwatch stopped.\nElapsed time: [{int((elapsed) // 3600):02d}:{int((elapsed) % 3600 // 60):02d}:{int((elapsed) % 60):02d}.{int(((elapsed) - int(elapsed)) * 1000):02d}]\n")
                        else:print("Stopwatch is not running.\n")
                    elif " ".join(parts[1:]) == "Reset":stopwatch=False;stopwatch_start_time=None;rset=0;shelve.open("data.db")["RecentStopwatchElapsedTime"]=0;print("Stopwatch reset.\n")
                    elif " ".join(parts[1:]) == "RecentElapsedTime":print(f"{shelve.open('data')['RecentStopwatchElapsedTime']}\n")
                    else:print("Invalid argument. Options are only Start, Stop, Reset, and RecentElapsedTime.\n")
                else:print("""Invalid usage. Usage
Stopwatch
└── Arg1
    ├── (Start)
    ├── (Stop)
    ├── (Reset)
    └── (RecentElapsedTime)\n""")
            elif main_command == "DaysUntil":
                if len(parts) >= 2:
                    try:
                        target_date=datetime.datetime.strptime(parts[1],"%Y/%m/%d").date()
                        if len(parts) >= 3:
                            target_date2=datetime.datetime.strptime(" ".join(parts[2:]),"%Y/%m/%d").date()
                            if target_date > target_date2:print("Invalid argument. Target date cannot be in the past.\n");continue
                            else:days_left=(target_date2 - target_date).days
                            if days_left == 0:print(f"The target date is today if the current date is {target_date}.\n")
                            else:print(f"There are {days_left} day{'' if days_left == 1 else 's'} left until {target_date2} if the current date is {target_date}.\n")
                        else:
                            today=datetime.date.today()
                            if target_date < today:print("Invalid argument. Target date cannot be in the past.\n");continue
                            else:days_left=(target_date - today).days
                            if days_left == 0:print("The target date is today.\n")
                            else:print(f"There are {days_left} day{'' if days_left == 1 else 's'} left until {target_date}.\n")
                    except ValueError as e:print(f"Invalid argument. {e}. Please use the format YYYY/MM/DD.\n")
                else:print("""Invalid usage. Usage
DaysUntil
├── Arg1
│   └── <<Date>>
└── Arg2
    ├── ()
    └── <<Date>>\n""")
            elif main_command == "TimeToLoadUrl":
                if len(parts) > 1:
                    url=" ".join(parts[1:])
                    if " " in url:print("Invalid argument. Url cannot contain spaces.\n");break
                    if ("https" or "http") not in url:url="https://"+url
                    start_time=time.time();requests.get(url);end_time=time.time();time_spent=end_time - start_time;print(f"Time spent: [{int(time_spent // 3600):02d}:{int(time_spent % 3600 // 60):02d}:{int(time_spent % 60):02d}.{int((time_spent - int(time_spent)) * 1000):02d}] loading url.\n")
                else:print("""Invalid usage. Usage
TimeToLoadUrl
└── Arg1
    └── <<Url>>\n""")
            elif command == "CheckInternetSpeed":
                while True:
                    try:start_time=time.time();st=speedtest.Speedtest();st.get_best_server();time_spent=end_time - start_time;print(f"Download speed: {(st.download() / 10000000):.2f} Mbps\nUpload speed:   {(st.upload() / 1000000):.2f} Mbps\nPing:           {(st.results.ping):.2f} ms");end_time=time.time();print(f"Duration:       [{int(time_spent // 3600):02d}:{int(time_spent % 3600 // 60):02d}:{int(time_spent % 60):02d}.{int((time_spent - int(time_spent)) * 1000):02d}]\n");break
                    except TimeoutError:time.sleep(5);continue
            elif command == "CheckInternet":
                try:requests.get("https://www.google.com",timeout=10).raise_for_status();internet_connection=True
                except Exception:internet_connection=False
                print(f"The internet connection is {'' if internet_connection else 'un'}stable.\n")
            elif main_command == "Calendar":
                if len(parts) > 1:
                    try:print(calendar.calendar(int(" ".join(parts[1:]))));print("" if " ".join(parts[1:]) != str(datetime.date.today().year) else f"Date: {time.strftime(f'%Y/%m/%d')}\n\n",end="")
                    except ValueError:print("Invalid argument. Year must be a number.\n")
                else:print(calendar.calendar(datetime.date.today().year));print(f"Date: {time.strftime(f'%Y/%m/%d')}\n")
            elif command == "Clear":print("\033c",end="")
            elif command == "RerunCode":print("\033c",end="");rerun()
            elif main_command == "ChangeUsername":
                if len(parts) > 1:
                    new_name=" ".join(parts[1:]).lstrip()
                    if not new_name:print("Invalid argument. Username cannot be empty.\n");continue
                    if new_name == "Default":shelve.open("data.db")["Username"]=f"User {random.randint(1,100)}";print()
                    else:shelve.open("data.db")["Username"]=new_name;print()
                else:print("""Invalid usage. Usage
ChangeUsername
└── Arg1
    └── <<Username>>\n""")
            elif command == "Time":
                while True:
                    try:print(time.strftime(f"\rDate: %Y/%m/%d Time: %I:%M:%S %p"),end="",flush=True);time.sleep(.001)
                    except (KeyboardInterrupt,EOFError):print();print();break
            elif main_command == "CommandHistory":
                if len(parts) > 1:
                    if " ".join(parts[1:]) == "List":
                        if not command_history():print("No recent commands.\n")
                        else:print("\n".join([f"{i}. {cmd}" for i,cmd in enumerate(command_history()[-len(command_history()):],1)]));print()
                    elif " ".join(parts[1:]) == "Delete":
                        if not command_history():print("No recent commands.\n")
                        else:shelve.open("data.db")["CommandHistory"]=[];print("Recent commands deleted.\n")
                    else:print("Invalid argument. Options are only List, and Delete.\n")
                else:print("""Invalid usage. Usage
CommandHistory
└── Arg1
    ├── (List)
    └── (Delete)\n""")
            elif main_command == "RandomChoice":
                if len(parts) > 1:items=parts[1:];print("Invalid argument. Please provide a list that contains atleast 2 objects separated by space.\n") if len(items) < 2 else print(f"{random.choice(items)}\n")
                else:print("""Invalid usage. Usage
RandomChoice
└── Arg1
    └── <<List>>\n""")
            elif command == "DeleteData":
                print()
                while True:
                    confirm=getch("\033[A\033[KConfirm (Y/N): ").lower()
                    if confirm == "y":print("\033[A\033[K",end="");os.remove("Data");print("\033c",end="");rerun()
                    elif confirm == "n":print("\033[A\033[KDeletion of data cancelled.\n");break
                    else:continue
            elif main_command == "Exit":
                if len(parts) > 1:
                    if " ".join(parts[1:]) == "Imm":end_time=time.time();time_spent=end_time - start_time;print(f"Exited, Time spent: [{int(time_spent // 3600):02d}:{int(time_spent % 3600 // 60):02d}:{int(time_spent % 60):02d}.{int((time_spent - int(time_spent)) * 1000):02d}]\033[m\n");exit()
                    else:print("Invalid argument. Options are only Imm\n")
                else:
                    print()
                    while True:
                        confirm=getch("\033[A\033[KConfirm (Y/N): ").lower()
                        if confirm == "y":end_time=time.time();time_spent=end_time - start_time;print(f"\033[A\033[KExited, Time spent: [{int(time_spent // 3600):02d}:{int(time_spent % 3600 // 60):02d}:{int(time_spent % 60):02d}.{int((time_spent - int(time_spent)) * 1000):02d}]\033[m\n");exit()
                        elif confirm == "n":print("\033[A\033[KExit cancelled.\n");break
                        else:continue
            else:
                if main_command in commands:not_implemented(main_command)
                else:
                    commands_lower=[cmd.lower() for cmd in commands];suggestions=difflib.get_close_matches(main_command.lower(),commands_lower,n=3,cutoff=.6)
                    if suggestions:suggestions_original_case=[commands[commands_lower.index(s)] for s in suggestions];print((f"Did you mean: \"{suggestions_original_case[0]}\".\n") if len(suggestions_original_case) == 1 else ("Did you mean one of these: "+", ".join(f"\"{s}\"" for s in suggestions_original_case)+".\n"))
                    else:print(f"Unknown command: \"{main_command}\".\n")
        except (KeyboardInterrupt,EOFError):print("\nError: PyExec interrupted.\n");exit()
        except (requests.ConnectionError,requests.Timeout):print("Error: Internet unstable.\n")
        except Exception as error:print(f"Error: {repr(error)}.\n")
        finally:print("\033[m\033[?25h",end="")

if __name__ == "__main__":main()
