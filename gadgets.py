
from typing import List, Optional


class Gadget:
    def __init__(self, id: str, input_names: List[str], output_names: List[str]):
        self.id = id
        self.input_names = list(input_names)
        self.output_names = list(output_names)

    def validate(self):
        raise NotImplementedError

    def evaluate(self, inputs: List[Optional[bool]]) -> List[Optional[bool]]:
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id})"


class NotGadget(Gadget):
    def __init__(self, id: str, input_names: List[str], output_names: List[str]):
        super().__init__(id, input_names, output_names)
        self.validate()

    def validate(self):
        if len(self.input_names) != 1 or len(self.output_names) != 1:
            raise ValueError("NOT gadget requiere 1 entrada y 1 salida")

    def evaluate(self, inputs: List[Optional[bool]]) -> List[Optional[bool]]:
        if inputs[0] is None:
            return [None]
        return [not inputs[0]]

class AndGadget(Gadget):
    def __init__(self, id: str, input_names: List[str], output_names: List[str]):
        super().__init__(id, input_names, output_names)
        self.validate()

    def validate(self):
        if len(self.input_names) < 2 or len(self.output_names) != 1:
            raise ValueError("AND gadget requiere >=2 entradas y 1 salida")

    def evaluate(self, inputs: List[Optional[bool]]) -> List[Optional[bool]]:
        if any(v is None for v in inputs):
            return [None]
        res = True
        for v in inputs:
            res = res and v
        return [res]

class OrGadget(Gadget):
    def __init__(self, id: str, input_names: List[str], output_names: List[str]):
        super().__init__(id, input_names, output_names)
        self.validate()

    def validate(self):
        if len(self.input_names) < 2 or len(self.output_names) != 1:
            raise ValueError("OR gadget requiere >=2 entradas y 1 salida")

    def evaluate(self, inputs: List[Optional[bool]]) -> List[Optional[bool]]:
        if any(v is None for v in inputs):
            return [None]
        res = False
        for v in inputs:
            res = res or v
        return [res]

class NandGadget(Gadget):
    def __init__(self, id: str, input_names: List[str], output_names: List[str]):
        super().__init__(id, input_names, output_names)
        self.validate()

    def validate(self):
        if len(self.input_names) < 2 or len(self.output_names) != 1:
            raise ValueError("NAND gadget requiere >=2 entradas y 1 salida")

    def evaluate(self, inputs: List[Optional[bool]]) -> List[Optional[bool]]:
        if any(v is None for v in inputs):
            return [None]
        and_res = True
        for v in inputs:
            and_res = and_res and v
        return [not and_res]


_GADGET_TYPES = {
    "NOT": NotGadget,
    "AND": AndGadget,
    "OR": OrGadget,
    "NAND": NandGadget,
}

def create_gadget(gtype: str, id: str, inputs: List[str], outputs: List[str]) -> Gadget:
    gtype = gtype.upper()
    if gtype not in _GADGET_TYPES:
        raise ValueError(f"Tipo de gadget desconocido: {gtype}")
    return _GADGET_TYPES[gtype](id, inputs, outputs)
