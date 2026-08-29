"""Lab intelligence — reflection, promotion, discovery, evaluation, pipeline."""
try:
    from lab.reflection import ReflectionPipeline, CandidateLesson, ExperimentResult
    from lab.discovery import LabDiscovery
    from lab.context import LabContext
    from lab.evaluator import Evaluator, EvaluationResult, DimensionScore, format_report, format_comparison
    from lab.pipeline import LearningPipeline, TrainingRun, LearningProposal
    from lab.brief import StructuredBrief
    from lab.trajectory import Trajectory, TrajectoryRecord, events_to_trajectory
    from lab.projection import LabProjector, wire_lab
except ImportError:
    from workerkit.lab.reflection import ReflectionPipeline, CandidateLesson, ExperimentResult
    from workerkit.lab.discovery import LabDiscovery
    from workerkit.lab.context import LabContext
    from workerkit.lab.evaluator import Evaluator, EvaluationResult, DimensionScore, format_report, format_comparison
    from workerkit.lab.pipeline import LearningPipeline, TrainingRun, LearningProposal
    from workerkit.lab.brief import StructuredBrief
    from workerkit.lab.trajectory import Trajectory, TrajectoryRecord, events_to_trajectory
    from workerkit.lab.projection import LabProjector, wire_lab

__all__ = [
    "ReflectionPipeline", "CandidateLesson", "ExperimentResult",
    "LabDiscovery", "LabContext",
    "Evaluator", "EvaluationResult", "DimensionScore", "format_report", "format_comparison",
    "LearningPipeline", "TrainingRun", "LearningProposal",
    "StructuredBrief",
    "Trajectory", "TrajectoryRecord", "events_to_trajectory",
    "LabProjector", "wire_lab",
]
