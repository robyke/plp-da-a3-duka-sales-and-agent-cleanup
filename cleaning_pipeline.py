import pandas as pd


def clean_agent_data(txns, agents):
    """
    Clean mobile-money agent transaction data and merge it with the agent register.

    Parameters
    ----------
    txns : pandas.DataFrame
        Raw agent transaction data.
    agents : pandas.DataFrame
        Agent register containing agent_id and county.

    Returns
    -------
    clean_df : pandas.DataFrame
        Cleaned and merged transaction data.
    log : list
        Cleaning log describing the changes made.
    """

    log = []

    # ---------------------------------------------------------
    # 1. Work on copies so raw data is not changed
    # ---------------------------------------------------------
    clean = txns.copy()
    agent_lookup = agents.copy()

    original_rows = len(clean)

    # ---------------------------------------------------------
    # 2. Remove duplicate transaction IDs
    # ---------------------------------------------------------
    duplicate_count = clean.duplicated(subset=["txn_id"]).sum()

    clean = (
        clean
        .drop_duplicates(subset=["txn_id"])
        .copy()
    )

    log.append(
        f"Removed {duplicate_count} duplicate transaction IDs."
    )

    # ---------------------------------------------------------
    # 3. Standardise transaction type
    # ---------------------------------------------------------
    clean["txn_type"] = (
        clean["txn_type"]
        .astype("string")
        .str.strip()
        .str.lower()
        .map({
            "deposit": "Deposit",
            "withdrawal": "Withdrawal"
        })
    )

    invalid_txn_types = clean["txn_type"].isna().sum()

    log.append(
        f"Standardised transaction type to Deposit and Withdrawal; "
        f"{invalid_txn_types} invalid transaction types remained."
    )

    # ---------------------------------------------------------
    # 4. Convert amount to numeric
    # ---------------------------------------------------------
    clean["amount"] = pd.to_numeric(
        clean["amount"],
        errors="coerce"
    )

    # Flag missing or invalid amounts before filling
    clean["amount_imputed"] = clean["amount"].isna()

    missing_amounts = clean["amount_imputed"].sum()

    # Median calculated from valid amounts
    median_amount = clean["amount"].median()

    clean["amount"] = clean["amount"].fillna(
        median_amount
    )

    log.append(
        f"Imputed {missing_amounts} missing or invalid amounts "
        f"using the median amount of KES {median_amount:.2f}."
    )

    # ---------------------------------------------------------
    # 5. Convert transaction dates
    # ---------------------------------------------------------
    clean["txn_date"] = pd.to_datetime(
        clean["txn_date"].astype("string").str.replace("/", "-", regex=False),
        errors="coerce"
    )

    invalid_dates = clean["txn_date"].isna().sum()

    log.append(
        f"Converted transaction dates to datetime; "
        f"{invalid_dates} invalid dates remained."
    )

    # ---------------------------------------------------------
    # 6. Flag amount outliers using IQR
    # ---------------------------------------------------------
    q1 = clean["amount"].quantile(0.25)
    q3 = clean["amount"].quantile(0.75)

    iqr = q3 - q1

    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr

    clean["is_outlier"] = (
        (clean["amount"] < lower_fence)
        | (clean["amount"] > upper_fence)
    )

    outlier_count = clean["is_outlier"].sum()

    log.append(
        f"Flagged {outlier_count} amount outliers using the IQR method."
    )

    # ---------------------------------------------------------
    # 7. Prepare agent register
    # ---------------------------------------------------------
    agent_lookup["onboarded"] = pd.to_datetime(
        agent_lookup["onboarded"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 8. Merge transactions with agent register
    # Left join keeps every valid transaction
    # ---------------------------------------------------------
    clean = clean.merge(
        agent_lookup[["agent_id", "county", "onboarded"]],
        on="agent_id",
        how="left",
        validate="many_to_one",
        indicator=True
    )

    unknown_agents = (
        clean["_merge"] == "left_only"
    ).sum()

    log.append(
        f"Found {unknown_agents} transactions with unknown agents."
    )

    clean["county"] = clean["county"].fillna(
        "Unknown"
    )

    clean = clean.drop(columns=["_merge"])

    # ---------------------------------------------------------
    # 9. Final validation
    # ---------------------------------------------------------
    final_rows = len(clean)

    log.append(
        f"Row count changed from {original_rows} raw rows "
        f"to {final_rows} cleaned rows."
    )

    return clean, log