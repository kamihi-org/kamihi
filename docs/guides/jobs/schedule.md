This guide details how to schedule actions to run at specific times using Kamihi's job scheduling feature.

## Overview

Kamihi allows you to schedule actions to be executed at specified times or intervals. This is useful for sending messages regularly to your users, performing routine maintenance tasks, or any other repetitive actions.

!!! tip
    An action does not have to return anything, so you can use scheduled actions for any kind of task, not just sending messages.

## Creating a scheduled job

Jobs are defined through the Kamihi admin interface. To create a scheduled job, follow these steps:

1. Navigate to the "Jobs" section in the Kamihi admin interface.
2. Click on "New Job".
3. Fill in the job details:
    - **Action**: Select the action you want to schedule from the dropdown list.
    - **Enabled**: Check this box to enable the job.
    - **Users**: Select the users that the job will target.
    - **Roles**: Select the roles that the job will target.
    - **Cron expression**: Define the schedule using a cron expression. You can use online tools like [crontab.guru](https://crontab.guru/) to help you create valid expressions.
    - **Args**: Provide any necessary arguments for the action in JSON format. This field only needs to be filled if the action uses reusable questions, and you only need to provide values for those parameters. This is because the job has to run without user interaction, so it cannot prompt for input.
4. Click "Save" to create the job.

## Run jobs manually

Jobs can also be run manually from the Kamihi admin interface to test their functionality or to execute them outside of their scheduled times. To run a job manually, you can select the option "Run job manually" from the Actions dropdown menu in the job row or from the job detail page.
