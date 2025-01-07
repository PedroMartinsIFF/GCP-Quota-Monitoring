# **Monitoração via Script**


## Requisitos 

É recomendável que o usuário utilize os scripts em um [ambiente virtual](https://gist.github.com/recto/def9706cc1f3b34667409dabd32df067).

  

Também é necessário ter o [PIP](https://pip.pypa.io/en/stable/installing/) instalado

  

Após instalar o pip, instale as dependências dos scripts com:

  

```sh

$ pip install --requirement requirements.txt

```

  

Será necessário o uso de uma credencial de acesso na GCP com a Role monitoring.viewer. Coloque a credencial dentro da pasta gcp_monitoring e declare o caminho para ela na variável de ambiente GOOGLE_APPLICATION_CREDENTIALS.

  

```

export GOOGLE_APPLICATION_CREDENTIALS= < PATH para sua credencial >

```

  

Crie um job cron com o formato * * * * * /path/to/virtenv/bin/python /usr/bin/python /path/to/file/main.py --projet PROJECT --host HOST

