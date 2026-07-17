# This is deliberately weak Terraform code to feed Gabrielle
# in order to get recommended code revisions

resource "aws_s3_bucket" "gr-example" {
  bucket = "mybucket"
}