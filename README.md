# Serverless AWS password reminder bot.

This framework deploys a lambda function that sends slack messages to users to reset their password before it expires.

## 1. How it works
The python bot generates AWS IAM credential reports, Formats the report into dictionary  `expiry_dict`  of users and their next password rotation date. Then adds the slack ID of all the users and creates a new dictionary ```users_dictionary``` .  

Logic within the send_slack_message() function, sends message  to slack users if their password expires in 14, 7, 3, 2, 1 days. The message body is  formatted from template.py. 

The message has 3 different formats depending on the number of days left for passwords to expire. It is prepared by the prepare_message() function. The formats include text (text_1-3) and  gifs (IMAGE_1-3).

The lambda function is scheduled to be triggered by Eventbridge every day at 10 am. 


## 2. Requirements

 - Requests layer added to lambda function
 - All Iam users with passwords must have slack_id tags
 - Slack bot token stored in Parameter store (environment variable oauth)

## 3. Deployment

Deployment is done with Serverless framework
### 1. Setup
Make sure `serverless` is installed. [See installation guide](https://serverless.com/framework/docs/providers/openwhisk/guide/installation/).

You will also need to set up your AWS credentials using environment variables or a configuration file. Please see the [this guide for more information](https://www.serverless.com/framework/docs/providers/aws/cli-reference/config-credentials).

### 2. Deploy
`serverless deploy` or `sls deploy`. `sls` is shorthand for the Serverless CLI command. You can also specifify the aws profile 

`sls deploy --aws-profile <PROFILE_NAME>` 
