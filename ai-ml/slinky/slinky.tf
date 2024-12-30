# Create namespace for Slinky
resource "kubernetes_namespace" "slinky" {
  metadata {
    name = "slinky"
  }
}

# Create a local file resource to store the values.yaml content
data "http" "values_operator" {
  url = "https://raw.githubusercontent.com/SlinkyProject/slurm-operator/refs/tags/v0.1.0/helm/slurm-operator/values.yaml"
}

# Install Slurm operator using Helm
resource "helm_release" "slurm_operator" {
  name             = "slurm-operator"
  repository       = "oci://ghcr.io/slinkyproject/charts"
  chart            = "slurm-operator"
  version          = "0.1.0"
  namespace        = kubernetes_namespace.slinky.metadata[0].name
  create_namespace = true

  # Use the values from the downloaded file
  values = [
    data.http.values_operator.response_body
  ]

  set {
    name  = "image.repository"
    value = "public.ecr.aws/u1m6g1t5/harish/slurm-operator-eks"
  }

    set {
    name  = "image.tag"
    value = "latest"
  }


  depends_on = [
    kubernetes_namespace.slinky
  ]

  # Add timeout in case installation takes longer
  timeout = 900 # 15 minutes
}

# Create namespace for Slurm
resource "kubernetes_namespace" "slurm" {
  metadata {
    name = "slurm"
  }
}

# Fetch the values.yaml content
data "http" "values_slurm" {
  url = "https://raw.githubusercontent.com/SlinkyProject/slurm-operator/refs/tags/v0.1.0/helm/slurm/values.yaml"
}


# Install Slurm using Helm
resource "helm_release" "slurm" {
  name             = "slurm"
  repository       = "oci://ghcr.io/slinkyproject/charts"
  chart            = "slurm"
  version          = "0.1.0"
  namespace        = kubernetes_namespace.slurm.metadata[0].name
  create_namespace = true

  values = [
    data.http.values_slurm.response_body
  ]

  # Configure storage class
  set {
    name  = "controller.persistence.storageClass"
    value = "fsx"
  }


  depends_on = [
    kubernetes_namespace.slurm,
    helm_release.slurm_operator
  ]

  timeout = 900
}
