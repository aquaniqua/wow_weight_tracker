# Classic-like curve control points (cumulative % of total XP)
GAMMA = 1

level_breakpoints = [
    (1, 0.0),
    (10, 4.0),
    (20, 16.1),
    (30, 33.7),
    (40, 55.0),
    (50, 78.4),
    (60, 100.0),
]

# Strict RXP-style route (no overlaps)
# Half-open [start, end) for all but last which is [start, end]
route_steps = [
    ("northshire",                    1,  6),
    ("elwynn",                        6, 12),
    ("loch_modan",                   12, 16),
    ("westfall",                     16, 18),
    ("redridge",                     19, 20),
    ("deadmines",                    20, 21), 
    ("wetlands",                     21, 25),
    ("hillsbrad_foothills",          25, 28),
    ("duskwood",                     28, 32),
    ("stranglethorn_north",          32, 36), # added
    ("shimmering_flats",             36, 38),
    ("desolace",                     38, 39),
    ("stranglethorn_south",          39, 41), # added
    ("tanaris",                      41, 45),
    ("zulfarrak",                    45, 48), # added
    ("feralas",                      48, 50),
    ("searing_gorge",                50, 53),
    ("felwood",                      53, 55), # added
    ("ungoro",                       55, 58),
    ("eastern_plaguelands",          58, 60),
]

def clamp(x, lo, hi):
    """Clamp value between lo and hi."""
    return max(lo, min(hi, x))

def wow_curve_map_smooth(linear_percentage, gamma=GAMMA):
    """Maps linear 0..100 to Classic-feel 0..100 with a power curve.
    gamma>1 => faster early progress visually (Classic vibe)."""
    x = clamp(linear_percentage, 0.0, 100.0) / 100.0
    y = x ** (1.0 / gamma)
    return y * 100.0

def percent_to_level(classic_percent):
    """Approximate level (float) for a Classic cumulative % using control points."""
    cp = clamp(classic_percent, 0.0, 100.0)
    pts = level_breakpoints
    for i in range(len(pts) - 1):
        L0, P0 = pts[i]
        L1, P1 = pts[i + 1]
        if P0 <= cp <= P1:
            t = 0 if P1 == P0 else (cp - P0) / (P1 - P0)
            return L0 + t * (L1 - L0)
    return 60.0

def pick_step_for_level(level):
    """Return (index, zone, L0, L1) for a given level using half-open brackets."""
    n = len(route_steps)
    for i, (zone, L0, L1) in enumerate(route_steps):
        if i < n - 1:
            if L0 <= level < L1:
                return i, zone, L0, L1
        else:
            if L0 <= level <= L1:  # last is closed interval
                return i, zone, L0, L1
    # Fallback to last step
    i = n - 1
    zone, L0, L1 = route_steps[i]
    return i, zone, L0, L1

def pick_zone_for_level(level):
    """Return only the zone name (helper that uses pick_step_for_level)."""
    _, zone, _, _ = pick_step_for_level(level)
    return zone

