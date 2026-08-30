from slopstream import config


def get_provider():
    if config.VIDEO_PROVIDER == "fal":
        from slopstream.providers.fal_provider import FalProvider

        return FalProvider()
    if config.VIDEO_PROVIDER == "replicate":
        from slopstream.providers.replicate_provider import ReplicateProvider

        return ReplicateProvider()
    if config.VIDEO_PROVIDER == "mock":
        from slopstream.providers.mock_provider import MockProvider

        return MockProvider()
    raise ValueError(f"Unknown VIDEO_PROVIDER: {config.VIDEO_PROVIDER}")
