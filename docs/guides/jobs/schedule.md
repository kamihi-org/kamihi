This guide details how to schedule actions to run at specific times using Kamihi's job scheduling feature.

## Overview

Kamihi allows you to schedule actions to be executed at specified times or intervals. This is useful for sending messages regularly to your users, performing routine maintenance tasks, or any other repetitive actions.

!!! tip
    An action does not have to return anything, so you can use scheduled actions for any kind of task, not just sending messages.

## Enabling jobs

Jobs are disabled by default in Kamihi. To enable job scheduling, you need to set the `jobs.enabled` configuration option to `true`.

=== "kamihi.yaml"

    ```yaml
    jobs:
        enabled: true
    ```

=== "`.env` file"

    ```env
    KAMIHI_JOBS__ENABLED=true
    ```

## Creating a scheduled job

Jobs, once enabled, are defined through the Kamihi admin interface. To create a scheduled job, follow these steps:

1. Navigate to the "Jobs" section in the Kamihi admin interface.
2. Click on "New Job".
3. Fill in the job details:
    - **Action**: Select the action you want to schedule from the dropdown list.
    - **Enabled**: Check this box to enable the job.
    - **Users**: Select the users that the job will target.
    - **Roles**: Select the roles that the job will target.
    - **Per user**: Check this box if you want the job to run separately for each user. See [the dedicated section](#the-per_user-option) for more details.
    - **Cron expression**: Define the schedule using a cron expression. You can use online tools like [crontab.guru](https://crontab.guru/) to help you create valid expressions.
    - **Args**: Provide any necessary arguments for the action in JSON format. More details in [the dedicated section](#job-arguments).
4. Click "Save" to create the job.

## Run jobs manually

Jobs can also be run manually from the Kamihi admin interface to test their functionality or to execute them outside of their scheduled times. To run a job manually, you can select the option "Run job manually" from the Actions dropdown menu in the job row or from the job detail page.

## The `per_user` option

The `per_user` option allows you to specify whether the job should be executed separately for each user or just once. This means several things:

- A job with a large number of users may take a long time to complete if `per_user` is enabled, as it will run the action once for each user. Be also careful that all requests to external datasources will be repeated for each user, which may lead to rate limiting or bans.
- A job with no users or roles selected and `per_user` enabled will not run at all, since there are no users to iterate over. If you plan to create jobs without specific users or roles, make sure to leave `per_user` disabled.
- If `per_user` is disabled, the parameter `user` passed to the action will be `None`, so the action will not be able to target specific users. Take this into account when designing an action that can be used both by command and in jobs and that needs the `user` parameter. In any case, the parameter `users` passed to the action will always contain the list of users selected for the job.

## Job arguments

Jobs cannot ask [reusable questions](../actions/ask-questions.md), since they can only run without user interaction. Therefore, if your action uses questions to gather input, you need to provide the answers in the job definition. To do this, you can use the Args field in the job creation form to provide a JSON object containing the necessary arguments. For example, if your action requires a `name` and a `city`, you can provide them like this:

```json
{
    "name": "John Doe",
    "city": "New York"
}
```

Make sure that:
- All the required arguments for the action to function correctly are provided. If any required arguments are missing, the job will fill them with `None`, which may lead to errors during execution.
- The keys in the JSON object match the parameter names expected by the action, since they will be passed as keyword arguments.
- The provided arguments are of the correct type, as no type validation is performed on the provided values.
