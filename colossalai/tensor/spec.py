from enum import Enum
from typing import Tuple, List
from colossalai.context.parallel_mode import ParallelMode

class ComputePattern(Enum):
    TP1DRow = 1
    TP1DCol = 2
    ZeRO = 3
    DP = 4


class ParallelAction(object):
    def __init__(self, priority=0, compute_pattern=ComputePattern.DP, parallel_mode=ParallelMode.DATA) -> None:
        self.priority = priority
        self.compute_pattern = compute_pattern
        self.parallel_mode = parallel_mode


class TensorSpec(object):
    """
    It contains two aspects of information: 
    First, How are tensors distributed in Heterougenous memory space.
    Second, if the tensor is a model parameter, the Spec contains the 
    parallel computation pattern of the Operator (Layer).
    We have to consider the hybrid parallel mode.
    """
    # a list of parallel actions.
    # For example: On 8 GPUs, a hybrid parallel strategy is applied using
    # using ZeRO with DP-degree = 4 and 1DRowTP with TP-degree = 2.
    # parallel_action_list = [
    # ParallelAction(10, ComputePattern.ZeRO, gpc.get_group(ParallelMode.DATA)),
    # ParallelAction(1, ComputePattern.TP1DRow, gpc.get_group(ParallelMode.PARALLEL_1D))
    # ]
    # When the ColoTensor is initialized,
    # we first splitting tensor according to ParallelAction of ZeRO,
    # then splitting tensor according to ParallelAction of TP1DRow.
    # During Linear computation
    # Before Linear Op, we gather the tensors according to ZeRO.
    # We perform Linear Op according to compute pattern of TP1DRow.
    # After Linear Op, we split the tensors according to ZeRO.
    def __init__(self, parallel_action_list: List[ParallelAction] = []):
        self._parallel_action_list = parallel_action_list
        self.sort()

    @property
    def parallel_action_list(self):
        return self._parallel_action_list

    @property
    def num_action(self):
        return len(self._parallel_action_list)

    @property
    def compute_patterns(self):
        return [parallel_action.compute_pattern for parallel_action in self._parallel_action_list]

    def sort(self):
        if len(self._parallel_action_list) > 0:
            self._parallel_action_list.sort(key=lambda parallel_action : parallel_action.priority)
    
    def get_action_by_compute_pattern(self, compute_pattern: ComputePattern):
        for parallel_action in self._parallel_action_list:
            if parallel_action.compute_pattern == compute_pattern:
                return parallel_action
        return None