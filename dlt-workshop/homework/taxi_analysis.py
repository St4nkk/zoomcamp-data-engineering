import marimo

__generated_with = "0.26.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import dlt
    import marimo as mo
    from html import escape
    from math import ceil

    def make_bar_chart(
        labels,
        values,
        details,
        title,
        x_axis_label,
        y_axis_label,
    ):
        width = 900
        height = 400
        left = 72
        right = 24
        top = 38
        bottom = 78
        plot_width = width - left - right
        plot_height = height - top - bottom
        max_value = max(values, default=1)
        if max_value <= 0:
            max_value = 1

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" role="img" '
            f'aria-label="{escape(title)}" '
            'style="width:100%;height:auto;font-family:system-ui,sans-serif;">',
            f'<text x="{left}" y="22" font-size="16" font-weight="600">'
            f"{escape(title)}</text>",
        ]

        for step in range(6):
            ratio = step / 5
            y = top + plot_height * (1 - ratio)
            tick_value = max_value * ratio
            svg.append(
                f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" '
                f'y2="{y:.1f}" stroke="#d9e0e8" stroke-width="1"/>'
            )
            svg.append(
                f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" '
                f'font-size="11" fill="#4a5560">{tick_value:,.1f}</text>'
            )

        slot_width = plot_width / max(len(values), 1)
        bar_width = slot_width * 0.72
        label_stride = max(1, ceil(len(labels) / 12))
        for index, (label, value, detail) in enumerate(
            zip(labels, values, details)
        ):
            x = left + index * slot_width + (slot_width - bar_width) / 2
            bar_height = value / max_value * plot_height
            y = top + plot_height - bar_height
            svg.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" '
                f'height="{bar_height:.1f}" rx="2" fill="#4c78a8">'
                f"<title>{escape(detail)}</title></rect>"
            )
            if index % label_stride == 0 or index == len(labels) - 1:
                svg.append(
                    f'<text x="{x + bar_width / 2:.1f}" y="{top + plot_height + 18}" '
                    f'text-anchor="middle" font-size="10" fill="#4a5560">'
                    f"{escape(label)}</text>"
                )

        svg.extend(
            [
                f'<text x="{left + plot_width / 2:.1f}" y="{height - 12}" '
                f'text-anchor="middle" font-size="12">{escape(x_axis_label)}</text>',
                f'<text x="16" y="{top + plot_height / 2:.1f}" '
                f'text-anchor="middle" font-size="12" '
                f'transform="rotate(-90 16 {top + plot_height / 2:.1f})">'
                f"{escape(y_axis_label)}</text>",
                "</svg>",
            ]
        )
        return mo.Html("".join(svg))

    return dlt, make_bar_chart, mo


@app.cell
def _(mo):
    mo.md(
        "# NYC Yellow Taxi analysis\n\n"
        "Queries use Ibis expressions against the loaded `taxi_pipeline` "
        "dataset. The average-tip chart groups trips into one-mile distance bins."
    )
    return


@app.cell
def _(dlt):
    pipeline = dlt.attach("taxi_pipeline")
    dataset = pipeline.dataset()
    trips = dataset["yellow_taxi_trips"].to_ibis()
    return dataset, trips


@app.cell
def _(dataset, trips):
    date_range_query = trips.aggregate(
        start_date=trips.trip_dropoff_date_time.date().min(),
        end_date=trips.trip_dropoff_date_time.date().max(),
    )
    payment_query = trips.aggregate(
        total_trips=trips.count(),
        credit_card_trips=(trips.payment_type == "Credit")
        .cast("int64")
        .sum(),
    )
    tips_query = trips.aggregate(total_tips=trips.tip_amt.sum())
    date_range_df = dataset(date_range_query).df()
    payment_df = dataset(payment_query).df()
    tips_df = dataset(tips_query).df()
    return date_range_df, payment_df, tips_df


@app.cell
def _(date_range_df, mo, payment_df, tips_df):
    start_date = date_range_df.loc[0, "start_date"]
    end_date = date_range_df.loc[0, "end_date"]
    total_trips = int(payment_df.loc[0, "total_trips"])
    credit_card_trips = int(payment_df.loc[0, "credit_card_trips"])
    credit_card_percentage = credit_card_trips / total_trips * 100
    total_tips = float(tips_df.loc[0, "total_tips"])
    mo.md(
        "## Homework answers\n\n"
        f"1. **Dataset date range:** {start_date} to {end_date}\n"
        f"2. **Paid by credit card:** {credit_card_percentage:.2f}% "
        f"({credit_card_trips:,} of {total_trips:,} trips)\n"
        f"3. **Total tips:** ${total_tips:,.2f}"
    )
    return


@app.cell
def _(dataset, trips):
    daily_distance_query = (
        trips.filter(
            trips.trip_pickup_date_time.notnull()
            & trips.trip_distance.notnull()
        )
        .group_by(day=trips.trip_pickup_date_time.date())
        .aggregate(total_distance=trips.trip_distance.sum())
        .order_by("day")
    )
    daily_distance_df = dataset(daily_distance_query).df()
    return (daily_distance_df,)


@app.cell
def _(daily_distance_df, make_bar_chart, mo):
    daily_labels = [
        str(day)[:10] for day in daily_distance_df["day"].tolist()
    ]
    daily_values = [
        float(value) for value in daily_distance_df["total_distance"].tolist()
    ]
    daily_details = [
        f"{label}: {value:,.2f} miles"
        for label, value in zip(daily_labels, daily_values)
    ]
    daily_distance_chart = make_bar_chart(
        daily_labels,
        daily_values,
        daily_details,
        "Total taxi distance by pickup day",
        "Pickup date",
        "Total distance (miles)",
    )
    daily_distance_chart
    return (daily_distance_chart,)


@app.cell
def _(daily_distance_df, mo):
    mo.ui.table(daily_distance_df)
    return


@app.cell
def _(dataset, trips):
    valid_tip_trips = trips.filter(
        trips.trip_distance.notnull()
        & trips.tip_amt.notnull()
        & (trips.trip_distance >= 0)
    )
    tip_by_distance_query = (
        valid_tip_trips.group_by(
            distance_miles=valid_tip_trips.trip_distance.floor()
        )
        .aggregate(
            average_tip=valid_tip_trips.tip_amt.mean(),
            trip_count=valid_tip_trips.tip_amt.count(),
        )
        .order_by("distance_miles")
    )
    tip_by_distance_df = dataset(tip_by_distance_query).df()
    return (tip_by_distance_df,)


@app.cell
def _(make_bar_chart, mo, tip_by_distance_df):
    distance_labels = [
        f"{int(distance)}–{int(distance) + 1}"
        for distance in tip_by_distance_df["distance_miles"].tolist()
    ]
    average_tips = [
        float(value) for value in tip_by_distance_df["average_tip"].tolist()
    ]
    trip_counts = [
        int(value) for value in tip_by_distance_df["trip_count"].tolist()
    ]
    tip_details = [
        f"{label} miles: ${tip:.2f} average tip, {count:,} trips"
        for label, tip, count in zip(
            distance_labels, average_tips, trip_counts
        )
    ]
    tip_by_distance_chart = make_bar_chart(
        distance_labels,
        average_tips,
        tip_details,
        "Average tip by trip-distance bin",
        "Trip distance (miles; one-mile bins)",
        "Average tip ($)",
    )
    tip_by_distance_chart
    return (tip_by_distance_chart,)


@app.cell
def _(mo, tip_by_distance_df):
    mo.ui.table(tip_by_distance_df)
    return


if __name__ == "__main__":
    app.run()
