from collections import defaultdict, deque

class OrderSorting:
    def __init__(self):
        pass

    def obtainOrder(self, repo_SPIs):
        bulk_species = []
        nonbulk_species = []
        prebulk_name = []

        for spi in repo_SPIs:
            if spi.isPrebulk:
                prebulk_name.append(spi.SProtocol.Name)
            if spi.isBulk or spi.isPrebulk or spi.well is not None:
                bulk_species.append(spi)
            else:
                nonbulk_species.append(spi)

        # Topologically sort bulks and non-bulks separately
        bulk_order_pre = self.topSort(bulk_species)
        bulk_order = []
        

        # Ensure the Pre-bulk is isolated properly if it shares a layer
        for name_list in bulk_order_pre:
            if prebulk_name and set(prebulk_name).issubset(name_list):
                bulk_order.append(prebulk_name)
                rest = [n for n in name_list if n not in prebulk_name]
                if rest:
                    bulk_order.append(rest)
            else:
                bulk_order.append(name_list)
        
        if prebulk_name:
            prebulk_name = bulk_order[-1] # Dual check to ensure the pre-bulk is returned properly

        nonbulk_order = self.topSort(nonbulk_species)
        combined_order = bulk_order + nonbulk_order
        return combined_order, prebulk_name, bulk_order, nonbulk_order

    def topSort(self, species_subset):
        # Use the function of tree to obtain the topological order of the calculation sequence (specified by the layer)
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        nodes = set()
        name_list = []
        for spi in species_subset:
            sp_name = spi.SProtocol.Name
            nodes.add(sp_name)
            name_list.append(sp_name)

        for node in nodes:
            in_degree[node] = 0
        for spi in species_subset:
            sp_name = spi.SProtocol.Name
            for component_name in spi.SProtocol.Components.keys():
                if component_name in name_list:
                    graph[component_name].append(sp_name)
                    in_degree[sp_name] += 1
        
        queue = deque([node for node in nodes if in_degree[node] == 0])
        layers = []

        while queue:
            current_layer = []
            next_queue = deque()

            while queue:
                node = queue.popleft()
                current_layer.append(node)
                for neighbor in graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)

            layers.append(current_layer)
            queue = next_queue

        ordered = layers[::-1]
        return ordered