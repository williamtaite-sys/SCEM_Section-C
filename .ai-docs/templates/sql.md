You are a database specialist writing technical documentation.

Please generate detailed documentation in Markdown for the SQL file: '{{filename}}'.

Structure:
1. **Query Overview**: A summary of what this SQL script or query accomplishes.
2. **Tables & Views Involved**: List the primary tables, views, or data sources accessed or modified.
3. **Key Logic**: Explain significant operations (e.g., complex JOINs, CTEs, window functions, aggregations, or specific business logic filters).
4. **Parameters**: List any variables or parameters (e.g., `?`, `:variable`, or stored procedure arguments) used in the script.
5. **Output/Impact**: Describe the resulting dataset (columns/granularity) for SELECT queries, or the data modification impact for INSERT/UPDATE/DELETE statements.

SQL content:
```sql
{{content}}
```