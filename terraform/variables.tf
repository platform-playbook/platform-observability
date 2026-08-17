variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
  default     = "rg-platform-observability"
}

variable "acr_name" {
  description = "Globally unique Azure Container Registry name"
  type        = string
}

variable "aks_name" {
  description = "AKS cluster name"
  type        = string
  default     = "aks-platform-observability"
}

variable "dns_prefix" {
  description = "AKS DNS prefix"
  type        = string
}

variable "vnet_address_space" {
  description = "VNet CIDR"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "aks_subnet_address_prefix" {
  description = "AKS subnet CIDR"
  type        = string
  default     = "10.0.1.0/24"
}

variable "system_node_count" {
  description = "Number of regular system nodes"
  type        = number
  default     = 2
}

variable "system_node_vm_size" {
  description = "VM size for regular system nodes"
  type        = string
  default     = "Standard_D2s_v5"
}

variable "spot_node_count" {
  description = "Initial number of Spot user nodes"
  type        = number
  default     = 1
}

variable "spot_node_vm_size" {
  description = "VM size for Spot nodes"
  type        = string
  default     = "Standard_D2s_v5"
}
variable "enable_spot_pool" {
  description = "Whether to create the Spot node pool"
  type        = bool
  default     = false
}
