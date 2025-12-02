resource "kubernetes_service" "payment_api" {
  metadata {
    name      = "payment-api-service"
    namespace = kubernetes_namespace.payment_api.metadata[0].name
  }

  spec {
    type = "ClusterIP"

    selector = {
      app = "payment-api"
    }

    port {
      port        = 80
      target_port = 8000
    }
  }
}
