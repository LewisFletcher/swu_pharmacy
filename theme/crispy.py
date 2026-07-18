from crispy_tailwind.tailwind import CSSContainer

INPUT = "input w-full"

daisy_css_container = CSSContainer(
    {
        "text": INPUT,
        "number": INPUT,
        "email": INPUT,
        "url": INPUT,
        "password": INPUT,
        "date": INPUT,
        "datetime": INPUT,
        "time": INPUT,
        "textarea": "textarea w-full",
        "select": "select w-full",
        "checkbox": "checkbox",
    }
)
