CLOUD-IN-ONE
==============

Travis CI Status:
[![Build Status](https://travis-ci.org/vguzmanp/cloud-in-one.svg?branch=master)](https://travis-ci.org/vguzmanp/cloud-in-one)

CLOUD-IN-ONE es un proyecto orientado a proporcionar una interfaz transparente y segura de servicios de almacenamiento en la nube.

Esto se consigue mediante una aplicación que sincroniza en segundo plano los archivos de la carpeta de sincronización con todas las cuentas vinculadas al sistema. La sincronización es similar al cliente oficial de Dropbox, pero conectada a diferentes cuentas.
Además, todos los ficheros de los diferentes servicios de almacenamiento se agregan en una misma carpeta de forma transparente al usuario, por lo que el usuario no necesita saber a qué servicio está subiendo sus ficheros, solo necesita saber que se han almacenado de forma segura.

El sistema puede, por otro lado, encriptar los ficheros antes de subirlos a los respectivos servicios. Así, si alguien accediera a la cuenta remota (por ejemplo, desde la web de Dropbox) no podría leer ninguno de los archivos.

¿Por qué cloud-in-one?
----------------------
- Tengo varias cuentas de Dropbox y quiero sincronizarlas en el mismo PC al mismo tiempo (Dropbox sólo permite una instalación con una cuenta).
- Tengo varias cuentas de almacenamiento en la nube. Si sumo el espacio de todas, mis archivos caben en ellas, pero no caben en cada cuenta por separado.
- Tengo un agregador de servicios de almacenamiento pero tengo que saber en qué cuenta está cada archivo.
- No confío en que mi proveedor de almacenamiento en la nube no leerá la información confidencial que subo a su servicio.
- No confío en que alguien consiga acceder a mi cuenta en un servicio de almacenamiento y pueda leer mis archivos.
- Quiero tener una alternativa de código abierto a las aplicaciones de sincronización de almacenamiento en la nube.

Comparación con otras aplicaciones similares:
------------------------------
Puede parecer que hay una gran cantidad de servicios y aplicaciones que hacen exactamente lo mismo que CLOUD-IN-ONE, pero no es así:
- A diferencia del cliente oficial de *Dropbox*, CLOUD-IN-ONE permite vincular más de una cuenta al mismo PC.
- CLOUD-IN-ONE se integra con el sistema operativo: el usuario solo se tiene que preocupar de guardar sus ficheros en una carpeta local, y la aplicación se encargará de monitorizarla y subirla a un servicio remoto. Otras aplicaciones como *Jolicloud*, *CloudKafé* o *MultCloud* se basan en web, con lo que el usuario se ve obligado a trabajar desde el navegador y no desde el propio sistema.
- Servicios como *Gladinet*, *odrive* o *otixo* separan los servicios en distintas carpetas, CLOUD-IN-ONE agrega todas las cuentas en una misma carpeta. De esta manera el usuario guarda sus ficheros en la carpeta, y CLOUD-IN-ONE organizará los ficheros entre los servicios.
- CLOUD-IN-ONE permite encriptar los ficheros para que ningún PC que no esté autorizado pueda leerlos.

Problemas:
--------------------
- Dependencia de APIs de terceros.
- Ficheros repartidos entre diferentes servicios.
- En caso de activar la encriptación para un fichero, dificultad de obtenerlo en una plataforma donde no esté instalada la aplicación.

<h2>Instalando desde código fuente</h2>
<h3>Software necesario</h3>
- Python 3.4.2
- Dropbox SDK ==> `pip install dropbox`
- Dataset ==> `pip install dataset`

Para pruebas:
- Nose ==> `pip install nose`


<h3>VirtualEnv en PowerShell</h3>
Para crear un venv:
`python.exe <Ruta a python>\Tools\Scripts\pyvenv.py <venv-path>`
Para activarlo:

    Set-ExecutionPolicy RemoteSigned
    <venv-path>\Scripts\Activate.ps1

<h2>Ejecutando las pruebas</h2>
`nosetests`
