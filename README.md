# MOM
> Repositorio para alojar la solución al proyecto #1 sobre MOM y comunicaciones.

## Información de la asignatura
---

 -  **Nombre de la asignatura:** Tópicos especiales en telemática.
-   **Código de la asignatura:**  C2361-ST0263-4528
-   **Departamento:** Departamento de Informática y Sistemas (Universidad EAFIT).
-   **Nombre del profesor:** Juan Carlos Montoya Mendoza.
-  **Correo electrónico del docente:** __[jcmontoy@eafit.edu.co](mailto:jcmontoy@eafit.edu.co)__.

## Datos de los estudiantes
---

-   **Nombre del estudiante:** Juan Pablo Rincon Usma.
-  **Correo electrónico del estudiante:** __[jprinconu@eafit.edu.co](mailto:jprinconu@eafit.edu.co)__.
--
-   **Nombre del estudiante:** Donovan Castrillon Franco.
-  **Correo electrónico del estudiante:** __[dcastrilf@eafit.edu.co](mailto:dcastrilf@eafit.edu.co)__.
--
-   **Nombre del estudiante:** Julian Gomez Benitez.
-  **Correo electrónico del estudiante:** __[jgomezb11@eafit.edu.co](mailto:jgomezb11@eafit.edu.co)__.

## Descripcion
---
Un middleware se entiende como un componente de software que implementa una funcionalidad compleja y ABSTRAE a las aplicaciones usuarias de la complejidad y detalles internos del sistemas.
El objetivo de este proyecto 1 es diseñar e implementar un MIDDLEWARE ORIENTADO A MENSAJES (MOM) que permita a un conjunto de CLIENTES enviar y recibir mensajes de datos.

## Documento de Requerimientos
---
#### Requisitos Funcionales:

- **Conexión y desconexión al servidor**: El sistema debe permitir que los usuarios se conecten y desconecten del servidor para el envío y recepción de mensajes. Debe existir una opción para conectarse de manera permanente (con estado) o sin conexión constante (sin estado).

- **Ciclo de vida de tópicos**: El sistema debe permitir a los usuarios crear, borrar y listar tópicos. Los tópicos tienen nombres únicos.

- **Ciclo de vida de colas**: El sistema debe permitir a los usuarios crear, borrar y listar colas. Las colas son tienen nombres únicos.

- **Envío de mensajes a colas**: El sistema debe permitir a los usuarios enviar mensajes a una cola.

- **Recepción de mensajes de tópicos**: El sistema debe permitir a los usuarios recibir mensajes de un tópico.

- **Recepción de mensajes de colas**: El sistema debe permitir a los usuarios recibir mensajes de una cola.

###### Además, el diseño y la implementación del sistema debe cumplir con los siguientes requisitos:

- La conexión y desconexión deben ser con usuarios autenticados.

- Solo se puede borrar topicos o colas de los usuarios que los crearon. En este caso, se debe definir qué sucederá con los mensajes existentes en un canal o una cola.

- El envío y la recepción de mensajes deben identificar a los usuarios.

- Todos los servicios deben estar expuestos como un API REST hacia los clientes.

- El transporte de los mensajes debe ser encriptado, así como el servicio de autenticación.

- Se debe implementar un mecanismo de persistencia de datos.

- Se debe implementar tolerancia a fallos en el servidor, teniendo en cuenta la posibilidad de tener varios servidores.

- La arquitectura debe aplicar uno de los conceptos vistos sobre replicación o particionamiento.

#### Requisitos No Funcionales:

- **Seguridad**: El sistema debe tener una autenticación y autorización segura para garantizar que solo los usuarios autorizados puedan acceder a los servicios y la información. Se deben usar técnicas de encriptación para proteger el transporte de mensajes y la información de autenticación.

- **Escalabilidad**: El sistema debe ser escalable para manejar un gran número de usuarios y mensajes. La arquitectura debe ser capaz de manejar un aumento en el volumen de mensajes y usuarios sin afectar el rendimiento.

- **Fiabilidad**: El sistema debe ser confiable y no debe perder mensajes. Se deben implementar mecanismos para garantizar la entrega de mensajes incluso en caso de fallo de la red o del servidor.

- **Disponibilidad**: El sistema debe estar disponible en todo momento para garantizar que los usuarios puedan acceder a los servicios y los mensajes. El tiempo de inactividad del sistema debe ser lo más bajo posible.

## Documento Diseño detallado desde el sistema distribuido y software
---
### Análisis
Un MOM resuelve el problema de la comunicación entre diferentes aplicaciones o sistemas que necesitan intercambiar información. En un entorno de microservicios o arquitectura basada en servicios, donde las aplicaciones se descomponen en componentes pequeños y autónomos, es común tener la necesidad de enviar y recibir mensajes entre diferentes servicios para que puedan colaborar juntos.

Los servicios pueden tener diferentes lenguajes de programación, sistemas operativos o incluso pueden estar en diferentes ubicaciones geográficas. En este contexto, nuestra propuesta proporciona una solución para enviar y recibir mensajes entre estos servicios de manera confiable y escalable. Todo esto teniendo en cuenta los requerimientos anteriormente descritos.

### Diseño

