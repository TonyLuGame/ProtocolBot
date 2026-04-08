from pathlib import Path
from protocol_bot import CompositeProtocol
from protocol_bot import FileGeneration
from protocol_bot import KeyValueRepository, PathConfig, stock_repo_load

# 1. SETUP
RUNNER_SCRIPT = Path(__file__).resolve()
PROJECT_ROOT = RUNNER_SCRIPT.parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'Stock_Repository'

path_config = PathConfig(
    stock_repo={
        DATA_DIR / 'Lab_Inventory.xlsx': {'val_col': 2, 'unit_col': 2},
    },
    output_file=PROJECT_ROOT / 'data' / 'Protocol_Output' / 'PCR_Protocol_Output.xlsx',
    central_registry=DATA_DIR / 'Lab_Record_History.xlsx',
)

sRepo = KeyValueRepository("PCR_Stocks")
stock_repo_load(path_config.stock_repo, sRepo, key_idx=0)
repo = sRepo.Repository.copy()
protocol = CompositeProtocol(stockRepo=sRepo.Repository)

# 2. DEFINE THE MASTER MIX
# Note: Use the EXACT names from your Lab_Inventory.xlsx to avoid [INFO] replacements
protocol.addPreBulkSP(
    name = 'PCR Master Mix',
    components = {
        "10x PCR Buffer": 1.0,
        "dNTP Mix (10mM)": 0.2,
        "Forward Primer": 0.4, # Verify these names in your Excel!
        "Reverse Primer": 0.4,
        "Taq DNA Polymerase": 0.05,
    },
    volumeDependency = 1.1 
)

protocol.stockRepo["PCR Master Mix"] = 1.0

# 3. ALIQUOT TO SAMPLES
samples = ["Template_DNA_1", "Template_DNA_2"]

for i, sample_name in enumerate(samples):
    protocol.addSP(
        name = f"Reaction_{sample_name}",
        components = {
            "PCR Master Mix": None,   # Changed to 0.92 (23uL) to leave 1uL for water
            sample_name: 0.2          # 1uL DNA
        },
        finalVolume = 25,             # 23 + 1 + 1 (water) = 25
        well = f"A{i+1}",
        textFeature = "PCR Cycle: 95C -> 60C -> 72C"
    )

# 4. EXPORT
result = protocol.compileCompositeProtocol(path_config, proofread=True)
file = FileGeneration()
file.composite_file(result, repo, path_config, author="Lab User", title="Standard PCR Setup")

print(f"Protocol generated successfully at: {path_config.output_file}")