# [Chef InSpec](https://docs.chef.io/inspec/)

More information can be found [here](https://docs.chef.io/inspec/platforms/#aws-platform-support-in-inspec).


To test the properties of some resources:
```
inspec exec . -t aws:// --silence-deprecations=all
```

Some resources could not be tested due to errors!

