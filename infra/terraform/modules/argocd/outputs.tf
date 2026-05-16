output "argocd_namespace" {
  description = "Kubernetes namespace where ArgoCD is deployed"
  value       = kubernetes_namespace_v1.argocd.metadata[0].name
}

output "argocd_hostname" {
  description = "Hostname used to access ArgoCD"
  value       = var.argocd_hostname
}

output "argocd_ingress_status" {
  description = "Status of the ArgoCD ingress (address may be pending until ALB provisions)"
  value       = try(kubernetes_ingress_v1.argocd.status[0].load_balancer[0].ingress[0].hostname, "pending")
}
