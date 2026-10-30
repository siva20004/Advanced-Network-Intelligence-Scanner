import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def generate_topology(scanner_ip, devices):
    G = nx.Graph()
    G.add_node(scanner_ip)

    for device in devices:
        G.add_node(device)
        G.add_edge(scanner_ip, device)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000)
    plt.title("Network Topology")
    plt.savefig("network_topology.png")
    plt.close()
