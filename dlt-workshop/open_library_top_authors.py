import marimo

__generated_with = "0.26.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import dlt
    import ibis
    import marimo as mo
    from html import escape

    return dlt, escape, ibis, mo


@app.cell
def _(mo):
    mo.md(
        "# Top 10 Open Library authors\n\n"
        "This chart counts distinct books per author from the loaded "
        "`open_library_pipeline` dataset. Author names are stored in the "
        "`books__author_name` child table."
    )
    return


@app.cell
def _(dlt):
    pipeline = dlt.attach("open_library_pipeline")
    dataset = pipeline.dataset()
    books = dataset["books"].to_ibis()
    author_rows = dataset["books__author_name"].to_ibis()
    return author_rows, books, dataset


@app.cell
def _(author_rows, books, dataset, ibis):
    book_authors = books.join(
        author_rows,
        books._dlt_id == author_rows._dlt_parent_id,
    )
    top_authors = (
        book_authors.filter(
            author_rows.value.notnull() & (author_rows.value != "")
        )
        .group_by(author=author_rows.value)
        .aggregate(book_count=books.key.nunique())
        .order_by(ibis.desc("book_count"), ibis.asc("author"))
        .limit(10)
    )
    top_authors_df = dataset(top_authors).df()
    return (top_authors_df,)


@app.cell
def _(escape, mo, top_authors_df):
    max_count = max(top_authors_df["book_count"], default=1)
    bars = []
    for row in top_authors_df.to_dict(orient="records"):
        author = escape(str(row["author"]))
        count = int(row["book_count"])
        width = count / max_count * 100
        bars.append(
            f"""
            <div style="display:grid;grid-template-columns:minmax(0,240px) 1fr 40px;
                        gap:12px;align-items:center;margin:10px 0;">
              <span style="overflow-wrap:anywhere;">{author}</span>
              <div style="background:#e8edf3;border-radius:4px;height:20px;">
                <div style="background:#4c78a8;border-radius:4px;height:20px;
                            width:{width:.1f}%;"></div>
              </div>
              <strong>{count}</strong>
            </div>
            """
        )
    chart = mo.Html(
        '<div style="font-family:system-ui,sans-serif;">'
        '<p>Books per author</p>'
        + "".join(bars)
        + "</div>"
    )
    chart
    return (chart,)


if __name__ == "__main__":
    app.run()
