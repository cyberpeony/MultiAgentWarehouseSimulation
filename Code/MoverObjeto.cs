using UnityEngine;

public class MoverObjeto : MonoBehaviour
{
    public Vector2 objetivo;  // Coordenada destino en el tablero (x, y)
    public float velocidad = 5f;  // Velocidad de movimiento

    private Vector3 objetivoUnity; // Coordenada destino en Unity (x, y, z)
    private bool enMovimiento = false;

    private void Update()
    {
        if (enMovimiento)
        {
            // Posición actual del objeto
            Vector3 posicionActual = transform.position;

            // Calculamos la posición objetivo en Unity (manteniendo la altura actual)
            Vector3 posicionObjetivo = new Vector3(objetivoUnity.x, posicionActual.y, objetivoUnity.z);

            // Mover el objeto hacia el objetivo con velocidad fija
            if (Vector3.Distance(posicionActual, posicionObjetivo) > 0.1f)
            {
                // Calcular la dirección hacia el objetivo y mover el objeto
                Vector3 direccion = (posicionObjetivo - posicionActual).normalized;
                transform.Translate(direccion * velocidad * Time.deltaTime, Space.World);
            }
            else
            {
                // Detener el movimiento al llegar cerca del objetivo
                transform.position = new Vector3(objetivoUnity.x, posicionActual.y, objetivoUnity.z);
                enMovimiento = false;
                // Puedes notificar que el robot ha llegado a su destino si es necesario
                Debug.Log($"Robot {gameObject.name} ha llegado a la posición ({objetivoUnity.x}, {objetivoUnity.z})");
            }
        }
    }

    // Método público para establecer el objetivo y comenzar el movimiento
    public void MoverHacia(Vector2 nuevaPosicion)
    {
        objetivo = nuevaPosicion;
        objetivoUnity = ConvertirCoordenadasAGrilla(objetivo.x, objetivo.y);
        enMovimiento = true;
    }

    // Método para convertir las coordenadas del tablero (x, y) a coordenadas de Unity (x, y, z)
    private Vector3 ConvertirCoordenadasAGrilla(float x, float y)
    {
        // Mapear y del tablero a z en Unity, y ajustar con 0.5 para centrar en las casillas
        return new Vector3(x + 0.5f, transform.position.y, y + 0.5f);
    }
}
