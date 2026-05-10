import json

import traci


OUTPUT_FILE = "simulation_state_data.json"
SIMULATION_STEPS = 1000
USE_GUI = False


def unique_lanes(lanes):
    """Traffic lights can report duplicate lanes, so keep first-seen order."""
    seen = set()
    result = []

    for lane in lanes:
        if lane not in seen:
            seen.add(lane)
            result.append(lane)

    return result


def collect_lane_state(lane_id):
    return {
        "lane_id": lane_id,
        "queue_length": traci.lane.getLastStepHaltingNumber(lane_id),
        "vehicle_count": traci.lane.getLastStepVehicleNumber(lane_id),
        "waiting_time": traci.lane.getWaitingTime(lane_id),
        "average_speed": traci.lane.getLastStepMeanSpeed(lane_id),
    }


def collect_traffic_light_state(tls_id):
    return {
        "traffic_light_id": tls_id,
        "current_phase": traci.trafficlight.getPhase(tls_id),
        "current_phase_state": traci.trafficlight.getRedYellowGreenState(tls_id),
    }


sumo_binary = "sumo-gui" if USE_GUI else "sumo"
sumo_cmd = [sumo_binary, "-c", "simulation.sumocfg"]
state_data = []

traci.start(sumo_cmd)

try:
    for step in range(SIMULATION_STEPS):
        traci.simulationStep()

        tls_list = traci.trafficlight.getIDList()

        if len(tls_list) == 0:
            print("No traffic lights found!")
            continue

        step_record = {
            "step": step,
            "time": traci.simulation.getTime(),
            "traffic_lights": [],
        }

        for tls_id in tls_list:
            lanes = unique_lanes(traci.trafficlight.getControlledLanes(tls_id))
            traffic_light_state = collect_traffic_light_state(tls_id)
            traffic_light_state["lanes"] = [
                collect_lane_state(lane_id)
                for lane_id in lanes
            ]

            step_record["traffic_lights"].append(traffic_light_state)

        state_data.append(step_record)

finally:
    traci.close()

with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
    json.dump(
        {
            "simulation": {
                "config": "simulation.sumocfg",
                "steps": SIMULATION_STEPS,
            },
            "records": state_data,
        },
        output_file,
        indent=2,
    )

print(f"Saved {len(state_data)} simulation records to {OUTPUT_FILE}")
