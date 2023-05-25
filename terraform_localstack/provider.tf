terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.63.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "2.3.0"
    }
  }

  required_version = "~> 1.4.1"
}

provider "aws" {
  region = "eu-central-1"

  default_tags {
    tags = {
      Env   = "Dev"
      Owner = "TFProviders"
    }
  }
}
