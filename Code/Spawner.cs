using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking; // Para realizar solicitudes HTTP

public class ResourceSpawnerFromJSON : MonoBehaviour
{
    [Header("Prefabs de Objetos")]
    public GameObject cuboRubikPrefab;
    public GameObject carroPrefab;
    public GameObject pelotaPrefab;
    public GameObject soldadoPrefab;
    public GameObject dinosaurioPrefab;

    [Header("Prefabs de Agentes")]
    public GameObject agentePrefab1;
    public GameObject agentePrefab2;
    public GameObject agentePrefab3;
    public GameObject agentePrefab4;
    public GameObject agentePrefab5;

    private Dictionary<int, GameObject> objectPrefabs;
    private Dictionary<int, GameObject> agentPrefabs;

    private BoardData boardData;
    private ActionsData actionsData;

    private List<GameObject> robotsInScene = new List<GameObject>();
    private bool actionsInProgress = false;

    private Dictionary<int, RobotActionData> robotActionsDict;
    private Dictionary<int, int> robotActionIndices = new Dictionary<int, int>();

    private void Start()
    {
        InitializePrefabs();
        StartCoroutine(LoadDataFromEndpoints());
    }

    void InitializePrefabs()
    {
        objectPrefabs = new Dictionary<int, GameObject>()
        {
            { 0, cuboRubikPrefab },
            { 1, soldadoPrefab },
            { 2, pelotaPrefab },
            { 3, dinosaurioPrefab },
            { 4, carroPrefab }
        };

        agentPrefabs = new Dictionary<int, GameObject>()
        {
            { 0, agentePrefab1 },
            { 1, agentePrefab2 },
            { 2, agentePrefab3 },
            { 3, agentePrefab4 },
            { 4, agentePrefab5 }
        };
    }

    IEnumerator LoadDataFromEndpoints()
    {
        string setupUrl = "http://localhost:5001/setup";
        string actionsUrl = "http://localhost:5001/results";

        // Solicitar datos de configuración inicial
        UnityWebRequest setupRequest = UnityWebRequest.Get(setupUrl);
        yield return setupRequest.SendWebRequest();

        if (setupRequest.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Error al cargar datos desde el endpoint de setup: " + setupRequest.error);
            yield break;
        }

        boardData = JsonUtility.FromJson<BoardData>(setupRequest.downloadHandler.text);

        // Solicitar datos de acciones
        UnityWebRequest actionsRequest = UnityWebRequest.Get(actionsUrl);
        yield return actionsRequest.SendWebRequest();

        if (actionsRequest.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Error al cargar datos desde el endpoint de acciones: " + actionsRequest.error);
            yield break;
        }

        actionsData = JsonUtility.FromJson<ActionsData>(actionsRequest.downloadHandler.text);

        // Si los datos son válidos, inicializar el entorno
        if (boardData != null && actionsData != null)
        {
            SpawnObjects();
            SpawnRobots();

            robotActionsDict = new Dictionary<int, RobotActionData>
            {
                { 0, actionsData.robotActions.robotCarro },
                { 1, actionsData.robotActions.robotCubo },
                { 2, actionsData.robotActions.robotDino },
                { 3, actionsData.robotActions.robotPelota },
                { 4, actionsData.robotActions.robotWarrior }
            };

            InitializeRobotActionIndices();
            StartCoroutine(ExecuteRobotActions());
        }
        else
        {
            Debug.LogError("No se pudieron cargar los datos necesarios desde los endpoints.");
        }
    }

    void SpawnObjects()
    {
        // Spawn de objetos basado en boardData.objects
        foreach (var obj in boardData.objects)
        {
            if (objectPrefabs.ContainsKey(obj.type))
            {
                Vector3 position = ConvertToUnityCoordinates(obj.x, obj.y);
                position.y += 0.08f; 
                Instantiate(objectPrefabs[obj.type], position, objectPrefabs[obj.type].transform.rotation);
                Debug.Log($"Objeto tipo {obj.type} instanciado en posición {position}");
            }
            else
            {
                Debug.LogWarning($"Tipo de objeto {obj.type} no definido en el diccionario de prefabs.");
            }
        }
    }

    void SpawnRobots()
    {
        // Suponiendo que los robots están en boardData.robots
        foreach (var robotData in boardData.robots)
        {
            if (agentPrefabs.ContainsKey(robotData.type))
            {
                Vector3 position = ConvertToUnityCoordinates(robotData.position.x, robotData.position.y);
                GameObject robot = Instantiate(agentPrefabs[robotData.type], position, Quaternion.identity);
                robot.name = "Robot_" + robotData.id;
                robotsInScene.Add(robot);
                Debug.Log($"Robot ID {robotData.id} de tipo {robotData.type} instanciado en posición {position}");
            }
            else
            {
                Debug.LogWarning($"Tipo de robot {robotData.type} no definido en el diccionario de prefabs.");
            }
        }
    }

    void InitializeRobotActionIndices()
    {
        foreach (var robotKey in robotActionsDict.Keys)
        {
            robotActionIndices[robotKey] = 0; // Inicializar todos los índices en 0
        }
    }

