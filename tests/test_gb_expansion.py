import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

prepare=load("prepare_gb_expansion_image","tools/prepare_gb_expansion_image.py")
audit=load("audit_gb_banking","tools/audit_gb_banking.py")

class GbExpansionTests(unittest.TestCase):
    def synthetic_red(self):
        d=bytearray(b"\xFF"*(512*1024))
        d[0x134:0x13F]=b"POKEMON RED"; d[0x146]=3; d[0x147]=0x03; d[0x148]=0x04; d[0x149]=0x03
        d[0x14D]=prepare.header_checksum(d); d[0x14E:0x150]=b"\0\0"
        d[0x14E:0x150]=prepare.global_checksum(d).to_bytes(2,"big")
        return bytes(d)

    def test_expand_to_mbc5_max_envelope(self):
        e=prepare.expand_image(self.synthetic_red())
        self.assertEqual(len(e),8*1024*1024)
        self.assertEqual((e[0x147],e[0x148],e[0x149]),(0x1B,0x08,0x04))
        self.assertEqual(e[0x14D],prepare.header_checksum(e))
        self.assertEqual(int.from_bytes(e[0x14E:0x150],"big"),prepare.global_checksum(e))

    def test_mapper_literal_counter(self):
        d=b"\xEA\x00\x20xx\xEA\x00\x30\xEA\x00\x20"
        self.assertEqual(audit.literal_store_count(d,0x2000),2)
        self.assertEqual(audit.literal_store_count(d,0x3000),1)

if __name__=="__main__":
    unittest.main()
