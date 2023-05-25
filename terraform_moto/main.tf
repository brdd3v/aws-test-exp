variable "suffix" {
  default = "exp-2"
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda-${var.suffix}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_logging" {
  name   = "lambda_logging-${var.suffix}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_s3" {
  name   = "lambda_s3-${var.suffix}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "${aws_s3_bucket.bucket.arn}/*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "policy_attachment_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "policy_attachment_s3" {
  role       = aws_iam_role.iam_for_lambda.id
  policy_arn = aws_iam_policy.lambda_s3.arn
}

data "archive_file" "lambda_zip" {
  type = "zip"
  # source_file = "${path.module}/lambda_func.py"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/lambda_func.zip"
}

resource "aws_lambda_function" "lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "lambda-func-${var.suffix}"
  layers           = ["arn:aws:lambda:eu-central-1:017000801446:layer:AWSLambdaPowertoolsPythonV2:30"]
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "lambda_func.lambda_handler"
  runtime          = "python3.9"
}

resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket.arn
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.lambda.function_name}"
  retention_in_days = 14
}

resource "random_string" "bucket" {
  length  = 6
  upper   = false
  special = false
}

resource "aws_s3_bucket" "bucket" {
  bucket        = "bucket-${random_string.bucket.result}-${var.suffix}"
  force_destroy = true
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda.arn
    events              = ["s3:ObjectCreated:*"]
  }
  depends_on = [aws_lambda_permission.lambda_permission]
}

