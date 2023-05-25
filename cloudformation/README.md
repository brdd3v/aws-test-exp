### NOTES


To create resources:
```
aws cloudformation deploy --stack-name="test-exp" --template-file="./resources.yml" --region="eu-central-1" --capabilities CAPABILITY_NAMED_IAM
```


To destroy resources:
```
aws cloudformation delete-stack --stack-name="test-exp" --region="eu-central-1"
```
