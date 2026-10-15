
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 3.0"
    }
  }
}

provider "kubernetes" {
  config_path    = pathexpand("~/.kube/config")
  config_context = "kind-cloudops-pro"
}

resource "kubernetes_config_map_v1" "cloudops_info" {
  metadata {
    name      = "cloudops-terraform-info"
    namespace = "cloudops-pro"

    labels = {
      app        = "cloudops-pro"
      managed-by = "terraform"
    }
  }

  data = {
    project     = "CloudOps Pro"
    environment = "local-kind"
    managed_by  = "Terraform"
  }
}