El resultante de nuestra propuesta es una API que expone varios metodos por medio de REST a nuestros clientes. Para esto usamos Python como lenguaje de programacion. Para asegurarnos de que nuestro sistema sea altamente disponible decidimos desplegarlo en tres maquinas de AWS distintas, que se sincronizan entre ellas usando el patron del Master/Slave. Ademas de esto vamos a hacer uso de un balanceador de carga que nos va a ayudar a filtrar las peticiones de escritura (POST, DELETE) y separarlas de las de lectura (GET) de tal manera que se puedan enrutar a el master y los slave respectivamente. Para temas de sincronizacion estamos usando gRPC para comunicar nuestros MOM's en caso de actualizacion de datos, en terminos tecnicos le estamos pasando por el protocolo gRPC el archivo binario de la base de datos para que el receptor genere la base de datos apartir de ahi y asi nos aseguramos de que las transacciones siempre se veran reflejadas en todos los servidores. Tenemos corriendo un servidor HTTP usando una libreria de python que nos permite manejar concurrentemente una alta cantidad de usuarios lo que facilitaria la interaccion de todos con todos. Para temas de persistencia decidimos usar la base de datos NoSQL MongoDB para facilitarnos las operaciones de CRUD, el diseno de la base de datos es bastante simple, solo tenemos una coleccion que se llama Users donde vamos a almacenar toda la informacion relacionada con un usuario, incluyendo colas y topicos que se creen, asi como la informacion respectiva a cada una. Para temas de seguridad estamos usando un metodo de encriptacion de vanguardia que encrypta contrasenas y mensajes con una salt aleateroria y una password privada que nosotros definimos, de tal manera que en la base de datos no se puede ver que es lo que se estan mandando los microservicios, la desencriptacion se hace directamente en el endpoint de la conexion con nuestros clientes. Para efectos de mantener la sesion implementamos una logica la cual nos permite relacionar la ultima ip de conexion de un usuario con todas las acciones que realice mientras se mantiene el estado de la conexion. Nuestro MOM implementa tanto comunicacion asincronica que se puede hacer tanto simetrica como asimetricamente. El mecanismo de recepcion de mensajes esta definido en modo pull para hacer mas sencilla la comunicacion asincronica entre dos partes. En el caso de querer escalar nuestra solucion se puede escalar horizontalmente sin mucho problema puesto que nuestra propuesta esta construida modularmente de tal manera que agregar un nodo mas no afecta el funcionamiento de los existentes.

### Arquitectura del despliegue

### Arquitectura de clases

### Arquitectura de datos

### Arquitectura de directorios

## Documento de detalles/dependencia de implementación, instalación y ejecución
---
### Dependencias

| Nombre del paquete | Versión | Descripción |
| --------- | --------- | --------- |
| Python   | 3.11   | Valor 3   |
| pyMongo   | Valor 5   | Valor 6   |
| http.server   | Valor 5   | Valor 6   |
| logging   | Valor 5   | Valor 6   |
| urllib   | Valor 5   | Valor 6   |
| dotenv   | Valor 5   | Valor 6   |
| bson   | Valor 5   | Valor 6   |
| json   | Valor 5   | Valor 6   |
| socketserver   | Valor 5   | Valor 6   |
| hashlib   | Valor 5   | Valor 6   |
| Crytodome   | Valor 5   | Valor 6   |
| base64   | Valor 5   | Valor 6   |
| Protobuf   | Valor 5   | Valor 6   |
| grpc   | Valor 5   | Valor 6   |

### Instalacion

Para instalar nuestra solucion en tus servidores es necesario que tengas instaladas todas las dependencias que fueron anteriormente listadas. De esta manera solo seria necesario compilar el archivo .proto que define el paso de mensajes por medio de gRPC para que todo funcione correctamente.

### Uso

#### Peticiones GET:

##### getQueues:
Función para listar todas las colas que pertenecen a un usuario.
- Método: **GET**
- Ruta: **/getQueues**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```
##### getTopics:
Función para listar todos los topicos que pertenecen a un usuario.
- Método: **GET**
- Ruta: **/getTopics**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```

##### consumeMessage:
Función para hacer pull del primer mensaje en la cola del usuario.
- Método: **GET**
- Ruta: **/consumeMessage**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```

#### Peticiones POST:

##### registerUser:
Función para registrar un usuario nuevo.
- Método: **POST**
- Ruta: **/registerUser**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```

##### loginUser:
Función para crear una sesion como un usuario ya existente.
- Método: **POST**
- Ruta: **/loginUser**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```

##### logoutUser:
Función para desloguearse de una sesion ya existente.
- Método: **POST**
- Ruta: **/logoutUser**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```

##### createQueue:
Función para crear una cola que se relaciona directamente con el usuario que la creo.
- Método: **POST**
- Ruta: **/createQueue**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```

##### createTopic:
Función para crear un topico que se relaciona directamente con el usuario que lo creo.
- Método: **POST**
- Ruta: **/createTopic**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```
	
##### subscribeToTopic:
Función que le permite a un usuario suscribirse a un topico ya existente.
- Método: **POST**
- Ruta: **/subscribeToTopic**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```
	
##### vinculateQueue:
Función que le permite a una cola registrar un exchange con otra cola.
- Método: **POST**
- Ruta: **/vinculateQueue**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```
	
##### publishMessage:
Función que le permite al dueno de un topico mandar un mensaje a todos los subscriptores.
- Método: **POST**
- Ruta: **/publishMessage**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```
	
##### sendMessage:
Función que le permite a las colas mandarse mensajes entre ellas.
- Método: **POST**
- Ruta: **/sendMessage**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```
	
#### Peticiones DELETE:

##### deleteQueue:
Función que le permite borrar una cola a su dueno.
- Método: **DELETE**
- Ruta: **/deleteQueue**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```
	
##### deleteTopic:
Función que le permite borrar un topico a su dueno.
- Método: **DELETE**
- Ruta: **/deleteTopic**
- QueryString:
- Valor de response:
	```json 
	{
		message: "mensaje de confirmación"
	}
	```
