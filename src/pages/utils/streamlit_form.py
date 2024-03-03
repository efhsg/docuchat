import streamlit as st
from typing import Dict, Any, Callable, Optional
from logging import Logger as StandardLogger

from injector import get_logger


def get_comparison_operator(operator: str) -> Callable[[Any, Any], bool]:
    operators = {
        "lt": lambda x, y: x < y,
        "le": lambda x, y: x <= y,
        "gt": lambda x, y: x > y,
        "ge": lambda x, y: x >= y,
        "eq": lambda x, y: x == y,
        "ne": lambda x, y: x != y,
    }
    return operators[operator]


class StreamlitForm:
    _widget_mapping: Dict[str, Callable] = {
        "string": st.text_input,
        "number": st.number_input,
        "select": st.selectbox,
        "checkbox": st.checkbox,
        "multi_select": st.multiselect,
    }
    _special_char_mapping: Dict[str, str] = {
        "Double New Line (\\n\\n)": "\n\n",
        "New Line (\\n)": "\n",
        "Carriage Return (\\r)": "\r",
        'Space (" ")': " ",
        'Empty String ("")': "",
    }
    _special_char_mapping_reverse: Dict[str, str] = {
        v: k for k, v in _special_char_mapping.items()
    }

    def __init__(
        self,
        form_config: Dict[str, Any],
        logger: StandardLogger = None,
    ):
        self.form_config = form_config
        self.logger = logger or get_logger()

    def generate_form(
        self, form_values: Dict[str, Any], name: str, submit_button_label: str
    ) -> Optional[Dict[str, Any]]:
        updated_form_values = form_values.copy()
        with st.form(key=name):
            for param, details in self.form_config["fields"].items():
                widget_func = self._widget_mapping.get(details["type"])
                if widget_func:
                    widget_args = self._build_widget_args(
                        name, param, details, updated_form_values
                    )
                    updated_form_values[param] = widget_func(**widget_args)
            submit_button_clicked = st.form_submit_button(label=submit_button_label)
            if submit_button_clicked:
                if "separators" in updated_form_values:
                    updated_form_values["separators"] = [
                        self._get_mapped_value(value)
                        for value in updated_form_values["separators"]
                    ]
                return updated_form_values
        return None

    def validate_form_values(self, form_values: Dict[str, Any]) -> bool:
        validations = self.form_config.get("validations", [])
        constants = self.form_config.get("constants", {})
        for validation in validations:
            if not self._evaluate_rule(validation, form_values, constants):
                st.error(validation["message"])
                return False
        return True

    def _evaluate_rule(
        self,
        validation: Dict[str, Any],
        form_values: Dict[str, Any],
        constants: Dict[str, Any],
    ) -> bool:
        rule = validation["rule"]
        field1, operator, field2 = rule
        value1 = form_values.get(field1)
        value2 = constants.get(field2, form_values.get(field2, field2))
        return get_comparison_operator(operator)(value1, value2)

    def _build_widget_args(
        self,
        name: str,
        param: str,
        details: Dict[str, Any],
        form_values: Dict[str, Any],
    ) -> Dict[str, Any]:
        widget_args = {"label": details["label"], "key": f"{name}_{param}"}
        default = self._get_default(details, form_values, param)
        if details["type"] == "number":
            widget_args.update(
                {"min_value": details.get("min_value"), "value": default}
            )
        elif details["type"] in ["select", "multi_select"]:
            options = [
                self._get_mapped_value(option, True) for option in details["options"]
            ]
            widget_args["options"] = options
            if details["type"] == "select":
                self.logger.info(options)
                self.logger.info(default)
                widget_args["index"] = (
                    options.index(default) if default in options else 0
                )
            else:
                widget_args["default"] = default
        elif details["type"] == "checkbox":
            widget_args["value"] = default
        else:
            widget_args["value"] = default
        return widget_args

    def _get_default(
        self, details: Dict[str, Any], form_values: Dict[str, Any], param: str
    ) -> Any:
        if details["type"] in ["select", "multi_select"]:
            default = [
                self._get_mapped_value(option, True)
                for option in form_values.get(param, details.get("default", []))
            ]
        else:
            default = form_values.get(param, details.get("default", ""))
        return default

    def _get_mapped_value(self, value: str, reverse: bool = False) -> str:
        mapping = (
            self._special_char_mapping_reverse
            if reverse
            else self._special_char_mapping
        )
        return mapping.get(value, value)
