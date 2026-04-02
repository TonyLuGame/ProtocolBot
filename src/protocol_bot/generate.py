from datetime import date
from itertools import groupby
from dataclasses import dataclass
from typing import Dict, Tuple
from pathlib import Path

@dataclass
class UserConfig:
    # absolute file paths: valueColumn
    stock_repo: Dict[any, int]

    output_parts: Tuple[str, ...]
    central_parts: Tuple[str, ...]

class IndepVariConc():
    def __init__(self, conc_list=None, cond_list=None, isBulk=False, bulkPriority=0, name=None, varname=None, component=None, conc=None):
        self.concs = conc_list
        self.isBulk = isBulk
        self.bulkPriority = bulkPriority
        self.name = name
        self.varname = varname
        self.conds = cond_list
        self.finalConc = conc
        self.component = component

class ComponentVar():
    def __init__(self, name, comp_list, volumeDependency, isPrebulk, isBulk, finalConcentration, finalVolume, ifupdate):
        self.comps = comp_list
        self.name = name
        self.isPrebulk = isPrebulk
        self.isBulk = isBulk
        self.volumeDependency = volumeDependency
        self.finalVolume = finalVolume
        self.finalConcentration = finalConcentration
        self.ifupdate = ifupdate

class InputStorage():
    def __init__(self):
        self.indevar = []
        self.compvar = []

    def addCompVariable(self, name, comp_list, finalConcentration, volumeDependency=None, finalVolume=None, isPrebulk=False, isBulk=False, ifupdate=False):
        self.compvar.append(ComponentVar(name=name, comp_list=comp_list, volumeDependency=volumeDependency, isPrebulk=isPrebulk, isBulk=isBulk, finalConcentration=finalConcentration, finalVolume=finalVolume, ifupdate=ifupdate))
    
    def addBulkVariable(self, conc_list, bulkPriority, name, varname, isBulk=True, component=None, conc=None):
        ele = conc_list[0]
        if isinstance(ele, str):
            if conc is None:
                raise ValueError("Please provide the final concentration for bulk solution from preivous layer with string condition list.")
            self.indevar.append(IndepVariConc(cond_list=conc_list, isBulk=isBulk, bulkPriority=bulkPriority, name=name, varname=varname, component=component, conc=conc))
        else:
            self.indevar.append(IndepVariConc(conc_list=conc_list, isBulk=isBulk, bulkPriority=bulkPriority, name=name, varname=varname, component=component))