    IEnumerator ExecuteRobotActions()
    {
        // Mapeo de robots por nombre para fácil acceso
        Dictionary<string, GameObject> robotGameObjects = new Dictionary<string, GameObject>();
        foreach (var robot in robotsInScene)
        {
            robotGameObjects[robot.name] = robot;
        }

        actionsInProgress = true;

        while (actionsInProgress)
        {
            bool anyActionExecuted = false;

            // Ejecutar la acción actual para cada robot
            foreach (var robotIndex in robotActionsDict.Keys)
            {
                RobotActionData robotActionData = robotActionsDict[robotIndex];

                int actionIndex = robotActionIndices[robotIndex];

                if (actionIndex < robotActionData.actions.Count)
                {
                    string action = robotActionData.actions[actionIndex];
                    CoordinateData coord = null;

                    if (robotActionData.actionCoords != null && actionIndex < robotActionData.actionCoords.Count)
                    {
                        coord = robotActionData.actionCoords[actionIndex];
                    }

                    ExecuteActionForRobot(robotIndex, action, coord, robotGameObjects);

                    robotActionIndices[robotIndex]++;
                    anyActionExecuted = true;
                }
            }

            if (!anyActionExecuted)
            {
                actionsInProgress = false; // No quedan más acciones por ejecutar
            }

            // Esperar un momento antes de pasar a la siguiente acción
            yield return new WaitForSeconds(1f); // Puedes ajustar el tiempo según tus necesidades
        }
    }

    void ExecuteActionForRobot(int robotIndex, string action, CoordinateData coord, Dictionary<string, GameObject> robotGameObjects)
    {
        // Encuentra el robot en la escena
        string robotName = "Robot_" + robotIndex;
        if (robotGameObjects.TryGetValue(robotName, out GameObject robot))
        {
            switch (action)
            {
                case "move":
                    if (coord != null)
                    {
                        // Obtener el componente MoverObjeto y establecer el objetivo
                        MoverObjeto moverObjeto = robot.GetComponent<MoverObjeto>();
                        if (moverObjeto != null)
                        {
                            // Crear un Vector2 con las coordenadas del tablero
                            Vector2 objetivoGrid = new Vector2(coord.x, coord.y);
                            moverObjeto.MoverHacia(objetivoGrid);
                            Debug.Log($"Robot {robotIndex} se mueve a ({coord.x}, {coord.y})");
                        }
                        else
                        {
                            Debug.LogWarning($"El robot {robotIndex} no tiene el componente MoverObjeto.");
                        }
                    }
                    else
                    {
                        Debug.LogWarning($"Coordenadas no disponibles para el movimiento del robot {robotIndex}.");
                    }
                    break;

                case "pickup":
                    // Obtener el componente RecogerYColocar y ejecutar la recogida
                    RecogerYColocar recogerYColocar = robot.GetComponent<RecogerYColocar>();
                    if (recogerYColocar != null)
                    {
                        recogerYColocar.IniciarRecogida();
                        Debug.Log($"Robot {robotIndex} recoge un objeto");
                    }
                    else
                    {
                        Debug.LogWarning($"El robot {robotIndex} no tiene el componente RecogerYColocar.");
                    }
                    break;

                case "stack":
                    // Obtener el componente SoltarYOrdenar y ejecutar el apilamiento
                    SoltarYOrdenar soltarYOrdenar = robot.GetComponent<SoltarYOrdenar>();
                    if (soltarYOrdenar != null)
                    {
                        // Debes definir las coordenadas donde se realizará el apilamiento
                        // Por ejemplo, podrías usar coord si es relevante
                        float xDestino = coord != null ? coord.x : robot.transform.position.x;
                        float zDestino = coord != null ? coord.y : robot.transform.position.z;

                        soltarYOrdenar.IniciarApilamiento(xDestino, zDestino, 1);
                        Debug.Log($"Robot {robotIndex} apila un objeto en ({xDestino}, {zDestino})");
                    }
                    else
                    {
                        Debug.LogWarning($"El robot {robotIndex} no tiene el componente SoltarYOrdenar.");
                    }
                    break;

                default:
                    // Acciones "thinking", "idle", etc., no requieren movimiento
                    Debug.Log($"Robot {robotIndex} ejecuta acción '{action}'");
                    break;
            }
        }
        else
        {
            Debug.LogWarning($"No se encontró el robot con nombre '{robotName}' en la escena.");
        }
    }

    Vector3 ConvertToUnityCoordinates(float x, float y)
    {
        return new Vector3(x + 0.5f, 0f, y + 0.5f);
    }
}

// Clases serializables
[System.Serializable]
public class BoardData
{
    public List<List<List<int>>> boardTiles;
    public GridSize gridSize;
    public List<GameObjectData> objects;
    public List<RobotData> robots;
    public List<StackData> stacks;
}

[System.Serializable]
public class GridSize
{
    public int cols;
    public int rows;
}

[System.Serializable]
public class GameObjectData
{
    public int type;
    public float x;
    public float y;
}

[System.Serializable]
public class RobotData
{
    public int id;
    public int type;
    public PositionData position;
    public string state;
}

[System.Serializable]
public class PositionData
{
    public float x;
    public float y;
}

[System.Serializable]
public class StackData
{
    public int x;
    public int y;
}

// Clases para data2.json
[System.Serializable]
public class ActionsData
{
    public EnvironmentData environment;
    public RobotActionsData robotActions;
}

[System.Serializable]
public class EnvironmentData
{
    public List<CoordinateData> objCoorList;
    public List<int> objTypeList;
    public List<CoordinateData> robotList;
    public List<CoordinateData> stackList;
}

[System.Serializable]
public class RobotActionsData
{
    public RobotActionData robotCarro;
    public RobotActionData robotCubo;
    public RobotActionData robotDino;
    public RobotActionData robotPelota;
    public RobotActionData robotWarrior;
}

[System.Serializable]
public class RobotActionData
{
    public List<CoordinateData> actionCoords;
    public List<string> actions;
}

[System.Serializable]
public class CoordinateData
{
    public float x;
    public float y;
}

