from enum import Enum

import sigrokdecode as sd

REGISTER_COUNT_TOTAL = 0x25
MAX_INTENSITY = 0x40


class Register(Enum):
    DecodeMode = 0x01
    Intensity = 0x02
    ScanLimit = 0x03
    Configuration = 0x04
    FactoryReserved = 0x05
    GpIo = 0x06
    DisplayTest = 0x07
    ReadKeyDebounced = 0x08
    ReadKeyPressed = 0x0C
    Digit_0 = 0x20
    Digit_1 = 0x21
    Digit_2 = 0x22
    Digit_3 = 0x23
    Segments = 0x24


class DecodeMode(Enum):
    NoDecode = 0x0
    HexDecodeDigit_0_No_3_1 = 0x1
    HexDecodeDigits_2_0_No_3 = 0x7
    HexDecodeDigit_3_No_2_0 = 0x8
    HexDecodeDigits_3_0 = 0xF


class Configuration(Enum):
    Shutdown = 0x0
    Normal = 0x1
    Reset = 0x20


class ScanLimit(Enum):
    Dig_0_Seg_04 = 0x00
    Dig_01_Seg_0145 = 0x01
    Dig_012_Seg_012456 = 0x02
    Dig_0123_Seg_01234567 = 0x03


class Decoder(sd.Decoder):
    api_version = 3
    id = "max6958"
    name = "MAX6958"
    longname = "MAX6958 7Segment display driver"
    desc = "MAX6958 decoder."
    license = "gplv2+"
    inputs = ["i2c"]
    outputs = ["max6958"]
    tags = ["I2C", "MAX6958", "7Segment", "LED", "Driver"]

    annotations = (("register", "Register"),)
    annotation_rows = (("max6958-register", "Register", (0,)),)

    SLAVE_ADDRS = [0x38, 0x39]

    def __init__(self):
        self.start_condition = (None, None)
        self.state = "UNKNOWN"
        self.is_target = False
        self.current_register = 0
        self.data = []

    def reset(self):
        self.start_condition = (None, None)
        self.state = "UNKNOWN"
        self.is_target = False
        self.current_register = 0
        self.data.clear()

    def start(self):
        self.out_ann = self.register(sd.OUTPUT_ANN)
        self.out_python = self.register(sd.OUTPUT_PYTHON, proto_id="max6958")

    def decode(self, ss, es, data):
        """Process I2C packets from the I2C decoder."""
        cmd, databyte = data
        # self.put(ss, es, self.out_ann, [1, [f"{data}"]])
        if cmd in ["ADDRESS READ", "ADDRESS WRITE"]:
            self.is_target = databyte in self.SLAVE_ADDRS
            if self.is_target:
                start_ss, start_es = self.start_condition
                self.put(start_ss, start_es, self.out_ann, [0, ["START", "S"]])
                self.put(ss, es, self.out_python, ["START", None])
                self.start_condition = (None, None)

        if cmd == "START":
            self.start_condition = (ss, es)
        elif not self.is_target:
            return
        elif cmd == "STOP":
            self.put(ss, es, self.out_ann, [0, ["STOP", "P"]])
            self.put(ss, es, self.out_python, ["STOP", None])
            self.annotate()
            self.reset()
        elif cmd == "ACK":
            pass
        elif cmd == "NACK":
            pass
            # elif cmd == "ADDRESS READ":
            # pass
            # elif cmd == "ADDRESS WRITE":
            # pass
        elif cmd == "DATA READ":
            pass
        elif cmd == "DATA WRITE":
            if not self.current_register:
                self.current_register = databyte
            else:
                self.data.append((ss, es, databyte))
        elif cmd == "BITS":
            pass
        elif cmd == "ADDRESS WRITE":
            pass
        else:
            raise Exception(cmd)

    def annotate(self):
        reg = self.current_register
        for ss, es, data in self.data:
            reg_enum = Register(reg % REGISTER_COUNT_TOTAL)
            annotation = ""
            if reg_enum == Register.Configuration:
                try:
                    config = Configuration(data).name
                except:
                    config = "UNKNOWN"

                annotation = f"{reg_enum.name}: {config} ({data:#02x})"
            elif reg_enum == Register.DecodeMode:
                try:
                    decode_mode = DecodeMode(data).name
                except:
                    decode_mode = "UNKNOWN"

                annotation = f"{reg_enum.name}: {decode_mode} ({data:#02x})"
            elif reg_enum == Register.ScanLimit:
                try:
                    scanlimit = ScanLimit(data).name
                except:
                    scanlimit = "UNKNOWN"

                annotation = f"{reg_enum.name}: {scanlimit} ({data:#02x})"
            elif reg_enum == Register.Intensity:
                intensity = (data / MAX_INTENSITY) * 100
                annotation = f"{reg_enum.name}: {intensity:.2f} % ({data}/{MAX_INTENSITY}) ({data:#02x})"
            else:
                annotation = f"{reg_enum.name}: {data:#02x}"

            self.put(ss, es, self.out_ann, [0, [annotation]])
            self.put(ss, es, self.out_python, [reg_enum.name, data])
            reg += 1