class CodeWriter():
    def __init__(self, input_storage, user_config):
        self.input_storage = input_storage
        self.user_config = user_config
        self.layers = []
        self.layers_names = None
        self.finalWellVolume = None
    '''
    def generate_init_code(self, code):
        uc = self.user_config
        code.append("# --------- AUTO-GENERATED RUNNER CODE ------------ #")
        code.append("import sys")
        code.append("import os")
        code.append("import openpyxl")
        #code.append("sys.path.append(os.path.dirname(os.path.dirname(__file__)))")
        #code.append("import Protocol_Generator as PG")
        #code.append("import Protocol_Building as PB\n")
        code.append("from protocol_bot import Protocol_Generator as PG")
        code.append("from protocol_bot import Protocol_Building as PB\n")

        code.append("# Define the project root on main folder")
        #code.append("project_root = os.path.dirname(os.path.dirname(__file__))")
        #code.append("stock_repo_folder = os.path.join(project_root, \"Stock_Repository\")\n")
        code.append("project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))")
        code.append("stock_repo_folder = os.path.join(project_root, \"data\", \"Stock_Repository\")\n")

        code.append("# Define a class to hold all relevant path configurations")
        code.append("class PathConfig:")
        code.append("    def __init__(self, stock_repo, output_file, central_registry):")
        code.append("        self.stock_repo = stock_repo")
        code.append("        self.output_file = output_file")
        code.append("        self.central_registry = central_registry\n")

        code.append("# ---- User Input ---- #")
        code.append("# Define the full path for stock repositories, output file, and central registry")
        code.append("path_config = PathConfig(")
        code.append(f"    stock_repo={uc.stock_repo!r},")
        code.append(f"    output_file=os.path.join(project_root, *{uc.output_parts!r}),")
        code.append(f"    central_registry=os.path.join(project_root, *{uc.central_parts!r}),")
        code.append(")\n")

        code.append("# Load repository in the structure of {repository_location: concentration_value_column_in_excel}")
        code.append("repository_list = path_config.stock_repo")
        code.append("sRepo = PG.KeyValueRepository(\"Stock Solutions\")")
        code.append("# ---- End of User Input ---- #\n")

        code.append("# Load repositories")
        code.append("for repoloc in repository_list:")
        code.append("    loc = repoloc")
        code.append("    wb = openpyxl.load_workbook(loc, read_only=True)")
        code.append("    all_sheets = wb.sheetnames")
        code.append("    for sheet in all_sheets:")
        code.append("        sRepo.addToKeyValueRepo(")
        code.append("            sRepo.getExcelRepoEntries(")
        code.append("                loc,")
        code.append("                sheetName=sheet,")
        code.append("                header=1,")
        code.append("                valueColumn=repository_list[repoloc]")
        code.append("            )")
        code.append("        )\n")

        code.append("# Define the composite protocol here")
        code.append("repo = sRepo.Repository.copy()")
        code.append("protocol = PG.CompositeProtocol(stockRepo=sRepo.Repository)\n")
        return code
    '''
    def generate_init_code(self, code):
        if isinstance(code, str):
            code = []
            
        uc = self.user_config
        code.append("# --------- AUTO-GENERATED RUNNER CODE ------------ #")
        code.append("from pathlib import Path")
        code.append("from protocol_bot import volume as PG")
        code.append("from protocol_bot import export as PB")
        code.append("from protocol_bot import repository as RP\n")

        code.append("# Define paths")
        code.append("RUNNER_SCRIPT = Path(__file__).resolve()")
        code.append("PROJECT_ROOT = RUNNER_SCRIPT.parent.parent")
        code.append("DATA_DIR = PROJECT_ROOT / 'data' / 'Stock_Repository'\n")

        code.append("# Define a class to hold all relevant path configurations")
        code.append("class PathConfig:")
        code.append("    def __init__(self, stock_repo, output_file, central_registry):")
        code.append("        self.stock_repo = stock_repo")
        code.append("        self.output_file = output_file")
        code.append("        self.central_registry = central_registry\n")

        code.append("# ---- User Input ---- #")
        code.append("path_config = PathConfig(")
        
        # Path reconstruction
        code.append("    stock_repo={")
        for path_obj, val in uc.stock_repo.items():
            filename = Path(path_obj).name 
            code.append(f"        DATA_DIR / '{filename}': {val},")
        code.append("    },")
        
        out_path = "PROJECT_ROOT"
        for part in uc.output_parts:
            out_path += f" / '{part}'"
        code.append(f"    output_file={out_path},")

        cent_path = "PROJECT_ROOT"
        for part in uc.central_parts:
            cent_path += f" / '{part}'"
        code.append(f"    central_registry={cent_path},")
        code.append(")\n")

        code.append("# Load repository structure")
        code.append("repository_list = path_config.stock_repo")
        code.append("sRepo = PG.KeyValueRepository(\"Stock Solutions\")")
        code.append("# ---- End of User Input ---- #\n")

        code.append("# Load repositories")
        code.append("print('⏳ Loading Stock Repositories (this might take a moment)...')")
        code.append("for repoloc, val_col in repository_list.items():")
        code.append("    # Load ALL sheets at once into a dictionary of DataFrames")
        code.append("    try:")
        code.append("        all_sheets_dict = pd.read_excel(repoloc, sheet_name=None, header=1)")
        code.append("    except FileNotFoundError:")
        code.append("        print(f'[ERROR] Could not find file: {repoloc}')")
        code.append("        continue")
        code.append("    ")
        code.append("    for sheet_name, df in all_sheets_dict.items():")
        code.append("        # Process the dataframe directly without re-reading the file")
        code.append("        sRepo.addToKeyValueRepo(")
        code.append("            sRepo.getDataFrameKeyValues(")
        code.append("                df,")
        code.append("                keyColumn=0,")
        code.append("                valueColumn=val_col")
        code.append("            )")
        code.append("        )\n")
        code.append("print('✅ Repositories Loaded.')")

        code.append("# Define the composite protocol here")
        code.append("repo = sRepo.Repository.copy()")
        code.append("protocol = PG.CompositeProtocol(stockRepo=sRepo.Repository)\n")
        return code

    def create_component_protocol(self, code):
        for comp in self.input_storage.compvar:
            try:
                comps = comp.comps
                name = comp.name
                isPrebulk = comp.isPrebulk
                volumeDep = comp.volumeDependency
                finalconc = comp.finalConcentration
            except AttributeError as e:
                raise ValueError(f"Cannot find the attributes for {comp.name}, please check if it is initialized properly.")
            code.append("protocol.addSP(")
            code.append(f"    name = {name!r},")
            code.append("    components = {")
            for k, v in comps.items():
                code.append(f'        "{k}": {repr(v)},')
            code.append("    },")
            if isPrebulk:
                code.append(f"    isPrebulk = {isPrebulk},")
            if comp.finalVolume is not None:
                code.append(f"    finalVolume = {comp.finalVolume},")
            else:
                code.append(f"    volumeDependency = {volumeDep},")
            code.append(f"    finalConcentration = {finalconc}")
            code.append(")\n")
        return code

    def form_layer_struc(self):
        indevar = self.input_storage.indevar
        objs_sorted = sorted(indevar, key=lambda x: x.bulkPriority)
        self.layers = [list(g) for _, g in groupby(objs_sorted, key=lambda o: o.bulkPriority)][::-1]

    def create_bulk_protocol(self, code, time_break=None):
        self.form_layer_struc()
        print(self.layers)
        if not self.layers:
            return code
        
        # Generate the code for concentration list
        for inde in self.layers:
            for var in inde:
                if var.conds is not None:
                    code.append(f"{var.varname} = {var.conds}")
                else:
                    code.append(f"{var.varname} = {var.concs}")
        code.append("wells = PG.getWellNames('B2', 'G6')")
        if time_break is not None:
            code.append(f"time_break = {time_break}")

        # Start nested loop generation
        self.generate_nested_loops(code, 0, self.layers_names[0])
        return code

    def generate_nested_loops(self, code, layer_idx, base_bulk_name):
        if layer_idx >= len(self.layers):
            return

        layer = self.layers[layer_idx]
        loop_vars = ['i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']

        for v_idx, inde in enumerate(layer):
            var_sym = loop_vars[layer_idx + v_idx]
            indent = "    " * (layer_idx + v_idx)
            code.append(f"{indent}for {var_sym}, {var_sym}_val in enumerate({inde.varname}):")

        inner_indent = "    " * (layer_idx + len(layer))

        combo_name_parts = [
            f"{{{loop_vars[layer_idx + v_idx]}_val}} {repr(inde.name)}"
            for v_idx, inde in enumerate(layer)
        ]
        combo_name_fmt = " - ".join(combo_name_parts)

        code.append(f"{inner_indent}# Combination of current layer: {combo_name_fmt}")

        component_list = [ind.component for ind in layer if ind.component is not None]
        component = component_list[0]
        indicator = []
        finalConc = 0
        for ind in layer:
            if ind.concs is not None:
                indicator.append(True)
            else:
                indicator.append(False)
                finalConc = ind.finalConc

        if layer_idx < len(self.layers_names) - 2:
            new_bulk_name_fmt = f"{self.layers_names[layer_idx+1]}, " + combo_name_fmt
            code.append(f"{inner_indent}protocol.addSP(")
            code.append(f"{inner_indent}    name = f\"{new_bulk_name_fmt}\",")
            code.append(f"{inner_indent}    components = {{")
            code.append(f"{inner_indent}        f\"{base_bulk_name}\": None,")
            for v_idx, inde in enumerate(layer):
                var_sym = loop_vars[layer_idx + v_idx]
                if False not in indicator:
                    code.append(f"{inner_indent}        \"{inde.name}\": {var_sym}_val,")
                else:
                    code.append(f"{inner_indent}        f\"{{{var_sym}_val}}\": {finalConc},")    
            for i, v in component.items():
                code.append(f"{inner_indent}        \"{i}\": {v},")
            code.append(f"{inner_indent}    }},")
            code.append(f"{inner_indent}    isBulk = True,")
            code.append(f"{inner_indent}    volumeDependency = 1.08,")
            code.append(f"{inner_indent}    finalConcentration = 100")
            code.append(f"{inner_indent})")

            self.generate_nested_loops(code, layer_idx + 1, new_bulk_name_fmt)
        else:
            name_fmt = combo_name_fmt
            code.append(f"{inner_indent}protocol.addSP(")
            code.append(f"{inner_indent}    name = f\"{name_fmt}\",")
            code.append(f"{inner_indent}    components = {{")
            
            code.append(f"{inner_indent}        f\"{base_bulk_name}\": None,")
            for v_idx, inde in enumerate(layer):
                var_sym = loop_vars[layer_idx + v_idx]
                if isinstance(inde.name, list):
                    for idx, i in enumerate(inde.name):
                        code.append(f"{inner_indent}        \"{i}\": {var_sym}_val[{idx}],")
                else:
                    if False not in indicator:
                        code.append(f"{inner_indent}        \"{inde.name}\": {var_sym}_val,")
                    else:
                        code.append(f"{inner_indent}        f\"{inde.name}\": {finalConc},")

            for i, v in component.items():
                code.append(f"{inner_indent}        \"{i}\": {v},")

            code.append(f"{inner_indent}    }},")
            code.append(f"{inner_indent}    finalVolume = {self.finalWellVolume},")
            code.append(f"{inner_indent}    well = \"A1\",")
            code.append(f"{inner_indent}    textFeature = f\"{name_fmt}\"")
            code.append(f"{inner_indent})")

            self.generate_nested_loops(code, layer_idx + 1, base_bulk_name)


    def generate_protocol_code(self, code, name, description, layer_names=["Pre-bulk", "Aliquot Bulk", "Well"], finalWellVolume=40, time_break=None):
        # Generate the full version of code
        self.layers_names = layer_names
        self.finalWellVolume = finalWellVolume
        self.generate_init_code(code)
        self.create_component_protocol(code)
        self.create_bulk_protocol(code, time_break=time_break)

        # Get the code for running protocol
        code.append("# You can enable the proofread function in compileCompositeProtocol() if needed.")
        code.append(f'comp_result, well_name, protocol_summary = protocol.compileCompositeProtocol(repository_list, path_config, repo, proofread=True)')
        code.append(f'file = PB.FileGeneration()')
        code.append(f'file.composite_file("{name}", "{date.today()}", "{description}", comp_result, well_name, protocol_summary, repo, path_config, time_break=time_break)')
        return "\n".join(code)
