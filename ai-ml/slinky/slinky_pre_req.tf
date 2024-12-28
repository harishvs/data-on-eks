# Create the namespaces
resource "kubernetes_namespace" "cert_manager" {
  metadata {
    name = "cert-manager"
  }
}

resource "kubernetes_namespace" "prometheus" {
  metadata {
    name = "prometheus"
  }
}

# Helm provider configuration for the repositories
resource "helm_release" "cert_manager" {
  name             = "cert-manager"
  repository       = "https://charts.jetstack.io"
  chart            = "cert-manager"
  namespace        = kubernetes_namespace.cert_manager.metadata[0].name
  version          = "v1.13.3"
  create_namespace = true

  set {
    name  = "installCRDs"
    value = "true"
  }

  set {
    name  = "webhook.timeoutSeconds"
    value = "30"
  }

  set {
    name  = "startupapicheck.timeout"
    value = "5m"
  }

  # Change the webhook port to something else (e.g., 10260)
  set {
    name  = "webhook.securePort"
    value = "10260"
  }

  set {
    name  = "webhook.hostNetwork"
    value = "true"
  }

  # Increase timeout for installation
  timeout = 1800 # 30 minutes

  depends_on = [kubernetes_namespace.cert_manager]
}



resource "helm_release" "prometheus" {
  name             = "prometheus"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = kubernetes_namespace.prometheus.metadata[0].name
  version          = "48.2.3"  # Specify the version you want to use
  create_namespace = true

  set {
    name  = "installCRDs"
    value = "true"
  }

  # Wait for cert-manager to be ready before installing prometheus
  depends_on = [helm_release.cert_manager]
}
