# Input files for generating protocol
from pathlib import Path
from protocol_bot import volume as PG
from protocol_bot import export as PB
from protocol_bot import repository as RP

# Define paths
RUNNER_SCRIPT = Path(__file__).resolve()
PROJECT_ROOT = RUNNER_SCRIPT.parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'Stock_Repository'

# ---- User Input ---- #
path_config = RP.PathConfig(
    stock_repo={
        DATA_DIR / 'GeneletRepository1.xlsx': {'val_col': 2, 'unit_col': None},
        DATA_DIR / 'ComponentRepository.xlsx': {'val_col': 1, 'unit_col': 2},
    },
    output_file=PROJECT_ROOT / 'data' / 'Protocol_Output' / 'protocol_output_2026-4-1.xlsx',
    central_registry=PROJECT_ROOT / 'data' / 'Stock_Repository' / 'Central_Protocol_Record.xlsx', #project root can be whatever
)
# ---- End of User Input ---- #

# Load repositories
repository_list = path_config.stock_repo
sRepo = RP.KeyValueRepository("Stock Solutions")
RP.stock_repo_load(repository_list, sRepo, key_idx=0) #key_idx is 0 because the first column in both repositories is the key column

# Define the composite protocol here
repo = sRepo.Repository.copy()
protocol = PG.CompositeProtocol(stockRepo=sRepo.Repository)

protocol.addSP(
    name = '20 uM S1 F-Q Pair',
    components = {
        "S1 Reporter 5' F rev": 20,
        "S1 Reporter 3' Q rev": 20,
        "10x Txn Buffer": 1,
    },
    finalVolume = 350,
    finalConcentration = 20,
    textFeature = "ANNEAL!"
)

protocol.addSP(
    name = '20 uM S10 F-Q Pair',
    components = {
        "Rep1a-F": 20,
        "Rep1a-Q": 20,
        "10x Txn Buffer": 1,
    },
    finalVolume = 350,
    finalConcentration = 20,
    textFeature = "ANNEAL!"
)

##pre anneal
protocol.addSP(
    name = '5 uM G1S10 OFF + B7',
    components = {
        "*G1S10-nt + B7": 5,
        "S10-t + B7": 5,
        "10x Txn Buffer": 1,
    },
    finalVolume = 40,
    finalConcentration = 5, 
    textFeature = "ANNEAL!"
)

# protocol.addSP(
#     name = '5 uM G4S1 OFF + B7',
#     components = {
#         "*G4S1-nt + B7": 5,
#         "S1-t + B7 (w/ 5PSHP)": 5,
#         "10x Txn Buffer": 1,
#     },
#     finalVolume = 40,
#     finalConcentration = 5, 
#     textFeature = "ANNEAL!"
# )

protocol.addSP(
    name = '5 uM G1R4 OFF + B7',
    components = {
        "*G1R4-nt + B7": 5,
        "R4-t + B7": 5,
        "10x Txn Buffer": 1,
    },
    finalVolume = 40,
    finalConcentration = 5, 
    textFeature = "ANNEAL!"
)

protocol.addSP(
    name = '5 uM G1R4 1.5x ON + B7',
    components = {
        "*G1R4-nt + B7": 5,
        "R4-t + B7": 5,
        "10x Txn Buffer": 1,
        "A1 (no q)": 7.5
    },
    finalVolume = 40,
    finalConcentration = 5, 
    textFeature = "ANNEAL!"
)
protocol.addSP(
    name = '5 uM G4R1 OFF + B7',
    components = {
        "*G4R1-nt + B7": 5,
        "R1-t + B7": 5,
        "10x Txn Buffer": 1,
    },
    finalVolume = 40,
    finalConcentration = 5, 
    textFeature = "ANNEAL!"
)

protocol.addSP(
    name = '5 uM G4R1 1.5x ON + B7',
    components = {
        "*G4R1-nt + B7": 5,
        "R1-t + B7": 5,
        "10x Txn Buffer": 1,
        "A4 (no Q)": 7.5
    },
    finalVolume = 40,
    finalConcentration = 5, 
    textFeature = "ANNEAL!"
)


# Template prep for G1S1 OFF (2x Neutravidin)
protocol.addSP(
    name = '1 uM G1S10 OFF 2x Neut',
    components = {
        "5 uM G1S10 OFF + B7": 1,
        "16.67 uM Neutravidin": 2,
        "10x Txn Buffer": 0.8,
    },
    finalVolume = 40,
    finalConcentration = 1,
    textFeature = "INCUBATE 1 HR!"
)

# Template prep for G1R5 OFF (2x Neutravidin)
protocol.addSP(
    name = '1 uM G1R4 OFF 2x Neut',
    components = {
        "5 uM G1R4 OFF + B7": 1,
        "16.67 uM Neutravidin": 2,
        "10x Txn Buffer": 0.8,
    },
    finalVolume = 40,
    finalConcentration = 1,
    textFeature = "INCUBATE 1 HR!"
)

# Template prep for G1R5 1.5x ON (2x Neutravidin)
protocol.addSP(
    name = '1 uM G1R4 1.5x ON 2x Neut',
    components = {
        "5 uM G1R4 1.5x ON + B7": 1,
        "16.67 uM Neutravidin": 2,
        "10x Txn Buffer": 0.8,
    },
    finalVolume = 40,
    finalConcentration = 1,
    textFeature = "INCUBATE 1 HR!"
)

