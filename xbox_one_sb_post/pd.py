from enum import Enum

import sigrokdecode as sd

MAX_CODE_INDEX = 3


class CodeFlavor(Enum):
    NONE = 0x00
    CPU = 0x10
    SP = 0x30
    SMC = 0x70
    OS = 0xF0


class Segment:
    def __init__(self, seg: int):
        self.seg = seg

    @classmethod
    def none(cls):
        return cls(0)

    @property
    def value(self) -> int:
        return self.seg

    @property
    def is_set(self) -> bool:
        return self.seg != 0

    @property
    def code_flavor(self) -> CodeFlavor:
        top_nibble = self.seg & 0xF0
        return CodeFlavor(top_nibble)

    @property
    def code_index(self) -> int:
        return self.seg & 0x0F

    def __repr__(self) -> str:
        return f"{self.code_flavor.name:3s}"

    def __eq__(self, obj) -> bool:
        if isinstance(obj, Segment):
            return self.value == obj.value
        return False


class Decoder(sd.Decoder):
    api_version = 3
    id = "xbox_one_sb_post"
    name = "Xbox One SB Post Code"
    longname = "Xbox One SB Post Code Protocol via MAX6958A"
    desc = "Decodes Xbox One POST codes from SB SMBUS2."
    license = "gplv2+"
    inputs = ["max6958"]
    outputs = []
    tags = ["I2C", "Xbox One", "POST", "Codes"]

    annotations = (("code", "Code"),)

    annotation_rows = (("post-code", "POST Code", (0,)),)

    def __init__(self):
        self._has_digit = False
        self._prev_segment = Segment.none()
        self.segment = Segment.none()
        self.first_bit_offset = None
        self.last_bit_offset = None
        self.code = 0
        self._code_cache = [0, 0, 0, 0]

    def reset(self):
        self._has_digit = False
        # self._prev_segment = None
        self.segment = Segment.none()
        self.first_bit_offset = None
        self.last_bit_offset = None
        self.code = 0
        # self._code_cache = [0, 0, 0, 0]

    @property
    def has_digit(self):
        return self._has_digit

    def start(self):
        self.out_ann = self.register(sd.OUTPUT_ANN)

    def decode(self, ss, es, data):
        """Process I2C packets from the max6958 decoder."""
        if len(data) == 0:
            raise Exception("Expected data list from MAX6958!")

        op = data[0]
        assert isinstance(op, str), "First element in data not a string!"

        annotation = None
        if op.startswith("Digit_"):
            digit_num = int(op[len("Digit_") :])
            digit_val = data[1]
            self.code |= (digit_val & 0xF) << (digit_num * 4)
            if not self.first_bit_offset:
                self.first_bit_offset = ss
            self._has_digit = True
        elif op == "Segments":
            self.segment = Segment(data[1])

            if (
                self._prev_segment.code_flavor == self.segment.code_flavor
                and self._prev_segment.code_index > self.segment.code_index
            ):
                # We are dealing with a multi value error code
                pass
            else:
                self._code_cache = [0, 0, 0, 0]

            self.last_bit_offset = es
            self._prev_segment = self.segment
            self._code_cache[MAX_CODE_INDEX - self.segment.code_index] = self.code
        elif op == "STOP":
            if self.segment.is_set and self.first_bit_offset and self.last_bit_offset:
                ss = self.first_bit_offset
                es = self.last_bit_offset
                code = " ".join([f"{c:#04x}" for c in self._code_cache if c != 0])
                annotation = f"{self.segment}: {code}"
                self.reset()

        if annotation:
            self.put(
                ss,
                es,
                self.out_ann,
                [0, [annotation]],
            )
