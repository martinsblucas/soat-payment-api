resource "kubernetes_namespace" "payment_api" {
  metadata {
    name = "tech-challenge-payment-api"
  }
}
