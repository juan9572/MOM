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
-  **Correo electrónico del estudiante:** __[dcastrillf@eafit.edu.co](mailto:dcastrillf@eafit.edu.co)__.
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

El resultado de nuestra propuesta es una API que expone varios métodos por medio de REST a nuestros clientes. Para esto, usamos Python como lenguaje de programación. Para asegurarnos de que nuestro sistema sea altamente disponible, decidimos desplegarlo en tres máquinas de AWS distintas que se sincronizan entre sí usando el patrón del Master/Slave.

Además de esto, vamos a hacer uso de un balanceador de carga que nos ayudará a filtrar las peticiones de escritura (POST, DELETE) y separarlas de las de lectura (GET) de tal manera que se puedan enrutar al master y los slaves respectivamente. Para temas de sincronización, estamos usando gRPC para comunicar nuestros MOM's en caso de actualización de datos. En términos técnicos, le estamos pasando por el protocolo gRPC el archivo binario de la base de datos para que el receptor genere la base de datos a partir de ahí y así nos aseguramos de que las transacciones siempre se verán reflejadas en todos los servidores.

Tenemos corriendo un servidor HTTP usando una librería de Python que nos permite manejar concurrentemente una alta cantidad de usuarios, lo que facilitaría la interacción de todos con todos. Para temas de persistencia, decidimos usar la base de datos NoSQL MongoDB para facilitarnos las operaciones de CRUD. El diseño de la base de datos es bastante simple: solo tenemos una colección que se llama Users, donde vamos a almacenar toda la información relacionada con un usuario, incluyendo colas y tópicos que se creen, así como la información respectiva a cada uno.

Para temas de seguridad, estamos usando un método de encriptación de vanguardia que encripta contraseñas y mensajes con una salt aleatoria y una password privada que nosotros definimos. De tal manera que en la base de datos no se puede ver qué es lo que se están mandando los microservicios. La desencriptación se hace directamente en el endpoint de la conexión con nuestros clientes. Para efectos de mantener la sesión, implementamos una lógica que nos permite relacionar la última IP de conexión de un usuario con todas las acciones que realice mientras se mantiene el estado de la conexión.

Nuestro MOM implementa comunicación asíncrona que se puede hacer tanto simétrica como asimétricamente. El mecanismo de recepción de mensajes está definido en modo pull para hacer más sencilla la comunicación asíncrona entre dos partes. En el caso de querer escalar nuestra solución, se puede escalar horizontalmente sin mucho problema, puesto que nuestra propuesta está construida modularmente de tal manera que agregar un nodo más no afecta el funcionamiento de los existentes.

Para efectos de la estabilidad y disponibilidad del servicio, implementamos un balanceador de carga propio que distribuye las peticiones GET (de lectura) entre los dos servidores esclavos que tenemos, la logica que implementamos para balancear es round robin con un maximo de 3 intentos a un nodo de la red antes de intentar mandar la peticion al siguiente en el ciclo. Las peticiones POST y DELETE (de escritura) solo llegan a una maquina (el master), el master de nosotros no tiene replicas, lo que hicimos fue agregar una logica en la cual un esclavo puede reemplazar al master en caso de que este se caiga.

