import numpy as np
import pandas as pd

# Returns "Name (str): Value (number)" as a string
def getStrNameValue(name, value, sigFig = 4):
    return
    #return f"{name}: " + (value if value == "BULK" else str(GU.roundToSigFig(value, sigFig)))

# Returns a list of well strings in the designated rectangle (i.e. A1 - C2 would return [A1, B1, C1, A2, B2, C2])
def getWellNames(topLeftName="A1", bottomRightName="P24"):
    letr1 = ord(topLeftName[0])
    letr2 = ord(bottomRightName[0])

    num1 = int(topLeftName[1:])
    num2 = int(bottomRightName[1:])

    return [chr(i)+str(j) for i in np.arange(letr1, letr2+1) for j in np.arange(num1, num2+1)]

def normalize_units(value, unit):
    factors = {
        'M': 1e6,
        'mM': 1e3,
        'uM': 1.0,
        'nM': 1e-3,
        'pM': 1e-6
    }

    if pd.isna(unit):
        return value
    
    unit_key = str(unit).strip()
    return value * factors.get(unit_key, 1)

def stock_repo_load(repository_list, sRepo, key_idx=0):
    print('⏳ Loading Stock Repositories (this might take a moment)...')
    for repoloc, settings in repository_list.items():
        # Load all sheets at once into a dictionary of DataFrames
        try:
            all_sheets_dict = pd.read_excel(repoloc, sheet_name=None, header=1)
        except FileNotFoundError:
            print(f'[ERROR] Could not find file: {repoloc}')
            continue
        
        val_col = settings.get('val_col')
        unit_col = settings.get('unit_col')
        key_idx = key_idx

        for sheet_name, df in all_sheets_dict.items():
            df = df.dropna(subset=[df.columns[0]])

            is_string = df.iloc[:, key_idx].apply(lambda x: isinstance(x, str))
            if not is_string.all():
                invalid_values = df.iloc[~is_string.values, key_idx].unique()
                raise TypeError(
                    f"Column at index {key_idx} in sheet '{sheet_name}' contains non-string values: {invalid_values}"
                )

            if unit_col is not None:
                df.iloc[:, val_col] = [
                    normalize_units(v, u) for v, u in zip(df.iloc[:, val_col], df.iloc[:, unit_col])
                ]
            
            # Process the dataframe directly without re-reading the file
            sRepo.addToKeyValueRepo(
                sRepo.getDataFrameKeyValues(
                    df,
                    keyColumn=key_idx,
                    valueColumn=val_col
                )
            )

    print('✅ Repositories Loaded.')

# Define a class to hold all relevant path configurations
class PathConfig:
    def __init__(self, stock_repo, output_file, central_registry):
        self.stock_repo = stock_repo
        self.output_file = output_file
        self.central_registry = central_registry

class SPInstance:
    def __init__(self, SProtocol, finalVolume = None, volumeDependency = None, isBulk = None, well = None, isPrebulk = None, textFeature = None, ifupdate = False):
        self.SProtocol = SProtocol
        self.finalVolume = finalVolume
        self.volumeDependency = volumeDependency
        self.isBulk = isBulk
        self.well = well
        self.isPrebulk = isPrebulk
        self.textFeature = textFeature
        self.ifupdate = ifupdate

