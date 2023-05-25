describe aws_s3_bucket(bucket_name: 'bucket-abc-xyz-exp-6') do
    it { should exist }
end

describe aws_iam_role(role_name: 'iam_for_lambda-exp-6') do
    it { should exist }
end

describe aws_iam_policy('lambda_logging-exp-6') do
    it { should exist }
    it { should be_attached_to_role('iam_for_lambda-exp-6') }
    its ('statement_count') { should eq 1 }
    it { should have_statement(Action: 'logs:CreateLogGroup', Effect: 'Allow') }
    it { should have_statement(Action: 'logs:CreateLogStream', Effect: 'Allow') }
    it { should have_statement(Action: 'logs:PutLogEvents', Effect: 'Allow') }
end

describe aws_iam_policy('lambda_s3-exp-6') do
    it { should exist }
    it { should be_attached_to_role('iam_for_lambda-exp-6') }
    its ('statement_count') { should eq 1 }
    it { should have_statement(Action: 's3:GetObject', 
                              Resource: 'arn:aws:s3:::bucket-abc-xyz-exp-6/*', 
                              Effect: 'Allow') }
end

# describe aws_lambda_permission(function_name: 'lambda-func-exp-6', Sid: 'AllowExecutionFromS3Bucket') do
#     its ('action') { should eq 'lambda:InvokeFunction' }
#     its ('principal') { should eq 's3.amazonaws.com' }
# end

# describe aws_lambda('lambda-func-exp-6') do
#     it { should exist}
#     its ('handler') { should eq 'lambda_func.lambda_handler'}
#     its ('runtime') { should eq 'python3.9' }
# end

# describe aws_cloudwatch_log_group(log_group_name: '/aws/lambda/lambda-func-exp-6') do
#     it { should exist }
#     its ('retention_in_days') { should eq 14 }
# end