### Arquitectura del despliegue
![Arquitectura de datos](https://raw.githubusercontent.com/juan9572/MOM/main/Diagrams/Diagrama%20de%20arquitectura.png)

### Arquitectura de clases
![Arquitectura de datos](https://raw.githubusercontent.com/juan9572/MOM/main/Diagrams/Diagrama_de_clases.drawio.png)

### Arquitectura de datos
![Arquitectura de datos](https://raw.githubusercontent.com/juan9572/MOM/main/Diagrams/Arquitectura%20de%20datos.png)

Representacion de la coleccion que tenemos en la base de datos.
## Documento de detalles/dependencia de implementación, instalación y ejecución
---
### Dependencias

| Nombre del paquete | Versión | Descripción |
| --------- | --------- | --------- |
| Python   | 3.11   | Lenguaje de programacion usado   |
| pymongo   | 4.3.3   | Libreria para establecer conexion con MongoDB   |
| python-dotenv   | 1.0   | Libreria para acceder a variables de entorno   |
| bson   | 0.5.10   | Libreria para maneajar archivos bson   |
| pycryptodome   |  3.17   | librería de criptografía de Python que proporciona una amplia variedad de algoritmos criptográficos    |
| protobuf   | 4.22.1   | La librería protobuf para Python proporciona un paquete para trabajar con protocol buffers en Python   |
| grpcio   | 1.53.0   | La librería grpc para Python proporciona una forma de utilizar gRPC en aplicaciones Python   |
| grpcio-tools   | 1.53.0   | La librería grpc para Python proporciona herramientas para usar grpc   |

### Instalacion

Para instalar nuestra solucion en tus servidores es necesario que tengas instaladas todas las dependencias que fueron anteriormente listadas. De esta manera solo seria necesario compilar el archivo .proto que define el paso de mensajes por medio de gRPC para que todo funcione correctamente.

```
pip install bson
pip install grpcio
pip install grpcio-tools
pip install pycryptodome
pip install pycryptodomex
pip install python-dotenv
pip install pymongo
pip install requests
```

### Uso
A continuacion la lista de todos los metodos que exponemos en el API, su ruta y los parametros que deberian ser usados para su correcto funcionamiento.
#### Peticiones GET:

##### getQueues:
Función para listar todas las colas que pertenecen a un usuario.
- Método: **GET**
- Ruta: **/getQueues**
- QueryString: No parameters requiered.

##### getTopics:
Función para listar todos los topicos que pertenecen a un usuario.
- Método: **GET**
- Ruta: **/getTopics**
- QueryString: No parameters requiered.


##### consumeMessage:
Función para hacer pull del primer mensaje en la cola del usuario.
- Método: **GET**
- Ruta: **/consumeMessage**
- QueryString: `?nameQueue=<NombreDeLaCola>`


#### Peticiones POST:

##### registerUser:
Función para registrar un usuario nuevo.
- Método: **POST**
- Ruta: **/registerUser**
- QueryString: `?username=<user>&password=<pass>`


##### loginUser:
Función para crear una sesion como un usuario ya existente.
- Método: **POST**
- Ruta: **/loginUser**
- QueryString: `?username=<user>&password=<pass>`


##### logoutUser:
Función para desloguearse de una sesion ya existente.
- Método: **POST**
- Ruta: **/logoutUser**
- QueryString: No parameters requiered.


##### createQueue:
Función para crear una cola que se relaciona directamente con el usuario que la creo.
- Método: **POST**
- Ruta: **/createQueue**
- QueryString: `?nameQueue=<Queue>`


##### createTopic:
Función para crear un topico que se relaciona directamente con el usuario que lo creo.
- Método: **POST**
- Ruta: **/createTopic**
- QueryString: `?nameTopic=<Topic>`

	
##### subscribeToTopic:
Función que le permite a un usuario suscribirse a un topico ya existente.
- Método: **POST**
- Ruta: **/subscribeToTopic**
- QueryString: `?nameTopic=<Topic>&nameQueue=<Queue>`

	
##### vinculateQueue:
Función que le permite a una cola registrar un exchange con otra cola.
- Método: **POST**
- Ruta: **/vinculateQueue**
- QueryString: `?nameExchange=<Exchange>&nameQueue=<Queue>`

	
##### publishMessage:
Función que le permite al dueno de un topico mandar un mensaje a todos los subscriptores.
- Método: **POST**
- Ruta: **/publishMessage**
- QueryString: `?nameTopic=<Topic>&message=<Message>`

	
##### sendMessage:
Función que le permite a las colas mandarse mensajes entre ellas.
- Método: **POST**
- Ruta: **/sendMessage**
- QueryString: `?nameExchange=<Exchange>&message=<Message>`

	
#### Peticiones DELETE:

##### deleteQueue:
Función que le permite borrar una cola a su dueno.
- Método: **DELETE**
- Ruta: **/deleteQueue**
- QueryString: `?nameQueue=<Queue>`

##### deleteTopic:
Función que le permite borrar un topico a su dueno.
- Método: **DELETE**
- Ruta: **/deleteTopic**
- QueryString: `?nameTopic=<Topic>`
