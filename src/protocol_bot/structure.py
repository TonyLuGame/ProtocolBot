class StructureProtocol:
    def __init__(self):
        pass

    def generateStructure(self, repo_SPIs, repo_stock, repo_volumeDoc):
        # Formulate the structure for solutions other than well plate
        comp_list = []
        for i, SPI in enumerate(repo_SPIs):
            if SPI.well is None:
                if SPI.textFeature is not None:
                    comp_list.append([None, SPI.SProtocol.Name, SPI.textFeature, None, None, None, None])
                else:
                    comp_list.append([None, SPI.SProtocol.Name, None, None, None, None, None])
                components = SPI.SProtocol.Components
                #print(components)
                #print(SPI.SProtocol.Name)
                for k in components:
                    if k == "Milli Q H2O":
                        comp_list.append([None, k, None, None, repo_volumeDoc[i][k], None, None])
                        comp_list.append([None, None, None, None, 'Volume Total', None, None])
                        comp_list.append([None, None, None, None, SPI.finalVolume, None, None])
                        comp_list.append([None, None, None, None, None, None, None])
                        comp_list.append([None, None, None, None, None, None, None])
                        comp_list.append([None, None, None, None, None, None, None])
                    else:
                        init_conc = repo_stock[k]
                        final_conc = components[k]
                        vol = repo_volumeDoc[i][k]
                        comp_list.append([None, k, init_conc, final_conc, vol, None, None])
        return comp_list
    
    def generateWellList(self, SPIs, stockRepo, volumeDoc):
        # Create the plate for all the designed well
        well_list = []
        well_name = []
        for i, combo in enumerate(SPIs):
            ind = True
            if combo.well is not None:
                if combo.textFeature is not None:
                    headline_list = [combo.textFeature, None, None, None, None, f"Well {combo.well}"]
                else:
                    headline_list = [combo.SProtocol.Name, None, None, None, None, f"Well: {combo.well}"]
                well_name.append(headline_list[0])
                well_list.append(headline_list)
                for item in combo.SProtocol.Components:
                    if item != "Milli Q H2O":
                        init_conc = stockRepo[item]
                        final_conc = combo.SProtocol.Components[item]
                        volume = volumeDoc[i][item]
                        if ind:
                            well = [item, init_conc, final_conc, volume, None, None]
                            ind = False
                        else:
                            well = [item, init_conc, final_conc, volume, None, None]
                        well_list.append(well)
                    else:
                        # Add the component of water to the well
                        water_place = ["Milli Q H2O", None, None, volumeDoc[i][item], None, None]
                        well_list.append(water_place)
                well_list.append([None, None, None, "Volume Total", None, None])
                well_list.append([None, None, None, combo.finalVolume, None, None])
                well_list.append([None, None, None, None, None, None])
        return well_list, well_name

    def combineResult(self, well_info, stock_info): 
        # Combine the result generated for the well plate and for the recipe of solution
        standard_list = [None, None, None, None, None, None, None]
        blank_list = [None, None, None, None, None, None]
        combined_list = []

        # Compare the length of well_info and stock_info
        if len(well_info) > len(stock_info):
            lengthy_info = well_info
        else:
            lengthy_info = stock_info

        # Combine the well_info and stock_info into a new list for file generation
        for i, item in enumerate(lengthy_info):
            if i < len(well_info) and i < len(stock_info):
                new_list = stock_info[i] + well_info[i]
                combined_list.append(new_list)
            elif i < len(well_info) and i >= len(stock_info):
                new_standard = standard_list.copy()
                new_list = new_standard + well_info[i]
                combined_list.append(new_list)
            else:
                new_blank = blank_list.copy()
                new_list = stock_info[i] + new_blank
                combined_list.append(new_list)
            
        return combined_list