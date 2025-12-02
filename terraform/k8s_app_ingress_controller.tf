resource "kubernetes_ingress_v1" "payment_api" {
  metadata {
    name      = "payment-api-route"
    namespace = kubernetes_namespace.payment_api.metadata[0].name
  }

  spec {
    ingress_class_name = "nginx"

    rule {
      http {
        path {
          path      = "/soat-fast-food/v1/payment"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.payment_api.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}
