"""Module for doing feature engineering on the data."""
import click
import pandas as pd
from azureml.core.workspace import Workspace
from dotenv import load_dotenv, find_dotenv
from os import getenv


@click.command()
@click.option(
    "--data-file", "-f", type=click.Path(exists=True), default="data/bookings.parquet"
)
@click.option("--output-file", "-o", type=click.Path(), default="data/model_data.parquet")
def engineer_features(data_file, output_file):
    """Get booking data from microsoft graph."""
    df = pd.read_parquet(data_file)
    date_cols = ["start", "end"]

    for dc in date_cols:
        df[dc] = pd.to_datetime(df[dc])
        df[dc] = df[dc].dt.tz_localize("UTC").dt.tz_convert("America/Chicago")
        df["{}_year_int".format(dc)] = df[dc].dt.year
        df["{}_year_str".format(dc)] = df[dc].dt.year.astype(str)
        df["{}_month_str".format(dc)] = df[dc].dt.month_name()
        df["{}_month_int".format(dc)] = df[dc].dt.month
        df["{}_weekday_str".format(dc)] = df[dc].dt.day_name()
        df["{}_weekday_int".format(dc)] = df[dc].dt.weekday
        df["{}_monthday_int".format(dc)] = df[dc].dt.day
        df["{}_hour_int".format(dc)] = df[dc].dt.hour
        df["{}_hour_str".format(dc)] = df[dc].dt.hour.astype(str)

    df["duration_minutes"] = (df.end - df.start).dt.total_seconds() / 60

    df = df.loc[df.duration_minutes <= (9 * 60), :]
    df["quarter"] = df.start.dt.quarter.apply(lambda x: "Q{}".format(x))
    df["floor"] = df.location.str.extract("(1[5|6|7|9])th").astype(float)
    df = df.loc[df.floor.notnull(), :]
    df.floor = df.floor.astype(int).astype(str)
    df["half_of_month"] = df.start_monthday_int.apply(
        lambda x: "first" if x < 16 else "second"
    )

    agg_df = (
        df.groupby(
            [
                "floor",
                "start_year_int",
                "start_month_str",
                "start_month_int",
                "start_weekday_str",
                "start_monthday_int",
                "start_weekday_int",
                "half_of_month",
                "quarter",
            ]
        )
        .agg({"location": pd.Series.nunique, "duration_minutes": "sum"})
        .reset_index()
    )

    agg_df["utilization"] = agg_df.duration_minutes / (agg_df.location * 540)

    model_data = (
        agg_df.groupby(
            [
                "floor",
                "start_month_str",
                "start_month_int",
                "start_weekday_str",
                "start_weekday_int",
                "half_of_month",
                "quarter",
            ]
        )
        .utilization.median()
        .reset_index()
        .sort_values(by=["floor", "start_month_int", "start_weekday_int"])
    )
    model_data = pd.get_dummies(model_data)
    model_data.to_parquet(output_file)

    target = "utilization"
    model_data_x = model_data[[c for c in model_data if c != target]]
    model_data_y = model_data[[target]]

    model_data_x.to_parquet("data/model_data_x.parquet")
    model_data_y.to_parquet("data/model_data_y.parquet")

    load_dotenv(find_dotenv())
    ws = Workspace(
        workspace_name=getenv("AML_WORKSPACE_NAME"),
        subscription_id=getenv("AML_SUBSCRIPTION_ID"),
        resource_group=getenv("AML_RESOURCE_GROUP"),
    )
    datastore = ws.get_default_datastore()
    datastore.upload_files([
        "data/model_data_x.parquet",
        "data/model_data_y.parquet"
    ])


if __name__ == "__main__":
    engineer_features()
