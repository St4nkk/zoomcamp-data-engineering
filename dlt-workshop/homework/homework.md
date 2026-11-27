## Questions

Once your pipeline has run successfully, use the methods covered in the workshop to investigate the following:

- **dlt Dashboard**: `dlt pipeline taxi_pipeline show`
- **dlt MCP Server**: Ask the agent questions about your pipeline
- **Marimo Notebook**: Build visualizations and run queries

We challenge you to try out the different methods explored in the workshop when answering these questions to see what works best for you. Feel free to share your thoughts on what worked (or didn't) in your submission!

### Question 1: What is the start date and end date of the dataset?

- 2009-01-01 to 2009-01-31
- **2009-06-01 to 2009-07-01**
- 2024-01-01 to 2024-02-01
- 2024-06-01 to 2024-07-01

Chat answer: The dataset’s date range is 2009-06-01 to 2009-07-01

```sql
SELECT
  MIN(trip_dropoff_date_time::DATE) AS first_date,
  MAX(trip_dropoff_date_time::DATE) AS last_date
FROM "yellow_taxi_trips"
```
### Question 2: What proportion of trips are paid with credit card?

- 16.66%
- **26.66%**
- 36.66%
- 46.66%

Chat answer: 26.66% of trips were paid by credit card: 2,666 out of 10,000 trips.

```sql
SELECT
  COUNT(CASE WHEN payment_type = 'Credit' THEN 1 END) * 100.0 / COUNT(*) AS credit_card_paid_pct
FROM "yellow_taxi_trips"
```

### Question 3: What is the total amount of money generated in tips?

- $4,063.41
- **$6,063.41**
- $8,063.41
- $10,063.41


Chat answer: The total amount generated in tips was $6,063.41.

```sql
SELECT
  ROUND(SUM(tip_amt), 2) AS total_tip
FROM "yellow_taxi_trips
```





