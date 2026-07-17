# AWS Bedrock Setup:
In order to access AWS Bedrock you either need to do an AWS Skills Builder course, or you have to setup your personal AWS account to have an SSO user with access to AWS Bedrock.

## High-Level
We are going to be settig up an SSO user through the AWS Identity Center (previously AWS SSO). This guide assumes you have an Admin (non-root) account access.

#### Identity Center
- Permissions Sets => This is what is used to anchor Groups and Users to individual AWS IAM Account policies.
- Users => these are the unique user (unique on email) who are registered in the Identity Center. These users can come from a federated 3rd party Adminstrator.
- Groups => these are groups of users in the Identity Center. These users can come from a federated 3rd party Adminstrator.
- Accounts => these are the accounts the IAM Identity Center has access to manage permissions for.

## Setup
1. Create an AWS Identity Center User (not an IAM User): AWS Identity Center => User => Add User
2. Attach the new User to the AWS Account: AWS Identity Center => AWS Accounts => <your acccount name> => Assign Users or Groups
3. Next create a group and attached the user to the group. Name the group based on the use case.
4. Repeat Step 2 , but with the new Group instead.
** IAM Policy Time
5. Got to AWS IAM and Create a managed policy for the Group:
    Options:
    A. Direct Policy where you attached the services and access rules directly to a policy and then Identity Center Permissons Set.
    B. Role Based Policies where you create an SSO group/user with no direct access, but can assume a set of roles which has access to the specific areas and services.


### Direct Policy
1. Create a custom managed policy with the select permission you want the group/user to have access to.
2. Research AWS pre-created managed policies for example: AWSBedrockFullAccess you may want to directly attach.
3. Go to the Identity Center under Permission Sets.
4. Click the "Create Permission Set" then select "Custom Permission Set"
5. Attach the managed policies from step 1 + 2
6. Finish the Review + Creation of the Permission Set.
7. Go  to AWS Identity Center => AWS Accounts => Change Permission Set
8. In here you will assign the Permission Set to the Group or User.
9. Test the permissions by trying an SSO Login to AWS
10. Once setup do a quick boto3 client/session check for the expected services in your policy.

### Role Base Policy
1. Go to the Identity Center under Permission Sets.
2. Click the "Create Permission Set" then select "Custom Permission Set"
3. Attach the managed policies from step 1 + 2
4. Finish the Review + Creation of the Permission Set.
5. Go  to AWS Identity Center => AWS Accounts => Change Permission Set
6. In here you will assign the Permission Set to the Group or User.
**Role Creation Time**
7. Go to IAM Roles to create a new role.
8. Add as a trusted entity the Permission Set ARN (will be an IAM role named "AWSReservedSSO_%")
9. In a separate window 
    a. Create a custom managed policy with the select permission you want the group/user to have access to.
    b. Research AWS pre-created managed policies for example: AWSBedrockFullAccess you may want to directly attach.
10. Add the policies to the role
11. Repeat 7 - 10 for however many roles you want to create.
12. Create a final policy called "<your identity center group name>-assumable-roles-policy" including all role ARNs created.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole"
            ],
            "Resource": [
                "arn:aws:iam::11111111111:role/terraform-deployer-role",
                "arn:aws:iam::11111111111:role/bedrock-ai-lead-role"
            ]
        }
    ]
}
```
13. Go back to the Identity Center to attach this new policy to you permission set.
** SSO Time (with a small trick) **
14. Complete your normal CLI SSO configure
15. Next access the .aws/config file and alter to allow for a chained role based login in.
**Example:**
```bash
# Linux
cat ~/.aws/config
# Windows
notepad .aws\config
```
16. Alter the file  to have the base "sso-session" for you Identity Center user, then add the "profiles" per role ARN you want to assume.
```text
[default]
region = us-east-1
output = json
[sso-session learn-terraform]
sso_start_url = https://d-xxxxxxxxxx.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access
[profile learn-terraform]
sso_session = learn-terraform
sso_account_id = 11111111111
sso_role_name = terraform-deployer-permission
region = us-east-1
output = json
[profile learn-bedrock]
role_arn = arn:aws:iam::xxxxxxxxxx:role/bedrock-ai-lead-role
source_profile = learn-terraform
region = us-east-1
output = json
```