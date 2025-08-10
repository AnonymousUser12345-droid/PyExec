#####---------- Import Modules ----------#####

import calendar
import datetime
import dbm # For getting error if data file gets corrupted.
import difflib
import importlib
import io
import itertools
import keyword
import math
import os
import pathlib
import random
import readline
import re
import shelve
import shlex
import shutil
import string
import subprocess
import sys
import tempfile
import termios
import threading
import time
import tty
import zipfile

#####---------- Check Python Packages ----------#####

REQUIRED_MODULES={
"faker":"Faker",
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
    import faker
    import requests
    import simpleeval
    import speedtest
    
except ImportError as e:print(f"Critical import error: {repr(e)}");sys.exit(1)

#####---------- Check System Packages ----------#####

'''
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
'''

#####---------- Data ----------#####

default_data={
"Username":f"User {random.randint(1,100)}",
"CommandHistory":[],
"RecentStopwatchElapsedTime":0,

}
try:
    with shelve.open("data.db") as db:
        for key,value in default_data.items():
            if key in db:pass
            else:db[key]=value
except dbm.gnu.error as e:print(f"File data.db is corrupted try deleting it using \"rm data.db\".\n");sys.exit(1)

#####---------- Other Functions ----------#####

def getch(prompt:str="")->str:
    print("\033[?25h",end="");print(prompt,end="",flush=True);fd=sys.stdin.fileno();old_settings=termios.tcgetattr(fd)
    try:tty.setraw(sys.stdin.fileno());ch=sys.stdin.read(1);print(ch,end="",flush=True)
    finally:termios.tcsetattr(fd,termios.TCSADRAIN,old_settings)
    print();print("\033[?25l",end="");return ch

def not_implemented(command:str)->None:
    print(f"Command functionality has not yet been implemented: \"{command}\".\n")





#####---------- Retrieve Data ----------#####

def version()->float:
    return float(open("version").read())

def username()->str:
    username=shelve.open("data.db")["Username"].strip()
    if not username.strip():shelve.open("data.db")["Username"]=f"User {random.randint(1,100)}";return username
    return username

def command_history()->list[str]:
    return shelve.open("data.db")["CommandHistory"]

def recent_stopwatch_elapsed_time()->int:
    return shelve.open("data.db")["RecentStopwatchElapsedTime"]

def data()->str:
    return f"""Version: {version()}\nUsername: {username()}\nCommand History Size: {len(command_history())}\nRecent Stopwatch Elapsed Time: {recent_stopwatch_elapsed_time()}"""



#####---------- Main ----------#####

"""

Prompt Text

╭ [ 2025/08/14 12:00:00 AM ]
╰── >>> Commands?

╭ [ YYYY/MM/DD HH:MM:SS XM ]—[ Exit: "Exit Imm" ]
╰── >>> 

"""

def Main()->None:
    print(f"""\033c\033[?25l\033[90;1m\
__________        ___________
\______   \___.__.\_   _____/__  ___ ____   ____
 |     ___<   |  | |    __)_\  \/  // __ \_/ ___\ 
 |    |    \___  | |        \>    <\  ___/\  \___
 |____|    / ____|/_______  /__/\_ \\\___  >\___  >
           \/             \/      \/    \/     \/\
\033[m\n\nWelcome to PyExec, {username()}!\n\nEnter "\033[1;4mCommands?\033[m" for commands and "\033[1;4mExit Imm\033[m" to exit.\n{data()}\n{time.strftime("Date: %Y/%m/%d")}\n{time.strftime("Time: %I:%M:%S %p")}\n""")
    valid_commands="""\
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
GenerateUsername
CheckInternetSpeed
Commands?
CommandHistory
Readline
Exit
Time
Clear
DeleteData
ChangeUsername
CheckInternet
GenerateFakeIdentity
GetSystemInfo
SeeData

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
            command=input("\033[1;90m╭ [\033[m YYYY/MM/DD HH:MM:SS XM \033[1;90m]—[\033[m Exit: \"Exit Imm\" \033[1;90m]\n"+input_text).strip()  # Main prompt. # Command - ex. Commands? | Evaluate - ex. 1 + 1 | Print text - ex. "Hello, World"
            print("\033[90m\033[?25l",end="")
            if command.strip():
                time_of_command=time.strftime("%Y/%m/%d %I:%M:%S %p");print(f"\033[A\033[K\033[A\033[K\033[1;90m╭ [\033[m {time_of_command} \033[1;90m]\n{input_text}{command}\033[0;90m");parts=shlex.split(command);main_command=parts[0]
                try:print(simpleeval.simple_eval(command));print();continue
                except:pass
                if not (main_command == "CommandHistory" and parts[1] in ["List","Delete"]):
                    with shelve.open("data.db") as db:temp_list=db["CommandHistory"];temp_list.append(f"{command} - {time_of_command}");db["CommandHistory"]=temp_list
            else:print("\033[A\033[K\033[A\033[K",end="");continue
            if command == "Commands?":print("""\
GetSystemInfo
Commands?
CommandHistory
└── Arg1
    ├── (List)
    └── (Delete)
ChangeUsername
└── Arg1
    └── <<Username>>
Clear
SeeData
DeleteData
RerunCode
UpdateCode
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
GenerateUsername
GenerateFakeIdentity
Matrix
TimeToLoadUrl
└── Arg1
    └── <<Url>>
CheckInternet
CheckInternetSpeed
""")

            elif command == "GenerateFakeIdentity":
                not_implemented(main_command)
            elif command == "UpdateCode":
                print()
                while True:
                    confirm=getch("\033[A\033[KConfirm (Y/N): ").lower()
                    if confirm == "y":
                        repo_url="https://github.com/AnonymousUser12345-droid/PyExec/archive/refs/heads/main.zip" # Url to the github repository.
                        ver_url="https://raw.githubusercontent.com/AnonymousUser12345-droid/PyExec/main/version" # Url to the github repository's version raw file.
                        response=requests.get(repo_url)
                        response.raise_for_status()
                        ver=requests.get(ver_url)
                        ver.raise_for_status()
                        if version() > float(ver.text):
                            print(f"\033[A\033[KStarting update. Please don't exit.");time.sleep(10);print("\033[A\033[K",end="") # Start update with 10 seconds countdown.
                            for file in os.listdir():
                                if file != "data.db":os.remove(file)
                            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                                root_folder=zip_ref.namelist()[0].split("/")[0]
                                for file in zip_ref.namelist(): # Extract all files, removing the root folder prefix.
                                    if not file.endswith("/"):  # Skip directories.
                                        new_path=file.replace(root_folder + "/","",1) # Remove the root folder from the path.
                                        zip_ref.extract(file,".")  # Extract directly to current directory.
                                        os.rename(file,new_path)
                                os.rmdir(root_folder) # Remove the empty root folder.
                            print("\033[A\033[KUpdate completed successfully.\n");exit()
                        else:print("\033[A\033[KUpdate code cancelled. PyExec is already up to date.\n");break
                    elif confirm == "n":print("\033[A\033[KUpdate code cancelled.\n");break
                    else:continue
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
            elif command == "GenerateUsername":
                noun=random.choice("airplane apple automobile ball balloon beach bird boat boot bottle box bug butter canoe carrot cartoon cello chair coconut comet cream curtain daisy desk diamond door earth elephant emerald fire flamingo flower flute forest free giraffe glove grasshopper hair hat hill house ink iris jade jungle kangaroo kayak lake lemon lightning lion lotus lump mint monkey moon motorcycle mountain nest oboe ocean octopus onion orange orchestra owl penguin phoenix piano planet pond potato prairie rabbit raccoon raid rain river road rosebud ruby sea ship shoe shrub sitter skates sky socks sparrow spider squash squirrel star stream street sun table teapot terrain toast tomato truck trumpet tuba tulip umbrella unicorn valley vase violet violin water wind window zebra zoo atm cd suv tv aardvark abacus abbey abbreviation abdomen ability abnormality abolishment abortion abrogation absence abundance abuse academics academy accelerant accelerator accent acceptance access accessory accident accommodation accompanist accomplishment accord accordance accordion account accountability accountant accounting accuracy accusation acetate achievement achiever acid acknowledgment acorn acoustics acquaintance acquisition acre acrylic act action activation activist activity actor actress acupuncture ad adaptation adapter addiction addition address adjective adjustment admin administration administrator admire admission adobe adoption adrenalin adrenaline adult adulthood advance advancement advantage advent adverb advertisement advertising advice adviser advocacy advocate affair affect affidavit affiliate affinity afoul afterlife aftermath afternoon aftershave aftershock afterthought age agency agenda agent aggradation aggression aglet agony agreement agriculture aid aide aim air airbag airbus aircraft airfare airfield airforce airline airmail airman airport airship airspace alarm alb albatross album alcohol alcove alder ale alert alfalfa algebra algorithm alias alibi alien allegation allergist alley alliance alligator allocation allowance alloy alluvium almanac almighty almond alpaca alpenglow alpenhorn alpha alphabet altar alteration alternative altitude alto aluminium aluminum amazement amazon ambassador amber ambience ambiguity ambition ambulance amendment amenity ammunition amnesty amount amusement anagram analgesia analog analogue analogy analysis analyst analytics anarchist anarchy anatomy ancestor anchovy android anesthesiologist anesthesiology angel anger angina angiosperm angle angora angstrom anguish animal anime anise ankle anklet anniversary announcement annual anorak answer ant anteater antecedent antechamber antelope antennae anterior anthropology antibody anticipation anticodon antigen antique antiquity antler antling anxiety anybody anyone anything anywhere apartment ape aperitif apology app apparatus apparel appeal appearance appellation appendix appetiser appetite appetizer applause applewood appliance application appointment appreciation apprehension approach appropriation approval apricot apron apse aquarium aquifer arcade arch archrival archaeologist archaeology archeology archer architect architecture archives area arena argument arithmetic ark arm armrest armadillo armament armchair armoire armor armour armpit army arrangement array arrest arrival arrogance arrow art artery arthur artichoke article artifact artificer artist ascend ascent ascot ash ashram ashtray aside asparagus aspect asphalt aspic ass assassination assault assembly assertion assessment asset assignment assist assistance assistant associate association assumption assurance asterisk astrakhan astrolabe astrologer astrology astronomy asymmetry atelier atheist athlete athletics atmosphere atom atrium attachment attack attacker attainment attempt attendance attendant attention attenuation attic attitude attorney attraction attribute auction audience audit auditorium aunt authentication authenticity author authorisation authority authorization auto autoimmunity automation automaton autumn availability avalanche avenue average avocado award awareness awe axis azimuth babe baboon babushka baby bachelor back backbone backburn backdrop background backpack backup backyard bacon bacterium badge badger bafflement bag bagel baggage baggie baggy bagpipe bail bait bake baker bakery bakeware balaclava balalaika balance balcony ballet balloonist ballot ballpark bamboo ban banana band bandana bandanna bandolier bandwidth bangle banjo bank bankbook banker banking bankruptcy banner banquette banyan baobab bar barbecue barbeque barber barbiturate bargain barge baritone barium bark barley barn barometer barracks barrage barrel barrier barstool bartender base baseball baseboard baseline basement basics basil basin basis basket basketball bass bassinet bassoon bat bath bather bathhouse bathrobe bathroom bathtub battalion batter battery batting battle battleship bay bayou bead beak beam bean beancurd beanie beanstalk bear beard beast beastie beat beating beauty beaver beck bed bedrock bedroom bee beech beef beer beet beetle beggar beginner beginning begonia behalf behavior behaviour beheading behest behold being belfry belief believer bell belligerency bellows belly belt bench bend beneficiary benefit beret berry bestseller bet beverage beyond bias bibliography bicycle bid bidder bidding bidet bifocals bijou bike bikini bill billboard billing billion bin binoculars biology biopsy biosphere biplane birch birdwatcher birdbath birdcage birdhouse birth birthday biscuit bit bite bitten bitter black blackberry blackbird blackboard blackfish blackness bladder blade blame blank blanket blast blazer blend blessing blight blind blinker blister blizzard block blocker blog blogger blood bloodflow bloom bloomer blossom blouse blow blowgun blowhole blue blueberry blush boar board boatload boatyard bob bobcat body bog bolero bolt bomb bomber bombing bond bonding bondsman bone bonfire bongo bonnet bonsai bonus boogeyman book bookcase bookend booking booklet bookmark boolean boom boon boost booster bootee bootie booty border bore borrower borrowing bosom boss botany bother bottling bottom bottomline boudoir bough boulder boulevard boundary bouquet bourgeoisie bout boutique bow bower bowl bowler bowling bowtie boxer boxspring boy boycott boyfriend boyhood boysenberry bra brace bracelet bracket brain brake bran branch brand brandy brass brassiere bratwurst bread breadcrumb breadfruit break breakdown breakfast breakpoint breakthrough breast breastplate breath breeze brewer bribery brick bricklaying bride bridge brief briefing briefly briefs brilliant brink brisket broad broadcast broccoli brochure brocolli broiler broker bronchitis bronco bronze brooch brood brook broom brother brotherinlaw brow brown brownie browser browsing brunch brush brushfire brushing bubble buck bucket buckle buckwheat bud buddy budget buffalo buffer buffet buggy bugle builder building bulb bulk bull bullfighter bulldozer bullet bump bumper bun bunch bungalow bunghole bunkhouse burden bureau burglar burial burlesque burn burnout burning burrito burro burrow burst bus bush business businessman bust bustle butane butcher butler butterfly button buy buyer buying buzz buzzard cclamp cabana cabbage cabin cabinet cable caboose cacao cactus caddy cadet cafe caffeine caftan cage cake calcification calculation calculator calculus calendar calf caliber calibre calico call calm calorie camel cameo camera camp campaign campaigning campanile camper campus can canal cancer candelabra candidacy candidate candle candy cane cannibal cannon canon canopy cantaloupe canteen canvas cap capability capacity cape caper capital capitalism capitulation capon cappelletti cappuccino captain caption captor car carabao caramel caravan carbohydrate carbon carboxyl card cardboard cardigan care career cargo caribou carload carnation carnival carol carotene carp carpenter carpet carpeting carport carriage carrier carry cart cartel carter cartilage cartload cartridge carving cascade case casement cash cashew cashier casino casket cassava casserole cassock cast castanet castle casualty cat catacomb catalogue catalysis catalyst catamaran catastrophe catch catcher category caterpillar cathedral cation catsup cattle cauliflower causal cause causeway caution cave caviar cayenne ceiling celebration celebrity celeriac celery cell cellar celsius cement cemetery cenotaph census cent center centimeter centre centurion century cephalopod ceramic ceramics cereal ceremony certainty certificate certification cesspool chafe chain chainstay chairlift chairman chairperson chaise chalet chalice chalk challenge chamber champagne champion championship chance chandelier change channel chaos chap chapel chaplain chapter character characteristic characterization chard charge charger charity charlatan charm charset chart charter chasm chassis chastity chasuble chateau chatter chauffeur chauvinist check checkbook checking checkout checkroom cheddar cheek cheer cheese cheesecake cheetah chef chem chemical chemistry chemotaxis cheque cherry chess chest chestnut chick chicken chicory chief chiffonier child childbirth childhood chili chill chime chimpanzee chin chinchilla chino chip chipmunk chitchat chivalry chive chives chocolate choice choir choker cholesterol choosing chop chops chopstick chopsticks chord chorus chow chowder chrome chromolithograph chronicle chronograph chronometer chrysalis chub chuck chug church churn chutney cicada cigarette cilantro cinder cinema cinnamon circadian circle circuit circulation circumference circumstance cirrhosis cirrus citizen citizenship citron citrus city civilian civilisation civilization claim clam clamp clan clank clapboard clarification clarinet clarity clasp class classic classification classmate classroom clause clave clavicle clavier claw clay cleaner clearance clearing cleat cleavage clef cleft clergyman cleric clerk click client cliff climate climb clinic clip clipboard clipper cloak cloakroom clock clockwork clogs cloister clone close closet closing closure cloth clothes clothing cloud cloudburst clove clover cloves club clue cluster clutch coproducer coach coal coalition coast coaster coat cob cobbler cobweb cock cockpit cockroach cocktail cocoa cod code codepage codling codon codpiece coevolution cofactor coffee coffin cohesion cohort coil coin coincidence coinsurance coke cold coleslaw coliseum collaboration collagen collapse collar collard collateral colleague collection collectivisation collectivization collector college collision colloquy colon colonial colonialism colonisation colonization colony color colorlessness colt column columnist comb combat combination combine comeback comedy comestible comfort comfortable comic comics comma command commander commandment comment commerce commercial commission commitment committee commodity common commonsense commotion communicant communication communion communist community commuter company comparison compass compassion compassionate compensation competence competition competitor complaint complement completion complex complexity compliance complication complicity compliment component comportment composer composite composition compost comprehension compress compromise comptroller compulsion computer comradeship con concentrate concentration concept conception concern concert conclusion concrete condition conditioner condominium condor conduct conductor cone confectionery conference confidence confidentiality configuration confirmation conflict conformation confusion conga congo congregation congress congressman congressperson conifer connection connotation conscience consciousness consensus consent consequence conservation conservative consideration consignment consist consistency console consonant conspiracy conspirator constant constellation constitution constraint construction consul consulate consulting consumer consumption contact contact lens contagion container content contention contest context continent contingency continuity contour contract contractor contrail contrary contrast contribution contributor control controller controversy convection convenience convention conversation conversion convert convertible conviction cook cookbook cookie cooking coonskin cooperation coordination coordinator cop copout cope copper copy copying copyright copywriter coral cord corduroy core cork cormorant corn corner cornerstone cornet cornflakes cornmeal corporal corporation corporatism corps corral correspondence correspondent corridor corruption corsage cosset cost costume cot cottage cotton couch cougar cough council councilman councilor councilperson counsel counseling counselling counsellor counselor count counter counterforce counterpart counterterrorism countess country countryside county couple coupon courage course court courthouse courtroom cousin covariate cover coverage coverall cow cowbell cowboy coyote crab crack cracker crackers cradle craft craftsman cranberry crane cranky crap crash crate cravat craw crawdad crayfish crayon crazy creation creationism creationist creative creativity creator creature creche credential credenza credibility credit creditor creek creme brulee crepe crest crew crewman crewmate crewmember crewmen cria crib cribbage cricket cricketer crime criminal crinoline crisis crisp criteria criterion critic criticism crocodile crocus croissant crook crop cross crosscontamination crossstitch crotch croup crow crowd crown crucifixion crude cruelty cruise crumb crunch crusader crush crust cry crystal crystallography cub cube cuckoo cucumber cue cufflink cuisine cultivar cultivator culture culvert cummerbund cup cupboard cupcake cupola curd cure curio curiosity curl curler currant currency current curriculum curry curse cursor curtailment curve cushion custard custody custom customer cut cuticle cutlet cutover cutting cyclamen cycle cyclone cyclooxygenase cygnet cylinder cymbal cynic cyst cytokine cytoplasm dad daddy daffodil dagger dahlia daikon daily dairy dam damage dame damn dance dancer dancing dandelion danger dare dark darkness darn dart dash dashboard data database date daughter dawn day daybed daylight dead deadline deal dealer dealing dearest death deathwatch debate debris debt debtor decade decadence decency decimal decision decisionmaking deck declaration declination decline decoder decongestant decoration decrease decryption dedication deduce deduction deed deep deer default defeat defendant defender defense deficit definition deformation degradation degree delay deliberation delight delivery demand democracy democrat demon demur den denim denominator density dentist deodorant department departure dependency dependent deployment deposit deposition depot depression depressive depth deputy derby derivation derivative derrick descendant descent description desert design designation designer desire desktop dessert destination destiny destroyer destruction detail detainee detainment detection detective detector detention determination detour devastation developer developing development developmental deviance deviation device devil dew dhow diabetes diadem diagnosis diagram dial dialect dialogue diam diaper diaphragm diarist diary dibble dick dickey dictaphone dictator diction dictionary die diesel diet difference differential difficulty diffuse dig digestion digestive digger digging digit dignity dilapidation dill dilution dime dimension dimple diner dinghy dining dinner dinosaur dioxide dip diploma diplomacy dipstick direction directive director directory dirndl dirt disability disadvantage disagreement disappointment disarmament disaster discharge discipline disclaimer disclosure disco disconnection discount discourse discovery discrepancy discretion discrimination discussion disdain disease disembodiment disengagement disguise disgust dish dishwasher disk disparity dispatch displacement display disposal disposer disposition dispute disregard disruption dissemination dissonance distance distinction distortion distribution distributor district divalent divan diver diversity divide dividend divider divine diving division divorce doc dock doctor doctorate doctrine document documentary documentation doe dog doggie dogsled dogwood doing doll dollar dollop dolman dolor dolphin domain dome domination donation donkey donor donut doorbell doorknob doorpost doorway dory dose dot double doubling doubt doubter dough doughnut down downfall downforce downgrade download downstairs downtown downturn dozen draft drag dragon dragonfly dragonfruit dragster drain drainage drake drama dramaturge drapes draw drawbridge drawer drawing dream dreamer dredger dress dresser dressing drill drink drinking drive driver driveway driving drizzle dromedary drop drudgery drug drum drummer drunk dryer duck duckling dud dude due duel dueling duffel dugout dulcimer dumbwaiter dump dump truck dune dune buggy dungarees dungeon duplexer duration durian dusk dust dust storm duster duty dwarf dwell dwelling dynamics dynamite dynamo dynasty dysfunction ebook ereader eagle eaglet ear eardrum earmuffs earnings earplug earring earrings earthquake earthworm ease easel east eating eaves eavesdropper ecclesia echidna eclipse ecliptic ecology economics economy ecosystem ectoderm ectodermal ecumenist eddy edge edger edible editing edition editor editorial education eel effacement effect effective effectiveness effector efficacy efficiency effort egg egghead eggnog eggplant ego eicosanoid ejector elbow elderberry election electricity electrocardiogram electronics element elevation elevator eleventh elf elicit eligibility elimination elite elixir elk ellipse elm elongation elver email emanate embarrassment embassy embellishment embossing embryo emergence emergency emergent emery emission emitter emotion emphasis empire employ employee employer employment empowerment emu enactment encirclement enclave enclosure encounter encouragement encyclopedia end endive endoderm endorsement endothelium endpoint enemy energy enforcement engagement engine engineer engineering enigma enjoyment enquiry enrollment enterprise entertainment enthusiasm entirety entity entrance entree entrepreneur entry envelope environment envy enzyme epauliere epee ephemera ephemeris ephyra epic episode epithelium epoch eponym epoxy equal equality equation equinox equipment equity equivalent era eraser erection erosion error escalator escape escort espadrille espalier essay essence essential establishment estate estimate estrogen estuary eternity ethernet ethics ethnicity ethyl euphonium eurocentrism evaluation evaluator evaporation eve evening eveningwear event everybody everyone everything eviction evidence evil evocation evolution exhusband exwife exaggeration exam examination examiner example exasperation excellence exception excerpt excess exchange excitement exclamation excursion excuse execution executive executor exercise exhaust exhaustion exhibit exhibition exile existence exit exocrine expansion expansionism expectancy expectation expedition expense experience experiment experimentation expert expertise explanation exploration explorer explosion export expose exposition exposure expression extension extent exterior external extinction extreme extremist eye eyeball eyebrow eyebrows eyeglasses eyelash eyelashes eyelid eyelids eyeliner eyestrain eyrie fabric face facelift facet facility facsimile fact factor factory faculty fahrenheit fail failure fairness fairy faith faithful fall fallacy fallingout fame familiar familiarity family fan fang fanlight fanny fannypack fantasy farm farmer farming farmland farrow fascia fashion fat fate father fatherinlaw fatigue fatigues faucet fault fav fava favor favorite fawn fax fear feast feather feature fedelini federation fedora fee feed feedback feeding feel feeling fellow felony female fen fence fencing fender feng fennel ferret ferry ferryboat fertilizer festival fetus few fiber fiberglass fibre fibroblast fibrosis ficlet fiction fiddle field fiery fiesta fifth fig fight fighter figure figurine file filing fill fillet filly film filter filth final finance financing finding fine finer finger fingerling fingernail finish finisher fir fireman fireplace firewall firm first fish fishbone fisherman fishery fishing fishmonger fishnet fisting fit fitness fix fixture flag flair flame flan flanker flare flash flat flatboat flavor flax fleck fledgling fleece flesh flexibility flick flicker flight flint flintlock flipflops flock flood floodplain floor floozie flour flow flu flugelhorn fluke flume flung fly flytrap foal foam fob focus fog fold folder folk folklore follower following fondue font food foodstuffs fool foot footage football footnote footprint footrest footstep footstool footwear forage forager foray force ford forearm forebear forecast forehead foreigner forelimb forestry forever forgery fork form formal formamide format formation former formicarium formula fort forte fortnight fortress fortune forum foundation founder founding fountain fourths fowl fox foxglove fraction fragrance frame framework fratricide fraud fraudster freak freckle freedom freelance freezer freezing freight freighter frenzy freon frequency fresco friction fridge friend friendship fries frigate fright fringe fritter frock frog front frontier frost frosting frown fruit frustration fry fuel fugato fulfillment full fun function functionality fund funding fundraising funeral fur furnace furniture furry fusarium futon future gadget gaffe gaffer gain gaiters gale gallbladder gallery galley gallon galoshes gambling game gamebird gaming gammaray gander gang gap garage garb garbage garden garlic garment garter gas gasket gasoline gasp gastronomy gastropod gate gateway gather gathering gator gauge gauntlet gavel gazebo gazelle gear gearshift geek gel gelatin gelding gem gemsbok gender gene general generation generator generosity genetics genie genius genocide genre gentleman geography geology geometry geranium gerbil gesture geyser gherkin ghost giant gift gig gigantism giggle ginger gingerbread ginseng girdle girl girlfriend git glacier gladiolus glance gland glass glasses glee glen glider gliding glimpse globe glockenspiel gloom glory glow glucose glue glut glutamate gnat gnu gokart goal goat gobbler god goddess godfather godmother godparent goggles going gold goldfish golf gondola gong good goodbye goodie goodness goodnight goodwill goose gopher gorilla gosling gossip governance government governor gown grabbag grace grade gradient graduate graduation graffiti graft grain gram grammar gran grand grandchild granddaughter grandfather grandma grandmom grandmother grandpa grandparent grandson granny granola grant grape grapefruit graph graphic grasp grass grassland gratitude gravel gravitas gravity gravy gray grease greatgrandfather greatgrandmother greatness greed green greenhouse greens grenade grey grid grief grill grin grip gripper grit grocery ground group grouper grouse grove growth grub guacamole guarantee guard guava guerrilla guess guest guestbook guidance guide guideline guilder guilt guilty guinea guitar guitarist gum gumshoe gun gunpowder gutter guy gym gymnast gymnastics gynaecology gyro habit habitat hacienda hacksaw hackwork hail haircut hake half halfbrother halfsister halibut hall halloween hallway halt ham hamburger hammer hammock hamster hand handholding handball handful handgun handicap handle handlebar handmaiden handover handrail handsaw hanger happening happiness harald harbor harbour hardboard hardcover hardening hardhat hardship hardware hare harm harmonica harmonise harmonize harmony harp harpooner harpsichord harvest harvester hash hashtag hassock haste hatbox hatchet hatchling hate hatred haunt haven haversack havoc hawk hay haze hazel hazelnut head headache headlight headline headphones headquarters headrest health healthcare hearing hearsay heart heartthrob heartache heartbeat hearth hearthside heartwood heat heater heating heaven heavy hectare hedge hedgehog heel heifer height heir heirloom helicopter helium hell hellcat hello helmet helo help hemisphere hemp hen hepatitis herb herbs heritage hermit hero heroine heron herring hesitation heterosexual hexagon heyday hiccups hide hierarchy high highrise highland highlight highway hike hiking hint hip hippodrome hippopotamus hire hiring historian history hit hive hobbit hobby hockey hoe hog hold holder hole holiday home homeland homeownership hometown homework homicide homogenate homonym homosexual homosexuality honesty honey honeybee honeydew honor honoree hood hoof hook hop hope hops horde horizon hormone horn hornet horror horse horseradish horst hose hosiery hospice hospital hospitalisation hospitality hospitalization host hostel hostess hotdog hotel hound hour hourglass houseboat household housewife housework housing hovel hovercraft howard howitzer hub hubcap hubris hug hugger hull human humanity humidity hummus humor humour hunchback hundred hunger hunt hunter hunting hurdle hurdler hurricane hurry hurt husband hut hutch hyacinth hybridisation hybridization hydrant hydraulics hydrocarb hydrocarbon hydrofoil hydrogen hydrolyse hydrolysis hydrolyze hydroxyl hyena hygienic hype hyphenation hypochondria hypothermia hypothesis ice iceberg icebreaker icecream icicle icing icon icy id idea ideal identification identity ideology idiom idiot igloo ignorance ignorant ikebana illegal illiteracy illness illusion illustration image imagination imbalance imitation immigrant immigration immortal impact impairment impala impediment implement implementation implication import importance impostor impress impression imprisonment impropriety improvement impudence impulse injoke inlaws inability inauguration inbox incandescence incarnation incense incentive inch incidence incident incision inclusion income incompetence inconvenience increase incubation independence independent index indication indicator indigence individual industrialisation industrialization industry inequality inevitable infancy infant infarction infection infiltration infinite infix inflammation inflation influence influx info information infrastructure infusion inglenook ingrate ingredient inhabitant inheritance inhibition inhibitor initial initialise initialize initiative injunction injury injustice inlay inn innervation innocence innocent innovation input inquiry inscription insect insectarium insert inside insight insolence insomnia inspection inspector inspiration installation instance instant instinct institute institution instruction instructor instrument instrumentalist instrumentation insulation insurance insurgence insurrection integer integral integration integrity intellect intelligence intensity intent intention intentionality interaction interchange interconnection intercourse interest interface interferometer interior interject interloper internet interpretation interpreter interval intervenor intervention interview interviewer intestine introduction intuition invader invasion invention inventor inventory inverse inversion investigation investigator investment investor invitation invite invoice involvement iridescence iron ironclad irony irrigation ischemia island isogloss isolation issue item itinerary ivory jack jackal jacket jackfruit jaguar jail jailhouse jalapeÃ±o jam jar jasmine jaw jazz jealousy jeans jeep jelly jellybeans jellyfish jerk jet jewel jeweller jewellery jewelry jicama jiffy job jockey jodhpurs joey jogging joint joke jot journal journalism journalist journey joy judge judgment judo jug juggernaut juice julienne jumbo jump jumper jumpsuit junior junk junker junket jury justice justification jute kale kamikaze karate kazoo kebab keep keeper kendo kennel ketch ketchup kettle kettledrum key keyboard keyboarding keystone kick kickoff kid kidney kielbasa kill killer killing kilogram kilometer kilt kimono kinase kind kindness king kingdom kingfish kiosk kiss kit kitchen kite kitsch kitten kitty kiwi knee kneejerk knickers knife knifeedge knight knitting knock knot knowhow knowledge knuckle koala kohlrabi kumquat lab label labor laboratory laborer labour labourer lace lack lacquerware lad ladder ladle lady ladybug lag lamb lambkin lament lamp lanai land landform landing landmine landscape lane language lantern lap laparoscope lapdog laptop larch lard larder lark larva laryngitis lasagna lashes last latency latex lathe latitude latte latter laugh laughter laundry lava law lawmaker lawn lawsuit lawyer lay layer layout lead leader leadership leading leaf league leaker leap learning leash leather leave leaver lecture leek leeway left leg legacy legal legend legging legislation legislator legislature legitimacy legume leisure lemonade lemur lender lending length lens lentil leopard leprosy leptocephalus lesbian lesson letter lettuce level lever leverage leveret liability liar liberty libido library licence license licensing licorice lid lie lieu lieutenant life lifestyle lifetime lift ligand light lighting lightscreen ligula likelihood likeness lilac lily limb lime limestone limit limitation limo line linen liner linguist linguistics lining link linkage linseed lip lipid lipoprotein lipstick liquid liquidity liquor list listening listing literate literature litigation litmus litter littleneck liver livestock living lizard llama load loading loaf loafer loan lobby lobotomy lobster local locality location lock locker locket locomotive locust lode loft log loggia logic login logistics logo loincloth lollipop loneliness longboat longitude look lookout loop loophole loquat lord loss lot lotion lottery lounge louse lout love lover lox loyalty luck luggage lumber lumberman lunch luncheonette lunchmeat lunchroom lung lunge lust lute luxury lychee lycra lye lymphocyte lynx lyocell lyre lyrics lysine macadamia macaroni macaroon macaw machine machinery macrame macro macrofauna madam maelstrom maestro magazine maggot magic magnet magnitude maid maiden mail mailbox mailer mailing mailman main mainland mainstream maintainer maintenance maize major majorleague majority makeover maker makeup making male malice mall mallard mallet malnutrition mama mambo mammoth man manacle management manager manatee mandarin mandate mandolin mangle mango mangrove manhunt maniac manicure manifestation manipulation mankind manner manor mansard manservant mansion mantel mantle mantua manufacturer manufacturing many map maple mapping maracas marathon marble march mare margarine margin mariachi marimba marines marionberry mark marker market marketer marketing marketplace marksman markup marmalade marriage marsh marshland marshmallow marten marxism mascara mask masonry mass massage mast master masterpiece mastication mastoid mat match matchmaker mate material maternity math mathematics matrix matter mattock mattress max maximum maybe mayonnaise mayor meadow meal mean meander meaning means meantime measles measure measurement meat meatball meatloaf mecca mechanic mechanism med medal media median medication medicine medium meet meeting melatonin melody melon member membership membrane meme memo memorial memory men menopause menorah mention mentor menu merchandise merchant mercury meridian meringue merit mesenchyme mess message messenger messy metabolite metal metallurgist metaphor meteor meteorology meter methane method methodology metric metro metronome mezzanine microlending micronutrient microphone microwave midcourse midden middle middleman midline midnight midwife might migrant migration mile mileage milepost milestone military milk milkshake mill millennium millet millimeter million millisecond millstone mime mimosa min mincemeat mind mine mineral mineshaft mini miniskirt minibus minimalism minimum mining minion minister mink minnow minor minorleague minority minute miracle mirror miscarriage miscommunication misfit misnomer misogyny misplacement misreading misrepresentation miss missile mission missionary mist mistake mister misunderstand miter mitten mix mixer mixture moai moat mob mobile mobility mobster moccasins mocha mochi mode model modeling modem modernist modernity modification molar molasses molding mole molecule mom moment monastery monasticism money monger monitor monitoring monk monocle monopoly monotheism monsoon monster month monument mood moody moonlight moonscape moonshine moose mop morale morbid morbidity morning moron morphology morsel mortal mortality mortgage mortise mosque mosquito most motel moth mother motherinlaw motion motivation motive motor motorboat motorcar mound mouse mouser mousse moustache mouth mouton movement mover movie mower mozzarella mud muffin mug mukluk mule multimedia murder muscat muscatel muscle musculature museum mushroom music musicbox musicmaking musician muskrat mussel mustache mustard mutation mutt mutton mycoplasma mystery myth mythology nail name naming nanoparticle napkin narrative nasal nation nationality native naturalisation nature navigation necessity neck necklace necktie nectar nectarine need needle neglect negligee negotiation neighbor neighborhood neighbour neighbourhood neologism neon neonate nephew nerve nestling nestmate net netball netbook netsuke network networking neurobiologist neuron neuropathologist neuropsychiatry news newsletter newspaper newsprint newsstand nexus nibble nicety niche nick nickel nickname niece night nightclub nightgown nightingale nightlife nightlight nightmare ninja nit nitrogen nobody nod node noir noise nonbeliever nonconformist nondisclosure nonsense noodle noodles noon norm normal normalisation normalization north nose notation note notebook notepad nothing notice notion notoriety nougat noun nourishment novel nucleotidase nucleotide nudge nuke number numeracy numeric numismatist nun nurse nursery nursing nurture nut nutmeg nutrient nutrition nylon nymph oak oar oasis oat oatmeal oats obedience obesity obi object objection objective obligation observation observatory obsession obsidian obstacle occasion occupation occurrence ocelot octagon octave octavo octet odometer odyssey oeuvre offramp offence offense offer offering office officer official offset oil okra oldie oleo olive omega omelet omission omnivore oncology online onset opening opera operating operation operator ophthalmologist opinion opium opossum opponent opportunist opportunity opposite opposition optimal optimisation optimist optimization option orangutan orator orchard orchid order ordinary ordination ore oregano organ organisation organising organization organizing orient orientation origin original originality ornament osmosis osprey ostrich other otter ottoman ounce outback outcome outfielder outfit outhouse outlaw outlay outlet outline outlook output outrage outrigger outrun outset outside oval ovary oven overcharge overclocking overcoat overexertion overflight overhead overheard overload overnighter overshoot oversight overview overweight owner ownership ox oxford oxygen oyster ozone pace pacemaker pack package packaging packet pad paddle paddock pagan page pagoda pail pain paint painter painting paintwork pair pajamas palace palate palm pamphlet pan pancake pancreas panda panel panic pannier panpipe pansy panther panties pantologist pantology pantry pants pantsuit panty pantyhose papa papaya paper paperback paperwork parable parachute parade paradise paragraph parallelogram paramecium paramedic parameter paranoia parcel parchment pard pardon parent parenthesis parenting park parka parking parliament parole parrot parser parsley parsnip part participant participation particle particular partner partnership partridge party pass passage passbook passenger passing passion passive passport password past pasta paste pastor pastoralist pastry pasture pat patch pate patent patentee path pathogenesis pathology pathway patience patient patina patio patriarch patrimony patriot patrol patroller patrolling patron pattern patty pattypan pause pavement pavilion paw pawnshop pay payee payment payoff pea peace peach peacoat peacock peak peanut pear pearl peasant pecan pecker pedal peek peen peer peertopeer pegboard pelican pelt pen penalty pence pencil pendant pendulum penicillin peninsula penis pennant penny pension pentagon peony people pepper pepperoni percent percentage perception perch perennial perfection performance perfume period periodical peripheral permafrost permission permit perp perpendicular persimmon person personal personality personnel perspective pest pet petal petition petitioner petticoat pew pharmacist pharmacopoeia phase pheasant phenomenon phenotype pheromone philanthropy philosopher philosophy phone phosphate photo photodiode photograph photographer photography photoreceptor phrase phrasing physical physics physiology pianist piccolo pick pickax pickaxe picket pickle pickup picnic picture picturesque pie piece pier piety pig pigeon piglet pigpen pigsty pike pilaf pile pilgrim pilgrimage pill pillar pillbox pillow pilot pimp pimple pin pinafore pincenez pine pineapple pinecone ping pink pinkie pinot pinstripe pint pinto pinworm pioneer pipe pipeline piracy pirate piss pistol pit pita pitch pitcher pitching pith pizza place placebo placement placode plagiarism plain plaintiff plan plane planning plant plantation planter planula plaster plasterboard plastic plate platelet platform platinum platter platypus play player playground playroom playwright plea pleasure pleat pledge plenty plier pliers plight plot plough plover plow plowman plug plugin plum plumber plume plunger plywood pneumonia pocket pocketwatch pocketbook pod podcast poem poet poetry poignance point poison poisoning poker polarisation polarization pole polenta police policeman policy polish politician politics poll polliwog pollutant pollution polo polyester polyp pomegranate pomelo pompom poncho pony pool poor pop popcorn poppy popsicle popularity population populist porcelain porch porcupine pork porpoise port porter portfolio porthole portion portrait position possession possibility possible post postage postbox poster posterior postfix pot potential pottery potty pouch poultry pound pounding poverty powder power practice practitioner praise pray prayer precedence precedent precipitation precision predecessor preface preference prefix pregnancy prejudice prelude premeditation premier premise premium preoccupation preparation prescription presence present presentation preservation preserves presidency president press pressroom pressure pressurisation pressurization prestige presume pretzel prevalence prevention prey price pricing pride priest priesthood primary primate prince princess principal principle print printer printing prior priority prison prisoner privacy private privilege prize prizefight probability probation probe problem procedure proceedings process processing processor proctor procurement produce producer product production productivity profession professional professor profile profit progenitor program programme programming progress progression prohibition project proliferation promenade promise promotion prompt pronoun pronunciation proof proofreader propaganda propane property prophet proponent proportion proposal proposition proprietor prose prosecution prosecutor prospect prosperity prostacyclin prostanoid prostrate protection protein protest protocol providence provider province provision prow proximal proximity prune pruner pseudocode pseudoscience psychiatrist psychoanalyst psychologist psychology ptarmigan pub public publication publicity publisher publishing pudding puddle puffin pug puggle pulley pulse puma pump pumpernickel pumpkin pumpkinseed pun punch punctuation punishment pup pupa pupil puppet puppy purchase puritan purity purple purpose purr purse pursuit push pusher put puzzle pyramid pyridine quadrant quail qualification quality quantity quart quarter quartet quartz queen query quest question questioner questionnaire quiche quicksand quiet quill quilt quince quinoa quit quiver quota quotation quote rabbi race racer racing racism racist rack radar radiator radio radiosonde radish raffle raft rag rage rail railing railroad railway raiment rainbow raincoat rainmaker rainstorm rainy raise raisin rake rally ram rambler ramen ramie ranch rancher randomisation randomization range ranger rank rap rape raspberry rat rate ratepayer rating ratio rationale rations raven ravioli rawhide ray rayon razor reach reactant reaction read reader readiness reading real reality realization realm reamer rear reason reasoning rebel rebellion reboot recall recapitulation receipt receiver reception receptor recess recession recipe recipient reciprocity reclamation recliner recognition recollection recommendation reconsideration record recorder recording recovery recreation recruit rectangle red redesign redhead redirect rediscovery reduction reef refectory reference referendum reflection reform refreshments refrigerator refuge refund refusal refuse regard regime region regionalism register registration registry regret regulation regulator rehospitalisation rehospitalization reindeer reinscription reject relation relationship relative relaxation relay release reliability relief religion relish reluctance remains remark reminder remnant remote removal renaissance rent reorganisation reorganization repair reparation repayment repeat replacement replica replication reply report reporter reporting repository representation representative reprocessing republic republican reputation request requirement resale rescue research researcher resemblance reservation reserve reservoir reset residence resident residue resist resistance resolution resolve resort resource respect respite response responsibility rest restaurant restoration restriction restroom restructuring result resume retailer retention rethinking retina retirement retouching retreat retrospect retrospective retrospectivity return reunion revascularisation revascularization reveal revelation revenant revenge revenue reversal reverse review revitalisation revitalization revival revolution revolver reward rhetoric rheumatism rhinoceros rhubarb rhyme rhythm rib ribbon rice riddle ride rider ridge riding rifle right rim ring ringworm riot rip ripple rise riser risk rite ritual riverbed rivulet roadway roar roast robe robin robot robotics rock rocker rocket rocketship rod role roll roller romaine romance roof room roommate rooster root rope rose rosemary roster rostrum rotation round roundabout route router routine row rowboat rowing rubber rubbish rubric ruckus rudiment ruffle rug rugby ruin rule ruler ruling rum rumor run runaway runner running runway rush rust rutabaga rye sabre sac sack saddle sadness safari safe safeguard safety saffron sage sail sailboat sailing sailor saint sake salad salami salary sale salesman salmon salon saloon salsa salt salute samovar sampan sample samurai sanction sanctity sanctuary sand sandal sandbar sandpaper sandwich sanity sardine sari sarong sash satellite satin satire satisfaction sauce saucer sauerkraut sausage savage savannah saving savings savior saviour savory saw saxophone scaffold scale scallion scallops scalp scam scanner scarecrow scarf scarification scenario scene scenery scent schedule scheduling schema scheme schizophrenic schnitzel scholar scholarship school schoolhouse schooner science scientist scimitar scissors scooter scope score scorn scorpion scotch scout scow scrambled scrap scraper scratch screamer screen screening screenwriting screw screwup screwdriver scrim scrip script scripture scrutiny sculpting sculptural sculpture seabass seafood seagull seal seaplane search seashore seaside season seat seaweed second secrecy secret secretariat secretary secretion section sectional sector security sediment seed seeder seeker seep segment seizure selection self selfconfidence selfcontrol selfesteem seller selling semantics semester semicircle semicolon semiconductor seminar senate senator sender senior sense sensibility sensitive sensitivity sensor sentence sentencing sentiment sepal separation septicaemia sequel sequence serial series sermon serum serval servant server service servitude sesame session set setback setting settlement settler severity sewer sex sexuality shack shackle shade shadow shadowbox shakedown shaker shallot shallows shame shampoo shanty shape share shareholder shark shaw shawl shear shearling sheath shed sheep sheet shelf shell shelter sherbet sherry shield shift shin shine shingle shipper shipping shipyard shirt shirtdress shit shoat shock shoehorn shoelace shoemaker shoes shoestring shofar shoot shootdown shop shopper shopping shore shoreline short shortage shorts shortwave shot shoulder shout shovel show showstopper shower shred shrimp shrine shutdown sibling sick sickness side sideboard sideburns sidecar sidestream sidewalk siding siege sigh sight sightseeing sign signal signature signet significance signify signup silence silica silicon silk silkworm sill silly silo silver similarity simple simplicity simplification simvastatin sin singer singing singular sink sinuosity sip sir sister sisterinlaw sitar site situation size skate skating skean skeleton ski skiing skill skin skirt skull skullcap skullduggery skunk skylight skyline skyscraper skywalk slang slapstick slash slate slave slavery slaw sled sledge sleep sleepiness sleeping sleet sleuth slice slide slider slime slip slipper slippers slope slot sloth slump smell smelting smile smith smock smog smoke smoking smolt smuggling snack snail snake snakebite snap snarl sneaker sneakers sneeze sniffle snob snorer snow snowboarding snowflake snowman snowmobiling snowplow snowstorm snowsuit snuck snug snuggle soap soccer socialism socialist society sociology sock soda sofa softball softdrink softening software soil soldier sole solicitation solicitor solidarity solidity soliloquy solitaire solution solvency sombrero somebody someone someplace somersault something somewhere son sonar sonata song songbird sonnet soot sophomore soprano sorbet sorghum sorrel sorrow sort soul soulmate sound soundness soup source sourwood sousaphone south southeast souvenir sovereignty sow soy soybean space spacing spade spaghetti span spandex spank sparerib spark spasm spat spatula spawn speaker speakerphone speaking spear spec special specialist specialty species specification spectacle spectacles spectrograph spectrum speculation speech speed speedboat spell spelling spelt spending sphere sphynx spice spiderling spike spill spinach spine spiral spirit spiritual spirituality spit spite spleen splendor split spokesman spokeswoman sponge sponsor sponsorship spool spoon spork sport sportsman spot spotlight spouse sprag sprat spray spread spreadsheet spree spring sprinkles sprinter sprout spruce spud spume spur spy spyglass square squatter squeegee squid stab stability stable stack stacking stadium staff stag stage stain stair staircase stake stalk stall stallion stamen stamina stamp stance stand standard standardisation standardization standing standoff standpoint starboard start starter state statement statin station stationwagon statistic statistics statue status statute stay steak stealth steam steamroller steel steeple stem stench stencil step stepaunt stepbrother stepdaughter stepfather stepgrandfather stepgrandmother stepmother stepsister stepson stepuncle steppingstone stereo stew steward stick sticker stiletto still stimulation stimulus sting stinger stirfry stitch stitcher stock stockintrade stockings stole stomach stone stonework stool stop stopsign stopwatch storage store storey storm story storytelling storyboard stot stove strait strand stranger strap strategy straw strawberry strawman streetcar strength stress stretch strife strike string strip stripe strobe stroke structure strudel struggle stucco stud student studio study stuff stumbling stump stupidity sturgeon sty style styling stylus sub subcomponent subconscious subcontractor subexpression subgroup subject submarine submitter subprime subroutine subscription subsection subset subsidence subsidiary subsidy substance substitution subtitle suburb subway success succotash suck sucker suede suet suffocation sugar suggestion suicide suit suitcase suite sulfur sultan sum summary summer summit sunbeam sunbonnet sundae sunday sundial sunflower sunglasses sunlamp sunlight sunrise sunroom sunset sunshine superiority supermarket supernatural supervision supervisor supper supplement supplier supply support supporter suppression supreme surface surfboard surge surgeon surgery surname surplus surprise surround surroundings surrounds survey survival survivor sushi suspect suspenders suspension sustainment sustenance swallow swamp swan swanling swath sweat sweater sweatshirt sweatshop sweatsuit sweets swell swim swimming swimsuit swine swing switch switchboard switching swivel sword swordfight swordfish sycamore symbol symmetry sympathy symptom syndicate syndrome synergy synod synonym synthesis syrup system tshirt tab tabby tabernacle tablecloth tablet tabletop tachometer tackle taco tactics tactile tadpole tag tail tailbud tailor tailspin takeout takeover tale talent talk talking tambour tambourine tan tandem tangerine tank tanktop tanker tankful tap tape tapioca target taro tarragon tart task tassel taste tatami tattler tattoo tavern tax taxi taxicab taxpayer tea teacher teaching team teammate tear tech technician technique technologist technology tectonics teen teenager teepee telephone telescreen teletype television tell teller temp temper temperature temple tempo temporariness temporary temptation temptress tenant tendency tender tenement tenet tennis tenor tension tensor tent tentacle tenth tepee teriyaki term terminal termination terminology termite terrace terracotta terrapin terrarium territory terror terrorism terrorist test testament testimonial testimony testing text textbook textual texture thanks thaw theater theft theism theme theology theory therapist therapy thermals thermometer thermostat thesis thickness thief thigh thing thinking thirst thistle thong thongs thorn thought thousand thread threat threshold thrift thrill throat throne thrush thrust thug thumb thump thunder thunderbolt thunderhead thunderstorm thyme tiara tic tick ticket tide tie tiger tights tile till tilt timbale timber time timeline timeout timer timetable timing timpani tin tinderbox tinkle tintype tip tire tissue titanium title toad toaster tobacco today toe toenail toffee tofu tog toga toilet tolerance tolerant toll tomtom tomatillo tomb tomography tomorrow ton tonality tone tongue tonic tonight tool toot tooth toothbrush toothpaste toothpick top tophat topic topsail toque toreador tornado torso torte tortellini tortilla tortoise tosser total tote touch toughguy tour tourism tourist tournament towtruck towel tower town townhouse township toy trace trachoma track tracking tracksuit tract tractor trade trader trading tradition traditionalism traffic trafficker tragedy trail trailer trailpatrol train trainer training trait tram tramp trance transaction transcript transfer transformation transit transition translation transmission transom transparency transplantation transport transportation trap trapdoor trapezium trapezoid trash travel traveler tray treasure treasury treat treatment treaty tree trek trellis tremor trench trend triad trial triangle tribe tributary trick trigger trigonometry trillion trim trinket trip tripod tritone triumph trolley trombone troop trooper trophy trouble trousers trout trove trowel trunk trust trustee truth try tsunami tub tube tuber tug tugboat tuition tumbler tummy tuna tune tuneup tunic tunnel turban turf turkey turmeric turn turning turnip turnover turnstile turret turtle tusk tussle tutu tuxedo tweet tweezers twig twilight twine twins twist twister twitter type typeface typewriter typhoon ukulele ultimatum unblinking uncertainty uncle underclothes underestimate underground underneath underpants underpass undershirt understanding understatement undertaker underwear underweight underwire underwriting unemployment unibody uniform uniformity union unique unit unity universe university update upgrade uplift upper upstairs upward urge urgency urn usage use user usher usual utensil utilisation utility utilization vacation vaccine vacuum vagrant valance valentine validate validity valuable value vampire van vanadyl vane vanilla vanity variability variable variant variation variety vascular vault vaulting veal vector vegetable vegetarian vegetarianism vegetation vehicle veil vein veldt vellum velocity velodrome velvet vendor veneer vengeance venison venom venti venture venue veranda verb verdict verification vermicelli vernacular verse version vertigo verve vessel vest vestment vet veteran veterinarian veto viability vibe vibraphone vibration vibrissae vice vicinity victim victory video view viewer vignette villa village vine vinegar vineyard vintage vintner vinyl viola violation violence virginal virtue virus visa viscose vise vision visit visitor visor vista visual vitality vitamin vitro vivo vixen vodka vogue voice void vol volatility volcano volleyball volume volunteer volunteering vomit vote voter voting voyage vulture wad wafer waffle wage wagon waist waistband wait waiter waiting waitress waiver wake walk walker walking walkway wall wallaby wallet walnut walrus wampum wannabe want war warden wardrobe warfare warlock warlord warmup warming warmth warning warrant warren warrior wasabi wash washbasin washcloth washer washtub wasp waste wastebasket wasting watch watcher watchmaker waterbed watercress waterfall waterfront watermelon waterskiing waterspout waterwheel wave waveform wax way weakness wealth weapon wear weasel weather web webinar webmail webpage website wedding wedge weed weeder weedkiller week weekend weekender weight weird welcome welfare well wellbeing west western wetbar wetland wetsuit whack whale wharf wheat wheel whelp whey whip whirlpool whirlwind whisker whiskey whisper whistle white whole wholesale wholesaler whorl wick widget widow width wife wifi wild wildebeest wilderness wildlife will willingness willow win windchime windage windscreen windshield wine winery wing wingman wingtip wink winner winter wire wiretap wiring wisdom wiseguy wish wisteria wit witch witchhunt withdrawal witness wok wolf woman wombat wonder wont wood woodchuck woodland woodshed woodwind wool woolens word wording work workbench worker workforce workhorse working workout workplace workshop world worm worry worship worshiper worth wound wrap wraparound wrapper wrapping wreck wrecker wren wrench wrestler wriggler wrinkle wrist writer writing wrong xylophone yacht yahoo yak yam yang yard yarmulke yarn yawl year yeast yellow yellowjacket yesterday yew yin yoga yogurt yoke yolk young youngster yourself youth yoyo yurt zampone zebrafish zen zephyr zero ziggurat zinc zipper zither zombie zone zoologist zoology zootsuit zucchini boat diamond lemon apple orange orchestra ruby sun ship owl star butter jungle stepmother sea sparrow stream ball glove elephant piano daisy valley motorcycle vase balloon iris ink river door chair lion zoo boot canoe ocean window shoe fire lightning rain raid squirrel stepson curtain hill armrest hat water kayak tomato cream zebra cartoon house bottle socks teapot onion flute desk kangaroo earth tulip moon forest bestseller emerald rabbit street cello potato mint table shoehorn oboe toast stepdaughter tuba coconut truck trumpet sky umbrella mountain giraffe planet squash violin hair box grasshopper penguin nest octopus bird road wind lake monkey airplane prairie".split())
                adjective=random.choice("ancient antique aquatic baby basic big bitter black blue bottle bottled brave breezy bright brown calm charming cheerful chummy classy clear clever cloudy cold cool crispy curly daily deep delightful dizzy down dynamic elated elegant excited exotic fancy fast fearless festive fluffy fragile fresh friendly funny fuzzy gentle gifted gigantic graceful grand grateful great green happy heavy helpful hot hungry husky icy imaginary invisible jagged jolly joyful joyous kind large light little lively lovely lucky lumpy magical manic melodic mighty misty modern narrow new nifty noisy normal odd old orange ordinary painless pastel peaceful perfect phobic pink polite precious pretty purple quaint quick quiet rapid red rocky rough round royal rugged rustic safe sandy shiny silent silky silly slender slow small smiling smooth snug soft sour strange strong sunny sweet swift thirsty thoughtful tiny uneven unusual vanilla vast violet warm watery weak white wide wild wilde windy wise witty wonderful yellow young zany abandoned able absolute academic acceptable acclaimed accomplished accurate aching acidic acrobatic active actual adept admirable admired adolescent adorable adored advanced adventurous affectionate afraid aged aggravating aggressive agile agitated agonizing agreeable ajar alarmed alarming alert alienated alive all altruistic amazing ambitious ample amused amusing anchored ancient angelic angry anguished animated annual another antique anxious any apprehensive appropriate apt arctic arid aromatic artistic ashamed assured astonishing athletic attached attentive attractive austere authentic authorized automatic avaricious average aware awesome awful awkward babyish back bad baggy bare barren basic beautiful belated beloved beneficial best better bewitched big big-hearted biodegradable bite-sized bitter black black-and-white bland blank blaring bleak blind blissful blond blue blushing bogus boiling bold bony boring bossy both bouncy bountiful bowed brave breakable brief bright brilliant brisk broken bronze brown bruised bubbly bulky bumpy buoyant burdensome burly bustling busy buttery buzzing calculating calm candid canine capital carefree careful careless caring cautious cavernous celebrated charming cheap cheerful cheery chief chilly chubby circular classic clean clear clear-cut clever close closed cloudy clueless clumsy cluttered coarse cold colorful colorless colossal comfortable common compassionate competent complete complex complicated composed concerned concrete confused conscious considerate constant content conventional cooked cool cooperative coordinated corny corrupt costly courageous courteous crafty crazy creamy creative creepy criminal crisp critical crooked crowded cruel crushing cuddly cultivated cultured cumbersome curly curvy cute cylindrical damaged damp dangerous dapper daring dark darling dazzling dead deadly deafening dear dearest decent decimal decisive deep defenseless defensive defiant deficient definite definitive delayed delectable delicious delightful delirious demanding dense dental dependable dependent descriptive deserted detailed determined devoted different difficult digital diligent dim dimpled dimwitted direct dirty disastrous discrete disfigured disguised disgusting dishonest disloyal dismal distant distinct distorted dizzy dopey doting double downright drab drafty dramatic dreary droopy dry dual dull dutiful ach eager early earnest easy easy-going ecstatic edible educated elaborate elastic elated elderly electric elegant elementary elliptical embarrassed embellished eminent emotional empty enchanted enchanting energetic enlightened enormous enraged entire envious equal equatorial essential esteemed ethical euphoric even evergreen everlasting every evil exalted excellent excitable excited exciting exemplary exhausted exotic expensive experienced expert extra-large extra-small extraneous extroverted fabulous failing faint fair faithful fake false familiar famous fancy fantastic far far-flung far-off faraway fast fat fatal fatherly favorable favorite fearful fearless feisty feline female feminine few fickle filthy fine finished firm first firsthand fitting fixed flaky flamboyant flashy flat flawed flawless flickering flimsy flippant flowery fluffy fluid flustered focused fond foolhardy foolish forceful forked formal forsaken forthright fortunate fragrant frail frank frayed free french frequent fresh friendly frightened frightening frigid frilly frivolous frizzy front frosty frozen frugal fruitful full fumbling functional funny fussy fuzzy gargantuan gaseous general generous gentle genuine giant giddy gifted gigantic giving glamorous glaring glass gleaming gleeful glistening glittering gloomy glorious glossy glum golden good good-natured gorgeous graceful gracious grand grandiose granular grateful grave gray great greedy green gregarious grim grimy gripping grizzled gross grotesque grouchy grounded growing growling grown grubby gruesome grumpy guilty gullible gummy hairy half handmade handsome handy happy happy-go-lucky hard hard-to-find harmful harmless harmonious harsh hasty hateful haunting healthy heartfelt hearty heavenly heavy hefty helpful helpless hidden hideous high high-level hilarious hoarse hollow homely honest honorable honored hopeful horrible hospitable hot huge humble humiliating humming humongous hungry hurtful husky icky icy ideal idealistic identical idiotic idle idolized ignorant ill ill-fated ill-informed illegal illiterate illustrious imaginary imaginative immaculate immaterial immediate immense impartial impassioned impeccable imperfect imperturbable impish impolite important impossible impractical impressionable impressive improbable impure inborn incomparable incompatible incomplete inconsequential incredible indelible indolent inexperienced infamous infantile infatuated inferior infinite informal innocent insecure insidious insignificant insistent instructive insubstantial intelligent intent intentional interesting internal international intrepid ironclad irresponsible irritating itchy jaded jagged jam-packed jaunty jealous jittery joint jolly jovial joyful joyous jubilant judicious juicy jumbo jumpy junior juvenile kaleidoscopic keen key kind kindhearted kindly klutzy knobby knotty knowing knowledgeable known kooky kosher lame lanky large last lasting late lavish lawful lazy leading leafy lean left legal legitimate light lighthearted likable likely limited limp limping linear lined liquid little live lively livid loathsome lone lonely long long-term loose lopsided lost loud lovable lovely loving low loyal lucky lumbering luminous lumpy lustrous luxurious mad made-up magnificent majestic major male mammoth married marvelous masculine massive mature meager mealy mean measly meaty medical mediocre medium meek mellow melodic memorable menacing merry messy metallic mild milky mindless miniature minor minty miserable miserly misguided misty mixed modern modest moist monstrous monthly monumental moral mortified motherly motionless mountainous muddy muffled multicolored mundane murky mushy musty muted mysterious naive narrow nasty natural naughty nautical near neat necessary needy negative neglected negligible neighboring nervous new next nice nifty nimble nippy nocturnal noisy nonstop normal notable noted noteworthy novel noxious numb nutritious nutty obedient obese oblong obvious occasional odd oddball offbeat offensive official oily old old-fashioned only open optimal optimistic opulent orange orderly ordinary organic original ornate ornery other our outgoing outlandish outlying outrageous outstanding oval overcooked overdue overjoyed overlooked palatable pale paltry parallel parched partial passionate past pastel peaceful peppery perfect perfumed periodic perky personal pertinent pesky pessimistic petty phony physical piercing pink pitiful plain plaintive plastic playful pleasant pleased pleasing plump plush pointed pointless poised polished polite political poor popular portly posh positive possible potable powerful powerless practical precious present prestigious pretty previous pricey prickly primary prime pristine private prize probable productive profitable profuse proper proud prudent punctual pungent puny pure purple pushy putrid puzzled puzzling quaint qualified quarrelsome quarterly queasy querulous questionable quick quick-witted quiet quintessential quirky quixotic quizzical radiant ragged rapid rare rash raw ready real realistic reasonable recent reckless rectangular red reflecting regal regular reliable relieved remarkable remorseful remote repentant repulsive required respectful responsible revolving rewarding rich right rigid ringed ripe roasted robust rosy rotating rotten rough round rowdy royal rubbery ruddy rude rundown runny rural rusty sad safe salty same sandy sane sarcastic sardonic satisfied scaly scarce scared scary scented scholarly scientific scornful scratchy scrawny second second-hand secondary secret self-assured self-reliant selfish sentimental separate serene serious serpentine several severe shabby shadowy shady shallow shameful shameless sharp shimmering shiny shocked shocking shoddy short short-term showy shrill shy sick silent silky silly silver similar simple simplistic sinful single sizzling skeletal skinny sleepy slight slim slimy slippery slow slushy small smart smoggy smooth smug snappy snarling sneaky sniveling snoopy sociable soft soggy solid somber some sophisticated sore sorrowful soulful soupy sour spanish sparkling sparse specific spectacular speedy spherical spicy spiffy spirited spiteful splendid spotless spotted spry square squeaky squiggly stable staid stained stale standard starchy stark starry steel steep sticky stiff stimulating stingy stormy straight strange strict strident striking striped strong studious stunning stupendous stupid sturdy stylish subdued submissive substantial subtle suburban sudden sugary sunny super superb superficial superior supportive sure-footed surprised suspicious svelte sweaty sweet sweltering swift sympathetic talkative tall tame tan tangible tart tasty tattered taut tedious teeming tempting tender tense tepid terrible terrific testy thankful that these thick thin third thirsty this thorny thorough those thoughtful threadbare thrifty thunderous tidy tight timely tinted tiny tired torn total tough tragic trained traumatic treasured tremendous triangular tricky trifling trim trivial troubled true trusting trustworthy trusty truthful tubby turbulent twin ugly ultimate unacceptable unaware uncomfortable uncommon unconscious understated unequaled uneven unfinished unfit unfolded unfortunate unhappy unhealthy uniform unimportant unique united unkempt unknown unlawful unlined unlucky unnatural unpleasant unrealistic unripe unruly unselfish unsightly unsteady unsung untidy untimely untried untrue unused unusual unwelcome unwieldy unwilling unwitting unwritten upbeat upright upset urban usable used useful useless utilized utter vacant vague vain valid valuable vapid variable vast velvety venerated vengeful verifiable vibrant vicious victorious vigilant vigorous villainous violent violet virtual virtuous visible vital vivacious vivid voluminous wan warlike warm warmhearted warped wary wasteful watchful waterlogged watery wavy weak wealthy weary webbed wee weekly weepy weighty weird welcome well-documented well-groomed well-informed well-lit well-made well-off well-to-do well-worn wet which whimsical whirlwind whispered white whole whopping wicked wide wide-eyed wiggly wild willing wilted winding windy winged wiry wise witty wobbly woeful wonderful wooden woozy wordy worldly worn worried worrisome worse worst worthless worthwhile worthy wrathful wretched writhing wry melodic watery wonderful precious fuzzy curly ancient unusual blue pink royal purple basic black white antique heavy grateful bright sandy cold helpful misty hungry round narrow quick clever charming safe warm cool noisy thoughtful silent uneven jolly quaint pretty icy witty red friendly bitter joyful lovely new orange joyous deep imaginary sweet windy gentle graceful great kind cloudy smooth gifted clear light shiny soft gigantic husky normal brown lucky polite sunny weak big fearless strong rapid pastel perfect delightful nifty happy excited ordinary thirsty old brave exotic lively dizzy elegant cheerful odd silly large small vast swift slow little funny lumpy silky fast tiny grand peaceful calm strange hot fancy modern fluffy violet rough jagged wise elated wide quiet green sour fresh wild".split())
                print(f"{random.choice([adjective.title(),adjective.capitalize(),adjective.lower(),adjective.upper()])}{random.choice(['-','_','.',''])}{random.choice([noun.title(),noun.capitalize(),noun.lower(),noun.upper()])}{''.join(str(random.randint(1,9)) for _ in range(1,random.randint(1,10)+1)) if random.choice([True,False]) else ''}\n")
            elif main_command == "RandomInteger":
                if len(parts) == 3:
                    try:first_num=int(parts[1])
                    except ValueError:print("Invalid argument. Please enter an integer for the first number.\n");continue
                    try:second_num=int(parts[2])
                    except ValueError:print("Invalid argument. Please enter an integer.\n");continue
                    if first_num > second_num:print("Invalid argument. Please enter an integer greater than the first integer for the second number.\n");continue
                    print(f"{random.randint(first_num,second_num)}\n")
                else:print("""Invalid argument. Usage
RandomInteger
├── Arg1
│   └── <<Integer>>
└── Arg2
    └── <<Integer>>\n""")
            elif main_command == "Stopwatch":
                if len(parts) > 1:
                    if ' '.join(parts[1:]) == "Start":
                        if stopwatch == False:stopwatch_start_time=time.time();stopwatch=True;print("Stopwatch is running.\n")
                        else:print("Stopwatch is already running.\n")
                    elif ' '.join(parts[1:]) == "Stop":
                        if stopwatch:elapsed=(time.time() - stopwatch_start_time) + rset;rset=elapsed;shelve.open("data.db")["RecentStopwatchElapsedTime"]=elapsed;stopwatch=False;print(f"Stopwatch stopped.\nElapsed time: [{int((elapsed) // 3600):02d}:{int((elapsed) % 3600 // 60):02d}:{int((elapsed) % 60):02d}.{int(((elapsed) - int(elapsed)) * 1000):02d}]\n")
                        else:print("Stopwatch is not running.\n")
                    elif ' '.join(parts[1:]) == "Reset":stopwatch=False;stopwatch_start_time=None;rset=0;shelve.open("data.db")["RecentStopwatchElapsedTime"]=0;print("Stopwatch reset.\n")
                    elif ' '.join(parts[1:]) == "RecentElapsedTime":print(f"{shelve.open('data')['RecentStopwatchElapsedTime']}\n")
                    else:print("Invalid argument. Options are only Start, Stop, Reset, and RecentElapsedTime.\n")
                else:print("""Invalid argument. Usage
Stopwatch
└── Arg1
    ├── (Start)
    ├── (Stop)
    ├── (Reset)
    └── (RecentElapsedTime)\n""")
            elif main_command == "Timer":
                if len(parts) > 1:
                    try:
                        time_str=' '.join(parts[1:]);time_parts=list(map(int,time_str.split(":")))
                        if len(time_parts) == 2:hours=0;minutes,seconds=time_parts
                        elif len(time_parts) == 3:hours,minutes,seconds=time_parts
                        else:print("Invalid argument. Please use the format HH:MM:SS.\n")
                        if any(t < 0 for t in (hours,minutes,seconds)):print("Invalid argument. Please enter non-negative values for hours, minutes and seconds.\n");continue
                        total_seconds=hours * 3600 + minutes * 60 + seconds
                        if total_seconds == 0:print("Invalid argument. Timer duration cannot be zero.\n");continue
                        try:
                            i=total_seconds
                            while i >= 0:
                                print(f"\r{i // 3600:02d}:{(i % 3600) // 60:02d}:{i % 60:02d}",end="",flush=True)
                                if i > 0:time.sleep(1)
                                i -= 1
                            print();print("\033[A\033[KTimes up!")
                            if shutil.which("play-audio") is not None and os.path.exists("beep.mp3") is True:
                                while True:
                                    try:os.system("play-audio -s alarm beep.mp3");time.sleep(29)
                                    except (KeyboardInterrupt,EOFError):raise KeyboardInterrupt
                            else:print()
                        except (KeyboardInterrupt,EOFError):print();print()
                    except ValueError as e:print(f"Invalid argument. {e}. Please use the format HH:MM:SS or MM:SS.\n")
                else:print("""Invalid argument. Usage
Timer
└── Arg1
    └── <<Time>>\n""")
            elif main_command == "DaysUntil":
                if len(parts) >= 2:
                    try:
                        target_date=datetime.datetime.strptime(parts[1],"%Y/%m/%d").date()
                        if len(parts) >= 3:
                            target_date2=datetime.datetime.strptime(' '.join(parts[2:]),"%Y/%m/%d").date()
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
                else:print("""Invalid argument. Usage
DaysUntil
├── Arg1
│   └── <<Date>>
└── Arg2
    ├── ()
    └── <<Date>>\n""")
            elif main_command == "TimeToLoadUrl":
                if len(parts) > 1:
                    url=' '.join(parts[1:])
                    if " " in url:print("Invalid argument. Url cannot contain spaces.\n");break
                    if ("https" or "http") not in url:url="https://"+url
                    start_time=time.time();requests.get(url);end_time=time.time();print(f"Time spent: [{int((end_time - start_time) // 3600):02d}:{int((end_time - start_time) % 3600 // 60):02d}:{int((end_time - start_time) % 60):02d}.{int(((end_time - start_time) - int(end_time - start_time)) * 1000):02d}] loading url.\n")
                else:print("""Invalid argument. Usage
TimeToLoadUrl
└── Arg1
    └── <<Url>>\n""")
            elif command == "CheckInternetSpeed":
                while True:
                    try:start_time=time.time();st=speedtest.Speedtest();st.get_best_server();print(f"Download speed: {(st.download() / 10000000):.2f} Mbps\nUpload speed:   {(st.upload() / 1000000):.2f} Mbps\nPing:           {(st.results.ping):.2f} ms");end_time=time.time();print(f"Duration:       [{int((end_time - start_time) // 3600):02d}:{int((end_time - start_time) % 3600 // 60):02d}:{int((end_time - start_time) % 60):02d}.{int(((end_time - start_time) - int(end_time - start_time)) * 1000):02d}]\n");break
                    except TimeoutError:time.sleep(5);continue
            elif command == "CheckInternet":
                try:requests.get("https://www.google.com",timeout=10).raise_for_status();internet_connection=True
                except Exception:internet_connection=False
                print(f"The internet connection is {'' if internet_connection else 'un'}stable.\n")
            elif main_command == "Calendar":
                if len(parts) > 1:
                    try:print(calendar.calendar(int(' '.join(parts[1:]))));print('' if ' '.join(parts[1:]) != str(datetime.date.today().year) else f'Date: {time.strftime(f"%Y/%m/%d")}\n\n',end='')
                    except ValueError:print("Invalid argument. Year must be a number.\n")
                else:print(calendar.calendar(datetime.date.today().year));print(f'Date: {time.strftime(f"%Y/%m/%d")}\n')
            elif command == "Clear":print("\033c",end="")
            elif command == "RerunCode":print("\033c",end="");os.system(f"{sys.executable} {__file__}")
            elif main_command == "ChangeUsername":
                if len(parts) > 1:
                    new_name=' '.join(parts[1:]).lstrip()
                    if not new_name:print("Invalid argument. Username cannot be empty.\n");continue
                    if new_name == "default":shelve.open("data.db")["Username"]=f"User {random.randint(1,100)}"
                    else:shelve.open("data.db")["Username"]=new_name
                else:print("""Invalid argument. Usage
ChangeUsername
└── Arg1
    └── <<Username>>\n""")
            elif command == "Time":
                while True:
                    try:print(time.strftime(f"\rDate: %Y/%m/%d Time: %I:%M:%S %p"),end="",flush=True);time.sleep(.001)
                    except (KeyboardInterrupt,EOFError):print();print();break
            elif main_command == "CommandHistory":
                if len(parts) > 1:
                    if ' '.join(parts[1:]) == "List":
                        if not command_history():print("No recent commands.\n")
                        else:print("\n".join([f"{i}. {cmd}" for i,cmd in enumerate(command_history()[-len(command_history()):],1)]));print()
                    elif ' '.join(parts[1:]) == "Delete":
                        if not command_history():print("No recent commands.\n")
                        else:shelve.open("data.db")["CommandHistory"]=[];print("Recent commands deleted.\n")
                    else:print("Invalid argument. Options are only List, and Delete.\n")
                else:print("""Invalid argument. Usage
CommandHistory
└── Arg1
    ├── (List)
    └── (Delete)\n""")
            elif main_command == "RandomChoice":
                if len(parts) > 1:items=parts[1:];print("Invalid argument. Please provide atleast 2 choices separated by space.\n") if len(items) < 2 else print(f"{random.choice(items)}\n")
                else:print("""Invalid argument. Usage
RandomChoice
└── Arg1
    └── <<List>>\n""")
            elif command == "DeleteData":
                print()
                while True:
                    confirm=getch("\033[A\033[KConfirm (Y/N): ").lower()
                    if confirm == "y":print("\033[A\033[K",end="");os.remove("Data");print("\033c",end="");os.system(f"{sys.executable} {__file__}")
                    elif confirm == "n":print("\033[A\033[KDeletion of data cancelled.\n");break
                    else:continue
            elif main_command == "Exit":
                if len(parts) > 1:
                    if ' '.join(parts[1:]) == "Imm":end_time=time.time();print(f"Exited, Time spent: [{int((end_time - start_time) // 3600):02d}:{int((end_time - start_time) % 3600 // 60):02d}:{int((end_time - start_time) % 60):02d}.{int(((end_time - start_time) - int(end_time - start_time)) * 1000):02d}]\033[m\n");exit()
                    else:print("""Invalid argument. Usage
Exit
└── Arg1
    ├── ()
    └── (Imm)\n""")
                else:
                    print()
                    while True:
                        confirm=getch("\033[A\033[KConfirm (Y/N): ").lower()
                        if confirm == "y":end_time=time.time();print(f"\033[A\033[KExited, Time spent: [{int((end_time - start_time) // 3600):02d}:{int((end_time - start_time) % 3600 // 60):02d}:{int((end_time - start_time) % 60):02d}.{int(((end_time - start_time) - int(end_time - start_time)) * 1000):02d}]\033[m\n");exit()
                        elif confirm == "n":print("\033[A\033[KExit cancelled.\n");break
                        else:continue
            else:
                if main_command in valid_commands:not_implemented(main_command)
                else:
                    valid_commands_lower=[cmd.lower() for cmd in valid_commands];suggestions=difflib.get_close_matches(main_command.lower(),valid_commands_lower,n=3,cutoff=.6)
                    if suggestions:suggestions_original_case=[valid_commands[valid_commands_lower.index(s)] for s in suggestions];print((f"Did you mean: \"{suggestions_original_case[0]}\".\n") if len(suggestions_original_case) == 1 else ("Did you mean one of these: "+", ".join(f"\"{s}\"" for s in suggestions_original_case)+".\n"))
                    else:print(f"Unknown command: \"{main_command}\".\n")
        except (KeyboardInterrupt,EOFError):print(f"\n\033[90mPyExec interrupted.\n\033[m");exit()
        except Exception as error:print(f"Error: {repr(error)}.\n")

try:
    if __name__ == "__main__":Main()
finally:print("\033[m\033[?25h",end="")

#####---------- END ----------#####
