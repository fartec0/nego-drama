terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Variables
variable "region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-west-2"
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "quantum-ui-cluster"
}

variable "node_group_name" {
  description = "Name of the EKS node group"
  type        = string
  default     = "quantum-ui-nodes"
}

# VPC for EKS
resource "aws_vpc" "quantum_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  
  tags = {
    Name = "quantum-ui-vpc"
    Project = "QuantumUI"
  }
}

# Subnets for EKS
resource "aws_subnet" "quantum_subnet_1" {
  vpc_id            = aws_vpc.quantum_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.region}a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "quantum-ui-subnet-1"
    Project = "QuantumUI"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}

resource "aws_subnet" "quantum_subnet_2" {
  vpc_id            = aws_vpc.quantum_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.region}b"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "quantum-ui-subnet-2"
    Project = "QuantumUI"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "quantum_igw" {
  vpc_id = aws_vpc.quantum_vpc.id
  
  tags = {
    Name = "quantum-ui-igw"
    Project = "QuantumUI"
  }
}

# Route Table
resource "aws_route_table" "quantum_rt" {
  vpc_id = aws_vpc.quantum_vpc.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.quantum_igw.id
  }
  
  tags = {
    Name = "quantum-ui-rt"
    Project = "QuantumUI"
  }
}

# Route Table Association
resource "aws_route_table_association" "quantum_rta_1" {
  subnet_id      = aws_subnet.quantum_subnet_1.id
  route_table_id = aws_route_table.quantum_rt.id
}

resource "aws_route_table_association" "quantum_rta_2" {
  subnet_id      = aws_subnet.quantum_subnet_2.id
  route_table_id = aws_route_table.quantum_rt.id
}

# IAM Role for EKS
resource "aws_iam_role" "quantum_eks_role" {
  name = "quantum-ui-eks-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy Attachment for EKS
resource "aws_iam_role_policy_attachment" "quantum_eks_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.quantum_eks_role.name
}

# EKS Cluster
resource "aws_eks_cluster" "quantum_eks" {
  name     = var.cluster_name
  role_arn = aws_iam_role.quantum_eks_role.arn
  
  vpc_config {
    subnet_ids = [
      aws_subnet.quantum_subnet_1.id,
      aws_subnet.quantum_subnet_2.id
    ]
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.quantum_eks_policy
  ]
}

# IAM Role for EKS Node Group
resource "aws_iam_role" "quantum_node_role" {
  name = "quantum-ui-node-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy Attachments for Node Group
resource "aws_iam_role_policy_attachment" "quantum_node_policy_1" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.quantum_node_role.name
}

resource "aws_iam_role_policy_attachment" "quantum_node_policy_2" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.quantum_node_role.name
}

resource "aws_iam_role_policy_attachment" "quantum_node_policy_3" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.quantum_node_role.name
}

# EKS Node Group
resource "aws_eks_node_group" "quantum_nodes" {
  cluster_name    = aws_eks_cluster.quantum_eks.name
  node_group_name = var.node_group_name
  node_role_arn   = aws_iam_role.quantum_node_role.arn
  subnet_ids      = [
    aws_subnet.quantum_subnet_1.id,
    aws_subnet.quantum_subnet_2.id
  ]
  
  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }
  
  instance_types = ["t3.medium"]
  
  depends_on = [
    aws_iam_role_policy_attachment.quantum_node_policy_1,
    aws_iam_role_policy_attachment.quantum_node_policy_2,
    aws_iam_role_policy_attachment.quantum_node_policy_3
  ]
}

# ECR Repository for the Quantum UI Docker image
resource "aws_ecr_repository" "quantum_ui_repo" {
  name                 = "quantum-ui"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = {
    Name = "quantum-ui-ecr"
    Project = "QuantumUI"
  }
}

# S3 Bucket for quantum computation results
resource "aws_s3_bucket" "quantum_results" {
  bucket = "quantum-ui-results"
  
  tags = {
    Name = "quantum-ui-results"
    Project = "QuantumUI"
  }
}

# S3 Bucket ACL
resource "aws_s3_bucket_acl" "quantum_results_acl" {
  bucket = aws_s3_bucket.quantum_results.id
  acl    = "private"
}

# Output values
output "eks_cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.quantum_eks.endpoint
}

output "ecr_repository_url" {
  description = "URL of ECR repository"
  value       = aws_ecr_repository.quantum_ui_repo.repository_url
}

output "s3_bucket_name" {
  description = "Name of S3 bucket for quantum results"
  value       = aws_s3_bucket.quantum_results.bucket
}