import reflex as rx
import polars as pl
import logging
from typing import Optional, Any
from app.utils.db import db_config


def get_polars_db_connection_string() -> str:
    """Constructs the database connection string for use with Polars/connectorx."""
    return f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"


def load_data_in_bulk(
    query: str, partition_on: Optional[str] = None
) -> Optional[pl.DataFrame]:
    """
    Loads a large dataset from the database into a Polars DataFrame using connectorx.

    Args:
        query: The SQL query to execute.
        partition_on: The column to partition the query on for parallel execution.

    Returns:
        A Polars DataFrame containing the query results, or None if an error occurs.
    """
    conn_str = get_polars_db_connection_string()
    try:
        logging.info(f"Executing bulk data query with Polars: {query[:100]}...")
        df = pl.read_database_uri(
            query, conn_str, engine="connectorx", partition_on=partition_on
        )
        logging.info(f"Successfully loaded {len(df)} rows into DataFrame.")
        return df
    except Exception as e:
        logging.exception(f"Failed to load data in bulk using Polars: {e}")
        return None


def execute_analytics_query(query: str) -> Optional[pl.DataFrame]:
    """
    Executes a complex analytical or aggregation query and returns the result as a Polars DataFrame.

    Args:
        query: The SQL aggregation query to execute.

    Returns:
        A Polars DataFrame with the analytics results, or None on failure.
    """
    conn_str = get_polars_db_connection_string()
    try:
        logging.info(f"Executing analytics query: {query[:100]}...")
        df = pl.read_database_uri(query, conn_str, engine="connectorx")
        logging.info(f"Analytics query returned {len(df)} rows.")
        return df
    except Exception as e:
        logging.exception(f"Analytics query failed: {e}")
        return None


def export_df_to_csv(df: pl.DataFrame, filename: str = "export.csv") -> Optional[bytes]:
    """
    Exports a Polars DataFrame to a CSV file in memory.

    Args:
        df: The DataFrame to export.
        filename: The name of the file for the user download (not used for path).

    Returns:
        The CSV data as bytes, or None if an error occurs.
    """
    try:
        list_cols_to_str = [
            pl.col(c).list.join(", ").alias(c)
            for c in df.columns
            if isinstance(df[c].dtype, pl.datatypes.List)
        ]
        if list_cols_to_str:
            df = df.with_columns(list_cols_to_str)
        csv_buffer = df.write_csv(None)
        return csv_buffer.encode("utf-8")
    except Exception as e:
        logging.exception(f"Failed to export DataFrame to CSV: {e}")
        return None


def prepare_for_comparison(nct_ids: list[str]) -> Optional[pl.DataFrame]:
    """
    Fetches and prepares data for a side-by-side comparison of multiple clinical trials.

    This function is a placeholder for a more complex implementation that would join
    multiple tables (studies, conditions, interventions, etc.) to create a comprehensive
    comparison view.

    Args:
        nct_ids: A list of NCT IDs to compare.

    Returns:
        A Polars DataFrame with key comparable fields, or None on failure.
    """
    if not nct_ids:
        return pl.DataFrame()
    query = f"""    SELECT \n        nct_id, brief_title, overall_status, phase, study_type, enrollment,\n        start_date, completion_date\n    FROM ctgov.studies\n    WHERE nct_id IN ({", ".join([f"'{nid}'" for nid in nct_ids])})    """
    return execute_analytics_query(query)


def get_phase_distribution() -> Optional[pl.DataFrame]:
    query = """
    SELECT phase, COUNT(*) as count
    FROM ctgov.studies
    WHERE phase IS NOT NULL AND phase != ''
    GROUP BY phase
    ORDER BY phase
    """
    return execute_analytics_query(query)


def get_status_distribution() -> Optional[pl.DataFrame]:
    query = """
    SELECT overall_status as status, COUNT(*) as count
    FROM ctgov.studies
    WHERE overall_status IS NOT NULL
    GROUP BY overall_status
    ORDER BY count DESC
    LIMIT 10
    """
    return execute_analytics_query(query)


def get_enrollment_trends() -> Optional[pl.DataFrame]:
    query = """
    SELECT 
        phase, 
        AVG(enrollment) as avg_enrollment,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY enrollment) as median_enrollment
    FROM ctgov.studies
    WHERE enrollment IS NOT NULL AND phase IS NOT NULL AND phase != ''
    GROUP BY phase
    ORDER BY phase
    """
    return execute_analytics_query(query)


def get_geographic_distribution() -> Optional[pl.DataFrame]:
    query = """
    SELECT country, COUNT(DISTINCT nct_id) as count
    FROM ctgov.facilities
    WHERE country IS NOT NULL
    GROUP BY country
    ORDER BY count DESC
    LIMIT 10
    """
    return execute_analytics_query(query)


