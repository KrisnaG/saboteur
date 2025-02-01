# Saboteur

## Author
Krisna Gusti

## Description

In "Saboteur," players will assume the roles of either dwarves or saboteurs with the common goal of reaching the hidden 
gold treasure by constructing a pathway. However, there's a twist – the saboteurs will secretly try to hinder the dwarves' 
progress, adding an element of uncertainty to the gameplay.

## Requirements

The une_ai Python package is required for the program. The package can be found here 
***https://pypi.org/project/une-ai/*** and installed using pip:

```Bash
pip install une_ai
```

If you have une_ai installed already, ensure it is up to date by executing the following command:

```Bash
pip install --upgrade une_ai
```

The package pomegranate is also required for the program. Install the package with the command:

```Bash
pip install pomegranate
```

A Python Virtual Environments is required to run this package. It can be created using conda:

```Bash
conda create -n <name>
```

## Usage

Move into the src folder from root directory:
```Bash
cd src/
```

Ensure a conda environment is created and activated:
```Bash
conda activate <name>
```

Ensure the packages une_ai and pomegranate listed in the requirements are installed (refer to the requirements section for installation). If you are unsure what packages you have installed in pip execute the following command:
```Bash
pip list
```

Execute the program in Python:
```python
python3 saboteur_app.py
```

Once the program starts a PyGame window should appear and the game immediately starts. To start a new game close any
PyGame windows and execute the program as above.

### Additional Information

The game is currently implemented with all AI players, with 8 players being either 2-3 saboteurs player and the 
remaining being gold miners. Players are listed from P0 to P7.

On the main PyGame window underneath the game lists the game state and information. This includes players current turn 
or winner, gold miner players, saboteur players, last action played, sabotaged players, cards currently in each players 
hand and the announcements made by each player (as ((coordinates), isGold)).

The knowledge base appears in the terminal console which specifies how a player perceives all other players 
(gold miner or saboteur).
