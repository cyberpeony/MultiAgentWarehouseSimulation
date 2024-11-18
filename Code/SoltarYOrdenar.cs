using UnityEngine;
using System.Collections.Generic;

public class SoltarYOrdenar : MonoBehaviour
{
    public float alturaSoltar = 0.5f; // Altura base a la que se soltará el objeto (eje Y en Unity)
    public float velocidadMovimiento = 2.0f; // Velocidad de movimiento del objeto al ser soltado
    public RecogerYColocar scriptRecogerYColocar; // Referencia al script RecogerYColocar

    private GameObject objetoSostenido; // Referencia al objeto que se está sosteniendo
    private Vector3 posicionDestino; // Posición donde se soltará el objeto
    private bool moviendoObjetoASoltar = false; // Bandera para controlar el movimiento al soltar
    private Dictionary<Vector2, float> alturasDeApilamiento = new Dictionary<Vector2, float>();

    void Update()
    {
        if (moviendoObjetoASoltar)
        {
            MoverObjetoASoltar();
        }
    }

    // Método para asignar el objeto que se sostendrá
    public void AsignarObjeto(GameObject objeto)
    {
        objetoSostenido = objeto;
        // Hacer que el objeto sea hijo de este GameObject (robot)
        objetoSostenido.transform.parent = transform;
    }

    // Método para soltar el objeto en las coordenadas X y Z (plano horizontal en Unity)
    public void SoltarObjetoEnPosicion(float x, float z, int numeroDeObjetosEnPila)
    {
        if (objetoSostenido != null)
        {
            // Desactivar la física temporalmente
            Rigidbody rb = objetoSostenido.GetComponent<Rigidbody>();
            if (rb)
            {
                rb.isKinematic = true;
            }

            // Desprender el objeto del robot
            objetoSostenido.transform.parent = null;

            // Calcular la altura de apilamiento
            float alturaBase = alturaSoltar;
            Vector2 coordenadaXZ = new Vector2(x, z);

            Renderer renderer = objetoSostenido.GetComponent<Renderer>();
            if (renderer == null)
            {
                // Intentar obtener el Renderer de los hijos
                renderer = objetoSostenido.GetComponentInChildren<Renderer>();
            }

            float alturaObjeto = 1.0f; // Altura predeterminada
            if (renderer != null)
            {
                alturaObjeto = renderer.bounds.size.y;
            }
            else
            {
                Debug.LogError("No se encontró un Renderer en objetoSostenido o sus hijos. Usando altura predeterminada.");
            }

            if (numeroDeObjetosEnPila > 0)
            {
                // Si ya hay objetos apilados, incrementamos la altura
                float alturaAnterior = 0f;
                alturasDeApilamiento.TryGetValue(coordenadaXZ, out alturaAnterior);

                alturaBase = alturaAnterior + alturaObjeto;
                // Actualizamos la altura en el diccionario
                alturasDeApilamiento[coordenadaXZ] = alturaBase;
            }
            else
            {
                // Si no hay objetos, reiniciamos la altura
                alturasDeApilamiento[coordenadaXZ] = alturaSoltar;
            }

            // Establecer la posición destino con la nueva altura
            posicionDestino = new Vector3(x, alturaBase, z);
            moviendoObjetoASoltar = true;

            Debug.Log("Iniciando movimiento para soltar objeto en la posición: " + posicionDestino);
        }
        else
        {
            Debug.LogWarning("No hay ningún objeto para soltar.");
        }
    }

    void MoverObjetoASoltar()
    {
        if (objetoSostenido != null)
        {
            // Mover el objeto hacia la posición destino
            float paso = velocidadMovimiento * Time.deltaTime;
            objetoSostenido.transform.position = Vector3.MoveTowards(objetoSostenido.transform.position, posicionDestino, paso);

            // Comprobar si el objeto ha llegado a la posición destino
            if (Vector3.Distance(objetoSostenido.transform.position, posicionDestino) < 0.01f)
            {
                moviendoObjetoASoltar = false;

                // Reactivar la física
                Rigidbody rb = objetoSostenido.GetComponent<Rigidbody>();
                if (rb)
                {
                    rb.isKinematic = false;
                }

                // *** Modificación: Cambiar el tag del objeto para que no pueda ser recogido de nuevo ***
                objetoSostenido.tag = "Untagged"; // Asegúrate de que este tag existe en tu proyecto

                // Limpiar las referencias
                objetoSostenido = null;

                Debug.Log("Objeto soltado en la posición: " + posicionDestino);

                // Notificar al script RecogerYColocar
                if (scriptRecogerYColocar != null)
                {
                    scriptRecogerYColocar.RobotDisponible(posicionDestino.x, posicionDestino.z);
                }
            }
        }
    }

    // Método público para iniciar la acción de apilar
    public void IniciarApilamiento(float xDestino, float zDestino, int numeroDeObjetosEnPila)
    {
        SoltarObjetoEnPosicion(xDestino, zDestino, numeroDeObjetosEnPila);
    }
}
