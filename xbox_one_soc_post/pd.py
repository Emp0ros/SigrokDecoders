import struct
import sigrokdecode as sd

TARGET_ADDR = 0x4C

def assemble_code(code_bytes: list[int]) -> int:
    assert len(code_bytes) == 4
    return struct.unpack("<I", bytes(code_bytes))[0]

class Decoder(sd.Decoder):
    api_version = 3
    id = "xbox_one_soc_post"
    name = "Xbox One SoC POST Code"
    longname = "Xbox One SoC POST Code protocol"
    desc = "Decodes Xbox One POST codes from SB SMBUS3 (SoC)."
    license = "gplv2+"
    inputs = ["i2c"]
    outputs = []
    tags = ["I2C", "Xbox One", "POST", "Codes"]

    annotations = (("code", "Code"),)

    annotation_rows = (("post-code", "POST Code", (0,)),)

    def __init__(self):
        self.is_target = False
        self.address = 0
        self._code_cache = [0] * 8

    def reset(self):
        self.is_target = False
        self.address = 0
        self._code_cache = [0] * 8

    def start(self):
        self.out_ann = self.register(sd.OUTPUT_ANN)

    def decode(self, ss, es, data):
        """Process I2C packets from the I2C decoder."""
        if len(data) == 0:
            raise Exception("Expected data list from I2C!")

        cmd, databyte = data

        if cmd == "START":
            pass
            # self._code_cache = [0, 0, 0, 0, 0, 0, 0, 0]
        elif cmd == "ADDRESS WRITE" or cmd == "ADDRESS_READ":
            self.is_target = databyte == TARGET_ADDR
            self.address = databyte
        elif not self.is_target:
            return
        elif cmd == "DATA WRITE":
            self.reg_addr = databyte
        elif cmd == "DATA READ":
            if 0xC0 <= self.reg_addr <= 0xC7:
                # Aka. reg_addr - 0xC0
                lower_nibble = self.reg_addr & 0x0F
                self._code_cache[lower_nibble] = databyte

            if self.reg_addr == 0xC3 and databyte & 0x01:
                # Check for flag in 0xC3 (POST Code available)
                code = assemble_code(self._code_cache[4:])
                if code != 0:
                    self.put(
                        ss,
                        es,
                        self.out_ann,
                        [0, ["CODE: {:#x}".format(code)]],
                    )
                self._code_cache = [0] * 8
