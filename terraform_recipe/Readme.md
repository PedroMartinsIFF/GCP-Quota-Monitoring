
# **Monitoração com Terraform**
Nesta opção, a aplicação será provisionada de forma automatizada diretamente na GCP.
Esta receita cria os seguintes recursos:
* Um bucket onde será armazenado o código;
* Uma Cloud Function para executar o código;
* Um Cloud Scheduler que acionará a Cloud Function;
* Uma Service Account para associar ao Scheduler, que tem a permissão de invoker.

## Requisitos 

Instale o [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)

Instale o [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

Siga esta [documentação](https://cloud.google.com/sdk/gcloud/reference/auth) para logar no seu projeto com o Google Cloud SDK

Será necessário que o usuário que realizar a instalação dos componentes via terraform tenha permissão de criar, editar e excluir os recursos de:
* Storage Bucket;
* Cloud Functions;
* Service Accounts;
* Cloud Scheduler;

Se o seu projeto já está em produção, ele já possui uma subnet para nosso proxy de coleta, para acessar essa subnet, vc precisa criar um VPC Connector.

## Instalação

Estando logado na sua conta com o Google Cloud SDK, entre na pasta terraform.

```
cd gcp_monitoring/terraform_recipe/terraform/
```

Edite o arquivo terraform.tfvars com as variáveis do seu projeto.

OBS: Lembre que a região onde você for fazer o deploy da aplicação deve ser a mesma região da APP Engine do seu projeto.

Em seguida basta executar o terraform

```
terraform plan
```

```
terraform apply
```