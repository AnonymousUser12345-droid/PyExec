# PyExec

## 🧑‍💻 Commands

```plain
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
    └── <<AlarmFileName>>
Clear
Pass
Usage
└── Arg1
    ├── (CommandHistory)
    ├── (ChangeUsername)
    ├── (ChangeAlarmSound)
    ├── (Usage)
    ├── (UpdateCode)
    ├── (Exit)
    ├── (DaysUntil)
    ├── (Calendar)
    ├── (Timer)
    ├── (Stopwatch)
    ├── (RandomChoice)
    ├── (RandomInteger)
    └── (TimeToLoadUrl)
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
├── Arg1
│   └── <<Time>>
└── Arg2
    ├── ()
    └── (Alarm)
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
```

## 📷 Screenshot

![screenshot](screenshot.png)

## 🛠️ Installation

```bash
pkg update && pkg upgrade
pkg install git python
git clone https://github.com/AnonymousUser12345-droid/PyExec
cd PyExec
python main.py
```

## 📦 Dependencies & 🛠️ Installation

- [requests](https://pypi.org/project/requests/)
- [simpleeval](https://pypi.org/project/simpleeval/)
- [speedtest-cli](https://pypi.org/project/speedtest-cli/)
```bash
pip install requests simpleeval speedtest-cli
```
- [play-audio](https://github.com/termux/play-audio)
- [fastfetch](https://github.com/fastfetch-cli/fastfetch)
```bash
pkg install play-audio fastfetch
```
