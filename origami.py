
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
import json
import sys
import collections

from gadgets import Gadget, create_gadget
from pleat import Pleat

class Network:
    def __init__(self):
        self.pleats: Dict[str, Pleat] = {}
        self.gadgets: Dict[str, Gadget] = {}
        self.readers: Dict[str, List[str]] = collections.defaultdict(list)
        
    def add_pleat(self, name: str, initial: Optional[bool] = None):
        if name in self.pleats:
            raise ValueError(f"Pleat {name} ya existe")
        self.pleats[name] = Pleat(name, initial)

    def get_pleat(self, name: str) -> Pleat:
        if name not in self.pleats:
            raise KeyError(f"Pleat {name} no encontrado")
        return self.pleats[name]

    def add_gadget(self, gadget: Gadget):
        if gadget.id in self.gadgets:
            raise ValueError(f"Gadget con id {gadget.id} ya existe")
        for pname in gadget.input_names + gadget.output_names:
            if pname not in self.pleats:
                self.add_pleat(pname, None)
        gadget.validate()
        self.gadgets[gadget.id] = gadget
        
        for pname in gadget.input_names:
            self.readers[pname].append(gadget.id)

    def connect(self, out_pleat_name: str, in_pleat_name: str):
        if out_pleat_name not in self.pleats:
            self.add_pleat(out_pleat_name, None)
        if in_pleat_name not in self.pleats:
            self.add_pleat(in_pleat_name, None)
        for gid, g in self.gadgets.items():
            if in_pleat_name in g.input_names:
                if gid not in self.readers[out_pleat_name]:
                    self.readers[out_pleat_name].append(gid)

    def set_inputs(self, values: Dict[str, Optional[bool]]):
        for name, val in values.items():
            if name not in self.pleats:
                self.add_pleat(name, val)
            else:
                self.pleats[name].signal = val

    def topological_order(self) -> List[str]:
        g_out = {gid: set() for gid in self.gadgets}  
        indeg = {gid: 0 for gid in self.gadgets}

        for aid, a in self.gadgets.items():
            for pout in a.output_names:
                readers = self.readers.get(pout, [])
                for bid in readers:                    
                    if bid == aid:
                        continue
                    if bid not in g_out[aid]:
                        g_out[aid].add(bid)
                        indeg[bid] += 1

        q = collections.deque([gid for gid, d in indeg.items() if d == 0])
        order = []
        while q:
            u = q.popleft()
            order.append(u)
            for v in g_out[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        if len(order) != len(self.gadgets):
            raise ValueError("Ciclo de dependencias en la red (no es un DAG)")
        return order

    def run(self, max_iter: int = 3, log: bool = False) -> Tuple[Dict[str, Optional[bool]], List[str]]:
        if log:
            logs = []
        else:
            logs = []

        order = self.topological_order()

        if log:
            logs.append("Orden topológico de gadgets: " + ", ".join(order))

        stable = False
        iteration = 0
        while not stable and iteration < max_iter:
            iteration += 1
            if log:
                logs.append(f"Iteración {iteration}")
            changed = False
            for gid in order:
                g = self.gadgets[gid]
                in_vals = [self.pleats[name].signal for name in g.input_names]
                if log:
                    logs.append(f"  Ejecutando {gid} ({g.__class__.__name__}), entradas: {g.input_names} -> {in_vals}")
                out_vals = g.evaluate(in_vals)
                for name, val in zip(g.output_names, out_vals):
                    old = self.pleats[name].signal
                    if old != val:
                        changed = True
                        if log:
                            logs.append(f"    {name}: {old} -> {val}")
                        self.pleats[name].signal = val
            if not changed:
                stable = True
            if log:
                logs.append(f"Fin iteración {iteration}, changed={changed}")
        pleat_values = {name: p.signal for name, p in self.pleats.items()}
        return pleat_values, logs


    @classmethod
    def from_spec(cls, spec: Dict[str, Any]) -> "Network":
        net = cls()
        pleat_list = spec.get("pleats", [])
        for pname in pleat_list:
            net.add_pleat(pname, None)        

        for gspec in spec.get("gadgets", []):
            g = create_gadget(gspec["type"], gspec["id"], gspec["inputs"], gspec["outputs"])
            net.add_gadget(g)
        
        for conn in spec.get("connections", []):
            net.connect(conn["from"], conn["to"])
        
        if "inputs" in spec:
            net.set_inputs(spec["inputs"])
        return net


def run_from_file(filename: str, log: bool = True):
    with open(filename, "r", encoding="utf-8") as f:
        spec = json.load(f)
    net = Network.from_spec(spec)
    pleat_values, logs = net.run(log=log)
    print("=== RESULTADO ===")
    for name, val in sorted(pleat_values.items()):
        print(f"{name}: {val}")
    if log:
        print("\n=== LOG ===")
        for line in logs:
            print(line)

def main():
    if len(sys.argv) < 2:
        print("Uso: python origami.py archivo.json")
        sys.exit(1)
    fname = sys.argv[1]
    run_from_file(fname, log=True)

if __name__ == "__main__":
    main()
