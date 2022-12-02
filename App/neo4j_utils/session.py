from neo4j import GraphDatabase
import os 

def connect():
    return GraphDatabase.driver("bolt://34.79.248.80:7687", auth=("neo4j", "azerty"))

def push(method, arg):
    with driver.session() as session:
        session.execute_write(method, arg)

def load_csv(tx, csv_file):
    tx.run("LOAD CSV WITH HEADERS FROM 'file:///ethereum/data/transactions/000000000001.csv' AS row FIELDTERMINATOR ';' MATCH (u1:User {pk: row.from_address})-[:SENDS {value: row.value}]->(u2:User {pk: row.to_address})")

def query_graph(tx, query):
    res = tx.run(query)
    return res.graph()

def push_csv(f):
    driver = connect()
    with driver.session() as session:
        session.execute_write(load_csv, f)
    driver.close()