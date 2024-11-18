from flask import Flask, jsonify, request
from Agentes import WealthModel

app = Flask(__name__)

parameters = {
    'robotCubo_agents': 1,
    'robotWarrior_agents': 1,
    'robotPelota_agents': 1,
    'robotDino_agents': 1,
    'robotCarro_agents': 1,
    'steps': 1500,
}

try:
    model = WealthModel(parameters)
    model.setup()
    print("Se inicializó el modelo.")
except Exception as e:
    print(f"Error al intentar inicializar el modelo: {e}")
    model = None


@app.route('/setup', methods=['GET'])
def setup():
    """
    Información inicial (spawn) para la simulación.
    """
    try:
        if model is None:
            return jsonify({"error": "El modelo no fue inicializado."}), 400

        grid_size = {"rows": 20, "cols": 20}

        objects = [
            {"type": model.objTypeList[idx], "x": coord[0], "y": coord[1]}
            for idx, coord in enumerate(model.objCoorList)
        ]

        robots = [
            {
                "id": idx,
                "type": idx,
                "position": {"x": coord[0], "y": coord[1]},
                "state": "idle",
                "done": False,
                "recorded_objects_handled": 0,
                "recorded_movements_made": 0,
                "recorded_steps_idle": 0,
                "recorded_avoided_collisions": 0,
                "recorded_utility": 0,
                "board": [],
                "lastGoAround": None,
                "currentIdles": 0,
                "path": [0, 0],
                "myself": {
                    "has_id": idx,
                    "has_state": {"state_value": 2}
                },
                "targetObjectType": None,
                "pathEnd": None,
                "nextTile": None,
                "myAvailableObjectsCoords": model.objCoorList,
                "myAvailableObjectsType": model.objTypeList,
                "currentStack": None,
                "stackAmount": None,
                "actions": [
                    "setTarget", "pickUp", "stack", "setNextHorTile",
                    "setNextVerticalTile", "goAroundHorizontal",
                    "goAroundVertical", "moveTo", "idle", "thinking"
                ],
                "rules": [
                    "rule_canSetTarget", "rule_canPick", "rule_canStack",
                    "rule_nextHor", "rule_nextVer", "rule_goAroundHorizontal",
                    "rule_goAroundVertical", "rule_canMove", "rule_idle"
                ]
            }
            for idx, coord in enumerate(model.robotList)
        ]

        robotList = [{"x": x, "y": y} for x, y in model.robotList]
        stacks = [{"x": x, "y": y} for x, y in model.stackList]

        robotActions = {
            "robotCubo": {
                "actions": model.robotCuboActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord else None
                    for coord in model.robotCuboActCoords
                ]
            },
            "robotWarrior": {
                "actions": model.robotWarriorActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord else None
                    for coord in model.robotWarriorActCoords
                ]
            },
            "robotPelota": {
                "actions": model.robotPelotaActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord else None
                    for coord in model.robotPelotaActCoords
                ]
            },
            "robotDino": {
                "actions": model.robotDinoActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord else None
                    for coord in model.robotDinoActCoords
                ]
            },
            "robotCarro": {
                "actions": model.robotCarroActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord else None
                    for coord in model.robotCarroActCoords
                ]
            }
        }

        return jsonify({
            "gridSize": grid_size,
            "boardTiles": model.boardTiles,
            "objects": objects,
            "robots": robots,
            "robotList": robotList,
            "stacks": stacks,
            "robotActions": robotActions
        }), 200

    except Exception as e:
        print(f"Error en el endpoint the /setup: {e}")
        return jsonify({"error": "Error de servidor"}), 500


@app.route('/results', methods=['GET'])
def results():
    """
    Corre toda la simulación y devuelve los resultados de la corrida.
    """
    try:
        if model is None:
            return jsonify({"error": "El modelo no fue inicializado."}), 400
        
        model.run()

        robots = []
        for idx, agent in enumerate(
            model.robotCubo_agents + model.robotWarrior_agents +
            model.robotPelota_agents + model.robotDino_agents +
            model.robotCarro_agents
        ):
            robots.append({
                "id": idx,
                "type": agent.robotID,
                "final_position": {"x": agent.position[0], "y": agent.position[1]},
                "final_state": agent.myself.has_state.state_value,
                "done": agent.done,
                "recorded_objects_handled": agent.recorded_objects_handled,
                "recorded_movements_made": agent.recorded_movements_made,
                "recorded_steps_idle": agent.recorded_steps_idle,
                "recorded_avoided_collisions": agent.recorded_avoided_collisions,
                "recorded_utility": agent.recorded_utility,
            })

        robotActions = {
            "robotCubo": {
                "actions": model.robotCuboActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord is not None else None
                    for coord in model.robotCuboActCoords
                ]
            },
            "robotWarrior": {
                "actions": model.robotWarriorActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord is not None else None
                    for coord in model.robotWarriorActCoords
                ]
            },
            "robotPelota": {
                "actions": model.robotPelotaActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord is not None else None
                    for coord in model.robotPelotaActCoords
                ]
            },
            "robotDino": {
                "actions": model.robotDinoActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord is not None else None
                    for coord in model.robotDinoActCoords
                ]
            },
            "robotCarro": {
                "actions": model.robotCarroActions,
                "actionCoords": [
                    {"x": coord[0], "y": coord[1]} if coord is not None else None
                    for coord in model.robotCarroActCoords
                ]
            }
        }

        environment = {
            "objCoorList": [{"x": x, "y": y} for x, y in model.objCoorList],
            "objTypeList": model.objTypeList,
            "robotList": [{"x": x, "y": y} for x, y in model.robotList],
            "stackList": [{"x": x, "y": y} for x, y in model.stackList],
        }

        results_data = {
            "environment": environment,
            "robots": robots,
            "robotActions": robotActions
        }

        with open("results.json", "w") as f:
            import json
            json.dump(results_data, f)

        return jsonify(results_data), 200

    except Exception as e:
        print(f"Error en el endpoint de /results: {e}")
        return jsonify({"error": "Error de servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)