# Contains information for every sub-solution created from the list of provided components
class SolutionProtocol:
    def __init__(self, name, components, finalConcentration, isscale = True):
        if sum(1 for x in components.values() if x == "BULK") > 1:
            raise ValueError("Only one BULK may be present in any solution protocol.")

        self.Name = name
        self.Components = components
        self.FinalConcentration = finalConcentration
        self.isscale = isscale

    # Returns a dictionary of volume values required for the current SP based on the provided stock concentrations and scaling factor.
    def getComponentVolumes(self, finalVolume, componentRepo, scalingFactor = 1.0):
        rawVolumeFromRepo = sum([0 if self.Components[x] == "BULK" else self.Components[x] / componentRepo[x] for x in self.Components])
        maxVolume = 1.000001*finalVolume # Account for float rounding
        if rawVolumeFromRepo > maxVolume:
            raise ValueError(str(self) + "\nThe solution cannot be created with the given component stocks. Use a larger dilution or more concentrated stocks.")
        elif rawVolumeFromRepo * scalingFactor > maxVolume:
            raise ValueError(str(self) + "\nThe solution cannot be created with the given scaling factor. Use a larger dilution or more concentrated stocks.")

        volumes = {}
        for x in self.Components:
            volumes[x] = self.Components[x] * finalVolume * scalingFactor / componentRepo[x]
        
        return volumes

    # Returns a SolutionProtocol that dilutes the components or the pre-mixed solution described in the current SP.
    def getDilutionProtocol(self, dilName, dilutionFactor = 1.0, useOriginals = False, isscale = True):
        if any(x is None for x in self.Components.values()):
            raise ValueError("Solution protocols with a 'BULK' should not be diluted due to their downstream calculation dependence.")
        
        dilComponents = {}
        finalDilConcentration = self.FinalConcentration / dilutionFactor

        if useOriginals:
            for x in self.Components:
                try:
                    dilComponents[x] = self.Components[x] / dilutionFactor
                except ZeroDivisionError as e:
                    raise ValueError(f"Dilution factor cannot be zero")
                except KeyError as e:
                    raise ValueError(f"Component '{x}' not found in the component repository, please double check if input is correct.") 
        else:
            dilComponents[self.Name] = finalDilConcentration

        return SolutionProtocol(
            dilName,
            dilComponents,
            finalDilConcentration,
            isscale
        )
    
    def setComponentConcentration(self, componentName, componentConc):
        if not componentName in componentConc:
            raise ValueError("Only existing components in a solution protocol may be modified.\n '{componentName}' is not a part of '{self.Name}'")
        self.Components[componentName] = componentConc

    # Return the name and components of the SP.
    def __str__(self):
        totalStr = "Solution Protocol of '{self.Name}'"
        for x in self.Components:
            totalStr += "\n   " + getStrNameValue(x, self.Components[x])
        return totalStr
    
# Stores and manages a dictionary containing designated key/value pairs
class KeyValueRepository:
    def __init__(self, name):
        self.Name = name
        self.Repository = {}

    # Obtain a key/value pair dictionary from an excel repository
    def getExcelRepoEntries(self, excelFile, sheetName = 0, header = 0, keyColumn = 0, valueColumn = 1):
        dataFrame = pd.read_excel(excelFile, sheet_name = sheetName, header = header)
        return self.getDataFrameKeyValues(dataFrame, keyColumn, valueColumn)

    # Obtain a key/value pair dictionary from a CSV repository
    def getCSVRepoEntries(self, csvFile, header = 0, sep = None, keyColumn = 0, valueColumn = 1):
        dataFrame = pd.read_csv(csvFile, header = header, sep = sep)
        return self.getDataFrameKeyValues(dataFrame, keyColumn, valueColumn)

    # Obtain a key/value pair dictionary from a data frame
    def getDataFrameKeyValues(self, dataFrame, keyColumn = 0, valueColumn = 1):
        keyValueColumns = dataFrame.iloc[:, [keyColumn, valueColumn]]
        keyValueDict = {}
        for _, dataEntry in keyValueColumns.iterrows():
            keyValueDict[dataEntry.iloc[0]] = dataEntry.iloc[1]
        return keyValueDict

    # Add a key/value pair dictionary to the current repository
    def addToKeyValueRepo(self, nameValueDict):
        for x in nameValueDict:
            if x in self.Repository:
                raise ValueError("This key/value repository cannot accept duplicate entries for '{x}'.")
        self.Repository |= nameValueDict

    # Return the name and current repository elements of the key/value repository
    def __str__(self):
        totalStr = "Key/Value Repository '" + self.Name + "'"
        for x in self.Repository:
            totalStr += "\n   " + getStrNameValue(x, self.Repository[x])
        return totalStr