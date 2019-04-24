"""Module for downloading booking data from Microsoft Graph."""
from copy import deepcopy
from datetime import datetime, timedelta
from itertools import chain
from os import getenv

import click
import pandas as pd
import requests
from dotenv import find_dotenv, load_dotenv
from yaml import safe_load


@click.command()
@click.option("--tenant-id", "-t", type=click.STRING, default="")
@click.option("--client_id", "-i", type=click.STRING, default="")
@click.option("--client_secret", "-s", type=click.STRING, default="")
@click.option("--years_in_past", "-y", type=click.INT, default=5)
@click.option("--config-file", "-c", type=click.File("r"), default="config.yml")
@click.option("--output-file", "-o", type=click.Path(), default="bookings.parquet")
def get_data(
    tenant_id, client_id, client_secret, years_in_past, config_file, output_file
):
    """Get booking data from microsoft graph."""
    max_days_in_query = 62
    max_batch = 10

    rooms = safe_load(config_file)["rooms"]

    required_args = [tenant_id, client_id, client_secret]

    if not (all(required_args)):
        load_dotenv(find_dotenv())

        if not (all([getenv(x) for x in ["TENANT_ID", "CLIENT_ID", "CLIENT_SECRET"]])):
            raise ValueError("Required arguments not found")
        else:
            tenant_id = getenv("TENANT_ID")
            client_id = getenv("CLIENT_ID")
            client_secret = getenv("CLIENT_SECRET")

    auth_url = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token".format(
        tenant_id=tenant_id
    )

    payload = {
        "grant_type": "client_credentials",
        "client_secret": client_secret,
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/.default",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(auth_url, data=payload, headers=headers)
    response.raise_for_status()

    access_token = response.json()["access_token"]

    end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = end.replace(year=end.year - years_in_past)

    day_range = [start + timedelta(days=i) for i in range((end - start).days + 1)]

    date_chunks = [
        day_range[i : i + max_days_in_query + 1]
        for i in range(0, len(day_range), max_days_in_query)
    ]

    graph_url = "users/cody.bushnell@cbre.com/calendar/getschedule"

    graph_body_template = {
        "Schedules": rooms,
        "StartTime": {"dateTime": "", "timeZone": "Central Standard Time"},
        "EndTime": {"dateTime": "", "timeZone": "Central Standard Time"},
        "availabilityViewInterval": "15",
    }

    graph_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(access_token),
    }

    request_chunks = []

    reqs = {"requests": []}

    for idx, dc in enumerate(date_chunks):
        body = deepcopy(graph_body_template)
        body["StartTime"]["dateTime"] = dc[0].isoformat()
        body["EndTime"]["dateTime"] = dc[-1].isoformat()
        print(dc[-1])
        req = {
            "id": str(idx + 1),
            "url": graph_url,
            "body": body,
            "method": "POST",
            "headers": graph_headers,
        }
        if len(reqs["requests"]) >= max_batch:
            request_chunks.append(reqs)
            reqs = {"requests": []}
        else:
            reqs["requests"].append(req)

    if len(reqs["requests"]) > 0:
        request_chunks.append(reqs)

    batch_url = "https://graph.microsoft.com/beta/$batch"

    responses = []
    for request_chunk in request_chunks:
        response = requests.post(batch_url, json=request_chunk, headers=graph_headers)
        responses += list(
            chain.from_iterable(
                [
                    list(
                        chain.from_iterable(
                            [y["scheduleItems"] for y in x["body"]["value"]]
                        )
                    )
                    for x in response.json()["responses"]
                ]
            )
        )

    responses = [
        dict(
            location=r["location"],
            start=r["start"]["dateTime"],
            end=r["end"]["dateTime"],
        )
        for r in responses
        if "location" in r
    ]

    pd.DataFrame(responses).to_parquet(output_file, index=None)


if __name__ == "__main__":
    get_data()