def get_top_sponsors() -> Optional[pl.DataFrame]:
    query = """
    SELECT name, COUNT(*) as count
    FROM ctgov.sponsors
    WHERE agency_class = 'INDUSTRY'
    GROUP BY name
    ORDER BY count DESC
    LIMIT 10
    """
    return execute_analytics_query(query)


def get_timeline_data() -> Optional[pl.DataFrame]:
    query = """
    SELECT 
        EXTRACT(YEAR FROM start_date) as year, 
        COUNT(*) as count
    FROM ctgov.studies
    WHERE start_date IS NOT NULL AND EXTRACT(YEAR FROM start_date) >= 2000
    GROUP BY year
    ORDER BY year
    """
    return execute_analytics_query(query)


def get_top_conditions() -> Optional[pl.DataFrame]:
    query = """
    SELECT name, COUNT(*) as count
    FROM ctgov.conditions
    GROUP BY name
    ORDER BY count DESC
    LIMIT 10
    """
    return execute_analytics_query(query)


def get_top_interventions() -> Optional[pl.DataFrame]:
    query = """
    SELECT name, COUNT(*) as count
    FROM ctgov.interventions
    WHERE intervention_type = 'DRUG'
    GROUP BY name
    ORDER BY count DESC
    LIMIT 10
    """
    return execute_analytics_query(query)


def get_us_state_distribution() -> Optional[pl.DataFrame]:
    query = """
    SELECT state, COUNT(DISTINCT nct_id) as count
    FROM ctgov.facilities
    WHERE country = 'United States' AND state IS NOT NULL
    GROUP BY state
    ORDER BY count DESC
    LIMIT 20
    """
    return execute_analytics_query(query)


def get_trial_duration_distribution() -> Optional[pl.DataFrame]:
    query = """
    SELECT 
        phase,
        AVG(completion_date - start_date) as avg_duration_days,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY completion_date - start_date) as median_duration_days
    FROM ctgov.studies
    WHERE start_date IS NOT NULL AND completion_date IS NOT NULL AND phase IS NOT NULL AND phase != ''
      AND completion_date > start_date
    GROUP BY phase
    ORDER BY phase
    """
    return execute_analytics_query(query)


def get_design_patterns() -> Optional[pl.DataFrame]:
    query = """
    SELECT 
        masking,
        COUNT(*) as count
    FROM ctgov.designs
    WHERE masking IS NOT NULL
    GROUP BY masking
    ORDER BY count DESC
    """
    return execute_analytics_query(query)


def get_trending_conditions() -> Optional[pl.DataFrame]:
    query = """
    WITH yearly_counts AS (
        SELECT 
            c.name,
            EXTRACT(YEAR FROM s.start_date) as year,
            COUNT(*) as trial_count
        FROM ctgov.conditions c
        JOIN ctgov.studies s ON c.nct_id = s.nct_id
        WHERE s.start_date >= '2020-01-01'
        GROUP BY c.name, year
    )
    SELECT name, SUM(trial_count) as total_trials
    FROM yearly_counts
    GROUP BY name
    ORDER BY total_trials DESC
    LIMIT 10
    """
    return execute_analytics_query(query)


def get_us_state_distribution() -> Optional[pl.DataFrame]:
    query = """
    SELECT state, COUNT(DISTINCT nct_id) as count
    FROM ctgov.facilities
    WHERE country = 'United States' AND state IS NOT NULL
    GROUP BY state
    ORDER BY count DESC
    LIMIT 20
    """
    return execute_analytics_query(query)


def get_trial_duration_distribution() -> Optional[pl.DataFrame]:
    query = """
    SELECT 
        phase,
        AVG(completion_date - start_date) as avg_duration_days,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY completion_date - start_date) as median_duration_days
    FROM ctgov.studies
    WHERE start_date IS NOT NULL AND completion_date IS NOT NULL AND phase IS NOT NULL AND phase != ''
      AND completion_date > start_date
    GROUP BY phase
    ORDER BY phase
    """
    return execute_analytics_query(query)


def get_design_patterns() -> Optional[pl.DataFrame]:
    query = """
    SELECT 
        masking,
        COUNT(*) as count
    FROM ctgov.designs
    WHERE masking IS NOT NULL
    GROUP BY masking
    ORDER BY count DESC
    """
    return execute_analytics_query(query)


def get_trending_conditions() -> Optional[pl.DataFrame]:
    query = """
    WITH yearly_counts AS (
        SELECT 
            c.name,
            EXTRACT(YEAR FROM s.start_date) as year,
            COUNT(*) as trial_count
        FROM ctgov.conditions c
        JOIN ctgov.studies s ON c.nct_id = s.nct_id
        WHERE s.start_date >= '2020-01-01'
        GROUP BY c.name, year
    )
    SELECT name, SUM(trial_count) as total_trials
    FROM yearly_counts
    GROUP BY name
    ORDER BY total_trials DESC
    LIMIT 10
    """
    return execute_analytics_query(query)