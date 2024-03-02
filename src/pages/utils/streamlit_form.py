import streamlit as st
from typing import Dict, Any, Callable
from operator import lt, le, gt, ge, eq, ne


class StreamlitForm:
    COMPARISON_OPERATORS: Dict[str, Callable] = {
        "lt": lt,
        "le": le,
        "gt": gt,
        "ge": ge,
        "eq": eq,
        "ne": ne,
    }
    SPECIAL_CHAR_MAPPING: Dict[str, str] = {
        "Double New Line (\\n\\n)": "\n\n",
        "New Line (\\n)": "\n",
        "Carriage Return (\\r)": "\r",
        'Space (" ")': " ",
        'Empty String ("")': "",
    }
    REVERSE_SPECIAL_CHAR_MAPPING: Dict[str, str] = {
        v: k for k, v in SPECIAL_CHAR_MAPPING.items()
    }
    WIDGET_MAPPING: Dict[str, Callable] = {
        "string": st.text_input,
        "number": st.number_input,
        "select": st.selectbox,
        "checkbox": st.checkbox,
        "multi_select": st.multiselect,
    }

    def __init__(self, form_config: Dict[str, Any]):
        self.form_config: Dict[str, Any] = form_config

    def generate_form(
        self, form_values: Dict[str, Any], name: str, submit_button_label: str
    ) -> bool:
        with st.form(key=name):
            for param, details in self.form_config["params"].items():
                widget_func = self.WIDGET_MAPPING.get(details["type"])
                if widget_func:
                    widget_args = self._build_widget_args(
                        name, param, details, form_values
                    )
                    form_values[param] = widget_func(**widget_args)
            submit_button_clicked = st.form_submit_button(label=submit_button_label)
            if submit_button_clicked and "separators" in form_values:
                form_values["separators"] = [
                    self.SPECIAL_CHAR_MAPPING.get(value, value)
                    for value in form_values["separators"]
                ]
            return submit_button_clicked

    def validate_form_values(self, form_values: Dict[str, Any]) -> bool:
        validations = self.form_config.get("validations", [])
        constants = self.form_config.get("constants", {})
        for validation in validations:
            rule = validation["rule"]
            field1, operator, field2 = rule
            value1 = form_values.get(field1)
            value2 = constants.get(field2, form_values.get(field2, field2))
            if not self._evaluate_rule(value1, operator, value2):
                st.error(validation["message"])
                return False
        return True

    @staticmethod
    def _evaluate_rule(value1: Any, operator: str, value2: Any) -> bool:
        comparison_func = StreamlitForm.COMPARISON_OPERATORS.get(operator)
        if not comparison_func:
            raise ValueError(f"Unrecognized comparison operator: {operator}")
        return comparison_func(value1, value2)

    def _build_widget_args(
        self,
        name: str,
        param: str,
        details: Dict[str, Any],
        form_values: Dict[str, Any],
    ) -> Dict[str, Any]:
        widget_args = {"label": details["label"], "key": f"{name}_{param}"}
        if details["type"] == "number":
            widget_args.update(
                {
                    "min_value": details.get("min_value", 0),
                    "value": form_values.get(param, details.get("default", 0)),
                }
            )
        elif details["type"] in ["select", "multi_select"]:
            options = [
                self.REVERSE_SPECIAL_CHAR_MAPPING.get(option, option)
                for option in details["options"]
            ]
            widget_args["options"] = options
            if details["type"] == "select":
                default_value = self.REVERSE_SPECIAL_CHAR_MAPPING.get(
                    form_values.get(param, details.get("default")),
                    details.get("default"),
                )
                widget_args["index"] = (
                    options.index(default_value) if default_value in options else 0
                )
            else:
                default_values = [
                    self.REVERSE_SPECIAL_CHAR_MAPPING.get(value, value)
                    for value in form_values.get(param, details.get("default", []))
                ]
                widget_args["default"] = default_values
        elif details["type"] == "checkbox":
            widget_args["value"] = form_values.get(param, details.get("default", False))
        else:
            widget_args["value"] = form_values.get(param, details.get("default", ""))
        return widget_args
