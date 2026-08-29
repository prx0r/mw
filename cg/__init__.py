"""cg — evolution laboratory with real evaluation interface."""
try:
    from cg.evolve import WorldPack, EvolutionLab, Mutation, CapabilityClaim, Replay
    from cg.evolve import Evaluator, DeterministicMockEvaluator, LiveEvaluator, EvaluationResult
except ImportError:
    from workerkit.cg.evolve import WorldPack, EvolutionLab, Mutation, CapabilityClaim, Replay
    from workerkit.cg.evolve import Evaluator, DeterministicMockEvaluator, LiveEvaluator, EvaluationResult
__all__ = ["WorldPack", "EvolutionLab", "Mutation", "CapabilityClaim", "Replay",
           "Evaluator", "DeterministicMockEvaluator", "LiveEvaluator", "EvaluationResult"]
