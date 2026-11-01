import test from "node:test";
import assert from "node:assert/strict";
import { normalizeHardwareHex, sortHexKeys, machineSortPlan } from "../src/machine.mjs";

test("explicit x86 Arm RISC-V POWER four times four row sorting", () => {
  const arches=["x86_64","aarch64","riscv64","ppc64le"];
  const layers=["isaCpu","firmwareBoot","memoryIo","acceleratorAi"];
  for(let a=0;a<4;a++)for(let l=0;l<4;l++){
    const p=machineSortPlan({architecture:arches[a],layer:layers[l],
      ramBytesDecimal:"8589934592",busKind:"pciVendorId",busHex:"8086"});
    assert.equal(p.machineSortOrdinal,a*4+l);
    assert.equal(p.ramBytesDecimal,"8589934592");
    assert.equal(p.physicalMachineProven,false);
    assert.equal(p.firmwareWritable,false);
  }
});

test("hex sorting uses numeric fixed width in one bus namespace",()=>{
  const sorted=sortHexKeys([
    {kind:"pciVendorId",value:"ff"},
    {kind:"pciVendorId",value:"1"},
    {kind:"pciVendorId",value:"10"},
  ]);
  assert.deepEqual(sorted.map(x=>x.valueHex),["0001","0010","00ff"]);
  assert.equal(normalizeHardwareHex("ipsOffset","f").valueHex,"00000f");
  assert.equal(normalizeHardwareHex("cpuidLeaf",15).valueHex,"0000000f");
  assert.equal(normalizeHardwareHex("sourceRef","a".repeat(40)).widthBits,160);
});

test("mixed bus or unlicensed/unsafe fake identifiers do not sort",()=>{
  assert.throws(()=>sortHexKeys([{kind:"pciVendorId",value:"1"},{kind:"usbVendorId",value:"1"}]));
  assert.throws(()=>sortHexKeys([]));
  for(const value of ["0xabcd","FF","12345","-1",true,{},null,65536]){
    assert.throws(()=>normalizeHardwareHex("usbVendorId",value));
  }
  assert.throws(()=>normalizeHardwareHex("sourceRef",1));
  assert.throws(()=>normalizeHardwareHex("artifactSha256","a".repeat(63)));
});

test("RAM stays integer byte decimal string, cannot round through JS Number",()=>{
  const p=machineSortPlan({architecture:"ppc64le",layer:"memoryIo",
    ramBytesDecimal:"9223372036854775807",busKind:"usbProductId",busHex:"1"});
  assert.equal(p.ramBytesDecimal,"9223372036854775807");
  for(const ramBytesDecimal of [NaN,1.5,Number.MAX_SAFE_INTEGER,"-1","1e20",
                               "9223372036854775808","00",""]){
    assert.throws(()=>machineSortPlan({architecture:"x86_64",layer:"memoryIo",
      ramBytesDecimal,busKind:"pciVendorId",busHex:"1"}));
  }
});
