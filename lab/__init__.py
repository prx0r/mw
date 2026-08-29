"""Lab intelligence — reflection, promotion, discovery, evaluation, pipeline."""
try:
    from lab.reflection import ReflectionPipeline, CandidateLesson, ExperimentResult
    from lab.discovery import LabDiscovery
    from lab.context import LabContext
    from lab.evaluator import Evaluator, EvaluationResult, DimensionScore, format_report, format_comparison
    from lab.brief import StructuredBrief
    from lab.trajectory import Trajectory, TrajectoryRecord, events_to_trajectory
except ImportError:
    try:
        from workerkit.lab.reflection import ReflectionPipeline, CandidateLesson, ExperimentResult
        from workerkit.lab.discovery import LabDiscovery
        from workerkit.lab.context import LabContext
        from workerkit.lab.evaluator import Evaluator, EvaluationResult, DimensionScore, format_report, format_comparison
        from workerkit.lab.brief import StructuredBrief
        from workerkit.lab.trajectory import Trajectory, TrajectoryRecord, events_to_trajectory
    except ImportError:
        pass

__all__ = [
    "ReflectionPipeline", "CandidateLesson", "ExperimentResult",
    "LabDiscovery", "LabContext",
    "Evaluator", "EvaluationResult", "DimensionScore", "format_report", "format_comparison",
    "StructuredBrief",
    "Trajectory", "TrajectoryRecord", "events_to_trajectory",
]
