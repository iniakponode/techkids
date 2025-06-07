# TechKids

This project powers the TechKids API and website. A background scheduler
periodically publishes `SocialMediaPost` entries when they become due.

## Running the Scheduler

The scheduler starts automatically with the FastAPI application. It checks for
social media posts whose `scheduled_at` time is in the past and whose status is
`draft`. After attempting to publish the post, the status is updated to either
`posted` or `failed`.

Environment variables control the scheduler behaviour and API credentials. The
most important ones are:

- `POST_SCHEDULER_INTERVAL` – interval in seconds between checks (default `60`).
- `FACEBOOK_API_TOKEN`, `X_API_TOKEN`, `INSTAGRAM_API_TOKEN` – credentials used
  by the placeholder posting functions.

Simply run the FastAPI app as usual (for example with `uvicorn main:app`) and
the scheduler will run in the background.
