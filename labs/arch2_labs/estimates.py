"""Literature-grounded first-order energy, roofline, and area estimates.

SCALE-Sim (Samajdar et al., ISPASS 2020) is cycle-accurate for compute,
utilization, bandwidth, and SRAM/DRAM *access counts*, but it does not model
energy, power, or area. SCALE-Sim v3 added energy/power by integrating Accelergy
(Wu, Emer, Sze, ICCAD 2019); this module does the same thing analytically, at
teaching fidelity, by multiplying SCALE-Sim's real access counts by sourced
per-operation energies.

Every constant below is an order-of-magnitude teaching value at 45 nm from
Horowitz, "Computing's Energy Problem (and what we can do about it)," ISSCC 2014.
These are NOT signoff numbers. For real energy/area, route to Accelergy+Timeloop
(Parashar et al., ISPASS 2019) or CACTI (Muralimanohar et al., 2009).

Known unmodeled terms (see run archives): on-chip network / interconnect energy,
static/leakage energy, and real DRAM controller behavior are all omitted, so the
dynamic-access estimate is a lower bound biased toward memory-movement dominance.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- Sourced per-operation energies (Horowitz, ISSCC 2014, 45 nm) -------------
# MAC = one multiply + one add.
E_MAC_PJ = {
    "int8": 0.2 + 0.03,  # 8-bit integer multiply + add
    "fp16": 1.1 + 0.4,  # 16-bit float multiply + add
    "fp32": 3.7 + 0.9,  # 32-bit float multiply + add
}
# On-chip SRAM and off-chip DRAM movement, expressed per byte so the estimate
# scales with operand precision. DRAM ~ 640 pJ per 8-byte word (~80 pJ/byte);
# a small on-chip SRAM access is ~1.5 pJ/byte. DRAM movement is the ~100-200x
# term that dominates the MAC, which is itself the lesson.
E_SRAM_PJ_PER_BYTE = 1.5
E_DRAM_PJ_PER_BYTE = 80.0

BYTES_PER_ELEMENT = {"int8": 1, "fp16": 2, "fp32": 4}

# Rough 45 nm area anchors (illustrative only; prefer CACTI/Accelergy).
AREA_PER_PE_UM2 = {"int8": 800.0, "fp16": 2500.0, "fp32": 5000.0}
AREA_PER_SRAM_KB_MM2 = 0.007

ESTIMATE_SOURCES = {
    "per_op_energy": "Horowitz, Computing's Energy Problem, ISSCC 2014 (45 nm, order-of-magnitude)",
    "method": "Accelergy-style linear access-count model (Wu/Emer/Sze, ICCAD 2019); SCALE-Sim v3 uses the same layering",
    "access_counts": "SCALE-Sim 3.0.0 DETAILED_ACCESS_REPORT (Samajdar et al., ISPASS 2020)",
    "roofline": "Williams, Waterman, Patterson, Roofline, CACM 2009",
    "unmodeled": "NoC/interconnect energy, static/leakage energy, and real DRAM controller behavior are omitted",
}


@dataclass(frozen=True)
class EnergyBreakdown:
    e_compute_pj: float
    e_sram_pj: float
    e_dram_pj: float
    e_total_pj: float
    e_total_uj: float
    dram_energy_fraction: float


def energy_estimate(
    macs: int,
    sram_accesses: int,
    dram_accesses: int,
    precision: str = "int8",
) -> EnergyBreakdown:
    """Dynamic-access energy from real SCALE-Sim counts and sourced constants.

    Access counts are in elements; multiply by bytes/element for the movement
    terms. Reuse is already baked into SCALE-Sim's counts, so we multiply raw
    counts directly and do not re-apply a reuse factor.
    """
    b = BYTES_PER_ELEMENT[precision]
    e_compute = macs * E_MAC_PJ[precision]
    e_sram = sram_accesses * b * E_SRAM_PJ_PER_BYTE
    e_dram = dram_accesses * b * E_DRAM_PJ_PER_BYTE
    e_total = e_compute + e_sram + e_dram
    return EnergyBreakdown(
        e_compute_pj=round(e_compute, 1),
        e_sram_pj=round(e_sram, 1),
        e_dram_pj=round(e_dram, 1),
        e_total_pj=round(e_total, 1),
        e_total_uj=round(e_total / 1e6, 4),
        dram_energy_fraction=round(e_dram / e_total, 4) if e_total else 0.0,
    )


@dataclass(frozen=True)
class Roofline:
    operational_intensity_flop_per_byte: float
    ridge_point_flop_per_byte: float
    bound: str  # "memory" or "compute"
    peak_gflops: float
    attainable_gflops: float
    achieved_gflops: float


def roofline(
    macs: int,
    dram_accesses: int,
    pe_count: int,
    total_cycles: int,
    clock_mhz: int,
    dram_bandwidth_words_per_cycle: int,
    precision: str = "int8",
) -> Roofline:
    """Classify a candidate as compute- or memory-bound (Williams et al., 2009).

    OI = FLOPs / off-chip bytes. Ridge = peak compute / peak DRAM bandwidth. A
    A config whose OI sits left of the ridge has analytic memory-pressure risk.
    This classification does not explain SCALE-Sim cycles or utilization because
    the lab configuration does not model bandwidth stalls.
    """
    b = BYTES_PER_ELEMENT[precision]
    flops = 2 * macs
    dram_bytes = dram_accesses * b
    clock_hz = clock_mhz * 1e6
    peak_flops = 2 * pe_count * clock_hz  # MACs/cycle -> FLOP/s
    peak_bw_bytes_s = dram_bandwidth_words_per_cycle * b * clock_hz
    oi = flops / dram_bytes if dram_bytes else float("inf")
    ridge = peak_flops / peak_bw_bytes_s if peak_bw_bytes_s else float("inf")
    attainable = min(peak_flops, oi * peak_bw_bytes_s)
    achieved = flops / (total_cycles / clock_hz) if total_cycles else 0.0
    return Roofline(
        operational_intensity_flop_per_byte=round(oi, 2),
        ridge_point_flop_per_byte=round(ridge, 2),
        bound="memory" if oi < ridge else "compute",
        peak_gflops=round(peak_flops / 1e9, 2),
        attainable_gflops=round(attainable / 1e9, 2),
        achieved_gflops=round(achieved / 1e9, 2),
    )


def derived_metrics(
    macs: int,
    total_cycles: int,
    clock_mhz: int,
    energy: EnergyBreakdown,
    pe_count: int,
    sram_kb: int,
    stall_cycles: float,
    precision: str = "int8",
) -> dict:
    """EDP, ED2P, energy efficiency, area, and area efficiency once E and T exist."""
    clock_hz = clock_mhz * 1e6
    seconds = total_cycles / clock_hz
    ops = 2 * macs
    e_joules = energy.e_total_pj * 1e-12
    tops = (ops / seconds) / 1e12 if seconds else 0.0
    area_mm2 = (
        pe_count * AREA_PER_PE_UM2[precision]
    ) / 1e6 + sram_kb * AREA_PER_SRAM_KB_MM2
    return {
        "latency_us": round(seconds * 1e6, 3),
        "edp_uj_us": round(energy.e_total_uj * seconds * 1e6, 4),
        "ed2p": round(energy.e_total_uj * (seconds * 1e6) ** 2, 4),
        "tops": round(tops, 4),
        "tops_per_watt": (
            round(tops / (e_joules / seconds), 3) if seconds and e_joules else 0.0
        ),
        "area_mm2": round(area_mm2, 4),
        "tops_per_mm2": round(tops / area_mm2, 4) if area_mm2 else 0.0,
        "stall_fraction": (
            round(stall_cycles / total_cycles, 4) if total_cycles else 0.0
        ),
    }


def estimate_candidate(metrics: dict, candidate, precision: str = "int8") -> dict:
    """Assemble the full first-order estimate block for one candidate.

    `metrics` is the parsed SCALE-Sim report dict; `candidate` is a Candidate.
    """
    energy = energy_estimate(
        macs=metrics["workload_macs"],
        sram_accesses=metrics["sram_accesses"],
        dram_accesses=metrics["dram_accesses"],
        precision=precision,
    )
    rl = roofline(
        macs=metrics["workload_macs"],
        dram_accesses=metrics["dram_accesses"],
        pe_count=candidate.pe_count,
        total_cycles=metrics["total_cycles"],
        clock_mhz=candidate.clock_mhz,
        dram_bandwidth_words_per_cycle=candidate.dram_bandwidth_words_per_cycle,
        precision=precision,
    )
    derived = derived_metrics(
        macs=metrics["workload_macs"],
        total_cycles=metrics["total_cycles"],
        clock_mhz=candidate.clock_mhz,
        energy=energy,
        pe_count=candidate.pe_count,
        sram_kb=candidate.sram_kb,
        stall_cycles=metrics["stall_cycles"],
        precision=precision,
    )
    return {
        "precision": precision,
        "energy": energy.__dict__,
        "roofline": rl.__dict__,
        "derived": derived,
        "sources": ESTIMATE_SOURCES,
    }
