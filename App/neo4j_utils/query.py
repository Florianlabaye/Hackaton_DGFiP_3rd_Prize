import networkx as nx
import pandas as pd
from pyvis.network import Network

def get_tx_value(properties): 
    return (float(properties["value"]) + float(properties["receipt_effective_gas_price"])) * 10**(-9)

def scale_weights(weights): 
    S = sum(weights)
    return [weight / S for weight in weights]

def graph_from_cypher(res):
    G = nx.MultiDiGraph()

    nodes = list(res._nodes.values())
    for node in nodes:
        properties = node._properties
        if "exchange" in properties.keys(): 
            title = f"{properties['exchange']}({properties['pk']})"
            group=2
        else: 
            title = properties["pk"]
            group=1

        G.add_node(node.element_id, group=group, title=title, label="")

    rels = list(res._relationships.values())

    weights = [
        get_tx_value(rel._properties)
        for rel in rels
    ]
    scaled_weights = scale_weights(weights)

    for ix, rel in enumerate(rels): 
        G.add_edge(
            rel.start_node.element_id, rel.end_node.element_id, 
            width=scaled_weights[ix], 
            title=f"{weights[ix]}ETH", 
            properties=rel._properties)
        
    return G


def nx_to_pyvis(nt: Network, G: nx.MultiDiGraph):  
    for node in G.nodes.data(): 
        id_, properties = node

        if properties["group"] == 2: 
            shape = "star"
            color = "#EEFD72"
        else: 
            shape = "dot"
            color = "#98DCF8"
        nt.add_node(id_, 
                    title=properties["title"],
                    color=color,
                    shape=shape)
    for edge in G.edges.data(): 
        from_, to_, properties = edge 
        nt.add_edge(from_, 
                    to_, 
                    title=properties["title"], 
                    width=properties["width"]) 

def subgraphs_from_node(tx, address):
    query = """MATCH (start:User {pk:{{}}})
    CALL apoc.path.subgraphNodes(start, {}) YIELD node
    MATCH (node)-[rel:SENDS]->()
    RETURN rel""".format(address)
    tx.run(query)
    
def get_data_transactions(edges, nodes):
    e_data = list(edges.data())
    n_data = dict(nodes.data())
    f_nodes, to_nodes, values, timestamps = [], [], [], []
    for e in e_data:
        f_nodes.append(n_data[e[0]]['title'])
        to_nodes.append(n_data[e[1]]['title'])
        values.append(e[2]['title'])
        timestamps.append(e[2]['properties']['timestamp'])
    return pd.DataFrame({'f_nodes': f_nodes, 'to_nodes': to_nodes, 'values': values, 'timestamps' : timestamps})
