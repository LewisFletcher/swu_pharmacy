from django.apps import AppConfig


class ThemeConfig(AppConfig):
    name = 'theme'

    def ready(self):
        from crispy_tailwind.templatetags.tailwind_field import CrispyTailwindFieldNode

        from .crispy import daisy_css_container

        CrispyTailwindFieldNode.default_container = daisy_css_container
