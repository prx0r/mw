"""cg — deterministic evolution laboratory."""
try:
    from cg.evolve import WorldPack, EvolutionLab, Mutation, CapabilityClaim, Replay
except ImportError:
    from workerkit.cg.evolve import WorldPack, EvolutionLab, Mutation, CapabilityClaim, Replay
__all__ = ["WorldPack", "EvolutionLab", "Mutation", "CapabilityClaim", "Replay"]
