import torch
import torch.nn as nn
from typing import Optional, Mapping, Union

from ttach import functional as F
from ttach.base import Merger, Compose


class ConfidenceTTAWrapper(nn.Module):
    """Wrap PyTorch nn.Module (segmentation model) with test time augmentation transforms
    Args:
        model (torch.nn.Module): segmentation model with single input and single output
            (.forward(x) should return either torch.Tensor or Mapping[str, torch.Tensor])
        transforms (ttach.Compose): composition of test time transforms
        merge_mode (str): method to merge augmented predictions mean/gmean/max/min/sum/tsharpen
        output_mask_key (str): if model output is `dict`, specify which key belong to `mask`
    """

    def __init__(
            self,
            model: nn.Module,
            transforms: Compose,
            output_mask_key: Optional[str] = None,
    ):
        super().__init__()
        self.model = model
        self.transforms = transforms
        self.output_key = output_mask_key

    def forward(
            self, image: torch.Tensor, *args
    ) -> Union[torch.Tensor, Mapping[str, torch.Tensor]]:
        merger = CustomMerger()

        for transformer in self.transforms:
            augmented_image = transformer.augment_image(image)
            augmented_output = self.model(augmented_image, *args)
            if self.output_key is not None:
                augmented_output = augmented_output[self.output_key]
            deaugmented_output = transformer.deaugment_mask(augmented_output)
            merger.append(deaugmented_output)

        result = merger.result
        if self.output_key is not None:
            result = {self.output_key: result}

        return result


class CustomMerger:

    def __init__(self, *args, **kwargs):
        self._current_result = None
        self._current_confidence = None

    def _get_confidence(self, x):
        h, w = x.shape[2:]
        x = x.view(x.shape[0], -1)
        x = torch.abs(x - 0.5)
        non_confident = (x < 0.2).sum(dim=-1)
        return 1. - non_confident.float() / (h * w)

    def append(self, x):
        if self._current_result is None:
            self._current_result = x
            self._current_confidence = self._get_confidence(x)
        else:
            confidence = self._get_confidence(x)
            mask = self._current_confidence < confidence
            self._current_result[mask] = x[mask]

    @property
    def result(self):
        return self._current_result
