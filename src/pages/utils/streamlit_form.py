import streamlit as st
from typing import Dict, Any, Callable


def comparison_operator(operator: str) -> Callable[[Any, Any], bool]:
    return {
        "lt": lambda x, y: x < y,
        "le": lambda x, y: x <= y,
        "gt": lambda x, y: x > y,
        "ge": lambda x, y: x >= y,
        "eq": lambda x, y: x == y,
        "ne": lambda x, y: x != y,
    }[operator]


def special_char_mapping(reverse: bool = False) -> Dict[str, str]:
    mapping = {
        "Double New Line (\\n\\n)": "\n\n",
        "New Line (\\n)": "\n",
        "Carriage Return (\\r)": "\r",
        'Space (" ")': " ",
        'Empty String ("")': "",
    }
    return {v: k for k, v in mapping.items()} if reverse else mapping


def widget_mapping() -> Dict[str, Callable]:
    return {
        "string": st.text_input,
        "number": st.number_input,
        "select": st.selectbox,
        "checkbox": st.checkbox,
        "multi_select": st.multiselect,
    }


class StreamlitForm:
    def __init__(self, form_config: Dict[str, Any]):
        self.form_config = form_config

    def generate_form(
        self, form_values: Dict[str, Any], name: str, submit_button_label: str
    ) -> bool:
        with st.form(key=name):
            for param, details in self.form_config["params"].items():
                widget_func = widget_mapping().get(details["type"])
                if widget_func:
                    widget_args = self._build_widget_args(
                        name, param, details, form_values
                    )
                    form_values[param] = widget_func(**widget_args)
            submit_button_clicked = st.form_submit_button(label=submit_button_label)
            if submit_button_clicked and "separators" in form_values:
                form_values["separators"] = [
                    special_char_mapping().get(value, value)
                    for value in form_values["separators"]
                ]
            return submit_button_clicked

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
        return comparison_operator(operator)(value1, value2)

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
                {"min_value": details.get("min_value", 0), "value": default}
            )
        elif details["type"] in ["select", "multi_select"]:
            options = self._get_options(details)
            widget_args["options"] = options
            if details["type"] == "select":
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
                special_char_mapping(reverse=True).get(option, option)
                for option in form_values.get(param, details.get("default", []))
            ]
        else:
            default = form_values.get(param, details.get("default", ""))
        return default

    def _get_options(self, details: Dict[str, Any]) -> list:
        return [
            special_char_mapping(reverse=True).get(option, option)
            for option in details["options"]
        ]
