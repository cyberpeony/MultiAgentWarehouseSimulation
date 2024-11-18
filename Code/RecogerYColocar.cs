using UnityEngine;
using System.Collections.Generic;

public class RecogerYColocar : MonoBehaviour
{
    [Header("Configuración de Recogida")]
    public string etiquetaObjeto = "ObjetoRecogible"; // Etiqueta del objeto a recoger

    [Header("Configuración de Detección Angular")]
    public float radioDeteccion = 4.0f; // Radio de detección alrededor del robot
    public float anguloDeteccion = 45.0f; // Ángulo de detección en cada dirección

    [Header("Configuración de Movimiento")]
    public float velocidadMovimiento = 2.0f; // Velocidad de movimiento del objeto
    public Transform posicionEncima; // Posición encima del robot donde se colocará el objeto

    [Header("Referencias")]
    public SoltarYOrdenar scriptSoltarYOrdenar; // Referencia al script SoltarYOrdenar

    private GameObject objetoARecoger; // Referencia al objeto a recoger
    private bool moviendoObjeto = false; // Bandera para controlar si se está moviendo el objeto
    private Vector3[] direccionesCardinales;
    private bool robotOcupado = false; // Indica si el robot está ocupado

    private Dictionary<Vector2, int> conteoDePilas = new Dictionary<Vector2, int>();

    void Start()
    {
        // Inicializar las direcciones cardinales relativas al robot
        direccionesCardinales = new Vector3[]
        {
            transform.forward,          // Adelante
            -transform.forward,         // Atrás
            transform.right,            // Derecha
            -transform.right            // Izquierda
        };
    }

    void Update()
    {
        // Comando para soltar el objeto al presionar la tecla Q
        if (Input.GetKeyDown(KeyCode.Q))
        {
            // Coordenadas X y Z donde se soltará el objeto
            float xDestino = -8.5f; // Ajusta este valor según tus necesidades
            float zDestino = -16.5f; // Ajusta este valor según tus necesidades
            int numeroDeObjetosEnPila = ObtenerNumeroDeObjetosEnPila(xDestino, zDestino);

            if (scriptSoltarYOrdenar != null)
            {
                scriptSoltarYOrdenar.SoltarObjetoEnPosicion(xDestino, zDestino, numeroDeObjetosEnPila);
            }
        }

        if (!moviendoObjeto)
        {
            DetectarYRecogerObjeto();
        }
        else
        {
            MoverObjeto();
        }
    }

    public void RobotDisponible(float x, float z)
    {
        robotOcupado = false;
        objetoARecoger = null;
        ActualizarNumeroDeObjetosEnPila(x, z);
        Debug.Log("El robot ahora está disponible para recoger otro objeto.");
    }

    int ObtenerNumeroDeObjetosEnPila(float x, float z)
    {
        Vector2 coordenada = new Vector2(x, z);
        int conteo = 0;
        conteoDePilas.TryGetValue(coordenada, out conteo);
        return conteo;
    }

    void ActualizarNumeroDeObjetosEnPila(float x, float z)
    {
        Vector2 coordenada = new Vector2(x, z);
        int conteo = 0;
        conteoDePilas.TryGetValue(coordenada, out conteo);
        conteo++;
        conteoDePilas[coordenada] = conteo;
    }

    void DetectarYRecogerObjeto()
    {
        // Verificar si el robot está ocupado
        if (robotOcupado)
        {
            return; // No hacer nada si el robot está ocupado
        }

        Collider[] objetosCercanos = Physics.OverlapSphere(transform.position, radioDeteccion);

        foreach (Collider col in objetosCercanos)
        {
            if (col.CompareTag(etiquetaObjeto))
            {
                // Calcular la dirección hacia el objeto
                Vector3 direccionAlObjeto = col.transform.position - transform.position;
                direccionAlObjeto.y = 0; // Ignorar la diferencia en altura

                // Iterar sobre las direcciones cardinales
                foreach (Vector3 direccion in direccionesCardinales)
                {
                    // Calcular el ángulo entre la dirección cardinal y el objeto
                    float angulo = Vector3.Angle(direccion, direccionAlObjeto);

                    if (angulo < anguloDeteccion / 2)
                    {
                        // Objeto dentro del ángulo de detección para esta dirección
                        objetoARecoger = col.gameObject;
                        moviendoObjeto = true;

                        // Desactivar la física del objeto mientras se mueve
                        if (objetoARecoger.GetComponent<Rigidbody>())
                        {
                            objetoARecoger.GetComponent<Rigidbody>().isKinematic = true;
                        }

                        Debug.Log("Objeto recogible detectado: " + objetoARecoger.name);
                        return; // Salir después de encontrar un objeto
                    }
                }
            }
        }
    }

    void MoverObjeto()
    {
        if (objetoARecoger != null)
        {
            // Mover el objeto hacia la posición encima del robot
            float paso = velocidadMovimiento * Time.deltaTime;
            objetoARecoger.transform.position = Vector3.MoveTowards(objetoARecoger.transform.position, posicionEncima.position, paso);

            // Comprobar si el objeto ha llegado a la posición
            if (Vector3.Distance(objetoARecoger.transform.position, posicionEncima.position) < 0.01f)
            {
                moviendoObjeto = false;

                // Hacer que el objeto sea hijo de la posición encima del robot
                objetoARecoger.transform.parent = posicionEncima;

                // Reactivar la física si es necesario
                if (objetoARecoger.GetComponent<Rigidbody>())
                {
                    objetoARecoger.GetComponent<Rigidbody>().isKinematic = false;
                }

                Debug.Log("Objeto colocado encima del robot.");

                // Asignar el objeto al script SoltarYOrdenar
                if (scriptSoltarYOrdenar != null)
                {
                    scriptSoltarYOrdenar.AsignarObjeto(objetoARecoger);
                }

                // Establecer robotOcupado en true
                robotOcupado = true;
            }
        }
    }
    // Método público para iniciar la acción de recoger
    public void IniciarRecogida()
    {
        // Puedes implementar lógica adicional si es necesario
        DetectarYRecogerObjeto();
    }

}
