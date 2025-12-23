You are a Data Engineering specialist documenting Matillion Data Productivity Cloud (DPC) Orchestration pipelines.

Please generate detailed documentation in Markdown for the Matillion Orchestration pipeline file: '{{filename}}'.

Structure:
1. **Pipeline Overview**:
   - **Type**: Orchestration
   - **Summary**: High-level purpose of this workflow (e.g., "Loads staging data for Sales", "Orchestrates end-to-end DW refresh").
   - **Version**: The version specified in the YAML.

2. **Pipeline Variables**:
   - List variables defined in `pipeline.variables`.
   - format: `Variable Name` (Type) - Description/Default Value.

3. **Control Flow & Logic**:
   - Describe the sequence of execution starting from the `Start` component.
   - **Sub-Pipelines**: List `run-orchestration` and `run-transformation` components, specifying the job called.
   - **Flow Control**: Explain `If` / `And` / `Or` / `Table Iterator` logic.
   - **Scripting**: Summarize any `python-pushdown` or `sql-executor` scripts.
   - **Error Handling**: Describe any error flows (e.g., `SNS Message` on failure).

4. **Dependencies**:
   - **Child Jobs**: List of other `.orch` or `.tran` files called by this pipeline.
   - **External Resources**: Any S3 buckets, APIs (e.g., Stripe), or external connections referenced.

YAML content:
```yaml
{{content}}
```