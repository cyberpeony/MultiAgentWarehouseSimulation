import json
import matplotlib.pyplot as plt

def plot_results(file_path="results.json"):

    """El results.json se crea automáticamente localmente cuando se corre el server 
    de flask (y por ende el modelo). Usando ese json se plotean las métricas de los robots."""
    with open(file_path, "r") as f: 
        data = json.load(f)

    robots = data["robots"]

    utilities = [robot["recorded_utility"] for robot in robots]
    movements = [robot["recorded_movements_made"] for robot in robots]
    stacks = [robot["recorded_objects_handled"] for robot in robots]
    idles = [robot["recorded_steps_idle"] for robot in robots]
    avoided_collisions = [robot["recorded_avoided_collisions"] for robot in robots]

    robot_labels = ["RobotCubo", "RobotWarrior", "RobotPelota", "RobotDino", "RobotCarro"]
    markers = ["o", "s", "^", "d", "*"]
    colors = ["red", "blue", "green", "purple", "orange"]
    x = range(len(robot_labels))

    # recorded utility
    for idx, label in enumerate(robot_labels):
        plt.plot(x[idx], utilities[idx], label=label, marker=markers[idx], color=colors[idx])
    plt.title('Utility of 5 Robots')
    plt.xlabel('Robot ID')
    plt.ylabel('Utility')
    plt.xticks(x, labels=[1, 2, 3, 4, 5])  
    plt.grid(True)
    plt.legend()
    plt.show()

    # recorded movements made
    for idx, label in enumerate(robot_labels):
        plt.plot(x[idx], movements[idx], label=label, marker=markers[idx], color=colors[idx])
    plt.title('Movements Made by 5 Robots')
    plt.xlabel('Robot ID')
    plt.ylabel('Movements')
    plt.xticks(x, labels=[1, 2, 3, 4, 5])  
    plt.grid(True)
    plt.legend()
    plt.show()

    # recorded objects handled
    for idx, label in enumerate(robot_labels):
        plt.plot(x[idx], stacks[idx], label=label, marker=markers[idx], color=colors[idx])
    plt.title('Stacks Made by 5 Robots')
    plt.xlabel('Robot ID')
    plt.ylabel('Stacks')
    plt.xticks(x, labels=[1, 2, 3, 4, 5])  
    plt.grid(True)
    plt.legend()
    plt.show()

    # recorded steps idle
    for idx, label in enumerate(robot_labels):
        plt.plot(x[idx], idles[idx], label=label, marker=markers[idx], color=colors[idx])
    plt.title('Idle Time of 5 Robots')
    plt.xlabel('Robot ID')
    plt.ylabel('Idle Time')
    plt.xticks(x, labels=[1, 2, 3, 4, 5])  
    plt.grid(True)
    plt.legend()
    plt.show()

    # recorded avoided collisions
    for idx, label in enumerate(robot_labels):
        plt.plot(x[idx], avoided_collisions[idx], label=label, marker=markers[idx], color=colors[idx])
    plt.title('Avoided Collisions by 5 Robots')
    plt.xlabel('Robot ID')
    plt.ylabel('Avoided Collisions')
    plt.xticks(x, labels=[1, 2, 3, 4, 5])  
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    plot_results("results.json")

