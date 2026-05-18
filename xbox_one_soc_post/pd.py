import sigrokdecode as sd

MAX_CODE_INDEX = 7
TARGET_ADDR = 0x4C


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
        self._code_cache = [0, 0, 0, 0, 0, 0, 0, 0]

    def reset(self):
        self.is_target = False
        self.address = 0
        self._code_cache = [0, 0, 0, 0, 0, 0, 0, 0]

    def start(self):
        self.out_ann = self.register(sd.OUTPUT_ANN)

    def decode(self, ss, es, data):
        """Process I2C packets from the I2C decoder."""
        if len(data) == 0:
            raise Exception("Expected data list from I2C!")

        cmd, databyte = data

        if cmd == "START":
            pass
            # self._code_cache = [0, 0, 0, 0]
        elif cmd == "ADDRESS WRITE" or cmd == "ADDRESS_READ":
            self.is_target = databyte == TARGET_ADDR
            self.address = databyte
        elif not self.is_target:
            return
        elif cmd == "DATA WRITE":
            self.register = databyte
        elif cmd == "DATA READ":
            if 0xC0 <= self.register <= 0xC7:
                """
                self.put(
                    ss,
                    es,
                    self.out_ann,
                    [0, ["REG={:02X}".format(self.register)]],
                )
                """
                lower_nibble = self.register & 0x0F
                self._code_cache[MAX_CODE_INDEX - lower_nibble] = databyte
            if self.register == 0xC4:
                code = "".join("{:02X}".format(b) for b in self._code_cache[:4])
                self.put(
                    ss,
                    es,
                    self.out_ann,
                    [0, ["CODE={}".format(code)]],
                )
                self._code_cache = [0, 0, 0, 0, 0, 0, 0, 0]
