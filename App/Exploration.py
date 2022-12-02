import streamlit as st
import pandas as pd
from neo4j import GraphDatabase
from utils import read_data, head
from neo4j_utils.session import connect, query_graph
from neo4j_utils.query import get_data_transactions
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


#General settings
st.set_page_config(
    page_title="DFiP",
    page_icon="👋",
    layout="wide",
)

st.markdown("<h1 style='text-align: center; color: black;text-shadow: 2px 4px 3px rgba(0,0,0,0.3);margin-top: 0px;'>Visualisation des transactions à partir d'une adresse</h1>", unsafe_allow_html=True)

st.text("")
st.text("")

st.markdown("<h1 style='color: black;text-decoration:underline solid #000000;font-size:25px'>Rentrer une adresse publique</h1>", unsafe_allow_html=True)

#st.subheader("Rentrer une adresse publique :")

st.sidebar.markdown("# Partir d'une adresse 🎈")

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

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

    nt.show('nx.html')

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


with st.form("form_adresse"):
    adresse = st.text_input("Adresse publique :")
    #distance = st.text_input("Distance à parcourir :")
    st.write("Afficher les transactions à partir d'une certaine date")
    filtre_date = st.text_input("Date :")
    st.write("Afficher les transactions à partir d'un certain montant")
    filtre_montant = st.text_input("Montant :")
    
    submitted = st.form_submit_button("Valider")
st.write('0x9afc988cb1fa3d74cfc4399aa0bdffc8a9d8a7b7')
st.write('0x94b335765a75c59854caf51b486430efee8f26bd')
st.write('0x87cbc48075d7aa1760ac71c41e8bc289b6a31f56')


if submitted:
    if (filtre_date=="" and filtre_montant==""):
        driver=connect()
        query = ("match (node1:Entity)-[r:TRANSFERRED]->(node2:Entity) where node1.pk= '%s' match p=(node1)-[:TRANSFERRED]-(n2) RETURN p" % (adresse))
        with driver.session() as session:
            res = session.execute_read(query_graph, query)
        G = graph_from_cypher(res)
        nt = Network('500px', '898px', directed=True, notebook=False, font_color='#10000000')
        # populates the nodes and edges data structures
        nx_to_pyvis(nt, G)
        HtmlFile = open("nx.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height = 900,width=900)


        #On génère le tableau
        table_data = get_data_transactions(G.edges, G.nodes)
        st.dataframe(table_data)

        #Export
        csv = convert_df(table_data)
        st.download_button(
            "Press to Download",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv'
            )
        
    if (filtre_date!="" and filtre_montant==""):
        driver=connect()
        query = ("match (e:Entity)-[r:TRANSFERRED]->(b:Entity) where date(left(r.timestamp,10)) > date('%s') and e.pk='%s' RETURN e,b,r " % (filtre_date, adresse))
        with driver.session() as session:
            res = session.execute_read(query_graph, query)
        G = graph_from_cypher(res)
        nt = Network('500px', '898px', directed=True, notebook=False, font_color='#10000000')
        # populates the nodes and edges data structures
        nx_to_pyvis(nt, G)
        HtmlFile = open("nx.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height = 900,width=900)


        #On génère le tableau
        table_data = get_data_transactions(G.edges, G.nodes)
        st.dataframe(table_data)

        #Export
        csv = convert_df(table_data)
        st.download_button(
            "Press to Download",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv'
            )

        
    if (filtre_date=="" and filtre_montant!=""):
        driver=connect()
        query = ("match (e:Entity)-[r:TRANSFERRED]->(b:Entity) where date(left(r.timestamp,10)) > date('%s') and e.pk='%s' and toInteger('r.value') >= toInteger('%s') RETURN e,b,r " % (filtre_date, adresse, filtre_montant))
        with driver.session() as session:
            res = session.execute_read(query_graph, query)
        G = graph_from_cypher(res)
        nt = Network('500px', '898px', directed=True, notebook=False, font_color='#10000000')
        # populates the nodes and edges data structures
        nx_to_pyvis(nt, G)
        HtmlFile = open("nx.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height = 900,width=900)


        #On génère le tableau
        table_data = get_data_transactions(G.edges, G.nodes)
        st.dataframe(table_data)

        #Export
        csv = convert_df(table_data)
        st.download_button(
            "Press to Download",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv'
            )

    
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()
    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", table_data.columns)
    for column in to_filter_columns:
        left, right = st.columns((1, 20))
        left.write("↳")
