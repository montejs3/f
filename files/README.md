# Redes-Lab-3

### Generalidades

* Es necesario instalar una libreria para el uso del programa. Adicionalmente, se requiere acceso a internet para descargar los archivos de prueba necesarios. Para esto se realiza el siguiente proceso.
* Ambos servidores y clientes se encuentran en este repositorio
* Cada Servidor-Cliente tiene su propia carpeta logs, ubicadas en **Servidor-Cliente-XXX/Cliente/Logs** o **Servidor-Cliente-XXX/Servidor/Logs**

### Requisitos

Instalar python 3.8, para esto usamos el siguiente comando:

```bash
$ apt install python3.8 -y
```

Instalar la siguiente libreria para la descarga de archivos subidos en Google Drive para las pruebas de los servidores

```bash
$ pip install gdown
```

### Instalación

Antes de iniciar, es necesario ubicarnos en la carpeta del proyecto

```bash
$ cd INFRACOM-Lab-3
```

Antes de la ejecución de cada servidor y cliente es necesario ejecutar el siguiente script que se encarga de descargar los archivos de una carpeta en drive

```bash
$ python3.8 files/file_download.py
```

Guardar la ip asignada en la maquina virtual usando el comando ifconfig

Una vez con esta ip se deben modificar los archivos con el fin poner la ip privada de la maquina virtual

**Archivo servidor_tcp_thread.py**
```bash
$ sudo nano Servidor-Cliente-TCP/Servidor/servidor_tcp_thread.py
```
* Modificamos la linea #15 agregando la IP de la maquina virtual.

```bash
s.bind(('IP MAQUINA', 5000))
```

**Archivo cliente_tcp_thread.py**
* Este es posible modificarlo en cualquier editor de texto dado a que no se debe correr en la maquina virtual
* Modificamos la linea #120 agregando la IP de la maquina virtual.

```bash
client = ClientThread(item, "IP MAQUINA", 5000, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-log.txt", file_num)
```

**Archivo servidor_udp_thread.py**
```bash
$ sudo nano Servidor-Cliente-UDP/Servidor/servidor_udp_thread.py
```
* Modificamos la linea #9 agregando la IP de la maquina virtual.

```bash
host = 'IP MAQUINA'
```

**Archivo cliente_tcp_thread.py**
* Este es posible modificarlo en cualquier editor de texto dado a que no se debe correr en la maquina virtual
* Modificamos la linea #85 agregando la IP de la maquina virtual.

```bash
host = 'IP MAQUINA'
```

### Ejecución (TCP)

* Para el servidor, se debe ejecutar este de la siguiente forma con el fin de no tener errores con los paths de los archivos usados, esto se hace desde la carpeta base del proyecto.

```bash
$ python3.8 Servidor-Cliente-TCP/Servidor/servidor_tcp_thread.py
```

* Para el cliente, este si debe ejecutarse estando desde su carpeta, de esta forma es necesario ubicarse en esa carpeta primero y luego ejecutar el archivo.

```bash
$ cd Servidor-Cliente-TCP/Cliente
```

```bash
$ python3.8 Cliente/cliente_tcp_thread.py
```

### Ejecución (UDP)

* Para el servidor, se debe ejecutar este de la siguiente forma con el fin de no tener errores con los paths de los archivos usados, esto se hace desde la carpeta base del proyecto.

```bash
$ python3.8 Servidor-Cliente-UDP/Servidor/servidor_udp_thread.py
```

* Para el cliente, este si debe ejecutarse estando desde su carpeta, de esta forma es necesario ubicarse en esa carpeta primero y luego ejecutar el archivo.

```bash
$ cd Servidor-Cliente-UDP/Cliente
```

```bash
$ python3.8 Cliente/cliente_udp_thread.py
```
