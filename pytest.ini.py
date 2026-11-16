import warnings
warnings.filterwarnings(
    "ignore",
    message="Your application has authenticated using end user credentials from Google Cloud SDK without a quota project.*",
    category=UserWarning
)