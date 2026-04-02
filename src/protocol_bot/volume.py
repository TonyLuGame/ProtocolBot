import copy
import math
from InquirerPy import inquirer
#import GeneralUse as GU
from .search import search_excel
from protocol_bot import registry
from protocol_bot import repository
from protocol_bot import semantic
from protocol_bot import structure
from protocol_bot import sort

# Define a class to hold the results
class ResultConfig:
    def __init__(self, comp_result, wells, protocol_summary, stock):
        self.comp = comp_result
        self.well = wells
        self.protocol = protocol_summary
        self.stock = stock

class CompositeProtocol:
    def __init__(self, name = "Protocol", stockRepo=None):
        self.Name = name
        self.minimumVolume = None
        self.stockRepo = stockRepo
        self.SPIs = []
        self.volumeDoc = []
        self.scaleFactor = []
    
    def addSP(self, name, components, finalConcentration=None, finalVolume = None, volumeDependency = None, well = None, textFeature=None, ifnew = False):
        newSP = repository.SolutionProtocol(
            name,
            components,
            finalConcentration,
            True
        )
        self.SPIs.append(
            repository.SPInstance(
                newSP,
                finalVolume = finalVolume,
                volumeDependency = volumeDependency,
                isBulk = None,
                isPrebulk = None,
                well = well,
                textFeature = textFeature,
                ifupdate = ifnew
            )
        )
        if finalConcentration is not None:
            self.stockRepo[name] = finalConcentration

    def addBulkSP(self, name, components, finalVolume = None, volumeDependency = None, textFeature=None, ifnew = False):
        newSP = repository.SolutionProtocol(
            name,
            components,
            None,
            True
        )
        self.SPIs.append(
            repository.SPInstance(
                newSP,
                finalVolume = finalVolume,
                volumeDependency = volumeDependency,
                isBulk = True,
                isPrebulk = None,
                well = None,
                textFeature = textFeature,
                ifupdate = ifnew
            )
        )
        #if finalConcentration is not None:
            #print("[WARNING]: Final concentration normally should be calculated through the algorithm")

    def addPreBulkSP(self, name, components, finalVolume = None, volumeDependency = None, textFeature=None, ifnew = False):
        newSP = repository.SolutionProtocol(
            name,
            components,
            None,
            True
        )
        self.SPIs.append(
            repository.SPInstance(
                newSP,
                finalVolume = finalVolume,
                volumeDependency = volumeDependency,
                isBulk = None,
                isPrebulk = True,
                well = None,
                textFeature = textFeature,
                ifupdate = ifnew
            )
        )
        #if finalConcentration is not None:
            #print("[WARNING]: Final concentration normally should be calculated through the algorithm")

    def compileCompositeProtocol(self, path, proofread = False):
        repo = path.stock_repo
        stock = copy.deepcopy(self.stockRepo)
        self.similarityProofread(proofread, repo)

        order = sort.OrderSorting()
        orderSPIs, name, bulk_order, nonbulk_order = order.obtainOrder(self.SPIs)
        self.volumeDoc = [{} for _ in range(len(self.SPIs))]
        print(orderSPIs)
        print(bulk_order)
        print(nonbulk_order)

        self.calculateBulkVolume(bulk_order)
        #print(self.volumeDoc)
        #well_result = self.generateWellList()
        self.volumeCalculation(nonbulk_order)
        
        org = structure.StructureProtocol()
        well_result, well_name = org.generateWellList(self.SPIs, self.stockRepo, self.volumeDoc)
        comp_mixture = org.generateStructure(self.SPIs, self.stockRepo, self.volumeDoc)  
        comp_result = org.combineResult(well_result, comp_mixture)
        
        track = registry.TrackRegistry()
        protocol_summary = track.updateCentralRegistry(self.SPIs, path.central_registry, stock)
        #print(self.volumeDoc)
        result = ResultConfig(comp_result, well_name, protocol_summary, stock)
        return result

    def compVolume(self, name):
        vol = 0
        scale_factor = 1.0
        for i, spi in enumerate(self.SPIs):
            if name in spi.SProtocol.Components.keys():
                #print(name)
                #print(self.volumeDoc[i][name])
                vol += self.volumeDoc[i][name]
                if self.volumeDoc[i][name] != 0:
                    try:
                        scale_factor = spi.finalVolume / self.volumeDoc[i][name]
                    except AttributeError as e:
                        raise ValueError(f"[ERROR] Cannot find the final volume, please check if the final volume is computed in previous step.")
        return vol, scale_factor

    def __str__(self):
        totalStr = "Protocol '" + self.Name + "'\nContains the following solution protocols:"
        for x in self.SPIs:
            totalStr += f"\n   {x.SProtocol.Name}"
        return totalStr

    def calculateBulkVolume(self, orderSPIs):
        for i, name_list in enumerate(orderSPIs):
            if i != 0:
                self.findFinalVolumes(name_list)
                #print(name_list)
            self.findMinimumVolume(name_list, i)
            #if set(prebulk_name).issubset(name_list):
                #break
    
    def findMinimumVolume(self, name_list, indicator):
        # Multiply the scale_factor together
        if len(self.scaleFactor) == 0:
            scale = 1
        else:
            scale = math.prod([x for i, x in enumerate(self.scaleFactor) if i < indicator])
        
        minVolume = 1000
        final_volume = 0
        for i, spi in enumerate(self.SPIs):
            if spi.SProtocol.Name in name_list:
                components = spi.SProtocol.Components
                total_volume = spi.finalVolume
                final_volume = spi.finalVolume
                isscale = spi.SProtocol.isscale

                for reagent in components:
                    if components[reagent] != None:
                        if isscale == False:
                            scale = 1
                        try:
                            print(f"{reagent}: {self.stockRepo[reagent]}")
                            print(f"component conc: {components[reagent]}, final volume: {spi.finalVolume}, scale: {scale}")
                            volume = components[reagent] * spi.finalVolume / self.stockRepo[reagent] * scale
                        except KeyError as e:
                            raise ValueError(f"[ERROR] {reagent} not found in the stock repository, please double check the input excel file for stock solution.")  
                        except AttributeError as e:
                            raise ValueError(f"[ERROR] Cannot find the final volume for {spi.SProtocol.Name}, please check if the final volume is computed in previous step.")
                        total_volume -= volume
                        try:
                            self.volumeDoc[i][reagent] = volume
                        except KeyError as e:
                            raise ValueError(f"[ERROR] Cannot find the volume document for {reagent}, please check if the volume document is initialized properly.")
                if total_volume < minVolume:
                    minVolume = total_volume
        self.minimumVolume = minVolume
        print(f"final volume: {final_volume}, min volume: {minVolume}")
        scale_factor = final_volume / minVolume
        print(scale_factor)
        self.scaleFactor.append(scale_factor)

        for i, spi in enumerate(self.SPIs):
            miliQVolume = spi.finalVolume
            if spi.SProtocol.Name in name_list:
                components = spi.SProtocol.Components
                for reagent in components:
                    if reagent in self.volumeDoc[i]:
                        volume = self.volumeDoc[i][reagent]
                        miliQVolume -= volume
                    else:
                        self.SPIs[i].SProtocol.Components[reagent] = self.minimumVolume
                        self.volumeDoc[i][reagent] = minVolume
                        miliQVolume -= minVolume
                        self.stockRepo[reagent] = spi.finalVolume
                    print(f"{reagent}: {miliQVolume}")
                if miliQVolume < -0.5:
                    print(miliQVolume)
                    raise ValueError(f"[ERROR] The calculated volume for Milli Q H2O is negative for {spi.SProtocol.Name}, please check the stock concentrations and the final volume for this solution protocol.")
                self.SPIs[i].SProtocol.Components['Milli Q H2O'] = None
                self.volumeDoc[i]['Milli Q H2O'] = miliQVolume
    
    def findFinalVolumes(self, name_list):
        # Calculate the final volume of each SP based on the dependencies and the final volume of the SPs that depend on it
        for i, spi in enumerate(self.SPIs):
            if spi.finalVolume is not None:
                continue
            if spi.SProtocol.Name in name_list:
                # Find all dependencies of this SP
                countVolume, _ = self.compVolume(spi.SProtocol.Name)

                if spi.volumeDependency is not None:
                    countVolume *= spi.volumeDependency
            
                finalVolume = countVolume
                self.SPIs[i].finalVolume = finalVolume
                #print(f"Final volume of {spi.SProtocol.Name} is determined to be {finalVolume} uL based on the dependencies.")
    
    def volumeCalculation(self, orderSPIs):
        # Calculate the final volume of SP not related to a bulk
        passPreBulk = True
        for name_list in orderSPIs:
            if passPreBulk:
                for i, spi in enumerate(self.SPIs):
                    if spi.finalVolume is not None:
                        continue
                    if spi.SProtocol.Name in name_list:
                        countVolume, _ = self.compVolume(spi.SProtocol.Name)
                        if spi.volumeDependency is not None:
                            self.SPIs[i].finalVolume = countVolume * spi.volumeDependency
                        else:
                            self.SPIs[i].finalVolume = countVolume

                for i, spi in enumerate(self.SPIs):
                    if spi.SProtocol.Name in name_list:
                        components = spi.SProtocol.Components
                        try:
                            milliQVolume = spi.finalVolume
                        except AttributeError as e:
                            raise ValueError(f"[ERROR]Cannot find the final volume for {spi.SProtocol.Name}, please check if the final volume is computed in previous step.")
                        for reagent in components:
                            if reagent not in self.volumeDoc[i]:
                                try:
                                    print(f"{reagent}: {self.stockRepo[reagent]}")
                                    volume = components[reagent] * spi.finalVolume / self.stockRepo[reagent]
                                    milliQVolume -= volume
                                    self.volumeDoc[i][reagent] = volume
                                except KeyError as e:
                                    raise ValueError(f"[ERROR] Cannot find the stock volume for {reagent}, please check if the stock volume is initialized properly.")
                        if 'Milli Q H2O' not in self.SPIs[i].SProtocol.Components:
                            self.SPIs[i].SProtocol.Components['Milli Q H2O'] = None
                            self.volumeDoc[i]['Milli Q H2O'] = milliQVolume
            #else:
                #if set(name).issubset(name_list):
                    #passPreBulk = True
                #continue
    
    def similarityProofread(self, proofread, repository_list):
        simi_func = semantic.similarityFunction()
        simi_func.generateNameList(self.SPIs, self.stockRepo)
        recipe = copy.deepcopy(self.SPIs)
        for i, spi in enumerate(recipe):
            components =spi.SProtocol.Components
            for item in components:
                matches = simi_func.similarityCheck(item)
                try:
                    if proofread == True:
                        val = components[item]
                        self.SPIs[i].SProtocol.Components.pop(item)
                        self.SPIs[i].SProtocol.Components[matches] = val
                        if matches != item:
                            print(f"[INFO] Component '{item}' in solution protocol '{spi.SProtocol.Name}' is replaced with '{matches}' for better match in the stock repository.")
                    else:
                        if matches != item:
                            message = (
                                f"\n"
                                f"[ERROR] Component name mismatch detected!!!\n"
                                f"[INFO] Component '{item}' in solution protocol '{spi.SProtocol.Name}' doesn't match any stock or prepared protocol.\n"
                                f"[INFO] System recommendation for replacement:'{matches}'"
                                f"\n"
                            )
                            print(message)
                            raise ValueError(message)
                except ValueError as e:
                    print("[ACTION] Opening interactive search to figure out the mismatch...\n")
                    open_search = inquirer.confirm(
                        message="Would you like to open the interactive search tool?",
                        default=True,
                    ).execute()
                    if open_search:
                        print("\n[ACTION] Launching search tool...\n")
                        search_excel(repository_list)
                    else:
                        print("[ACTION] Skipping search tool. Continuing proofreading.\n")
                    return