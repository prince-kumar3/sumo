from pathlib import Path
import math
import xml.etree.ElementTree as ET


NODES_FILE = Path("curved_city.nod.xml")
EDGES_FILE = Path("curved_city.edg.xml")
NET_FILE = Path("net_half_tls.net.xml")

NODE_POSITIONS = {
    "A0": (0.0, 0.0),
    "A1": (-18.0, 118.0),
    "A2": (6.0, 244.0),
    "B0": (126.0, -10.0),
    "B1": (114.0, 104.0),
    "B2": (150.0, 232.0),
    "C0": (260.0, 12.0),
    "C1": (244.0, 136.0),
    "C2": (282.0, 246.0),
    "D0": (388.0, -14.0),
    "D1": (420.0, 116.0),
    "D2": (392.0, 260.0),
}

EDGE_PAIRS = [
    ("A0", "A1"),
    ("A1", "A2"),
    ("A0", "B0"),
    ("A1", "B1"),
    ("A2", "B2"),
    ("B0", "B1"),
    ("B1", "B2"),
    ("B0", "C0"),
    ("B1", "C1"),
    ("B2", "C2"),
    ("C0", "C1"),
    ("C1", "C2"),
    ("C0", "D0"),
    ("C1", "D1"),
    ("C2", "D2"),
    ("D0", "D1"),
    ("D1", "D2"),
]

# Stable, hand-tuned bends. Positive values curve one direction, negative the other.
CURVE_STRENGTHS = {
    ("A0", "A1"): -9.0,
    ("A1", "A2"): 12.0,
    ("B0", "B1"): 7.0,
    ("B1", "B2"): -13.0,
    ("C0", "C1"): 11.0,
    ("C1", "C2"): -10.0,
    ("D0", "D1"): -14.0,
    ("D1", "D2"): 16.0,
    ("A0", "B0"): 7.0,
    ("A1", "B1"): -9.0,
    ("A2", "B2"): 13.0,
    ("B0", "C0"): -10.0,
    ("B1", "C1"): 10.0,
    ("B2", "C2"): -8.0,
    ("C0", "D0"): 8.0,
    ("C1", "D1"): -14.0,
    ("C2", "D2"): 14.0,
}


def indent(element, level=0):
    gap = "\n" + level * "    "
    child_gap = "\n" + (level + 1) * "    "

    if len(element):
        if not element.text or not element.text.strip():
            element.text = child_gap
        for child in element:
            indent(child, level + 1)
        if not element.tail or not element.tail.strip():
            element.tail = gap
    elif level and (not element.tail or not element.tail.strip()):
        element.tail = gap


def fmt(value):
    return f"{value:.2f}"


def curved_shape(start_id, end_id, reverse=False):
    x1, y1 = NODE_POSITIONS[start_id]
    x2, y2 = NODE_POSITIONS[end_id]
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    nx = -dy / length
    ny = dx / length
    strength = CURVE_STRENGTHS[(start_id, end_id)]

    points = [
        (x1, y1),
        (x1 + dx * 0.33 + nx * strength, y1 + dy * 0.33 + ny * strength),
        (x1 + dx * 0.67 - nx * strength * 0.55, y1 + dy * 0.67 - ny * strength * 0.55),
        (x2, y2),
    ]

    if reverse:
        points = list(reversed(points))

    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def write_nodes():
    root = ET.Element("nodes")
    for node_id, (x, y) in NODE_POSITIONS.items():
        ET.SubElement(
            root,
            "node",
            {
                "id": node_id,
                "x": fmt(x),
                "y": fmt(y),
                "type": "traffic_light",
            },
        )
    indent(root)
    ET.ElementTree(root).write(NODES_FILE, encoding="utf-8", xml_declaration=True)


def write_edges():
    root = ET.Element("edges")
    for start_id, end_id in EDGE_PAIRS:
        ET.SubElement(
            root,
            "edge",
            {
                "id": f"{start_id}{end_id}",
                "from": start_id,
                "to": end_id,
                "priority": "2",
                "numLanes": "1",
                "speed": "13.89",
                "shape": curved_shape(start_id, end_id),
            },
        )
        ET.SubElement(
            root,
            "edge",
            {
                "id": f"{end_id}{start_id}",
                "from": end_id,
                "to": start_id,
                "priority": "2",
                "numLanes": "1",
                "speed": "13.89",
                "shape": curved_shape(start_id, end_id, reverse=True),
            },
        )
    indent(root)
    ET.ElementTree(root).write(EDGES_FILE, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    write_nodes()
    write_edges()
    print(f"Wrote {NODES_FILE} and {EDGES_FILE}; run netconvert to build {NET_FILE}.")
