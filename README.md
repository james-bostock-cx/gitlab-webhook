# Introduction

The **gitlab-webhook-flask** application is a *proof of concept*
[Flask](https://flask.palletsprojects.com/en/2.0.x/) application
which, on receipt of a branch deletion push event Webhook request from
GitLab, deletes the Checkmarx CxSAST project associated with the
branch.

**Note:** GitLab does not document the payload of a push event Webhook
request sent on branch deletion. This application uses information
provided in a comment to [an
issue](https://gitlab.com/gitlab-org/gitlab/-/issues/25305) raised on
GitLab to determine that a given push event corresponds to the
deletion of a branch.

# Running

When run outside of a Docker container, the CxSAST details can also be
configured in a `config.ini` file located in the current user’s home
directory (see the [Checkmarx Python
SDK](https://github.com/checkmarx-ts/checkmarx-python-sdk) for more
information).

## Docker

The `Dockerfile` and `docker-compose.yml` files can be used to create
and run a Docker container running the application.

**Note:** currently the application is run in *dev* mode. For a
production environment, a server such as **nginx** should be used.

The easiest way to run the application using Docker is to use the
**docker-compose** command:

```
$ docker-compose up -d
```

This will build the Docker image, if it does not already exist, and
run it. The `docker-compose.yml` file expects that a
`gitlab-webhook-flask.env` file be present in the current directory
specifying the environment variables with which to configure the
application (see below).

## Windows PowerShell

To run the application, set the appropriate environment variables (see
below) and then run the following commands:

```
PS C\...\gitlab-webhook> pipenv shell
PS C\...\gitlab-webhook> $Env:FLASK_APP = 'gitlab-webhook-flask'
PS C\...\gitlab-webhook> flask run
```

## Configuration

The **gitlab-webhook-flask** application is configured via environment
variables. The following sections describe this configuration.

### Project Name

The name of the project to be deleted is constructed by retrieving the
`CX_PROJECT_PATTERN` environment variable and substituting the
following strings with the corresponding values from the Webhook
payload. If the `CX_PROJECT_PATTERN` environment variable is not set,
a default value of `{project_path_with_namespace}-{branch_name}` is
used.

- `{branch_name}`: the last component of the top-level `refs`
  property. For example, the `{branch_name}` value for the sample
  Webhook request below would be `test001`.
- `{project_name}`: the value of the `name` property of the
  `property`. For example, the `{project_name}` value for the sample
  Webhook request below would be `webhook-test`.
- `{project_namespace}`: the value of the `namespace` property of the
  `project` property. For example, the `{project_namespace}` value for
  the sample Webhook request below would be `James Bostock`.
- `{project_path_with_namespace}`: the value of the
  `project_path_with_namespace` property of the `project`
  property. Note that CxSAST project names may not contain forward
  slashes so these are replaced by dashes. For example, the
  `{project_path_with_namespace}` value for the sample Webhook request
  below would be `james-bostock-cx-webhook-test`.

### GitLab Token

The application expects a token to have been configured for the
Webhook. GitLab sends this token in the `X-GitLab-Token` HTTP
header. To specify the value of the token, use the `GITLAB_TOKEN`
environment variable.

### Logging

The log level can be specified by setting the `LOG_LEVEL` environment
variable. If not specified, a default level of `WARN` is used.

### Checkmarx Python SDK Configuration

The following environment variables must be used to configure the
Checkmarx Python SDK:

- `cxsast_base_url`
- `cxsast_username`
- `cxsast_password`

# Sample Webhook Payload

Here is a sample GitLab push event payload sent on deletion of the
`test001` branch.

```
{
  "object_kind": "push",
  "event_name": "push",
  "before": "ba3ed382b9b76858fa85269565083a657f1b2174",
  "after": "0000000000000000000000000000000000000000",
  "ref": "refs/heads/test001",
  "checkout_sha": null,
  "message": null,
  "user_id": 8133674,
  "user_name": "James Bostock",
  "user_username": "james-bostock-cx",
  "user_email": "",
  "user_avatar": "https://gitlab.com/uploads/-/system/user/avatar/8133674/avatar.png",
  "project_id": 28279834,
  "project": {
    "id": 28279834,
    "name": "webhook-test",
    "description": "A dummy project for testing GitLab Webhooks",
    "web_url": "https://gitlab.com/james-bostock-cx/webhook-test",
    "avatar_url": null,
    "git_ssh_url": "git@gitlab.com:james-bostock-cx/webhook-test.git",
    "git_http_url": "https://gitlab.com/james-bostock-cx/webhook-test.git",
    "namespace": "James Bostock",
    "visibility_level": 0,
    "path_with_namespace": "james-bostock-cx/webhook-test",
    "default_branch": "main",
    "ci_config_path": "",
    "homepage": "https://gitlab.com/james-bostock-cx/webhook-test",
    "url": "git@gitlab.com:james-bostock-cx/webhook-test.git",
    "ssh_url": "git@gitlab.com:james-bostock-cx/webhook-test.git",
    "http_url": "https://gitlab.com/james-bostock-cx/webhook-test.git"
  },
  "commits": [],
  "total_commits_count": 0,
  "push_options": {
  },
  "repository": {
    "name": "webhook-test",
    "url": "git@gitlab.com:james-bostock-cx/webhook-test.git",
    "description": "A dummy project for testing GitLab Webhooks",
    "homepage": "https://gitlab.com/james-bostock-cx/webhook-test",
    "git_http_url": "https://gitlab.com/james-bostock-cx/webhook-test.git",
    "git_ssh_url": "git@gitlab.com:james-bostock-cx/webhook-test.git",
    "visibility_level": 0
  }
}
```

# References

- [Checkmarx Python SDK](https://github.com/checkmarx-ts/checkmarx-python-sdk)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [GitLab issue #25305: Trigger webhook on branch removal](https://gitlab.com/gitlab-org/gitlab/-/issues/25305)
- [Write Gitlab Webhook using Flask to automatically pull code to the server](https://www.programmersought.com/article/9998712133/)
