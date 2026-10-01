"""
Core logic for the TUFRater predictions. Contains all the functions needed.
Import what you need here. E.g.
    from core.py import load_model, predict_difficulty
"""

from pathlib import Path
import pandas as pd
import lightgbm as lgb

TIER_VALUES = {"P": 0, "G": 20, "U": 40}

MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "difficulty_model.txt"

FEATURE_COLUMNS = [
    "tilecount", "bpm", "twirl_count", "speed_change_count",
    "s_norm", "rt_score", "p_var",
]

# .adofai feature extraction

def extract_gameplay_features(level_json):
    settings = level_json.get("settings", {})
    angle_data = level_json.get("angleData", [])
    actions = level_json.get("actions", [])

    tile_count = len(angle_data)
    bpm = settings.get("bpm", 0)

    twirl_count = 0
    speed_change_count = 0
 
    for action in actions:
        event_type = action.get("eventType")
        if event_type == "Twirl":
            twirl_count += 1
        elif event_type == "SetSpeed":
            speed_change_count += 1

    _, s_norm = calculate_stamina_difficulty(level_json)
    _, _, rt_score = calculate_rhythm_tech(level_json)
    _, _, p_var = calculate_pattern_variety(level_json)

    return {
        "tilecount": tile_count,
        "bpm": bpm,
        "twirl_count": twirl_count,
        "speed_change_count": speed_change_count,
        "s_norm": s_norm,
        "rt_score": rt_score,
        "p_var": p_var,
    }
# Prediction process

def num_to_pgu(number):
    rounded = round(number)
    clamped = max(1, min(rounded, 60))

    if clamped <= 20:
        letter = "P"
        tier_number = clamped
    elif clamped <= 40:
        letter = "G"
        tier_number = clamped - 20
    elif clamped <= 60:
        letter = "U"
        tier_number = clamped - 40
    return f"{letter}{tier_number}"

# TODO STILL WORKING ON
def calculate_stamina_difficulty(level_json):
    settings = level_json.get("settings", {})
    angle_data = level_json.get("angleData", [])
    actions = level_json.get("actions", [])

    tile_count = len(angle_data)
    if tile_count == 0:
        return 0.0, 0.0

    bpm_changes = {}
    base_bpm = settings.get("bpm", 0) or 1

    for action in actions:
        if action.get("eventType") == "SetSpeed":
            tile = action.get("floor", 0)
            speed_type = action.get("speedType")
            if speed_type == "Bpm":
                bpm_changes[tile] = action.get("beatsPerMinute", base_bpm)
                base_bpm = bpm_changes[tile]
            elif speed_type == "Multiplier":
                multiplier = action.get("bpmMultiplier", 1)
                bpm_changes[tile] = base_bpm * multiplier

    bpm = settings.get("bpm", 0) or 1
    s_raw = 0

    for tile in range(tile_count):
        if tile in bpm_changes:
            bpm = bpm_changes[tile]
        s_raw += bpm

    s_norm = s_raw / tile_count
    return s_raw, s_norm

def calculate_rhythm_tech(level_json):
    settings = level_json.get("settings", {})
    angle_data = level_json.get("angleData", [])
    actions = level_json.get("actions", [])

    tile_count = len(angle_data)
    if tile_count < 2:
        return 0.0, 0.0, 0.0

    bpm_changes = {}
    base_bpm = settings.get("bpm", 0) or 1

    for action in actions:
        if action.get("eventType") == "SetSpeed":
            tile = action.get("floor", 0)
            speed_type = action.get("speedType")

            if speed_type == "Bpm":
                bpm_changes[tile] = action.get("beatsPerMinute", base_bpm)
                base_bpm = bpm_changes[tile]
            elif speed_type == "Multiplier":
                multiplier = action.get("bpmMultiplier", 1)
                bpm_changes[tile] = base_bpm * multiplier

    bpm = settings.get("bpm", 0) or 1
    current_time = 0
    times = [] # THE TIMINGS BETWEEN EACH TILE e.g. 0, 500, 1000 (ms)
    angles = [] # ANGLE NUMBERS e.g. 0, 180, 45
    
    for tile in range(tile_count):
        if tile in bpm_changes:
            bpm = bpm_changes[tile] # GRABS NEW BPM IF THE BPM CHANGES

        raw_angle = angle_data[tile] 
        if raw_angle == 999 or raw_angle is None: # SOME ANGLES DO A BREAK AND SPINS A FEW TIMES BEFORE GOING TO NEXT TILE SO SETS TO 180. the none is a protection against levels that contain "null" in angle data
            angle = 180
        else:
            angle = raw_angle
        times.append(current_time)
        angles.append(angle)

        current_time += 60000 / bpm

    time_intervals = [] # GAPS BETWEEN TIMINGS
    for i in range(1, len(times)):
        gap = times[i] - times[i - 1]
        time_intervals.append(gap)

    # add time_intervals then divide by amount of times for mean gap
    mean_time = sum(time_intervals) / len(time_intervals)

    variance_sum = 0
    for time_diff in time_intervals:
        variance_sum += (time_diff - mean_time) ** 2

    r_irr = variance_sum / len(time_intervals)

    angle_sharpness_sum = 0
    for i in range(1, len(angles)):
        time_diff = time_intervals[i - 1]
        if time_diff == 0:
            time_diff = 1

        sharpness = abs(180 - angles[i])
        angle_sharpness_sum += (1000.0 / time_diff) * sharpness
    g_tech = angle_sharpness_sum / tile_count
    rt_score = r_irr * g_tech
    
    return r_irr, g_tech, rt_score

def calculate_pattern_variety(level_json):
    angle_data = level_json.get("angleData", [])
    actions = level_json.get("actions", [])
    
    tile_count = len(angle_data)

    if tile_count == 0:
        return 0.0, 0.0, 0.0

    twirl_positions = []
    for action in actions:
        if action.get("eventType") == "Twirl":
            twirl = action.get("floor", 0)
            twirl_positions.append(twirl)

    twirl_positions.sort()
    t_w = len(twirl_positions)

    d_twirl = t_w / tile_count

    if t_w < 2:
            return d_twirl, 0.0, 0.0

    gaps = []
    for i in range(1, len(twirl_positions)):
        gap = twirl_positions[i] - twirl_positions[i - 1]
        gaps.append(gap)

    mean_gap = sum(gaps) / len(gaps)

    variance_sum = 0
    for gap in gaps:
        variance_sum += (gap - mean_gap) ** 2

    v_twirl = variance_sum / len(gaps)
    p_var = d_twirl * v_twirl
    return d_twirl, v_twirl, p_var
    
def predict_difficulty(level_json, model):
    features = extract_gameplay_features(level_json)
    X_input = pd.DataFrame([features])[FEATURE_COLUMNS] 
    predicted_number = model.predict(X_input)[0]
    return num_to_pgu(predicted_number), predicted_number

# Model usage

def load_model(path=MODEL_PATH):
    return lgb.Booster(model_file=str(path))