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

### Diseño

## Documento de detalles/dependencia de implementación, instalación y ejecución
---
### Dependencias

### Instalacion

### Uso
