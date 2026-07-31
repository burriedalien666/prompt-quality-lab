# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
"""
Core module for prompt migration and optimization.

This module provides the main functionality for migrating and optimizing prompts.
"""

import importlib

_LAZY_EXPORTS = {
    "PromptMigrator": ("prompt_ops.core.migrator", "PromptMigrator"),
    "BaseStrategy": ("prompt_ops.core.prompt_strategies", "BaseStrategy"),
    "BasicOptimizationStrategy": (
        "prompt_ops.core.prompt_strategies",
        "BasicOptimizationStrategy",
    ),
    "MetricBase": ("prompt_ops.core.metrics", "MetricBase"),
    "ExactMatchMetric": ("prompt_ops.core.metrics", "ExactMatchMetric"),
    "Evaluator": ("prompt_ops.core.evaluation", "Evaluator"),
    "StatisticalEvaluator": ("prompt_ops.core.evaluation", "StatisticalEvaluator"),
    "StatisticalResults": ("prompt_ops.core.evaluation", "StatisticalResults"),
    "create_evaluator": ("prompt_ops.core.evaluation", "create_evaluator"),
}
_LAZY_SUBMODULES = {
    "datasets",
    "evaluation",
    "metrics",
    "migrator",
    "model",
    "prompt_strategies",
    "quality",
}


def __getattr__(name):
    """Load AI-heavy core exports only when a caller requests them."""
    if name in _LAZY_SUBMODULES:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module

    try:
        module_name, attribute_name = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    module = importlib.import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value


__all__ = [
    "PromptMigrator",
    "BaseStrategy",
    "BasicOptimizationStrategy",
    "MetricBase",
    "ExactMatchMetric",
    "Evaluator",
    "StatisticalEvaluator",
    "StatisticalResults",
    "create_evaluator",
]