# Template prep for G5R1 OFF (2x Neutravidin)
protocol.addSP(
    name = '1 uM G4R1 OFF 2x Neut',
    components = {
        "5 uM G4R1 OFF + B7": 1,
        "16.67 uM Neutravidin": 2,
        "10x Txn Buffer": 0.8,
    },
    finalVolume = 40,
    finalConcentration = 1,
    textFeature = "INCUBATE 1 HR!"
)

# Template prep for G5R1 1.5x ON (2x Neutravidin)
protocol.addSP(
    name = '1 uM G4R1 1.5x ON 2x Neut',
    components = {
        "5 uM G4R1 1.5x ON + B7": 1,
        "16.67 uM Neutravidin": 2,
        "10x Txn Buffer": 0.8,
    },
    finalVolume = 40,
    finalConcentration = 1,
    textFeature = "INCUBATE 1 HR!"
)

protocol.addSP(
    name = '20 U/uL T7 RNAP',
    components = {
        "200 U/uL RNAP": 20,
    },
    volumeDependency= 1.3,
    finalConcentration = 20 #20:1 dilution
)

protocol.addSP(
    name = '10 uM A1',
    components = {
        "A1 (no q)": 10,
    },
    finalVolume = 40,
    finalConcentration = 10
)

protocol.addSP(
    name = '10 uM A4',
    components = {
        "A4 (no Q)": 10,
    },
    volumeDependency= 1.1,
    finalConcentration = 10
)

# Fixed naming to match what's used in conditions
protocol.addSP(
    name = '20x 0.0375 A1, 0.1125 A4',
    components = {
        "10 uM A1": 0.75,
        "10 uM A4": 2.25,
    },
    volumeDependency= 1.1,
    finalConcentration = 20
)

protocol.addSP(
    name = '20x 0.1125 A1, 0.0375 A4',
    components = {
        "10 uM A1": 2.25,
        "10 uM A4": 0.75,
    },
    volumeDependency = 1.05, #dont need final volume
    finalConcentration = 20 #based on 20 x dilution in the end, change final volumes to 25 ul
)

# IMPORTANT: Define Pre-bulk FIRST before any pre-bulks that use it
protocol.addPreBulkSP(
    name = 'Aliquot Bulk',
    components = {
        "20 uM S1 F-Q Pair": 1.5,
        "20 uM S10 F-Q Pair": 1.5,
        "1 uM G1S10 OFF 2x Neut": .01,
        #"1 uM G4S1 OFF 2x Neut": .01,
        "10x Txn Buffer": 1,
        "25 mM NTP": 6,
        "1 M MgCl2": 0.024,
        "0.1 mg/mL BSA": 0.001,
        "0.1 U/uL YIPP": 0.00045,
    },
    volumeDependency = 1.05
)

# IMPORTANT: Manually add Pre-bulk to the stock repository so it can be used by other pre-bulks
# This is a workaround for the limitation in the CompositeProtocol class
protocol.stockRepo["Pre-bulk"] = 1.0  # Assuming Pre-bulk is at 1x concentration

wells = ["N19", "N20", "N21", "N22"]  # Rows 19-22

protocol.addSP(
    name = "G1 ON, G4 OFF",
    components = {
        "Aliquot Bulk": None,
        "1 uM G1R4 1.5x ON 2x Neut": 0.025,
        "1 uM G4R1 OFF 2x Neut": 0.025,
        "20 U/uL T7 RNAP": 1,
        "20x 0.0375 A1, 0.1125 A4": 1
    },
    finalVolume = 25,
    well = wells[0]
)

protocol.addSP(
    name = "G1 ON",
    components = {
        "Aliquot Bulk": None,
        "1 uM G1R4 1.5x ON 2x Neut": 0.025,
        "20 U/uL T7 RNAP": 1,
        "20x 0.0375 A1, 0.1125 A4": 1
    },
    finalVolume = 25,
    well = wells[0]
)

protocol.addSP(
    name = "G1 OFF, G4 ON",
    components = {
        "Aliquot Bulk": None,
        "1 uM G1R4 OFF 2x Neut": 0.025,
        "1 uM G4R1 1.5x ON 2x Neut": 0.025,
        "20 U/uL T7 RNAP": 1,
        "20x 0.1125 A1, 0.0375 A4": 1
    },
    finalVolume = 25,
    well = wells[0]
)

protocol.addSP(
    name = "G4 ON",
    components = {
        "Aliquot Bulk": None,
        "1 uM G4R1 1.5x ON 2x Neut": 0.025,
        "20 U/uL T7 RNAP": 1,
        "20x 0.1125 A1, 0.0375 A4": 1
    },
    finalVolume = 25,
    well = wells[0]
)

time_break = [10, 30]

# You can enable the proofread function in compileCompositeProtocol() if needed.
result = protocol.compileCompositeProtocol(path_config, proofread=True)
file = PB.FileGeneration()
file.composite_file(result, repo, path_config, author="Prisha Agrawal", time="2026-03-04", title="G1G4Bistable switch", time_break=time_break)