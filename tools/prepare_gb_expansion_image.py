#!/usr/bin/env python3
"""Prepare an 8 MiB MBC5 RED cartridge envelope; not boot certification."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASELINES=ROOT/"research"/"rom-baselines.csv"
TARGET_ROM_BYTES=8*1024*1024
TARGET_ROM_BANKS=512
TARGET_CART_TYPE=0x1B
TARGET_ROM_SIZE_CODE=0x08
TARGET_RAM_SIZE_CODE=0x04
TARGET_SRAM_BYTES=128*1024

def sha256(data): return hashlib.sha256(data).hexdigest()

def header_checksum(data):
    value=0
    for b in data[0x134:0x14D]: value=(value-b-1)&0xFF
    return value

def global_checksum(data):
    return (sum(data[:0x14E])+sum(data[0x150:]))&0xFFFF

def load_baselines():
    with BASELINES.open(newline="",encoding="utf-8") as f:
        return {row["id"]:row for row in csv.DictReader(f)}

def verify_source(data,source_id):
    row=load_baselines().get(source_id)
    if row is None: raise ValueError(f"unknown source id: {source_id}")
    if len(data)!=int(row["rom_size_bytes"]): raise ValueError("size mismatch")
    if sha256(data)!=row["sha256"]: raise ValueError("SHA-256 mismatch")
    if data[0x134:0x13F]!=b"POKEMON RED": raise ValueError("not POKEMON RED")
    if data[0x14D]!=header_checksum(data): raise ValueError("header checksum mismatch")
    if int.from_bytes(data[0x14E:0x150],"big")!=global_checksum(data): raise ValueError("global checksum mismatch")
    return row

def expand_image(data):
    if len(data)>TARGET_ROM_BYTES: raise ValueError("source too large")
    out=bytearray(b"\xFF"*TARGET_ROM_BYTES)
    out[:len(data)]=data
    out[0x147]=TARGET_CART_TYPE
    out[0x148]=TARGET_ROM_SIZE_CODE
    out[0x149]=TARGET_RAM_SIZE_CODE
    out[0x14D]=header_checksum(out)
    out[0x14E:0x150]=b"\0\0"
    out[0x14E:0x150]=global_checksum(out).to_bytes(2,"big")
    return bytes(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path); ap.add_argument("output",type=Path,nargs="?")
    ap.add_argument("--source-id",required=True); ap.add_argument("--plan-only",action="store_true")
    args=ap.parse_args()
    source=args.input.read_bytes(); verify_source(source,args.source_id)
    expanded=expand_image(source)
    info={"source_id":args.source_id,"source_bytes":len(source),"target_bytes":len(expanded),
          "target_rom_banks_16k":TARGET_ROM_BANKS,"target_mapper":"MBC5+RAM+BATTERY",
          "target_sram_bytes":TARGET_SRAM_BYTES,"header_checksum_ok":expanded[0x14D]==header_checksum(expanded),
          "global_checksum_ok":int.from_bytes(expanded[0x14E:0x150],"big")==global_checksum(expanded),
          "boot_certified":False,
          "required_next_gate":"patch and verify MBC5 9th ROM-bank bit writes at 0x3000-0x3FFF"}
    if not args.plan_only:
        if args.output is None: raise SystemExit("output required unless --plan-only")
        args.output.write_bytes(expanded); info["output"]=str(args.output)
    print(json.dumps(info,indent=2)); return 0

if __name__=="__main__":
    raise SystemExit(main())
