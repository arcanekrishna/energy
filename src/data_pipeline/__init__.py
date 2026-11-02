"""
data_pipeline — Data ingestion, validation, synthetic generation, and
feature engineering for IEX DAM / RTM electricity markets.
"""

try:
    from .iex_schema import (
        BLOCKS_PER_DAY,
        CERC_PRICE_CAP,
        CERC_PRICE_FLOOR,
        GridRegime,
        MarketRecord,
        SESSIONS_PER_DAY,
        block_to_time,
        session_to_blocks,
        validate_record,
    )
    from .iex_loader import (
        load_dam_from_kaggle,
        load_mendeley_demand,
        load_rtm_from_csv,
        load_zenodo_weather,
        merge_dam_rtm,
        standardize_columns,
    )
    from .synthetic_generator import (
        generate_full_synthetic,
        generate_synthetic_rtm,
    )
    from .feature_engine import (
        build_features,
        get_feature_columns,
        validate_no_leakage,
    )
except ImportError:
    from src.data_pipeline.iex_schema import (
        BLOCKS_PER_DAY,
        CERC_PRICE_CAP,
        CERC_PRICE_FLOOR,
        GridRegime,
        MarketRecord,
        SESSIONS_PER_DAY,
        block_to_time,
        session_to_blocks,
        validate_record,
    )
    from src.data_pipeline.iex_loader import (
        load_dam_from_kaggle,
        load_mendeley_demand,
        load_rtm_from_csv,
        load_zenodo_weather,
        merge_dam_rtm,
        standardize_columns,
    )
    from src.data_pipeline.synthetic_generator import (
        generate_full_synthetic,
        generate_synthetic_rtm,
    )
    from src.data_pipeline.feature_engine import (
        build_features,
        get_feature_columns,
        validate_no_leakage,
    )

__all__ = [
    # schema
    "BLOCKS_PER_DAY",
    "SESSIONS_PER_DAY",
    "CERC_PRICE_CAP",
    "CERC_PRICE_FLOOR",
    "GridRegime",
    "MarketRecord",
    "block_to_time",
    "session_to_blocks",
    "validate_record",
    # loaders
    "standardize_columns",
    "load_dam_from_kaggle",
    "load_rtm_from_csv",
    "load_mendeley_demand",
    "load_zenodo_weather",
    "merge_dam_rtm",
    # synthetic
    "generate_synthetic_rtm",
    "generate_full_synthetic",
    # features
    "build_features",
    "get_feature_columns",
    "validate_no_leakage",
]
