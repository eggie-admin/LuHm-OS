#!/usr/bin/env python3
"""No-video six-camera timing assessor for Linux V4L2 studio receipts.

Accepts ONLY numerical timestamp samples. Does not access cameras.
"""
import json
import math
import statistics

def assess(samples,*,expected=6,min_frames=30,max_spread_ms=33.4,max_p95_jitter_ms=20.0):
    if not isinstance(samples,dict) or len(samples)!=expected:
        raise ValueError("EXACT_CAMERA_LANES_REQUIRED")
    streams={}
    for name,times in samples.items():
        if not isinstance(name,str) or not name.startswith("cam") or len(name)>12:
            raise ValueError("INVALID_STREAM_ID")
        if not isinstance(times,list) or len(times)<min_frames or len(times)>3000:
            raise ValueError("INSUFFICIENT_FRAMES")
        if not all(type(x) in (int,float) and math.isfinite(x) and x>=0 for x in times):
            raise ValueError("TIMESTAMPS_INVALID")
        deltas=[(b-a)*1000 for a,b in zip(times,times[1:])]
        if not all(x>0 for x in deltas):
            raise ValueError("NON_MONOTONIC_TIMESTAMPS")
        jitters=sorted(abs(x-1000/30) for x in deltas)
        p95=jitters[min(len(jitters)-1,math.ceil(.95*len(jitters))-1)]
        streams[name]={"frameCount":len(times),"fpsEstimate":round(1000/statistics.median(deltas),2),
          "p95JitterMs":round(p95,3)}
    # For unsynchronized USB cameras only a coarse start-of-frame delta can be checked.
    starts=[x[0] for x in samples.values()]
    spread_ms=(max(starts)-min(starts))*1000
    jitter_ok=all(x["p95JitterMs"]<=max_p95_jitter_ms for x in streams.values())
    return {"schema":"luhmOs.sixCamTimingAssessment.v1","streams":streams,
            "startupSpreadMs":round(spread_ms,3),
            "verdict":"PASS_SUBMITTED_TIMESTAMPS_ONLY" if spread_ms<=max_spread_ms and jitter_ok else "GAP_TIMING",
            "cameraDevicesOpened":False,"framesCaptured":False,"calibrationProven":False,
            "hardwareSource":"CALLER_SUPPLIED_NOT_AUTHENTICATED","crownStatus":"STOP"}

if __name__=="__main__":
    print(json.dumps({"schema":"luhmOs.sixCamTimingAssessment.v1",
      "status":"NO_SAMPLES_NO_CAMERA_TEST_RUN","cameraDevicesOpened":False,"crownStatus":"STOP"}))
