# Protocol_bot (Experimental Protocol)
## General Purpose
This module is designed to save the effort of constructing experimental protocol for running bio-related experiments. In general, it consists of code generation portion and protocol building portion, in which the user can choose their desired features based on the input files.

## Installation
This library requires the python version ">= 3.9". Please follow the instruction below to install this module.

To get started, you should first clone the repository to your local computer:
```bash
git clone https://github.com/TonyLuGame/Protocol_bot.git
```
Then, you need to get into the repository:
```bash
cd Protocol_bot/
```
Later on, install the package on your local computer:
```bash
chmod +x install.sh
./install.sh
```
With this installs, you will be able to import Protocol_bot in your file!!!

## Protocol_bot User Guide
The Protocol_bot package follows the follwing structure:
```bash
Protocol_bot/
├── data/
│   └── Stock_Repository/      # Your Stock Solution Repository File
├── src/
│   └── protocol_bot/          # Core library source code
├── Code_Generator_Test_Output/ # Default place for generated python runners
├── Protocol_Test_File/        # Default place for generated protocols
├── install.sh                 # Help file for package download
├── pyproject.toml             # Required Package List File
└── experiments/               # Default place for storing input files
```
Guide for Quick Start:
- Store your stock repository file in the data/Stock_Repository/ folder
- Create a copy of the input template and move it to experiments/ folder (template for protocol or for code generation)
- Fill out the template file following its instruction and run it
- (optional) If you choose template for code generation, go to Code_Generator_Test_Output/ folder to check the runner_output and run to generate the protocol

Overview of Library Function in Protocol_bot:
- generate.py: generate input code for volume calculation
- repository.py: store the function for building the protocol repository
- search.py: search stock solution name in stock repository files of folder data/Stock_Repository/
- semantic.py: include function for finding the best match of solution names
- sort.py: operate tree sort to form calculation order of designed protocol
- volume.py: perform calculation on volumes and concentrations of solutions
- structure.py: generate the structure for protocol after calculations
- export.py: create the designed protocol based on the formed structure
- registry.py: contain functions for updating the central registry

```bash
For more details on protocol_bot, please check the input templates!!!
```