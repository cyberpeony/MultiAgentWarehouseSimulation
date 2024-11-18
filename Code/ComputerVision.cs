using UnityEngine;
using System.Collections;
using System.Net.Sockets;
using System.Text;
using UnityEngine.UI;
using System.Threading;
using TMPro; // Agregar esta línea

public class CameraCapture : MonoBehaviour
{
    public Camera mainCamera;
    public float sendInterval = 2.0f; // Enviar una imagen cada 2 segundos
    private Texture2D texture2D;
    private float timer = 0f;
    private bool isSending = false;

    public TextMeshProUGUI responseText; // Cambiado a TextMeshProUGUI

    // Cola de acciones para ejecutar en el hilo principal
    private System.Collections.Generic.Queue<System.Action> executeOnMainThread = new System.Collections.Generic.Queue<System.Action>();

    void Start()
    {
        if (mainCamera == null)
        {
            mainCamera = Camera.main;
        }

        int width = Screen.width;
        int height = Screen.height;
        texture2D = new Texture2D(width, height, TextureFormat.RGB24, false);
    }

    void Update()
    {
        // Ejecutar acciones encoladas en el hilo principal
        lock (executeOnMainThread)
        {
            while (executeOnMainThread.Count > 0)
            {
                var action = executeOnMainThread.Dequeue();
                action();
            }
        }

        timer += Time.deltaTime;
        if (timer >= sendInterval && !isSending)
        {
            StartCoroutine(CaptureAndSend());
            timer = 0f;
        }
    }

    IEnumerator CaptureAndSend()
    {
        isSending = true;

        // Esperar al final del frame para asegurar que todo se ha renderizado
        yield return new WaitForEndOfFrame();

        // Capturar la imagen de la pantalla
        texture2D.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0);
        texture2D.Apply();

        // Convertir la imagen a bytes (PNG o JPG)
        byte[] imageBytes = texture2D.EncodeToJPG();

        // Enviar la imagen al script de Python
        yield return StartCoroutine(SendImageToPython(imageBytes));

        isSending = false;
    }

    IEnumerator SendImageToPython(byte[] imageBytes)
    {
        bool completed = false;
        string responseString = null;

        // Iniciar un nuevo hilo para la comunicación de red
        Thread networkThread = new Thread(() =>
        {
            try
            {
                TcpClient client = new TcpClient();
                client.Connect("localhost", 9999); // Asegúrate de que el puerto coincide con el de Python
                NetworkStream stream = client.GetStream();

                // Enviar la longitud de los bytes y luego los bytes de la imagen
                byte[] lengthPrefix = System.BitConverter.GetBytes(imageBytes.Length);
                if (System.BitConverter.IsLittleEndian)
                {
                    System.Array.Reverse(lengthPrefix);
                }
                stream.Write(lengthPrefix, 0, lengthPrefix.Length);
                stream.Write(imageBytes, 0, imageBytes.Length);

                // Ahora, recibir la longitud de la respuesta
                byte[] responseLengthPrefix = new byte[4];
                int bytesRead = 0;
                while (bytesRead < 4)
                {
                    int read = stream.Read(responseLengthPrefix, bytesRead, 4 - bytesRead);
                    if (read == 0)
                    {
                        // Conexión cerrada
                        Debug.LogError("Conexión cerrada al leer la longitud de la respuesta");
                        break;
                    }
                    bytesRead += read;
                }
                if (bytesRead < 4)
                {
                    Debug.LogError("No se pudo leer la longitud de la respuesta");
                }
                else
                {
                    if (System.BitConverter.IsLittleEndian)
                    {
                        System.Array.Reverse(responseLengthPrefix);
                    }
                    int responseLength = System.BitConverter.ToInt32(responseLengthPrefix, 0);

                    // Ahora, leer la respuesta completa
                    byte[] responseBytes = new byte[responseLength];
                    bytesRead = 0;
                    while (bytesRead < responseLength)
                    {
                        int read = stream.Read(responseBytes, bytesRead, responseLength - bytesRead);
                        if (read == 0)
                        {
                            // Conexión cerrada
                            Debug.LogError("Conexión cerrada al leer la respuesta");
                            break;
                        }
                        bytesRead += read;
                    }
                    if (bytesRead < responseLength)
                    {
                        Debug.LogError("No se pudo leer la respuesta completa");
                    }
                    else
                    {
                        responseString = Encoding.UTF8.GetString(responseBytes);
                    }
                }

                // Cerrar la conexión
                stream.Close();
                client.Close();
            }
            catch (SocketException e)
            {
                Debug.Log("SocketException: " + e.Message);
            }
            finally
            {
                completed = true;
            }
        });

        networkThread.Start();

        // Esperar a que la operación de red termine sin bloquear el hilo principal
        while (!completed)
        {
            yield return null;
        }

        // Encolar la actualización de la UI en el hilo principal
        if (!string.IsNullOrEmpty(responseString))
        {
            Debug.Log("Respuesta desde Python: " + responseString);

            lock (executeOnMainThread)
            {
                executeOnMainThread.Enqueue(() =>
                {
                    if (responseText != null)
                    {
                        responseText.text = responseString;
                    }
                });
            }
        }
    }
}