import json


def convert_value(value: str, parameter_type: str):
    """
    Convert user input into the expected MCP parameter type.
    """

    if parameter_type == "integer":
        return int(value)

    if parameter_type == "number":
        return float(value)

    if parameter_type == "boolean":
        if value.lower() in ("true", "yes", "1"):
            return True

        if value.lower() in ("false", "no", "0"):
            return False

        raise ValueError("Enter true or false.")

    if parameter_type in ("array", "object"):
        return json.loads(value)

    return value


def collect_arguments(input_schema: dict) -> dict:
    """
    Collect tool arguments dynamically from the MCP input schema.
    """

    arguments = {}

    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])

    for name, schema in properties.items():

        parameter_type = schema.get("type", "string")
        is_required = name in required

        while True:

            prompt = f"{name} ({parameter_type})"

            if "default" in schema:
                prompt += f" [default: {schema['default']}]"
            elif not is_required:
                prompt += " [optional]"

            value = input(f"{prompt}: ").strip()

            if not value:
                if is_required:
                    print("This parameter is required.")
                    continue

                break

            try:
                arguments[name] = convert_value(
                    value,
                    parameter_type
                )
                break

            except ValueError as error:
                print(f"Invalid input: {error}")

    return arguments