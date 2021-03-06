# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import pytest

import numpy as np
import tensorflow as tf
from tensorflow_addons.activations import gelu
from tensorflow_addons.activations.gelu import _gelu_py
from tensorflow_addons.utils import test_utils


@pytest.mark.parametrize("dtype", [np.float16, np.float32, np.float64])
def test_gelu(dtype):
    x = tf.constant([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=dtype)
    expected_result = tf.constant(
        [-0.04540229, -0.158808, 0.0, 0.841192, 1.9545977], dtype=dtype
    )
    test_utils.assert_allclose_according_to_type(gelu(x), expected_result)

    expected_result = tf.constant(
        [-0.04550028, -0.15865526, 0.0, 0.8413447, 1.9544997], dtype=dtype
    )
    test_utils.assert_allclose_according_to_type(gelu(x, False), expected_result)


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
@pytest.mark.parametrize("approximate", [True, False])
def test_same_as_py_func(dtype, approximate):
    np.random.seed(100)
    for _ in range(20):
        verify_funcs_are_equivalent(dtype, approximate)


def verify_funcs_are_equivalent(dtype, approximate):
    x_np = np.random.uniform(-10, 10, size=(4, 4)).astype(dtype)
    x = tf.convert_to_tensor(x_np)
    with tf.GradientTape(persistent=True) as t:
        t.watch(x)
        y_native = gelu(x, approximate=approximate)
        y_py = _gelu_py(x, approximate=approximate)
    test_utils.assert_allclose_according_to_type(y_native, y_py)
    grad_native = t.gradient(y_native, x)
    grad_py = t.gradient(y_py, x)
    # TODO: lower atol to 1e-6
    # currently it doesn't work.
    # It necessitates changing the Python or C++ implementation.
    test_utils.assert_allclose_according_to_type(grad_native, grad_py, atol=1e-5)


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
@pytest.mark.parametrize("approximate", [True, False])
def test_theoretical_gradients(dtype, approximate):
    # Only test theoretical gradients for float32 and float64
    # because of the instability of float16 while computing jacobian
    x = tf.constant([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=dtype)

    theoretical, numerical = tf.test.compute_gradient(
        lambda x: gelu(x, approximate=approximate), [x]
    )
    test_utils.assert_allclose_according_to_type(theoretical, numerical, atol=1e-4)
