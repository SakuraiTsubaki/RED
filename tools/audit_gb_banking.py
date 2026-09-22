#!/usr/bin/env python3
"""Audit RED Game Boy headers and raw mapper-register literal patterns."""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path

CART_TYPES={0x03:"MBC1+RAM+BATTERY",0x13:"MBC3+RAM+BATTERY",0x1B:"MBC5+RAM+BATTERY"}
ROM_SIZES={0x04:512*1024,0x05:1024*1024,0x08:8*1024*1024}
RAM_SIZES={0x03:32*1024,0x04:128*1024}
REGISTERS=(0x0000,0x2000,0x3000,0x4000,0x6000)

def header_checksum(data):
    value=0
    for b in data[0x134:0x14D]:
        value=(value-b-1)&0xFF
    return value

def global_checksum(data):
    return (sum(data[:0x14E])+sum(data[0x150:]))&0xFFFF

def literal_store_count(data,address):
    return data.count(bytes((0xEA,address&0xFF,address>>8)))

def inspect(path):
    data=path.read_bytes()
    row={
      "filename":path.name,"bytes":len(data),"rom_banks_16k":len(data)//0x4000,
      "cartridge_type_code":f"0x{data[0x147]:02X}","cartridge_type":CART_TYPES.get(data[0x147],"UNKNOWN"),
      "declared_rom_bytes":ROM_SIZES.get(data[0x148],0),"declared_sram_bytes":RAM_SIZES.get(data[0x149],0),
      "header_version":data[0x14C],"header_checksum_ok":data[0x14D]==header_checksum(data),
      "global_checksum_ok":int.from_bytes(data[0x14E:0x150],"big")==global_checksum(data),
    }
    for address in REGISTERS:
        row[f"raw_EA_{address:04X}"]=literal_store_count(data,address)
    return row

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("rom",nargs="+",type=Path)
    rows=[inspect(p) for p in ap.parse_args().rom]
    w=csv.DictWriter(sys.stdout,fieldnames=list(rows[0]),lineterminator="\n")
    w.writeheader(); w.writerows(rows)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
