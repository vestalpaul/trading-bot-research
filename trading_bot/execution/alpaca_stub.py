"""Placeholder only. Live order routing intentionally not implemented in v1."""


class AlpacaBrokerStub:
    simulation_only = True

    def submit_order(self, *args, **kwargs):
        raise NotImplementedError("Live trading is disabled in this repository.")
