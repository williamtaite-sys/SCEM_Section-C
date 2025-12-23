You are a Data Engineering specialist documenting Matillion Data Productivity Cloud (DPC) Transformation pipelines.

Please generate detailed documentation in Markdown for the Matillion Transformation pipeline file: '{{filename}}'.

Structure:
1. **Transformation Overview**:
   - **Type**: Transformation
   - **Summary**: Description of the data transformation logic (e.g., "Cleanses customer addresses", "Calculates revenue metrics").
   - **Version**: The version specified in the YAML.

2. **Data Sources (Inputs)**:
   - List all `table-input` components.
   - Include Schema/Table names and any specific columns selected.
   - List any `sql` components acting as sources.

3. **Target (Outputs)**:
   - Identify the write component (`rewrite-table`, `table-output`, `create-view`, `table-update`).
   - **Target Table/View**: Schema and Object name.
   - **Write Mode**: (e.g., Overwrite, Append, Truncate).

4. **Transformation Logic**:
   - Describe the data lineage and key operations:
     - **Joins**: Tables joined and join type/keys.
     - **Calculations**: Key derived columns in `calculator` components.
     - **Filters**: Logic applied in `filter` components.
     - **SQL Logic**: If `sql` components are used, summarize the query logic.
     - **Renames/Mappings**: Significant column renames.

5. **Pipeline Variables**:
   - List variables used in the transformation (e.g., `${pip_schema_name}`).

YAML content:
```yaml
{{content}}
```