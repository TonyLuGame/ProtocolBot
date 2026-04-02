from datetime import date
from pathlib import Path
from protocol_bot import generate as va

CURRENT_FILE = Path(__file__).resolve()
SCRIPT_DIR = CURRENT_FILE.parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "Stock_Repository"

USER_CONFIG = va.UserConfig(
    stock_repo={
        "GeneletRepository1.xlsx": 2,
        "ComponentRepository.xlsx": 1,
    },
    output_parts=("Protocol_Test_File", "protocol_output.xlsx"),
    central_parts=("Central_Protocol_Record.xlsx",),
)

input = va.InputStorage()

# --- 1. Define Static Components ---
input.addCompVariable("20 uM S1 F-Q Pair", {"S1-F": 20, "S1-Q": 20}, 20, finalVolume=350)

# --- 2. Define the "Base" Pre-bulk (Layer 0) ---
aliquot_bulk_comp = {
    "20 uM S1 F-Q Pair": 1.5,
    "10x Txn Buffer": 1,
    "25 mM NTP": 6
}
input.addCompVariable("Aliquot Bulk", aliquot_bulk_comp, 1, volumeDependency=1.05, isPrebulk=True)

# --- 3. Define Independent Variables (Bulk Layers) ---
# This adds a layer of bulks (BulkPriority=1)
# These will use 'addBulkSP' because they are between Pre-bulk and Wells
bulk_concs = [0, 5, 10, 20]
input.addBulkVariable(
    conc_list=bulk_concs, 
    bulkPriority=1, 
    name="T7 RNAP", 
    varname="rnap_concs", 
    component={"200 U/uL RNAP": 1}
)

# This defines the final Well layer (BulkPriority=0)
other_conditions = ["Light", "Dark"]
input.addBulkVariable(
    conc_list=other_conditions, 
    bulkPriority=0, 
    name="Condition", 
    varname="light_conds", 
    component={}, 
    conc=1 # finalConc required for string lists
)

layer_names = ["Aliquot Bulk", "Intermediate Bulk", "Well"]
time_break = [10, 30]

code_perform = va.CodeWriter(input, USER_CONFIG)
code = []
return_code = code_perform.generate_protocol_code(
    code, 
    "Prisha Agrawal", 
    "G1G4 Bistable Switch", 
    layer_names=layer_names, 
    finalWellVolume=25, 
    time_break=time_break
)

# --- Write to file ---
output_folder = PROJECT_ROOT / "Code_Generator_Test_Output"
output_folder.mkdir(parents=True, exist_ok=True)
filepath = output_folder / f"runner_{date.today()}.py"
with open(filepath, "w") as f:
    f.write(return_code)

print(f"Runner generated: {filepath}")