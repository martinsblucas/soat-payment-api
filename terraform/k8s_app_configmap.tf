resource "kubernetes_config_map" "payment_api" {
  metadata {
    name      = "payment-api-config"
    namespace = kubernetes_namespace.payment_api.metadata[0].name
  }

  data = {
    APP_TITLE                         = var.app_title
    APP_VERSION                       = var.app_version
    APP_ENVIRONMENT                   = var.app_environment
    APP_ROOT_PATH                     = var.app_root_path
    AWS_REGION_NAME                   = var.region
    DATABASE_ECHO                     = tostring(var.database_echo)
    MERCADO_PAGO_CALLBACK_URL         = "${local.api_gateway_url}${var.app_root_path}/v1/payment/notifications/mercado-pago"
    ORDER_CREATED_LISTENER_QUEUE_NAME = var.order_created_listener_queue_name
  }
}
