# pyright: reportPrivateUsage=false

"""Unit-test suite for the `unstructured.partition.utils.ocr_models.ocr_interface` module."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from test_unstructured.unit_utils import (
    FixtureRequest,
    LogCaptureFixture,
    Mock,
    instance_mock,
    method_mock,
    property_mock,
)
from unstructured.partition.utils.config import ENVConfig
from unstructured.partition.utils.constants import (
    OCR_AGENT_PADDLE,
    OCR_AGENT_PADDLE_OLD,
    OCR_AGENT_TESSERACT,
    OCR_AGENT_TESSERACT_OLD,
)
from unstructured.partition.utils.ocr_models.ocr_interface import OCRAgent


class DescribeOCRAgent:
    """Unit-test suite for `unstructured.partition.utils...ocr_interface.OCRAgent` class."""

    def it_provides_access_to_the_configured_OCR_agent(
        self, _get_ocr_agent_cls_qname_: Mock, get_instance_: Mock, ocr_agent_: Mock
    ):
        _get_ocr_agent_cls_qname_.return_value = OCR_AGENT_TESSERACT
        get_instance_.return_value = ocr_agent_

        ocr_agent = OCRAgent.get_agent()

        _get_ocr_agent_cls_qname_.assert_called_once_with()
        get_instance_.assert_called_once_with(OCR_AGENT_TESSERACT)
        assert ocr_agent is ocr_agent_

    def but_it_raises_whan_no_such_ocr_agent_class_is_found(self, _get_ocr_agent_cls_qname_: Mock):
        _get_ocr_agent_cls_qname_.return_value = "Invalid.Ocr.Agent.Qname"
        with pytest.raises(ValueError) as exc_info:
            OCRAgent.get_agent()
        assert "must be set to a whitelisted module" in str(exc_info.value)

        _get_ocr_agent_cls_qname_.return_value = OCR_AGENT_TESSERACT
        for exception_cls in [ImportError, AttributeError]:
            with patch("importlib.import_module", side_effect=exception_cls), pytest.raises(
                RuntimeError
            ) as exc_info:
                OCRAgent.get_agent()
            assert "Could not get the OCRAgent instance" in str(exc_info.value)

    @pytest.mark.parametrize(
        ("OCR_AGENT", "expected_value"),
        [
            (OCR_AGENT_PADDLE, OCR_AGENT_PADDLE),
            (OCR_AGENT_PADDLE_OLD, OCR_AGENT_PADDLE),
            (OCR_AGENT_TESSERACT, OCR_AGENT_TESSERACT),
            (OCR_AGENT_TESSERACT_OLD, OCR_AGENT_TESSERACT),
        ],
    )
    def it_computes_the_OCR_agent_qualified_module_name(
        self, OCR_AGENT: str, expected_value: str, OCR_AGENT_prop_: Mock
    ):
        OCR_AGENT_prop_.return_value = OCR_AGENT
        assert OCRAgent._get_ocr_agent_cls_qname() == expected_value

    @pytest.mark.parametrize("OCR_AGENT", [OCR_AGENT_PADDLE_OLD, OCR_AGENT_TESSERACT_OLD])
    def and_it_logs_a_warning_when_the_OCR_AGENT_module_name_is_obsolete(
        self, caplog: LogCaptureFixture, OCR_AGENT: str, OCR_AGENT_prop_: Mock
    ):
        OCR_AGENT_prop_.return_value = OCR_AGENT
        OCRAgent._get_ocr_agent_cls_qname()
        assert f"OCR agent name {OCR_AGENT} is outdated " in caplog.text

    # -- fixtures --------------------------------------------------------------------------------

    @pytest.fixture()
    def get_instance_(self, request: FixtureRequest):
        return method_mock(request, OCRAgent, "get_instance")

    @pytest.fixture()
    def _get_ocr_agent_cls_qname_(self, request: FixtureRequest):
        return method_mock(request, OCRAgent, "_get_ocr_agent_cls_qname")

    @pytest.fixture()
    def ocr_agent_(self, request: FixtureRequest):
        return instance_mock(request, OCRAgent)

    @pytest.fixture()
    def OCR_AGENT_prop_(self, request: FixtureRequest):
        return property_mock(request, ENVConfig, "OCR_AGENT")
